#!/usr/bin/env python3
"""Operator for the second-brain workers: stage, run, apply and undo.

An operator (the owner, or a primary agent using the second-brain-operator
skill) runs one operation at a time:

  capture fetch one URL without any model, keep the page's main content as
         Markdown and save it to raw/ with provenance frontmatter.
  pending list raw/ captures no source page references yet, oldest first.
  stage  copy the adopted wiki, the contract/templates and the operation's
         inputs into a new directory outside the vault, with a manifest of
         every vault file's hash.
  run    launch the worker role (sb-ingestor or sb-researcher) on that copy
         with exact read grants and every other tool denied, verify what it
         read, and save its proposal or answer.
  revise rerun the worker once, telling it why its proposal was refused.
  apply  validate the proposal (allowed paths, page cap, unchanged vault files,
         append-only log record, managed checker clean on the result), back up
         the files it replaces and write it into the vault.
  undo   restore an applied operation's files if nothing changed them since.

Workers never hold edit rights; only `apply` writes, and only under wiki/.
Settings come from VAULT/.opencode/second-brain/operator.json (see
framework/operator.example.json). Standard library only; Linux for `run`.
"""

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import textwrap

if __package__:
    from . import link_check
    from . import web_capture
    from .sb_runtime import (answer_text, configure_worker, full_read, relative_read, run_role, tool_calls,
                             validate_scope)
else:
    import link_check
    import web_capture
    from sb_runtime import (answer_text, configure_worker, full_read, relative_read, run_role, tool_calls,
                            validate_scope)


ROOT = Path(__file__).resolve().parents[1]
ROLES = {"ingest": ("sb-ingestor", "second-brain-ingest"), "compile": ("sb-ingestor", "second-brain-ingest"),
         "query": ("sb-researcher", "second-brain-query")}
CONTRACT = "instructions/wiki-contract.md"
INSTALLED = {
    "contract": (".opencode/instructions/second-brain/wiki-contract.md", "framework/instructions/wiki-contract.md"),
    "templates": ("templates/second-brain", "framework/templates"),
}
TEMPLATES = ("source", "concept", "entity", "synthesis")
CONFIG_KEYS = {"cli", "agent", "model", "opencode_version", "workdir", "max_pages", "steps", "timeout", "auto_apply"}
WRITABLE = re.compile(r"wiki/(?:sources|concepts|entities|synthesis)/.+\.md|wiki/index\.md")
RECORD = re.compile(r"## (\d{4}-\d{2}-\d{2}) — .+ — partial")
FILE_BLOCK = re.compile(r"^<<<FILE ([^\n]+)>>>\n(.*?)^<<<END FILE>>>[ \t]*$", re.M | re.S)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(path.read_bytes()) if path.is_file() else None


def load_config(vault, path=None):
    path = Path(path) if path else vault / ".opencode/second-brain/operator.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    missing = {"agent", "model", "opencode_version", "workdir"} - config.keys()
    if missing or set(config) - CONFIG_KEYS:
        raise ValueError(f"operator config needs {sorted(CONFIG_KEYS)}; missing {sorted(missing)}")
    config = {"max_pages": 10, "steps": 10, "timeout": 600, "auto_apply": True, **config}
    workdir = Path(config["workdir"]).expanduser().resolve()
    if workdir == vault.resolve() or vault.resolve() in workdir.parents:
        raise ValueError("operator workdir must be outside the vault")
    config["workdir"] = str(workdir)
    return config


def wiki_state(vault):
    """Hash of every adopted wiki file; refuses links like the checker does."""
    pages, _ = link_check.collect(vault)
    return {key: file_hash(vault / key) for key in pages}


CAPTURE_SUFFIXES = (".md", ".txt", ".html", ".htm")
MIN_WORDS, MAX_LINES, WRAP_AT = 150, 1900, 1500


def slugify(text, limit=60):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:limit].rstrip("-") or "capture"


