"""Opt-in semantic check through an owner-approved primary OpenCode agent.

Uses the owner's existing OpenCode authentication, not the isolated fake profile.
Only supplied test records are synthetic/public. Ordinary profile context,
including config-directory AGENTS.md, and OpenCode session retention still apply.
No raw response/config is printed or saved by this script. This is not a clean
profile, permission-confinement or native-ingestion acceptance test.
Run explicitly with --live --agent APPROVED_AGENT --model PROVIDER/MODEL.
"""

import argparse
import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from runtime_read_probe import validate_scope


ROOT = Path(__file__).resolve().parents[1]


def decoded(text, stage):
    try:
        return json.loads(text)
    except ValueError as error:
        raise RuntimeError(
            f"Non-JSON output during {stage}: {getattr(error, 'msg', 'decode failure')}; "
            f"starts_json={text.lstrip().startswith('{')}, ansi={chr(27) in text}; contents withheld"
        ) from None


def prepare_environment(agent_name, approved_model):
    provider, separator, model_id = approved_model.partition("/")
    if not separator or not provider or not model_id or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", agent_name):
        raise RuntimeError("Supply an approved primary agent and provider/model")
    expected_model = {"providerID": provider, "modelID": model_id}
    env = dict(os.environ)
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
    if version.returncode or version.stdout.strip() != "1.18.32":
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


def call_model(env, prompt):
    # Reject tokens rather than guess at escaping; arbitrary captures need a
    # separately verified literal-input API, not this fixed-fixture CLI probe.
    if "@" in prompt or re.search(r"!\s*`", prompt):
        raise RuntimeError("Refusing native preprocessing tokens in model input")
    with os.fdopen(os.memfd_create("opencode-synthetic-response", os.MFD_CLOEXEC), "w+b") as output:
        result = subprocess.run(
            ["opencode", "run", "--pure", "--agent", env["SB_SEMANTIC_AGENT"], "--format", "json", prompt],
            cwd=ROOT, env=env, stdout=output, stderr=subprocess.PIPE, text=True, timeout=180,
        )
        output.seek(0)
        events = [decoded(line, "model event") for line in output.read().decode("utf-8").splitlines() if line.startswith("{")]
    tool_events = sum(event.get("type") == "tool_use" or bool(event.get("part", {}).get("tool")) for event in events)
    if result.returncode or tool_events:
        raise RuntimeError("Model call failed or attempted a tool; response withheld")
    text = "".join(event.get("part", {}).get("text", "") for event in events if event.get("type") == "text").strip()
    if text.startswith("```json\n") and text.endswith("```"):
        text = text[8:-3].strip()
    answer = decoded(text, "structured model response")
    if not isinstance(answer, dict):
        raise RuntimeError("Model response is not an object")
    return answer, {"runtime_exit": result.returncode, "tool_events": tool_events,
                    "steps": sum(event.get("type") == "step_start" for event in events)}


def semantic_checks(answer):
    expected = {
        "preferred_vent": "not_established", "trial_a_open_minutes": 18, "trial_a_closed_minutes": 24,
        "trial_b_open_minutes": 25, "trial_b_closed_minutes": 19, "trial_b_publication_date": None,
        "why_results_differ": "not_covered",
    }
    checks = {key: key in answer and answer[key] == value for key, value in expected.items()}
    checks["recommendation_attribution"] = answer.get("recommendation_claim_ids") in (["A2", "B2"], ["B2", "A2"])
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="authorize one synthetic model turn")
    parser.add_argument("--agent", required=True, help="owner-approved existing primary agent")
    parser.add_argument("--model", required=True, help="approved provider/model; routing must match")
    args = parser.parse_args()
    if not args.live:
        parser.error("live provider use is opt-in; pass --live only after owner approval")
    env = prepare_environment(args.agent, args.model)
    fixture = ROOT / "tests/fixtures/contract"
    files = [Path(path) for path in ("raw/trial-a.md", "raw/trial-b.md", "wiki/sources/trial-a.md", "wiki/sources/trial-b.md")]
    validate_scope(fixture, files)
    prompt = (
        "This is an owner-approved synthetic semantic test, not an ingest. Do not use any tools. "
        "Use ONLY the complete fictional records below. Return just one JSON object with these keys: "
        "All minute values must be integers. preferred_vent (open, closed, or not_established); trial_a_open_minutes; trial_a_closed_minutes; "
        "trial_b_open_minutes; trial_b_closed_minutes; trial_b_publication_date (ISO string or null); "
        "why_results_differ (not_covered if the records do not explain it); "
        "recommendation_claim_ids (array of claim IDs supporting the two author recommendations). "
        "Do not guess dates, generalize one trial, or choose the newer source by default.\n\n"
    )
    for path in files:
        prompt += f"BEGIN COMPLETE RECORD {path.as_posix()}\n{(fixture / path).read_text()}\nEND RECORD\n\n"
    answer, observed = call_model(env, prompt)
    checks = semantic_checks(answer)
    passed = all(checks.values())
    print(json.dumps({"agent": args.agent, "model": args.model, "synthetic_records": len(files),
                      "checks": checks, "observed": observed, "passed": passed}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"setup_error": type(error).__name__, "detail": str(error) if isinstance(error, RuntimeError) else "Output withheld; no semantic pass claimed"}))
        sys.exit(2)
