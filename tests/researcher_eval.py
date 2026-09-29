"""Opt-in evaluation of sb-researcher answers on a staged copy of a managed wiki.

Stages the adopted wiki pages, the installed contract and the researcher role
and skill in a new temporary directory, then asks each question from a JSON
file in its own native `opencode run`. Personal vault instructions, settings and
unrelated folders are never staged. Scores are deterministic: skill load,
index-first retrieval, citations that exist and were actually read, expected
pages and terms, Read/Not covered sections, abstention on unsupported questions
and unchanged corpus bytes. The abstention check is a phrase heuristic, so the
answers are kept in the local results file for human review; stdout carries
scores only. Owner authentication and session retention apply; the staged copy
is not filesystem isolation.

Run: python3 tests/researcher_eval.py --live --vault VAULT --questions FILE \\
       --agent APPROVED_PRIMARY --model PROVIDER/MODEL --opencode-version X.Y.Z
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import link_check  # noqa: E402
from scripts.sb_runtime import (  # noqa: E402
    answer_text, configure_worker, relative_read, run_role, tool_calls, validate_scope)


ROLE, SKILL = "sb-researcher", "second-brain-query"
CONTRACT = "instructions/wiki-contract.md"
INSTALLED = {
    "contract": (".opencode/instructions/second-brain/wiki-contract.md", "framework/instructions/wiki-contract.md"),
    "role": (f".opencode/agents/{ROLE}.md", f"framework/agents/{ROLE}.md"),
    "skill": (f".opencode/skills/{SKILL}/SKILL.md", f"framework/skills/{SKILL}/SKILL.md"),
}
CONTENT = re.compile(r"wiki/(?:sources|concepts|entities|synthesis)/[^\s\[\]|#`'\"()<>,;*]+")
ABSTAIN = re.compile(
    r"not covered|not (?:recorded|stated|established|found|mentioned|addressed|specified|documented|identified)"
    r"|no (?:evidence|information|record|source|page)|unknown|cannot (?:answer|determine|confirm)"
    r"|does(?: not|n't) (?:say|state|cover|mention|address|specify|name|identify|record)", re.I)
SECTION = {"read": re.compile(r"(?im)^[#>*\s-]*\**read\**\s*(?::|$)"),
           "not_covered": re.compile(r"(?im)^[#>*\s-]*\**not covered\**\s*(?::|$)")}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_questions(path, vault):
    """Validate the question file against the vault before any model call."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    questions = data.get("questions") if isinstance(data, dict) else None
    if not isinstance(questions, list) or not questions:
        raise ValueError("questions must be a nonempty list")
    pages, _ = link_check.collect(vault)
    seen = set()
    for item in questions:
        qid, text, expect = item.get("id"), item.get("question"), item.get("expect")
        if not isinstance(qid, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", qid) or qid in seen:
            raise ValueError(f"invalid or duplicate question id: {qid!r}")
        seen.add(qid)
        if not isinstance(text, str) or not text.strip() or "@" in text or re.search(r"!\s*`", text):
            raise ValueError(f"{qid}: question must be plain text without @ or !` preprocessing tokens")
        if expect not in ("answer", "abstain"):
            raise ValueError(f"{qid}: expect must be answer or abstain")
        expected = item.get("expected_pages", [])
        terms = item.get("expected_terms", [])
        if not isinstance(expected, list) or not isinstance(terms, list) or not all(isinstance(t, str) and t for t in terms):
            raise ValueError(f"{qid}: expected_pages and expected_terms must be lists of strings")
        if expect == "answer" and not expected:
            raise ValueError(f"{qid}: answer questions need expected_pages")
        for page in expected:
            if page not in pages or page in link_check.CONTROLS:
                raise ValueError(f"{qid}: expected page is not an adopted content page: {page}")
        if set(item) - {"id", "question", "expect", "expected_pages", "expected_terms"}:
            raise ValueError(f"{qid}: unknown question fields")
    return questions


def stage(vault, base, include_raw=False):
    """Copy only adopted pages, the contract and role/skill; never vault instructions."""
    vault = Path(vault)
    corpus, profile = base / "corpus", base / "profile"
    corpus.mkdir(mode=0o700)
    profile.mkdir(mode=0o700)
    pages, _ = link_check.collect(vault)  # refuses links, hardlinks and protected entries
    copies = {key: vault / key for key in pages}
    if include_raw:
        for key, page in pages.items():
            raw = page["metadata"].get("raw") if key.startswith("wiki/sources/") else None
            if isinstance(raw, str) and link_check.canonical_parts(raw) and (vault / raw).is_file():
                copies[raw] = vault / raw
    origin = {}
    for name, (installed, public) in INSTALLED.items():
        use_vault = (vault / installed).is_file()
        root, relative = (vault, installed) if use_vault else (ROOT, public)
        validate_scope(root, [Path(relative)])
        origin[name] = {"from": "vault" if use_vault else "framework",
                        "sha256": digest((root / relative).read_bytes())}
        target = {"contract": corpus / CONTRACT, "role": profile / f"agents/{ROLE}.md",
                  "skill": profile / f"skills/{SKILL}/SKILL.md"}[name]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root / relative).read_bytes())
    for key, source in sorted(copies.items()):
        validate_scope(vault, [Path(key)])
        target = corpus / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    subprocess.run(["git", "init", "--quiet", str(corpus)], check=True, capture_output=True)
    return corpus, profile, origin


