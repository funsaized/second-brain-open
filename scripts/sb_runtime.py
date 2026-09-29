"""Shared OpenCode runtime helpers for operator tools and opt-in live drivers.

Builds a temporary configuration overlay that denies every tool, adds exact
role grants, verifies the effective result with `opencode debug`, and runs a
named role with `opencode run --format json`. Raw config and events stay in
anonymous memory; nothing here prints credentials. Linux only (memfd).
"""

import fnmatch
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]


def validate_scope(root, relative_paths):
    """Reject absolute/traversal paths, symlinks and hardlinks before launch.

    This check is not a lock against concurrent filesystem replacement.
    """
    for relative in relative_paths:
        relative = Path(relative)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Scope must contain only confined relative files")
        path = root / relative
        if any(part.is_symlink() for part in (path, *path.parents)):
            raise ValueError("Symlinks are not allowed in the prepared corpus")
        if not path.is_file() or path.stat().st_nlink != 1:
            raise ValueError("Scope must contain regular, non-hardlinked files")


def decoded(text, stage):
    try:
        return json.loads(text)
    except ValueError as error:
        raise RuntimeError(
            f"Non-JSON output during {stage}: {getattr(error, 'msg', 'decode failure')}; "
            f"starts_json={text.lstrip().startswith('{')}, ansi={chr(27) in text}; contents withheld"
        ) from None


