"""Opt-in exact-patch native edits/query for the approved synthetic R8 packet.

No driver writes to wiki pages. Each native permission is answered once only
after matching one operator-validated full-file patch and its live preimage.
Requires the owner's separate four-path synthetic edit authorization.
"""

import argparse
import base64
import json
import os
from pathlib import Path
import re
import secrets
import selectors
import signal
import subprocess
import tempfile
import time
import urllib.request

from native_chat_proposal import (ARTIFACT_NAME, ARTIFACT_SHA256, CHANGES, MODEL,
                                 ROLES, ROOT, TODAY, debug, digest, verify_agent, verify_skills)
from runtime_read_probe import validate_scope
from semantic_probe import prepare_environment
from scripts import link_check


def write_local(path, text):
    # Staging is owner-frozen, not a defense against concurrent replacement.
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise RuntimeError("Linked local evidence destination")
    if path.exists():
        validate_scope(path.parent, [Path(path.name)])
        path.chmod(0o600)
    path.write_text(text)
    path.chmod(0o600)


def patch_for(path, old, new):
    if not new.endswith("\n"):
        raise RuntimeError("Approved Markdown must end with newline")
    header = f"*** Add File: {path}\n" if old is None else f"*** Update File: {path}\n@@\n"
    removed = "" if old is None else "".join("-" + line + "\n" for line in old.splitlines())
    return "*** Begin Patch\n" + header + removed + "".join("+" + line + "\n" for line in new.splitlines()) + "*** End Patch"


def validate_permission(request, parts, corpus, approved, used):
    if request.get("permission") != "edit" or len(request.get("patterns", [])) != 1:
        raise RuntimeError("Unapproved permission type or batch")
    name = request["patterns"][0]
    if name not in CHANGES or name not in approved or name in used:
        raise RuntimeError("Unapproved or repeated edit path")
    pointer = request.get("tool", {})
    matches = [p for p in parts if p.get("callID") == pointer.get("callID")
               and p.get("messageID") == pointer.get("messageID")]
    if len(matches) != 1 or matches[0].get("tool") != "apply_patch":
        raise RuntimeError("Permission not tied to an approved native apply_patch call")
    state = matches[0].get("state", {})
    if (state.get("status") != "running"
            or state.get("input", {}).get("patchText", "").strip() != approved[name]["patchText"]):
        raise RuntimeError("Native patch differs from validated patch")
    files = request.get("metadata", {}).get("files", [])
    if len(files) != 1 or files[0].get("filePath") != str(corpus / name) or files[0].get("movePath"):
        raise RuntimeError("Permission metadata differs from validated path")
    path = corpus / name
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise RuntimeError("Linked native destination")
    old = approved[name]["before"]
    if old is None:
        if path.exists():
            raise RuntimeError("New native destination already exists")
    else:
        validate_scope(corpus, [Path(name)])
        if path.read_text() != old:
            raise RuntimeError("Native preimage drift; preserve current work")
    return name


def check_pages(root):
    report = link_check.check(root)
    if report["errors"] or report["unsupported"] or report["unchecked"]:
        raise RuntimeError("Synthetic pages failed metadata/link validation")
    edges = set(map(tuple, report["links"]))
    source, concept = "wiki/sources/lantern-chat.md", "wiki/concepts/lantern-preferences.md"
    if (source, concept) not in edges or (concept, source) not in edges:
        raise RuntimeError("Reciprocal source/concept links missing")
    return report