def corpus_state(corpus):
    return {p.relative_to(corpus).as_posix(): digest(p.read_bytes())
            for p in sorted(corpus.rglob("*")) if p.is_file() and ".git" not in p.relative_to(corpus).parts}


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


def score(question, events, corpus, before, after, returncode=0, search=False):
    """Deterministic checks for one answer; returns checks, metrics and answer."""
    calls, text = tool_calls(events), answer_text(events)
    reads = []
    for call in calls:
        state = call.get("state", {})
        if call["tool"] == "read" and state.get("status") == "completed":
            reads.append(relative_read(corpus, state.get("input", {}).get("filePath", "")))
    content_reads = [p for p in reads if p and CONTENT.fullmatch(p)]
    cited = extract_citations(text)
    index_at = reads.index("wiki/index.md") if "wiki/index.md" in reads else None
    first_content = next((i for i, p in enumerate(reads) if p in content_reads), None)
    checks = {
        "run_completed": returncode == 0 and bool(text),
        "skill_loaded": any(c["tool"] == "skill" and c.get("state", {}).get("status") == "completed"
                            and c["state"].get("input", {}).get("name") == SKILL for c in calls),
        "tools_ok": all(c["tool"] in (("read", "skill", "grep", "glob") if search else ("read", "skill"))
                        and c.get("state", {}).get("status") == "completed" for c in calls),
        "index_first": index_at is not None and (first_content is None or index_at < first_content),
        "citations_exist": all(p in before for p in cited),
        "citations_read": all(p in reads for p in cited),
        "sections": all(pattern.search(text) for pattern in SECTION.values()),
        "zero_writes": before == after,
    }
    if question["expect"] == "answer":
        checks["cited_any"] = bool(cited)
        checks["expected_cited"] = set(question["expected_pages"]) <= set(cited)
    else:
        # The required "Not covered:" label is not itself an abstention.
        checks["abstained"] = bool(ABSTAIN.search(re.sub(r"(?im)^[#>*\s-]*\**not covered\**\s*:?", "", text)))
    if question.get("expected_terms"):
        lowered = text.lower()
        checks["expected_terms"] = all(term.lower() in lowered for term in question["expected_terms"])
    tokens = {"input": 0, "output": 0}
    for event in events:
        part = event.get("part") if isinstance(event.get("part"), dict) else {}
        for key in tokens:
            value = part.get("tokens", {}).get(key) if isinstance(part.get("tokens"), dict) else None
            tokens[key] += value if isinstance(value, int) else 0
    metrics = {"content_pages_read": len(set(content_reads)), "read_calls": len(reads),
               "searches": sum(c["tool"] in ("grep", "glob") for c in calls),
               "failed_tool_calls": sum(c.get("state", {}).get("status") != "completed" for c in calls),
               "steps": sum(e.get("type") == "step_start" for e in events),
               "tokens_input": tokens["input"], "tokens_output": tokens["output"]}
    return {"id": question["id"], "expect": question["expect"], "passed": all(checks.values()),
            "checks": checks, "metrics": metrics, "cited": cited, "answer": text}


def summarize(results):
    names = sorted({name for result in results for name in result["checks"]})
    return {"questions": len(results), "passed": sum(r["passed"] for r in results),
            "checks": {name: f"{sum(r['checks'].get(name) is True for r in results)}/"
                             f"{sum(name in r['checks'] for r in results)}" for name in names},
            "content_pages_read_mean": round(sum(r["metrics"]["content_pages_read"] for r in results) / len(results), 2),
            "seconds_total": round(sum(r["metrics"].get("seconds", 0) for r in results), 1)}