def readable_lines(body):
    """Wrap only overlong prose lines so a worker can read every line in full; code is untouched."""
    out, fence = [], None
    for line in body.splitlines():
        marker = re.match(r"^(`{3,}|~{3,})", line)
        if marker and (fence is None or marker.group(1)[0] == fence[0]):
            fence = None if fence else marker.group(1)
        if fence is None and not marker and len(line) > WRAP_AT and not line.lstrip().startswith("|"):
            out.extend(textwrap.wrap(line, 500, break_long_words=False, break_on_hyphens=False))
        else:
            out.append(line)
    return "\n".join(out).rstrip("\n") + "\n"


def capture_text(url, final_url, body, meta, captured):
    header = {"url": url, "final_url": final_url if final_url != url else None, "title": meta["title"],
              "author": meta["author"], "published": meta["published"], "captured": captured,
              "fetched_with": "sb_operator capture (main-content extraction, no model)",
              "body_sha256": digest(body.encode())}
    return "---\n" + "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in header.items()) + "---\n\n" + body


def capture(vault, url, config_path=None, today=None, fetch=None):
    """Save one page's main content to raw/; refuses fragments and pages too long for one full read."""
    vault = Path(vault).resolve()
    load_config(vault, config_path)
    if not re.fullmatch(r"https?://[^\s@]{3,2000}", url):
        raise ValueError("capture takes one http(s) URL without spaces or @")
    text, kind, final_url = (fetch or web_capture.fetch)(url)
    if kind in ("text/plain", "text/markdown"):
        heading = re.search(r"(?m)^# (.+)$", text)
        body, meta = text, {"title": heading.group(1).strip() if heading else None, "author": None, "published": None}
    elif kind in ("text/html", "application/xhtml+xml"):
        body, meta = web_capture.extract(text, final_url)
    else:
        raise ValueError(f"unsupported content type {kind}; save the file into raw/ yourself")
    body = readable_lines(body)
    words, lines = len(body.split()), body.count("\n")
    if words < MIN_WORDS:
        raise ValueError(f"only {words} words of main content: the page may need JavaScript, a login or a "
                         "subscription. Save it with the Obsidian Web Clipper into raw/ instead")
    if lines > MAX_LINES:
        raise ValueError(f"{lines} lines is more than a worker can read in one pass ({MAX_LINES}); "
                         "save the page in parts into raw/ instead")
    captured = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    today = today or date.today().isoformat()
    (vault / "raw").mkdir(exist_ok=True)
    stem = f"raw/{today}-{slugify(meta['title'] or re.sub(r'^https?://', '', url))}"
    for n in range(1, 100):
        relative = stem + (f"-{n}" if n > 1 else "") + ".md"
        try:
            with open(vault / relative, "x", encoding="utf-8") as stream:
                stream.write(capture_text(url, final_url, body, meta, captured))
            break
        except FileExistsError:
            continue
    else:
        raise ValueError("too many captures with the same name")
    return {"raw": relative, "title": meta["title"], "words": words, "lines": lines}


def pending(vault):
    """Captures no source page references, oldest first; folders of multi-file captures count as referenced."""
    vault = Path(vault).resolve()
    pages, _ = link_check.collect(vault)
    referenced = {page["metadata"].get("raw") for key, page in pages.items() if key.startswith("wiki/sources/")}
    used_dirs = {str(Path(r).parent) for r in referenced if isinstance(r, str)} - {"raw"}
    found = []
    raw = vault / "raw"
    for path in (raw.rglob("*") if raw.is_dir() else ()):
        relative = path.relative_to(vault).as_posix()
        if (not path.is_file() or path.is_symlink() or path.suffix.lower() not in CAPTURE_SUFFIXES
                or any(part.startswith(".") for part in path.relative_to(raw).parts)
                or relative.startswith("raw/assets/") or relative in referenced
                or str(Path(relative).parent) in used_dirs):
            continue
        found.append((path.stat().st_mtime, relative))
    return [relative for _, relative in sorted(found)]