def approve_packet(base):
    corpus = base / "corpus"
    validate_scope(base, [Path("proposal.json"), Path("summary.json"), Path("corpus/raw") / ARTIFACT_NAME])
    summary = json.loads((base / "summary.json").read_text())
    if digest((base / "proposal.json").read_bytes()) != summary["proposal_sha256"]:
        raise RuntimeError("Proposal packet drift")
    if digest((corpus / "raw" / ARTIFACT_NAME).read_bytes()) != ARTIFACT_SHA256:
        raise RuntimeError("Synthetic raw artifact drift")
    packet = json.loads((base / "proposal.json").read_text())
    if set(packet["files"]) != CHANGES:
        raise RuntimeError("Proposal path manifest mismatch")
    approved = {}
    for name, text in packet["files"].items():
        path = corpus / name
        old = None
        if path.exists():
            validate_scope(corpus, [Path(name)])
            old = path.read_text()
        if (digest(old.encode()) if old is not None else None) != packet["preimages"][name]:
            raise RuntimeError("Proposal preimage drift")
        # Operator-reviewed correction: all occurrences refer to Message 1's
        # enclosing timestamp, not the explicitly year-less trial wording.
        text = re.sub(r"2026-09-21(?!T)", "2026-09-21T01:30:00Z", text)
        if name == "wiki/log.md":
            if old is None or not text.startswith(old) or "partial" not in text[len(old):]:
                raise RuntimeError("Proposed log must preserve history and partial status")
            text += (f"\n## {TODAY} — Native synthetic apply — partial\n"
                     "- Source identity: synthetic-lantern-01, branch m4.\n"
                     "- Changed paths: wiki/sources/lantern-chat.md, wiki/concepts/lantern-preferences.md, wiki/index.md, wiki/log.md.\n"
                     "- Verification: exact-patch one-time approvals; raw and preimages checked by operator. Post-apply checker and query pending.\n"
                     "- Gaps: unknown change/message dates; unsupported generated battery claim; owner content acceptance pending.\n")
        approved[name] = {"before": old, "after": text, "patchText": patch_for(path, old, text)}
    with tempfile.TemporaryDirectory(prefix="sb-r8-review-", dir="/tmp/opencode") as temporary:
        review = Path(temporary)
        (review / "raw").mkdir()
        (review / "raw" / ARTIFACT_NAME).write_bytes((corpus / "raw" / ARTIFACT_NAME).read_bytes())
        for name, item in approved.items():
            path = review / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(item["after"])
        check_pages(review)
    write_local(base / "validated-patch.json", json.dumps(approved, indent=2) + "\n")
    patch_file = corpus / "approved-edits.md"
    # Native read truncates individual long lines, including JSON-escaped pages.
    write_local(patch_file, "# Exact operator-validated patches\n\n" + "\n".join(
        f"## {name}\n\n```patch\n{approved[name]['patchText']}\n```\n"
        for name in sorted(approved, key=lambda p: p == "wiki/log.md")))
    patch_file.chmod(0o400)
    return approved