def prompt_for(question, corpus, include_raw, search=False):
    raw = ("Approved raw captures are staged under raw/." if include_raw else
           "Raw captures are not staged for this evaluation; rely on the wiki's recorded locators and "
           "list raw evidence as not consulted.")
    return (
        "Operator preflight verified your exact read grants"
        + ("; you can also search the staged files with grep and glob" if search else "")
        + ". Edits and all other tools are denied. "
        f"Load your designated skill with the skill tool. Working directory: {corpus}. "
        f"The operation manifest is {corpus / 'operation.md'} and the contract is {CONTRACT}. "
        f"Read wiki/index.md first, then only the pages you need, and follow their links. {raw} "
        + ("When the index does not point to the answer, search the staged pages with grep before concluding "
           "the wiki does not cover it; read every page you cite completely. " if search else "")
        +
        f"Question: {question['question']} "
        "Answer only from pages you actually read. Put exact vault-relative page paths such as "
        "wiki/sources/name.md beside each claim, with section locators. If the wiki does not answer, say so. "
        "End with a line starting 'Read:' and a line starting 'Not covered:'. Do not write files."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--live", action="store_true", help="authorize provider calls for these questions")
    parser.add_argument("--vault", required=True, type=Path, help="corpus root containing wiki/")
    parser.add_argument("--questions", required=True, type=Path, help="JSON question file")
    parser.add_argument("--agent", required=True, help="owner-approved existing primary agent for auth routing")
    parser.add_argument("--model", required=True, help="approved provider/model")
    parser.add_argument("--opencode-version", required=True, help="installed OpenCode version the owner approved")
    parser.add_argument("--base", type=Path, help="parent directory for the staging copy (default: system temp)")
    parser.add_argument("--include-raw", action="store_true", help="also stage raw captures named by source pages")
    parser.add_argument("--steps", type=int, default=8, help="researcher step limit per question")
    parser.add_argument("--timeout", type=int, default=300, help="seconds per question")
    parser.add_argument("--search", action="store_true", help="also grant grep and glob over the staged copy")
    args = parser.parse_args()
    if not args.live:
        parser.error("provider use is opt-in; pass --live only after owner approval")
    questions = load_questions(args.questions, args.vault)
    base = Path(tempfile.mkdtemp(prefix="sb-researcher-eval-", dir=args.base))
    corpus, profile, origin = stage(args.vault, base, args.include_raw)
    reads = sorted(corpus_state(corpus)) + ["operation.md"]
    (corpus / "operation.md").write_text(
        "# Operator-verified evaluation manifest\n\n```json\n" + json.dumps({
            "status": "operator preflight verified before inference",
            "scope": "read-only researcher evaluation on a staged copy; no edits approved",
            "role": ROLE, "skill": SKILL, "model": args.model, "worktree": str(corpus),
            "approved_reads": f"{len(reads)} staged files: wiki pages, {CONTRACT}, this manifest"
                              + (", raw captures" if args.include_raw else ""),
            "search": "grep and glob over these staged files" if args.search else "not available",
            "limitation": "owner auth/session context; staged copy, not filesystem isolation"}, indent=2) + "\n```\n")
    env = configure_worker(corpus, profile, ROLE, SKILL, reads, args.agent, args.model,
                           args.opencode_version, args.steps, args.search)
    results = []
    for question in questions:
        before = corpus_state(corpus)
        events, returncode, seconds = run_role(env, corpus, ROLE, prompt_for(question, corpus, args.include_raw, args.search),
                                               args.timeout)
        result = score(question, events, corpus, before, corpus_state(corpus), returncode, args.search)
        result["question"] = question["question"]
        result["metrics"]["seconds"] = seconds
        results.append(result)
        print(json.dumps({k: result[k] for k in ("id", "passed", "checks", "metrics")}), flush=True)
    report = {"summary": summarize(results), "opencode_version": args.opencode_version, "model": args.model,
              "search": args.search,
              "staged": origin, "include_raw": args.include_raw, "results": results}
    output = base / "results.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    output.chmod(0o600)
    print(json.dumps({"summary": report["summary"], "results": str(output)}, indent=2))
    return 0 if report["summary"]["passed"] == len(results) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(json.dumps({"setup_error": type(error).__name__,
                          "detail": str(error) if isinstance(error, (RuntimeError, ValueError)) else "withheld"}))
        sys.exit(2)