def stage(vault, kind, inputs=(), task=None, config_path=None, today=None, url=None):
    vault = Path(vault).resolve()
    if url is not None:
        if kind != "ingest" or inputs:
            raise ValueError("--url is for ingest and replaces --input")
        if not task or "@" in task or re.search(r"!\s*`", task):
            raise ValueError("ingest needs a plain-text --task without @ or !` tokens")
        inputs = [capture(vault, url, config_path, today)["raw"]]
    config = load_config(vault, config_path)
    role, skill = ROLES[kind]
    inputs = sorted(set(inputs))
    if kind == "query":
        if inputs or not task:
            raise ValueError("query takes --question and no inputs")
    elif not inputs or not task:
        raise ValueError(f"{kind} needs --input and --task")
    for item in inputs:
        valid = item.startswith("raw/") if kind == "ingest" else WRITABLE.fullmatch(item) and item != "wiki/index.md"
        if not valid or not link_check.canonical_parts(item):
            raise ValueError(f"{kind} input not allowed: {item}")
        validate_scope(vault, [Path(item)])
    if "@" in task or re.search(r"!\s*`", task):
        raise ValueError("task/question must be plain text without @ or !` preprocessing tokens")
    state = wiki_state(vault)
    today = today or date.today().isoformat()
    workdir = Path(config["workdir"])
    workdir.mkdir(parents=True, exist_ok=True, mode=0o700)
    op = workdir / f"{today}-{kind}-{secrets.token_hex(3)}"
    corpus, profile = op / "corpus", op / "profile"
    op.mkdir(mode=0o700)
    corpus.mkdir()
    profile.mkdir()
    copies = {key: vault / key for key in state}
    copies.update({item: vault / item for item in inputs})
    installed, public = INSTALLED["contract"]
    copies[CONTRACT] = vault / installed if (vault / installed).is_file() else ROOT / public
    if kind != "query":
        installed, public = INSTALLED["templates"]
        for name in TEMPLATES:
            local = vault / installed / f"{name}.md"
            copies[f"templates/{name}.md"] = local if local.is_file() else ROOT / public / f"{name}.md"
    for target, source in sorted(copies.items()):
        base = vault if source.is_relative_to(vault) else ROOT
        validate_scope(base, [source.relative_to(base)])
        path = corpus / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source.read_bytes())
    origin = {}
    for name in (f"agents/{role}.md", f"skills/{skill}/SKILL.md"):
        local = vault / ".opencode" / name
        source = local if local.is_file() else ROOT / "framework" / name
        base = vault if source.is_relative_to(vault) else ROOT
        validate_scope(base, [source.relative_to(base)])
        (profile / name).parent.mkdir(parents=True, exist_ok=True)
        (profile / name).write_bytes(source.read_bytes())
        origin[name] = {"from": "vault" if base == vault else "framework", "sha256": file_hash(source)}
    manifest = {"id": op.name, "kind": kind, "role": role, "skill": skill, "vault": str(vault), "date": today,
                "task": task, "inputs": inputs, "input_sha256": {i: file_hash(vault / i) for i in inputs},
                "wiki_preimages": state, "reads": sorted(copies) + ["operation.md"], "origin": origin,
                "config": {k: config[k] for k in sorted(config)}}
    (corpus / "operation.md").write_text(
        "# Operator-verified operation manifest\n\n```json\n" + json.dumps({
            "status": "operator preflight verifies these read grants before the worker starts",
            "operation": kind, "role": role, "task": task, "inputs": inputs, "date": today,
            "readable": f"{len(manifest['reads'])} staged files: every wiki page, the contract"
                        + (", page templates" if kind != "query" else "") + (", the inputs" if inputs else ""),
            "writes": "none; the worker returns a proposal and the operator validates and applies it"},
            indent=2) + "\n```\n")
    write_json(op / "manifest.json", manifest)
    subprocess.run(["git", "init", "--quiet", str(corpus)], check=True, capture_output=True)
    return op


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    path.chmod(0o600)


def corpus_state(corpus):
    return {p.relative_to(corpus).as_posix(): digest(p.read_bytes())
            for p in sorted(corpus.rglob("*")) if p.is_file() and ".git" not in p.relative_to(corpus).parts}


