"""Opt-in, four-turn synthetic source-to-wiki rehearsal (Linux).

The model proposes Markdown; this operator driver validates exact paths and
applies only those synthetic files. It does NOT prove native accepted edit
permissions or replace owner acceptance. All generated artifacts are temporary;
the owner's normal OpenCode auth/session infrastructure still applies.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from semantic_probe import ROOT, call_model, prepare_environment, semantic_checks
from runtime_read_probe import validate_scope

sys.path.insert(0, str(ROOT))
from scripts import link_check


TODAY = "2026-09-24"
CONCEPT = "wiki/concepts/vent-choice.md"


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*.md")}


def context(root):
    return {p.relative_to(root).as_posix(): p.read_text() for p in sorted(root.rglob("*.md"))}


def apply_proposal(root, proposal, expected):
    files = proposal.get("files")
    if not isinstance(files, dict) or set(files) != expected or not all(isinstance(v, str) for v in files.values()):
        raise RuntimeError("Proposal does not match the approved synthetic path manifest")
    old_log = (root / "wiki/log.md").read_text()
    if not files["wiki/log.md"].startswith(old_log):
        raise RuntimeError("Proposal rewrites an existing log prefix")
    appended = files["wiki/log.md"][len(old_log):]
    if not re.search(r"\bpartial\b", appended, re.I) or re.search(r"\bcompleted\b", appended, re.I):
        raise RuntimeError("Proposal must leave owner acceptance explicitly partial")
    for name, body in files.items():
        if "{{" in body or "@" in body or re.search(r"!\s*`", body):
            raise RuntimeError("Proposal contains unresolved or unsafe preprocessing tokens")
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    report = link_check.check(root)
    if report["errors"] or report["unsupported"] or report["unchecked"]:
        raise RuntimeError("Generated wiki failed managed metadata/link validation")
    pages, _ = link_check.collect(root)
    source = next(name for name in expected if name.startswith("wiki/sources/"))
    edges = set(map(tuple, report["links"]))
    for current_source in (name for name in pages if name.startswith("wiki/sources/")):
        if (current_source, CONCEPT) not in edges or (CONCEPT, current_source) not in edges:
            raise RuntimeError("Generated source/concept links are not reciprocal")
    fields = pages[source]["metadata"]
    if fields.get("author") != "Aster Desk Lab" or fields.get("captured") != TODAY or fields.get("url") is not None:
        raise RuntimeError("Generated provenance does not match the synthetic source")
    wanted_publication = "2026-09-01" if source.endswith("trial-a.md") else None
    if fields.get("published") != wanted_publication or fields.get("raw") != source.replace("wiki/sources/", "raw/"):
        raise RuntimeError("Generated source guessed or changed provenance")
    archive = (root / fields["raw"]).read_text()
    body = " ".join(re.sub(r"(?m)^[ \t]*> ?", "", pages[source]["body"]).split())
    for section in ("Measurements", "Recommendation"):
        excerpt = archive.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
        if " ".join(excerpt.split()) not in body:
            raise RuntimeError("Generated source did not preserve the required evidence excerpts")
    index_targets = {match for _, line in link_check.body_lines(pages["wiki/index.md"]["body"])
                     for match in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", line)}
    for name in pages:
        if name not in ("wiki/index.md", "wiki/log.md") and name.removesuffix(".md") not in index_targets:
            raise RuntimeError("Generated index omits an actual page")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="authorize at most four synthetic model turns")
    parser.add_argument("--agent", required=True, help="owner-approved existing primary agent")
    parser.add_argument("--model", required=True, help="approved provider/model; routing must match")
    args = parser.parse_args()
    if not args.live:
        parser.error("requires --live and owner approval")
    env = prepare_environment(args.agent, args.model)
    fixture = ROOT / "tests/fixtures/contract"
    validate_scope(ROOT, [Path("framework/instructions/wiki-contract.md"),
                         *[Path(f"framework/templates/{kind}.md") for kind in ("source", "concept", "index", "log")],
                         Path("tests/fixtures/contract/raw/trial-a.md"), Path("tests/fixtures/contract/raw/trial-b.md")])
    contract = (ROOT / "framework/instructions/wiki-contract.md").read_text()
    templates = {kind: (ROOT / f"framework/templates/{kind}.md").read_text()
                 for kind in ("source", "concept", "index", "log")}
    results = []
    observations = []
    with tempfile.TemporaryDirectory(prefix="sb-ingest-", dir="/tmp/opencode") as temporary:
        root = Path(temporary)
        (root / "wiki").mkdir()
        (root / "raw").mkdir()
        for kind in ("index", "log"):
            seed = templates[kind].replace("{{CREATED}}", TODAY).replace("{{UPDATED}}", TODAY)
            seed = re.sub(r"<!--.*?-->", "", seed, flags=re.S)
            (root / f"wiki/{kind}.md").write_text(seed.rstrip() + "\n")
        for slug in ("trial-a", "trial-b"):
            source = f"wiki/sources/{slug}.md"
            raw = f"raw/{slug}.md"
            (root / raw).write_bytes((fixture / raw).read_bytes())
            before = hashes(root)
            expected = {source, CONCEPT, "wiki/index.md", "wiki/log.md"}
            prompt = (
                "Perform a synthetic ingest proposal under the complete contract below. No tools. "
                "Return only JSON: {\"files\":{vault_relative_filename:complete_markdown}}. "
                f"The exact approved changed paths are {json.dumps(sorted(expected))}. No other file may change. "
                f"Fully read and ingest the new input {raw}. Existing records below are complete, not excerpts. "
                "Create only a source and concept, not entity/synthesis pages. Preserve earlier competing claims "
                "and link each material claim to source evidence with raw section locators. Use A1 for trial A "
                "measurements/A2 for its recommendation, B1/B2 for trial B. All metadata strings including type "
                f"and dates MUST be JSON quoted; created/updated/captured are {TODAY}. Remove all placeholders. "
                "Source author is exactly Aster Desk Lab (use the name only in metadata). "
                "In the source page, preserve the FULL Measurements and Recommendation paragraphs VERBATIM "
                "as evidence excerpts for the claim IDs. Blockquotes are fine; do not reword, emphasize, "
                "or change punctuation inside the quoted text. There is no source URL; do not invent one. "
                "Do not use fragments, embeds, bare links, or extra metadata keys. Unknown publication stays null. "
                "Index actual pages only. Preserve wiki/log.md EXACTLY as a byte-for-byte prefix and append a "
                "new partial operation record with source identity, paths, contradictions/gaps and verification pending. "
                "Use the exact word partial, never completed, in the new entry. "
                "No owner approval or checks have happened yet; do not claim completion. "
                "Later observations do not automatically supersede earlier ones.\n\n"
                + contract + "\n\nTEMPLATES:\n" + json.dumps(templates)
                + "\n\nCOMPLETE EXISTING RECORDS:\n" + json.dumps(context(root))
            )
            proposal, observed = call_model(env, prompt)
            observations.append(observed)
            report = apply_proposal(root, proposal, expected)
            after = hashes(root)
            if any(after[name] != digest for name, digest in before.items() if name not in expected):
                raise RuntimeError("Unapproved synthetic file changed")
            results.append({"operation": slug, "pages": report["pages"], "links": len(report["links"]),
                            "raw_and_unrelated_unchanged": True, "metadata_links_provenance_passed": True})
        before = hashes(root)
        repeat, observed = call_model(env,
            "No tools. Repeat ingestion of unchanged raw/trial-b.md using these COMPLETE records. "
            "If its claims and index are already represented, do not duplicate pages/claims/log records. "
            "Return only JSON {\"files\":{},\"status\":\"unchanged\"}; propose changes only if genuinely needed. "
            "Existing partial status records owner acceptance pending, not missing source content.\n" + json.dumps(context(root)))
        observations.append(observed)
        repeat_passed = repeat.get("files") == {} and repeat.get("status") == "unchanged" and before == hashes(root)
        if not repeat_passed:
            raise RuntimeError("Repeat ingestion was not a no-op")
        answer, observed = call_model(env,
            "No tools. Query ONLY the COMPLETE generated wiki and raw evidence below. Return only JSON with "
            "preferred_vent (open/closed/not_established); integer trial_a_open_minutes, trial_a_closed_minutes, "
            "trial_b_open_minutes, trial_b_closed_minutes; trial_b_publication_date (ISO string or null); "
            "why_results_differ (not_covered when unsupported); recommendation_claim_ids (array); "
            "citations (array of {page,locator}: canonical source page paths; locator must be exactly Measurements "
            "or Recommendation. Include both sections for EACH source, four citations total). "
            "Distinguish author recommendations from established knowledge, preserve the disagreement, and "
            "do not invent a cause or date.\n" + json.dumps(context(root)))
        observations.append(observed)
        checks = semantic_checks(answer)
        citations = answer.get("citations", [])
        expected_citations = {(f"wiki/sources/{slug}", section) for slug in ("trial-a", "trial-b")
                              for section in ("Measurements", "Recommendation")}
        actual_citations = {(cite["page"].removesuffix(".md"), cite["locator"]) for cite in citations
                            if isinstance(cite, dict) and isinstance(cite.get("page"), str)
                            and isinstance(cite.get("locator"), str)} if isinstance(citations, list) else set()
        checks["source_citations"] = isinstance(citations, list) and len(citations) == 4 and actual_citations == expected_citations and all(
            f"## {section}\n" in (root / page.replace("wiki/sources/", "raw/")).with_suffix(".md").read_text()
            for page, section in actual_citations
        )
        checks["query_corpus_unchanged"] = before == hashes(root)
        checks["repeat_no_duplicates"] = repeat_passed
        passed = all(checks.values())
        print(json.dumps({"agent": args.agent, "model": args.model, "model_turns": len(observations),
                          "observed": observations,
                          "ingests": results, "query_checks": checks, "passed": passed,
                          "native_accepted_edit_proof": False, "owner_content_acceptance": "pending",
                          "generated_artifacts": "temporary staging removed; normal OpenCode session retention applies; not published"}, indent=2))
        return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"passed": False, "error": type(error).__name__,
                          "detail": str(error) if isinstance(error, RuntimeError) else "Response withheld"}))
        sys.exit(2)