def configure(base, editing):
    corpus, profile = base / "corpus", base / "profile"
    validate_scope(base, [Path("corpus/operation.md"), Path("corpus/raw") / ARTIFACT_NAME,
                         Path("validated-patch.json"), *[Path("profile") / name for role, skill in ROLES.items()
                         for name in (f"agents/{role}.md", f"skills/{skill}/SKILL.md")]])
    # Preparation changes only disposable role copies; the native role cannot.
    for role, skill in ROLES.items():
        for name in (f"agents/{role}.md", f"skills/{skill}/SKILL.md"):
            target = profile / name
            target.chmod(0o600)
            target.write_bytes((ROOT / "framework" / name).read_bytes())
            target.chmod(0o400)
    env = prepare_environment("dingus", MODEL)
    env.update(PWD=str(corpus), OPENCODE_CONFIG_DIR=str(profile))
    config = json.loads(env["OPENCODE_CONFIG_CONTENT"])
    config["compaction"] = {"auto": False}
    reads = {"operation.md", "approved-edits.md", f"raw/{ARTIFACT_NAME}", "instructions/wiki-contract.md",
             *CHANGES, *[f"templates/{kind}.md" for kind in ("source", "concept", "index", "log")]}
    if not editing:
        reads.remove("approved-edits.md")
    for role, skill in ROLES.items():
        permissions = {"*": "deny", "read": {"*": "deny", **{p: "allow" for p in sorted(reads)}},
                       "edit": {"*": "deny", **({p: "ask" for p in sorted(CHANGES)} if editing and role == "sb-ingestor" else {})},
                       "question": "deny", "skill": {"*": "deny", skill: "allow"},
                       "external_directory": {"*": "deny", str(profile / f"skills/{skill}/*"): "allow"}}
        config["agent"][role] = {"model": MODEL, "steps": 6, "permission": permissions}
    env["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)
    effective = debug(env, corpus, "config")
    if not any(p.get("worktree") == str(corpus) for p in debug(env, corpus, "scrap")):
        raise RuntimeError("Handoff native worktree mismatch")
    if (effective.get("model") != MODEL or effective.get("small_model") != MODEL
            or effective.get("instructions") or effective.get("enabled_providers") != ["openai"]
            or effective.get("skills", {}).get("paths") or effective.get("skills", {}).get("urls")
            or any(m.get("enabled") is not False for m in effective.get("mcp", {}).values())):
        raise RuntimeError("Unreviewed native handoff profile")
    output_gate = ("external_directory", str(Path(env.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "opencode/tool-output/*"))
    for role, skill in ROLES.items():
        body = (profile / f"agents/{role}.md").read_text().split("---", 2)[2].strip()
        allowed = {("read", p) for p in reads} | {("skill", skill), output_gate,
                   ("external_directory", str(profile / f"skills/{skill}/*"))}
        verify_agent(debug(env, corpus, "agent", role), role, body, allowed,
                     edits=CHANGES if editing and role == "sb-ingestor" else ())
    verify_skills(debug(env, corpus, "skill"), profile)
    manifest_path = corpus / "operation.md"
    manifest = json.loads(manifest_path.read_text().split("```json\n", 1)[1].split("\n```", 1)[0])
    manifest["scope"] = ("owner-authorized four-file native apply after operator validation; per-request once, content acceptance pending"
                         if editing else "owner-authorized read-only query; content acceptance pending")
    manifest["verified_scoped_grants"] = {r: config["agent"][r]["permission"] for r in ROLES}
    manifest["approved_reads"] = sorted(reads)
    manifest["validated_patch_sha256"] = digest((base / "validated-patch.json").read_bytes())
    manifest["backup"] = "validated-patch.json outside corpus retains exact before/after bytes; reject drift, no broad reset"
    manifest_path.chmod(0o600)
    manifest_path.write_text("# Operator-verified synthetic operation manifest\n\n```json\n" + json.dumps(manifest, indent=2) + "\n```\n")
    manifest_path.chmod(0o400)
    return env


class NativeServer:
    def __init__(self, env, corpus):
        self.corpus = corpus
        password = secrets.token_urlsafe(32)
        self.auth = "Basic " + base64.b64encode(f"opencode:{password}".encode()).decode()
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.process = subprocess.Popen(
            ["opencode", "serve", "--pure", "--hostname", "127.0.0.1", "--port", "0"], cwd=corpus,
            env={**env, "OPENCODE_SERVER_PASSWORD": password, "OPENCODE_SERVER_USERNAME": "opencode"},
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, start_new_session=True,
        )
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(self.process.stdout, selectors.EVENT_READ)
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    if not selector.select(timeout=1):
                        continue
                    line = self.process.stdout.readline().decode()
                    match = re.search(r"http://127\.0\.0\.1:(\d+)", line)
                    if match:
                        self.url = match.group()
                        return
                    if self.process.poll() is not None:
                        break
            raise RuntimeError("Native server failed to start")
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.process.poll() is None:
            os.killpg(self.process.pid, signal.SIGKILL)
        self.process.wait()
        self.process.stdout.close()

    def api(self, method, path, data=None):
        request = urllib.request.Request(self.url + path, method=method,
                                        data=json.dumps(data).encode() if data is not None else None,
                                        headers={"Authorization": self.auth, "Content-Type": "application/json",
                                                 "x-opencode-directory": str(self.corpus)})
        with self.opener.open(request, timeout=15) as response:
            body = response.read()
            return json.loads(body) if body else None

    def turn(self, role, prompt, approved=None):
        session = self.api("POST", "/session", {"agent": role})["id"]
        self.api("POST", f"/session/{session}/prompt_async", {
            "agent": role, "model": {"providerID": "openai", "modelID": "gpt-6-luna"},
            "parts": [{"type": "text", "text": prompt}],
        })
        used, answered = set(), set()
        try:
            deadline = time.monotonic() + 180
            while time.monotonic() < deadline:
                messages = self.api("GET", f"/session/{session}/message")
                parts = [p for m in messages for p in m.get("parts", [])]
                for request in self.api("GET", "/permission"):
                    if request.get("sessionID") != session or request["id"] in answered:
                        continue
                    if approved is None:
                        raise RuntimeError("Read-only turn requested permission")
                    # The log is last, after all other exact postimages exist.
                    if request.get("patterns") == ["wiki/log.md"] and any(
                        not (self.corpus / p).exists() or (self.corpus / p).read_text() != approved[p]["after"]
                        for p in CHANGES - {"wiki/log.md"}
                    ):
                        continue
                    fresh = self.api("GET", f"/session/{session}/message")
                    parts = [p for m in fresh for p in m.get("parts", [])]
                    if not any(p.get("tool") == "skill" and p.get("state", {}).get("status") == "completed"
                               and p["state"].get("input", {}).get("name") == ROLES[role] for p in parts):
                        raise RuntimeError("Native designated skill not loaded before edit")
                    name = validate_permission(request, parts, self.corpus, approved, used)
                    self.api("POST", f"/permission/{request['id']}/reply", {"reply": "once"})
                    used.add(name)
                    answered.add(request["id"])
                statuses = self.api("GET", "/session/status")
                assistants = [m for m in messages if m.get("info", {}).get("role") == "assistant"]
                if any(m["info"].get("error") for m in assistants):
                    raise RuntimeError("Native session error; details withheld")
                if assistants and statuses.get(session, {"type": "idle"}).get("type") == "idle" and all(m["info"].get("time", {}).get("completed") for m in assistants):
                    calls = [p for p in parts if p.get("type") == "tool"]
                    if any(p.get("state", {}).get("status") != "completed" for p in calls):
                        raise RuntimeError("Native tool failed")
                    text = "\n".join(p["text"] for m in assistants for p in m.get("parts", []) if p.get("type") == "text")
                    return {"text": text, "calls": calls, "approved_once": sorted(used)}
                time.sleep(0.25)
            raise RuntimeError("Native turn timed out")
        except BaseException:
            self.api("POST", f"/session/{session}/abort")
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live-approve-four-files", action="store_true")
    mode.add_argument("--live-query-only", action="store_true")
    args = parser.parse_args()
    base = args.base
    if base.parent != Path("/tmp/opencode") or not re.fullmatch(r"sb-native-r8-[a-z0-9_]+", base.name):
        parser.error("requires owner-authorized generated synthetic staging")
    if args.live_query_only:
        query(base)
        return
    corpus = base / "corpus"
    approved = approve_packet(base)
    env = configure(base, editing=True)
    protected = {
        p: digest(p.read_bytes()) for p in corpus.rglob("*") if p.is_file() and ".git" not in p.parts
        and p.relative_to(corpus).as_posix() not in CHANGES}
    profile_files = [base / "profile" / name for role, skill in ROLES.items()
                     for name in (f"agents/{role}.md", f"skills/{skill}/SKILL.md")]
    protected.update({p: digest(p.read_bytes()) for p in profile_files})
    protected[base / "export.json"] = digest((base / "export.json").read_bytes())
    original_files = {p.relative_to(corpus).as_posix() for p in corpus.rglob("*") if p.is_file() and ".git" not in p.parts}
    for name in CHANGES:
        if (corpus / name).exists():
            (corpus / name).chmod(0o600)
    server = NativeServer(env, corpus)
    try:
        result = server.turn("sb-ingestor", (
            f"Operator preflight passed. Exact operation-manifest path: {corpus / 'operation.md'} (worktree-relative: operation.md). "
            f"Exact approved patch file: {corpus / 'approved-edits.md'}. Working directory: {corpus}. "
            "Load your designated skill, then read those two files completely. "
            "The owner explicitly authorized one-time approvals of the four validated synthetic patches. "
            "This application stage supersedes the old proposal-only operation manifest's edit status, not its source scope. "
            "Use apply_patch exactly once per file, copying its exact fenced patch text from approved-edits.md; no reformulation. "
            "The three independent source/concept/index patches may be submitted in one tool-call batch; log last. "
            "The operator will hold the log permission until the other three exact postimages exist. No other edits. "
            "The operator will validate each tool request and reply once, never always. "
            "Do not claim owner content acceptance. Stop on any denial/drift. Report actual changed paths and partial status."
        ), approved)
        write_local(base / "native-ingest-response.txt", result["text"])
        write_local(base / "native-ingest-attempt.json", json.dumps({"approved_once": result["approved_once"],
            "tool_calls": [p["tool"] for p in result["calls"]]}, indent=2) + "\n")
        if set(result["approved_once"]) != CHANGES:
            raise RuntimeError("Native four-file application incomplete")
        for name, item in approved.items():
            if (corpus / name).read_text() != item["after"]:
                raise RuntimeError("Native postimage differs from approved patch")
        if any(digest(p.read_bytes()) != before for p, before in protected.items()):
            raise RuntimeError("Protected synthetic input changed")
        after_files = {p.relative_to(corpus).as_posix() for p in corpus.rglob("*") if p.is_file() and ".git" not in p.parts}
        if after_files != original_files | CHANGES:
            raise RuntimeError("Unexpected native corpus file set")
        check_pages(corpus)
        write_local(base / "native-ingest-result.json", json.dumps({"approved_once": result["approved_once"],
            "native_tool_calls": [p["tool"] for p in result["calls"]], "checker": "passed",
            "protected_bytes_unchanged": True, "owner_content_acceptance": "pending"}, indent=2) + "\n")
    finally:
        server.close()
    query(base)


def query(base):
    corpus = base / "corpus"
    env = configure(base, editing=False)
    before = {p: digest(p.read_bytes()) for p in corpus.rglob("*") if p.is_file() and ".git" not in p.parts}
    pages = sorted(p for p in CHANGES if p not in ("wiki/index.md", "wiki/log.md") and (corpus / p).exists())
    required = {"operation.md", "wiki/index.md", "instructions/wiki-contract.md", f"raw/{ARTIFACT_NAME}", *pages}
    server = NativeServer(env, corpus)
    try:
        result = server.turn("sb-researcher", (
            "Operator preflight verified your exact read grants and denied edits. Load your designated skill. "
            f"Exact operation-manifest path: {corpus / 'operation.md'}. Working directory: {corpus}. "
            f"Read the manifest, then index first for retrieval; all required full reads: {json.dumps(sorted(required))}. "
            f"Applied content pages currently present: {json.dumps(pages)}. "
            "If none exist, disclose no wiki ingest has been applied and answer directly from the approved raw artifact, "
            "not nonexistent source pages. Answer: What preferences were recorded, when did they change, "
            "and what supports the battery-life claim? Cite source page plus Message N, distinguish explicit dates "
            "from inference, user reports from generated assertions, and end with Read / Not covered. No writes."
        ))
        seen, loaded = set(), False
        for call in result["calls"]:
            state = call.get("state", {})
            if call["tool"] == "skill" and state.get("input", {}).get("name") == ROLES["sb-researcher"]:
                loaded = True
            elif call["tool"] == "read":
                path = corpus / state["input"]["filePath"]
                if str(path) not in {str(corpus / p) for p in required}:
                    raise RuntimeError("Query read outside requested evidence set")
                if (state["input"].get("offset", 1) != 1 or "limit" in state["input"]
                        or state.get("metadata", {}).get("truncated") or "(End of file" not in state.get("output", "")
                        or "(line truncated to" in state.get("output", "")):
                    raise RuntimeError("Query full-read evidence incomplete")
                seen.add(str(path))
            else:
                raise RuntimeError("Unexpected query tool")
        if not loaded or not {str(corpus / p) for p in required} <= seen:
            raise RuntimeError("Native query skill or required reads missing")
        after = {p: digest(p.read_bytes()) for p in corpus.rglob("*") if p.is_file() and ".git" not in p.parts}
        if before != after:
            raise RuntimeError("Query changed corpus bytes")
        write_local(base / "native-query.txt", result["text"])
        evidence = {"content_pages_present": pages, "native_query_skill_loaded": loaded,
                          "required_full_reads": len(required), "corpus_bytes_and_file_set_unchanged": True,
                          "native_query": str(base / "native-query.txt"), "query_tool_calls": [p["tool"] for p in result["calls"]],
                          "owner_content_acceptance": "pending"}
        write_local(base / "native-query-evidence.json", json.dumps(evidence, indent=2) + "\n")
        print(json.dumps(evidence, indent=2))
    finally:
        server.close()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(json.dumps({"passed": False, "error": str(error) if isinstance(error, RuntimeError) else type(error).__name__,
                          "recovery": "preserve staging; inspect actual native writes before retry"}))
        raise SystemExit(2)