def worker_prompt(manifest, corpus):
    kind, config = manifest["kind"], manifest["config"]
    head = ("You are running under an operator. Your read grants were verified before this call; edits and all "
            "other tools are denied. Load your designated skill with the skill tool. "
            f"Working directory: {corpus}. The operation manifest is operation.md and the contract is {CONTRACT}. "
            "Read wiki/index.md first. ")
    if kind == "query":
        return head + (
            f"Question: {manifest['task']} Answer only from pages you actually read. Put exact vault-relative "
            "page paths such as wiki/sources/name.md beside each claim, with section locators. If the wiki does "
            "not answer, say so. End with a line starting 'Read:' and a line starting 'Not covered:'.")
    inputs = ", ".join(manifest["inputs"])
    source = ("This is an ingest: the input is an approved raw capture; use its path as the source page's raw "
              "field. When the capture has frontmatter, take the source page's url, author and published from it "
              f"and the date part of its captured timestamp as captured; otherwise use {manifest['date']}. "
              if kind == "ingest" else
              "This is a compile: the inputs are existing source notes; build concept, entity or synthesis pages "
              "from them and add the reciprocal links on those source notes. ")
    return head + source + (
        f"Task: {manifest['task']} Read these inputs completely before proposing: {inputs}. Readable files, by "
        f"exact path only (directory listings are not available): every page the index links, wiki/log.md, "
        f"{', '.join(f'templates/{name}.md' for name in TEMPLATES)}, the inputs and the manifest. "
        "Open candidate pages from the index as needed. "
        f"Today is {manifest['date']}. Propose at most {config['max_pages']} new or changed pages under "
        "wiki/sources, wiki/concepts, wiki/entities or wiki/synthesis, plus wiki/index.md when the catalog "
        "changes. Never propose wiki/log.md, raw/ or any other path. Reply with no outer code fence, in this "
        "format:\n<<<FILE path>>>\ncomplete Markdown with final newline\n<<<END FILE>>>\n(one block per page)\n"
        f"<<<LOG>>>\none log record whose heading is '## {manifest['date']} — <operation> — partial', followed "
        "by bullets for source identity, changed paths, contradictions, gaps and pending verification\n"
        "<<<NOTES>>>\ncoverage review, claim/locator notes and open questions.\n"
        "If nothing should change (for example an unchanged repeat) or you cannot finish (truncated or "
        "unreadable input, conflicting evidence you cannot represent), reply with only <<<NOTES>>> and the reason.")