def prepare_environment(agent_name, approved_model, opencode_version="1.18.32", clean=False):
    """Environment whose overlay denies every tool; callers add role grants.

    clean=True drops inherited OPENCODE_* variables, e.g. when an operator agent
    running inside an OpenCode session launches a worker process.
    """
    provider, separator, model_id = approved_model.partition("/")
    if not separator or not provider or not model_id or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", agent_name):
        raise RuntimeError("Supply an approved primary agent and provider/model")
    expected_model = {"providerID": provider, "modelID": model_id}
    env = {k: v for k, v in os.environ.items() if not (clean and k.startswith("OPENCODE"))}
    env["SB_SEMANTIC_AGENT"] = agent_name
    env["SB_SEMANTIC_MODEL"] = approved_model
    for flag in (
        "OPENCODE_PURE", "OPENCODE_DISABLE_MODELS_FETCH", "OPENCODE_DISABLE_AUTOUPDATE",
        "OPENCODE_DISABLE_LSP_DOWNLOAD", "OPENCODE_DISABLE_SHARE",
        "OPENCODE_DISABLE_CLAUDE_CODE", "OPENCODE_DISABLE_EXTERNAL_SKILLS",
        "OPENCODE_DISABLE_PROJECT_CONFIG",
    ):
        env[flag] = "1"
    if not hasattr(os, "memfd_create"):
        raise RuntimeError("This opt-in diagnostic requires Linux memory-backed inspection")
    version = subprocess.run(["opencode", "--version"], env=env, capture_output=True, text=True, timeout=10)
    if version.returncode or version.stdout.strip() != opencode_version:
        raise RuntimeError("Review this live profile before using a different OpenCode release")
    # Keep the same environment for inspection and inference. The owner's native
    # authentication plugins remain available; --pure disables external plugins.
    info = subprocess.run(["opencode", "debug", "agent", agent_name, "--pure"],
                          cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    if info.returncode:
        raise RuntimeError("Primary-agent routing inspection failed")
    agent = decoded(info.stdout, "primary-agent routing inspection")
    model = agent.get("model", {})
    if agent.get("name") != agent_name or agent.get("mode") != "primary" or model != expected_model:
        raise RuntimeError("Primary-agent routing differs from the approved model")
    permissions = agent.get("permission", [])
    tools = {"*", "read", "edit", "bash", "task", "grep", "glob", "list", "lsp", "webfetch", "websearch", "skill", "question"}
    if not isinstance(permissions, list):
        raise RuntimeError("Unexpected native agent permission summary")
    tools.update(rule["permission"] for rule in permissions)
    overrides = decoded(env.get("OPENCODE_CONFIG_CONTENT", "{}"), "inherited inline configuration")
    overrides.update({
        "share": "disabled", "snapshot": False, "formatter": False, "lsp": False,
        "autoupdate": False, "model": approved_model, "small_model": approved_model,
        "enabled_providers": [provider], "permission": {tool: "deny" for tool in sorted(tools)},
    })
    agents = overrides.setdefault("agent", {})
    agents[agent_name] = {**agents.get(agent_name, {}), "model": approved_model,
                        "steps": 1, "permission": {tool: "deny" for tool in sorted(tools)}}
    for name in ("title", "summary", "compaction"):
        agents[name] = {**agents.get(name, {}), "disable": True}
    env["OPENCODE_CONFIG_CONTENT"] = json.dumps(overrides)
    config = inspect_config(env)
    if config.get("instructions") or config.get("skills", {}).get("urls"):
        raise RuntimeError("Additional instruction sources require separate review")
    # Disable configured MCPs rather than assuming an empty map erases inheritance.
    overrides["mcp"] = {name: {"enabled": False} for name in config.get("mcp", {})}
    env["OPENCODE_CONFIG_CONTENT"] = json.dumps(overrides)
    final = inspect_config(env)
    required = {"share": "disabled", "snapshot": False, "formatter": False, "lsp": False,
                "autoupdate": False, "model": approved_model, "small_model": approved_model,
                "enabled_providers": [provider]}
    if (any(final.get(key) != value for key, value in required.items())
            or any(item.get("enabled") is not False for item in final.get("mcp", {}).values())
            or final.get("instructions") or final.get("skills", {}).get("urls")
            or any(final.get("agent", {}).get(name, {}).get("disable") is not True for name in ("title", "summary", "compaction"))):
        raise RuntimeError("Final live profile does not match its approved settings")
    checked = subprocess.run(
        ["opencode", "debug", "agent", agent_name, "--pure"], cwd=ROOT,
        env=env,
        capture_output=True, text=True, timeout=30,
    )
    if checked.returncode:
        raise RuntimeError("Tool-disabled agent verification failed")
    selected = decoded(checked.stdout, "tool-disabled agent inspection")
    if selected.get("name") != agent_name or selected.get("model") != model or selected.get("mode") != "primary" or selected.get("steps") != 1 or selected.get("prompt") != agent.get("prompt"):
        raise RuntimeError("Selected primary agent, prompt, model or turn limit changed")
    rules = selected.get("permission", [])
    # external_directory is a gate, not a callable tool. OpenCode appends a native
    # tool-output directory exception; all file/tool actions must still be denied.
    # This ordinary-profile semantic test makes no filesystem-confinement claim.
    for tool in tools - {"*", "external_directory"}:
        matching = [rule for rule in rules if fnmatch.fnmatchcase(tool, rule["permission"])]
        if not matching or matching[-1].get("pattern") != "*" or matching[-1].get("action") != "deny":
            raise RuntimeError("The primary agent still has an unreviewed tool grant")
    return env


def inspect_config(env):
    # Large debug output can truncate on a pipe at CLI exit. Keep the unredacted
    # intermediate in anonymous RAM only, never on disk or in a public transcript.
    with os.fdopen(os.memfd_create("opencode-profile-inspection", os.MFD_CLOEXEC), "w+b") as output:
        result = subprocess.run(["opencode", "debug", "config", "--pure"], cwd=ROOT, env=env,
                                stdout=output, stderr=subprocess.PIPE, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError("Effective profile inspection failed")
        output.seek(0)
        return decoded(output.read().decode("utf-8"), "effective configuration inspection")


def debug(env, cwd, *args):
    with os.fdopen(os.memfd_create("sb-native-inspection", os.MFD_CLOEXEC), "w+b") as output:
        result = subprocess.run(["opencode", "debug", *args, "--pure"], cwd=cwd, env=env,
                                stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.PIPE, timeout=30)
        if result.returncode:
            raise RuntimeError("Native inspection failed; output withheld")
        output.seek(0)
        return decoded(output.read().decode(), "native inspection")


DENIED_TOOLS = ("edit", "bash", "task", "glob", "grep", "webfetch", "websearch", "question")


def verify_role(agent, role, prompt, allowed, model, steps, denied=DENIED_TOOLS):
    """Every non-deny effective rule must be one of the expected grants."""
    provider, _, model_id = model.partition("/")
    if (agent.get("name") != role or agent.get("mode") != "primary"
            or agent.get("prompt", "").strip() != prompt
            or agent.get("model") != {"providerID": provider, "modelID": model_id}
            or agent.get("steps") != steps):
        raise RuntimeError("Selected native role/prompt/route/steps mismatch")
    rules = agent.get("permission")
    if not isinstance(rules, list) or not rules:
        raise RuntimeError("Native permission rules unavailable")
    for index, rule in enumerate(rules):
        if rule.get("action") == "deny":
            continue
        pair = (rule.get("permission"), rule.get("pattern"))
        if any(later.get("permission") in ("*", pair[0]) and later.get("pattern") in ("*", pair[1])
               for later in rules[index + 1:]):
            continue
        if pair not in allowed:
            raise RuntimeError("Unexpected effective native permission grant; pattern withheld")
    for tool, pattern in allowed:
        matching = [r for r in rules if fnmatch.fnmatchcase(tool, r["permission"])
                    and fnmatch.fnmatchcase(pattern, r["pattern"])]
        if not matching or matching[-1].get("action") != "allow":
            raise RuntimeError("Approved native grant is not effective")
    for tool in denied:
        matched = [r for r in rules if fnmatch.fnmatchcase(tool, r["permission"])]
        if not matched or matched[-1].get("pattern") != "*" or matched[-1].get("action") != "deny":
            raise RuntimeError(f"Tool denial missing: {tool}")


SEARCH_TOOLS = ("grep", "glob")


def configure_worker(corpus, profile, role, skill, reads, agent, model, version, steps, search=False):
    """Overlay granting `role` exact reads plus its skill; verified before use.

    search=True also grants grep and glob. Their permission matches the search
    pattern, not the files it returns, so they are safe only when the corpus
    holds nothing but readable files; external_directory keeps them inside it.
    """
    env = prepare_environment(agent, model, version, clean=True)
    env.update(PWD=str(corpus), OPENCODE_CONFIG_DIR=str(profile))
    config = json.loads(env["OPENCODE_CONFIG_CONTENT"])
    config["compaction"] = {"auto": False}
    skill_dir = str(profile / f"skills/{skill}/*")
    config["agent"][role] = {"model": model, "steps": steps, "permission": {
        "*": "deny", "read": {"*": "deny", **{p: "allow" for p in reads}}, "edit": "deny",
        "question": "deny", "skill": {"*": "deny", skill: "allow"},
        **({tool: "allow" for tool in SEARCH_TOOLS} if search else {}),
        "external_directory": {"*": "deny", skill_dir: "allow"}}}
    env["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)
    effective = debug(env, corpus, "config")
    if not any(p.get("worktree") == str(corpus) for p in debug(env, corpus, "scrap")):
        raise RuntimeError("Native worktree does not match the staged corpus")
    provider = model.partition("/")[0]
    if (effective.get("model") != model or effective.get("small_model") != model
            or effective.get("instructions") or effective.get("enabled_providers") != [provider]
            or effective.get("skills", {}).get("paths") or effective.get("skills", {}).get("urls")
            or any(m.get("enabled") is not False for m in effective.get("mcp", {}).values())):
        raise RuntimeError("Unreviewed worker profile")
    output_gate = ("external_directory", str(Path(env.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
                                              / "opencode/tool-output/*"))
    body = (profile / f"agents/{role}.md").read_text().split("---", 2)[2].strip()
    allowed = {("read", p) for p in reads} | {("skill", skill), ("external_directory", skill_dir), output_gate}
    allowed |= {(tool, "*") for tool in SEARCH_TOOLS} if search else set()
    denied = tuple(t for t in DENIED_TOOLS if not (search and t in SEARCH_TOOLS))
    verify_role(debug(env, corpus, "agent", role), role, body, allowed, model, steps, denied)
    skills = [s for s in debug(env, corpus, "skill") if s.get("name") == skill]
    if len(skills) != 1 or Path(skills[0].get("location", "")) != profile / f"skills/{skill}/SKILL.md":
        raise RuntimeError("Designated skill is missing or shadowed")
    return env


def run_role(env, corpus, role, prompt, timeout):
    """One native turn; returns decoded events, exit code and seconds."""
    if "@" in prompt or re.search(r"!\s*`", prompt):
        raise RuntimeError("Refusing native preprocessing tokens in model input")
    started = time.monotonic()
    with os.fdopen(os.memfd_create("sb-worker-events", os.MFD_CLOEXEC), "w+b") as output:
        with subprocess.Popen(["opencode", "run", "--pure", "--dir", str(corpus), "--agent", role,
                               "--format", "json", prompt], cwd=corpus, env=env, stdin=subprocess.DEVNULL,
                              stdout=output, stderr=subprocess.DEVNULL, start_new_session=True) as process:
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        output.seek(0)
        events = [decoded(line, "native event") for line in output.read().decode().splitlines()
                  if line.startswith("{")]
    return events, process.returncode, round(time.monotonic() - started, 1)


def tool_calls(events):
    return [e["part"] for e in events if isinstance(e.get("part"), dict) and e["part"].get("tool")]


def answer_text(events):
    return "\n".join(e["part"].get("text", "") for e in events
                     if e.get("type") == "text" and isinstance(e.get("part"), dict)).strip()


CONTENT = re.compile(r"wiki/(?:sources|concepts|entities|synthesis)/[^\s\[\]|#`'\"()<>,;*]+")


def extract_citations(text):
    """Canonical content paths cited in an answer, as `.md` paths."""
    found = set()
    for token in re.findall(r"\[\[([^\]]+)\]\]", text):
        target = token.split("|", 1)[0].split("#", 1)[0].strip()
        if CONTENT.match(target):
            found.add(target)
    bare = re.sub(r"\[\[[^\]]+\]\]", " ", text)  # wikilink targets may contain spaces
    found.update(match.rstrip(".:") for match in CONTENT.findall(bare))
    return sorted({path if path.endswith(".md") else path + ".md" for path in found})


def relative_read(corpus, file_path):
    path = Path(file_path)
    if path.is_absolute():
        try:
            return path.relative_to(corpus).as_posix()
        except ValueError:
            return None
    return path.as_posix()


def full_read(state):
    """A read counts as complete only without offset/limit or truncation markers."""
    args, output = state.get("input", {}), state.get("output", "")
    return (args.get("offset", 1) in (0, 1) and "limit" not in args
            and not state.get("metadata", {}).get("truncated")
            and "(line truncated to" not in output and "(End of file" in output)