def section(text, name):
    """Section body without an optional closing marker (<<<NAME>>> or <<<END NAME>>>)."""
    lines = text.strip().splitlines()
    if lines and lines[-1].strip() in (f"<<<{name}>>>", f"<<<END {name}>>>"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_proposal(text):
    files, end = {}, 0
    for match in FILE_BLOCK.finditer(text):
        name, body = match.group(1).strip(), match.group(2)
        if text[end:match.start()].strip() or name in files or re.search(r"(?m)^<<<", body):
            raise ValueError("unexpected text, marker or duplicate FILE block in proposal")
        files[name] = body
        end = match.end()
    rest = text[end:].strip()
    log, notes = None, rest
    if rest.startswith("<<<LOG>>>"):
        log, found, notes = rest.removeprefix("<<<LOG>>>").partition("<<<NOTES>>>")
        if not found:
            raise ValueError("proposal LOG section must be followed by NOTES")
        log = section(log, "LOG")
        if re.search(r"(?m)^<<<", log):
            raise ValueError("stray marker inside the LOG record")
    elif rest.startswith("<<<NOTES>>>"):
        notes = rest.removeprefix("<<<NOTES>>>")
    else:
        raise ValueError("proposal must end with LOG and NOTES (or NOTES only)")
    if files and not log:
        raise ValueError("a proposal with pages needs a LOG record")
    return {"files": files, "log": log, "notes": section(notes, "NOTES")}


def verify_events(manifest, corpus, events, returncode, before, after):
    """Worker evidence: designated skill, only complete in-scope reads, no writes."""
    calls = tool_calls(events)
    reads = {}
    for call in calls:
        state = call.get("state", {})
        if call["tool"] == "read" and state.get("status") == "completed":
            path = relative_read(corpus, state.get("input", {}).get("filePath", ""))
            reads[path] = reads.get(path, False) or full_read(state)
    required = {"wiki/index.md", CONTRACT, *manifest["inputs"]}
    checks = {
        "run_completed": returncode == 0 and bool(answer_text(events)),
        "skill_loaded": any(c["tool"] == "skill" and c.get("state", {}).get("status") == "completed"
                            and c["state"].get("input", {}).get("name") == manifest["skill"] for c in calls),
        "only_reads": all(c["tool"] in ("read", "skill") for c in calls),
        "reads_in_scope": all(p in manifest["reads"] for p in reads),
        "required_full_reads": all(reads.get(p) for p in required),
        "zero_writes": before == after,
    }
    failed = [{"tool": c["tool"] if c["tool"] in ("read", "skill", "edit", "bash") else "other",
               "path": relative_read(corpus, c.get("state", {}).get("input", {}).get("filePath", "")) or None}
              for c in calls if c.get("state", {}).get("status") != "completed"]
    evidence = {"checks": checks, "reads": sorted(p or "(outside)" for p in reads),
                "failed_tool_calls": failed,
                "unread_required": sorted(p for p in required if not reads.get(p))}
    return all(checks.values()), evidence


def run(op, feedback=None):
    op = Path(op)
    manifest = json.loads((op / "manifest.json").read_text())
    if (op / "run.json").exists() and feedback is None:
        raise ValueError("operation already ran; use revise or stage a new one")
    corpus, profile, config = op / "corpus", op / "profile", manifest["config"]
    prompt = worker_prompt(manifest, corpus)
    if feedback is not None:
        prompt += ("\n\nThe operator's checks rejected your previous proposal, saved as previous-proposal.md. "
                   "Problems: " + "; ".join(feedback) + ". Read previous-proposal.md, fix every problem and return "
                   "a complete corrected proposal in the same format, including every page that should change.")
    env = configure_worker(corpus, profile, manifest["role"], manifest["skill"], manifest["reads"],
                           config["agent"], config["model"], config["opencode_version"], config["steps"])
    before = corpus_state(corpus)
    events, returncode, seconds = run_role(env, corpus, manifest["role"], prompt, config["timeout"])
    text = answer_text(events)
    (op / "response.md").write_text(text + "\n")
    (op / "response.md").chmod(0o600)
    passed, evidence = verify_events(manifest, corpus, events, returncode, before, corpus_state(corpus))
    result = {"passed": passed, "seconds": seconds, **evidence}
    if passed and manifest["kind"] != "query":
        try:
            proposal = parse_proposal(text)
            write_json(op / "proposal.json", proposal)
            result["proposed_files"] = sorted(proposal["files"])
        except ValueError as error:
            result.update(passed=False, proposal_error=str(error))
    write_json(op / "run.json", result)
    return result


def revise(op):
    """One worker retry with the dry-run problems as feedback; earlier attempt archived."""
    op = Path(op)
    manifest = json.loads((op / "manifest.json").read_text())
    if manifest["kind"] == "query" or (op / "receipt.json").exists() or not (op / "proposal.json").exists():
        raise ValueError("revise needs an unapplied ingest or compile proposal")
    if (op / "attempt-1").exists():
        raise ValueError("already revised once; stage a new operation")
    problems = apply(op, dry_run=True)["problems"]
    if not problems:
        raise ValueError("the proposal already passes; apply it")
    archive = op / "attempt-1"
    archive.mkdir(mode=0o700)
    for name in ("run.json", "proposal.json", "response.md"):
        os.replace(op / name, archive / name)
    corpus = op / "corpus"
    shutil.copy2(archive / "response.md", corpus / "previous-proposal.md")
    manifest["reads"] = sorted({*manifest["reads"], "previous-proposal.md"})
    write_json(op / "manifest.json", manifest)
    result = run(op, feedback=problems)
    result["feedback"] = problems
    return result


def check_proposal(manifest, proposal):
    vault, config = Path(manifest["vault"]), manifest["config"]
    files, record = proposal["files"], proposal["log"]
    problems = []
    if not files:
        problems.append("proposal has no pages")
    if len(files) > config["max_pages"]:
        problems.append(f"proposal changes {len(files)} pages; the limit is {config['max_pages']}")
    for path in files:
        if (not WRITABLE.fullmatch(path) or not link_check.canonical_parts(path)
                or Path(path).name in link_check.INSTRUCTIONS):
            problems.append(f"path not writable by the operator: {path}")
    if not record or not RECORD.fullmatch(record.splitlines()[0].strip()):
        problems.append("log record must start with '## YYYY-MM-DD — operation — partial'")
    elif re.search(r"(?m)^(#{1,2} |<<<)", "\n".join(record.splitlines()[1:])):
        problems.append("log record must be a single record without markers")
    for path in sorted({*files, "wiki/log.md"}):
        if file_hash(vault / path) != manifest["wiki_preimages"].get(path):
            problems.append(f"vault file changed since staging: {path}")
    return problems


def appended_log(vault, record):
    current = (vault / "wiki/log.md").read_text() if (vault / "wiki/log.md").is_file() else ""
    return current.rstrip("\n") + "\n\n" + record.strip() + "\n"


def candidate_check(manifest, proposal):
    """Run the managed checker on a copy of the vault's wiki with the proposal applied."""
    vault = Path(manifest["vault"])
    with tempfile.TemporaryDirectory(prefix="sb-candidate-") as tmp:
        root = Path(tmp)
        for key in manifest["wiki_preimages"]:
            (root / key).parent.mkdir(parents=True, exist_ok=True)
            (root / key).write_bytes((vault / key).read_bytes())
        for path, body in proposal["files"].items():
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(body)
        (root / "wiki/log.md").write_text(appended_log(vault, proposal["log"]))
        report = link_check.check(root)
    return {"errors": report["errors"] + report["unsupported"], "unchecked": len(report["unchecked"]),
            "pages": report["pages"], "links": len(report["links"])}


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.sb-{secrets.token_hex(4)}")
    with open(temporary, "x", encoding="utf-8") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def apply(op, dry_run=False):
    op = Path(op)
    manifest = json.loads((op / "manifest.json").read_text())
    if manifest["kind"] == "query":
        raise ValueError("query operations write nothing")
    if not json.loads((op / "run.json").read_text()).get("passed"):
        raise ValueError("the worker run did not pass verification")
    if (op / "receipt.json").exists():
        raise ValueError("operation already applied")
    proposal = json.loads((op / "proposal.json").read_text())
    vault = Path(manifest["vault"])
    problems = check_proposal(manifest, proposal)
    checker = None if problems else candidate_check(manifest, proposal)
    if checker and checker["errors"]:
        problems += [f"checker: {d['kind']} {d['page']} {d.get('target') or d.get('detail', '')}".strip()
                     for d in checker["errors"]]
    summary = {"operation": manifest["id"], "dry_run": dry_run, "problems": problems,
               "files": [{"path": p, "action": "update" if manifest["wiki_preimages"].get(p) else "create"}
                         for p in sorted(proposal["files"])],
               "log_record": (proposal["log"] or "").splitlines()[0] if proposal["log"] else None,
               "checker": checker and {k: checker[k] for k in ("pages", "links", "unchecked")}}
    if problems or dry_run:
        return summary
    backup = op / "backup"
    backup.mkdir(mode=0o700)
    changes = {**proposal["files"], "wiki/log.md": appended_log(vault, proposal["log"])}
    receipt = []
    for path, text in sorted(changes.items()):
        target = vault / path
        before = file_hash(target)
        if before:
            (backup / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup / path)
        atomic_write(target, text)
        receipt.append({"path": path, "before": before, "after": file_hash(target)})
        write_json(op / "receipt.json", {"files": receipt, "complete": False})
    after = link_check.check(vault)
    ok = not (after["errors"] or after["unsupported"])
    write_json(op / "receipt.json", {"files": receipt, "complete": True, "post_check_clean": ok})
    if not ok:
        undo(op)
        summary["problems"] = ["post-apply checker errors; the operation was undone"]
        return summary
    summary["applied"] = True
    return summary


def undo(op):
    op = Path(op)
    manifest = json.loads((op / "manifest.json").read_text())
    receipt = json.loads((op / "receipt.json").read_text())
    vault, restored, skipped = Path(manifest["vault"]), [], []
    for entry in reversed(receipt["files"]):
        target = vault / entry["path"]
        if file_hash(target) != entry["after"]:
            skipped.append(entry["path"])
            continue
        if entry["before"] is None:
            target.unlink()
        else:
            atomic_write(target, (op / "backup" / entry["path"]).read_text())
        restored.append(entry["path"])
    write_json(op / "undo.json", {"restored": sorted(restored), "skipped_changed_since": sorted(skipped)})
    return {"restored": sorted(restored), "skipped_changed_since": sorted(skipped)}


def status(op):
    op = Path(op)
    manifest = json.loads((op / "manifest.json").read_text())
    stages = [name for name in ("run.json", "proposal.json", "receipt.json", "undo.json") if (op / name).exists()]
    result = {"operation": manifest["id"], "kind": manifest["kind"], "task": manifest["task"],
              "inputs": manifest["inputs"], "stages": stages}
    if (op / "run.json").exists():
        result["run"] = json.loads((op / "run.json").read_text())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    staging = commands.add_parser("stage", help="copy an operation's inputs outside the vault")
    staging.add_argument("vault", type=Path)
    staging.add_argument("kind", choices=sorted(ROLES))
    staging.add_argument("--input", action="append", default=[], help="raw/ capture (ingest) or source note (compile)")
    staging.add_argument("--task", help="what to ingest or compile")
    staging.add_argument("--question", help="query question")
    staging.add_argument("--url", help="ingest: capture this URL into raw/ first")
    staging.add_argument("--config", type=Path, help="operator config (default: VAULT/.opencode/second-brain/operator.json)")
    capturing = commands.add_parser("capture", help="fetch one URL into raw/ with a webfetch-only worker")
    capturing.add_argument("vault", type=Path)
    capturing.add_argument("url")
    capturing.add_argument("--config", type=Path)
    commands.add_parser("pending", help="list raw/ captures without a source page").add_argument("vault", type=Path)
    for name, text in (("run", "run the worker on a staged operation"), ("status", "show an operation's stage"),
                       ("revise", "rerun the worker once with the dry-run problems as feedback"),
                       ("undo", "restore files an applied operation changed")):
        commands.add_parser(name, help=text).add_argument("operation", type=Path)
    applying = commands.add_parser("apply", help="validate and write a proposal into the vault")
    applying.add_argument("operation", type=Path)
    applying.add_argument("--dry-run", action="store_true", help="validate and check without writing")
    args = parser.parse_args()
    try:
        if args.command == "stage":
            if args.kind == "query" and args.task:
                parser.error("query uses --question, not --task")
            result = {"operation": str(stage(args.vault, args.kind, args.input,
                                             args.question if args.kind == "query" else args.task, args.config,
                                             url=args.url))}
        elif args.command == "capture":
            result = capture(args.vault, args.url, args.config)
        elif args.command == "pending":
            result = {"pending": pending(args.vault)}
        elif args.command == "run":
            result = run(args.operation)
            if json.loads((args.operation / "manifest.json").read_text())["kind"] == "query":
                result["answer"] = str(args.operation / "response.md")
        elif args.command == "apply":
            result = apply(args.operation, args.dry_run)
        else:
            result = {"status": status, "undo": undo, "revise": revise}[args.command](args.operation)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error) if isinstance(error, (ValueError, RuntimeError)) else type(error).__name__}))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    failed = result.get("passed") is False or result.get("problems") or result.get("skipped_changed_since")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
