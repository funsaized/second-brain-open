"""Offline operator checks on invented vaults; `run` is covered by its event verifier only."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import sb_operator as op


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/contract"
CLI = ROOT / "scripts/sb_operator.py"
CONCEPT = """---
title: "Oven airflow"
type: "concept"
created: "2026-09-28"
updated: "2026-09-28"
aliases: []
tags: []
---

# Oven airflow

Trial A timed the open vent at 18 minutes ([[wiki/sources/trial-a|Trial A]], raw Measurements).
"""
RECORD = "## 2026-09-28 — Compile oven airflow — partial\n- Changed paths: two pages.\n- Verification: pending."


class OperatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.vault = base / "vault"
        for path in FIXTURE.rglob("*"):
            if path.is_file():
                target = self.vault / path.relative_to(FIXTURE)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(path.read_bytes())
        (self.vault / "AGENTS.md").write_text("Private owner context\n")
        self.config = base / "operator.json"
        self.config.write_text(json.dumps({"agent": "primary", "model": "p/m", "opencode_version": "0",
                                           "workdir": str(base / "ops"), "max_pages": 3}))

    def tearDown(self):
        self.tmp.cleanup()

    def staged(self, kind="compile", inputs=("wiki/sources/trial-a.md",), task="Explain oven airflow"):
        return op.stage(self.vault, kind, inputs, task, self.config, today="2026-09-28")

    def proposal(self, operation, files=None, log=RECORD, index=None):
        source = (self.vault / "wiki/sources/trial-a.md").read_text()
        files = files if files is not None else {
            "wiki/concepts/oven-airflow.md": CONCEPT,
            "wiki/sources/trial-a.md": source + "\nSee [[wiki/concepts/oven-airflow|Oven airflow]].\n"}
        index = index if index is not None else [["Concepts", "- [[wiki/concepts/oven-airflow|Oven airflow]] — airflow."]]
        (operation / "run.json").write_text(json.dumps({"passed": True}))
        (operation / "response.md").write_text("previous reply\n")
        (operation / "proposal.json").write_text(json.dumps({"files": files, "index": index, "log": log, "notes": ""}))

    def test_stage_copies_scope_without_owner_instructions(self):
        operation = self.staged()
        manifest = json.loads((operation / "manifest.json").read_text())
        files = {p.relative_to(operation / "corpus").as_posix() for p in (operation / "corpus").rglob("*")
                 if p.is_file() and ".git" not in p.parts}
        self.assertEqual(files, set(manifest["reads"]))
        self.assertIn("templates/concept.md", files)
        self.assertIn("instructions/wiki-contract.md", files)
        self.assertNotIn("AGENTS.md", files)
        self.assertFalse(any(p.startswith("raw/") for p in files))
        self.assertEqual((manifest["role"], manifest["skill"]), ("sb-ingestor", "second-brain-ingest"))
        self.assertTrue((operation / "profile/skills/second-brain-ingest/SKILL.md").is_file())
        self.assertEqual(manifest["wiki_preimages"]["wiki/log.md"],
                         op.file_hash(self.vault / "wiki/log.md"))
        ingest = self.staged("ingest", ["raw/trial-b.md"], "Ingest trial B")
        self.assertIn("raw/trial-b.md", json.loads((ingest / "manifest.json").read_text())["reads"])
        query = op.stage(self.vault, "query", [], "What did Trial A find?", self.config)
        self.assertNotIn("templates/concept.md", json.loads((query / "manifest.json").read_text())["reads"])

    def test_stage_refuses_bad_inputs_and_workdir(self):
        for kind, inputs, task in (("ingest", ["wiki/sources/trial-a.md"], "t"), ("compile", ["raw/trial-a.md"], "t"),
                                   ("compile", ["wiki/index.md"], "t"), ("ingest", ["raw/../AGENTS.md"], "t"),
                                   ("ingest", [], "t"), ("query", [], None), ("ingest", ["raw/trial-a.md"], "read @x")):
            with self.subTest(kind=kind, inputs=inputs, task=task), self.assertRaises(ValueError):
                op.stage(self.vault, kind, inputs, task, self.config)
        (self.vault / "raw/linked.md").symlink_to(self.vault / "raw/trial-a.md")
        with self.assertRaises(ValueError):
            op.stage(self.vault, "ingest", ["raw/linked.md"], "t", self.config)
        inside = json.loads(self.config.read_text())
        inside["workdir"] = str(self.vault / "ops")
        self.config.write_text(json.dumps(inside))
        with self.assertRaisesRegex(ValueError, "outside the vault"):
            op.stage(self.vault, "compile", ["wiki/sources/trial-a.md"], "t", self.config)

    def test_merge_index_adds_replaces_and_keeps_entries(self):
        index = (self.vault / "wiki/index.md").read_text()
        before = [line for line in index.splitlines() if line.startswith("- ")]
        merged = op.merge_index(index, [
            ["Concepts", "- [[wiki/concepts/oven-airflow|Oven airflow]] — airflow."],
            ["Sources", "- [[wiki/sources/trial-a|Trial A]] — revised description."],
            ["Synthesis", "- [[wiki/synthesis/new|New]] — new section entry."],
            ["Gaps", "- No replicated trial yet."]], "2026-09-29")
        self.assertIn('updated: "2026-09-29"', merged)
        self.assertIn("- [[wiki/sources/trial-a|Trial A]] — revised description.", merged)
        self.assertEqual(merged.count("[[wiki/sources/trial-a|"), 1)
        kept = [line for line in before if "wiki/sources/trial-a|" not in line]
        self.assertTrue(all(line in merged for line in kept))
        concepts = merged.split("## Concepts", 1)[1].split("\n## ", 1)[0]
        self.assertIn("[[wiki/concepts/oven-airflow|", concepts)
        self.assertIn("- No replicated trial yet.", merged.split("## Gaps", 1)[1])
        self.assertNotIn("\n\n\n", merged)
        empty = op.merge_index("# Index\n\n## Concepts\n\nNo pages yet.\n\n## Gaps\n",
                               [["Concepts", "- [[wiki/concepts/a|A]] — a."]], "2026-09-29")
        self.assertEqual(empty, "# Index\n\n## Concepts\n\n- [[wiki/concepts/a|A]] — a.\n\n## Gaps\n")

    def test_links_patch_existing_pages_without_rewriting(self):
        page = '---\ntitle: "t"\nupdated: "2026-01-01"\n---\n\n# T\n\nBody.\n\n## Links\n\n- [[wiki/concepts/a|A]] — old.\n\n## Notes\n\nEnd.\n'
        patched = op.add_links(page, ["- [[wiki/concepts/b|B]] — new.", "- [[wiki/concepts/a|A]] — duplicate."], "2026-09-29")
        self.assertIn('updated: "2026-09-29"', patched)
        self.assertIn("- [[wiki/concepts/a|A]] — old.\n- [[wiki/concepts/b|B]] — new.\n\n## Notes", patched)
        self.assertEqual(patched.count("wiki/concepts/a|"), 1)
        created = op.add_links("---\ntitle: \"t\"\n---\n\nBody.\n", ["- [[wiki/concepts/b|B]] — new."], "2026-09-29")
        self.assertTrue(created.endswith("Body.\n\n## Links\n\n- [[wiki/concepts/b|B]] — new.\n"))
        operation = self.staged()
        before = (self.vault / "wiki/sources/trial-a.md").read_text()
        self.proposal(operation, files={"wiki/concepts/oven-airflow.md": CONCEPT})
        proposal = json.loads((operation / "proposal.json").read_text())
        proposal["links"] = [["wiki/sources/trial-a.md", "- [[wiki/concepts/oven-airflow|Oven airflow]] — timing."]]
        (operation / "proposal.json").write_text(json.dumps(proposal))
        result = op.apply(operation)
        self.assertTrue(result.get("applied"), result)
        after = (self.vault / "wiki/sources/trial-a.md").read_text()
        self.assertIn("[[wiki/concepts/oven-airflow|Oven airflow]] — timing.", after)
        self.assertTrue(set(before.splitlines()) - {l for l in before.splitlines() if l.startswith("updated:")}
                        <= set(after.splitlines()))
        self.assertEqual(op.link_check.check(self.vault)["errors"], [])
        for links, expected in (([["wiki/sources/nope.md", "- [[wiki/concepts/x|X]]"]], "dropped link"),
                                ([["wiki/concepts/oven-airflow.md", "- [[wiki/sources/trial-b|Trial B]]"]],
                                 "merged link")):
            operation = self.staged()
            self.proposal(operation, files={"wiki/concepts/oven-airflow.md": CONCEPT})
            proposal = json.loads((operation / "proposal.json").read_text())
            proposal["links"] = links
            (operation / "proposal.json").write_text(json.dumps(proposal))
            self.assertTrue(any(expected in f for f in op.apply(operation, dry_run=True)["fixes"]))

    def test_normalize_repairs_are_reported(self):
        operation = self.staged()
        manifest = json.loads((operation / "manifest.json").read_text())
        body = ("See [[wiki/sources/trial-a|Trial A]] and [[wiki/sources/part-36|Part 36]] and ![[wiki/x]].\n"
                "```\n[[wiki/sources/part-36|kept in code]]\n```\n")
        proposal = {"files": {"wiki/concepts/new.md": body}, "links": [],
                    "index": [["Concepts", "- [[wiki/concepts/new|New]] — n."], ["Sources", "- [[wiki/sources/gone|Gone]]"]],
                    "log": "Ingested things.", "notes": ""}
        fixed, fixes = op.normalize(manifest, proposal)
        text = fixed["files"]["wiki/concepts/new.md"]
        self.assertIn("[[wiki/sources/trial-a|Trial A]] and Part 36 and ![[wiki/x]]", text)
        self.assertIn("[[wiki/sources/part-36|kept in code]]", text)
        self.assertEqual(fixed["index"], [["Concepts", "- [[wiki/concepts/new|New]] — n."]])
        self.assertTrue(fixed["log"].startswith("## 2026-09-28 — compile wiki/sources/trial-a.md — partial"))
        self.assertEqual(len(fixes), 3)
        completed = dict(proposal, log="## 2026-09-28 — x — completed\n- y")
        self.assertTrue(op.normalize(manifest, completed)[0]["log"].startswith("## 2026-09-28 — x — partial"))

    def test_compile_by_topic_needs_no_inputs(self):
        operation = op.stage(self.vault, "compile", [], "Explain vent choice across the trials", self.config,
                             today="2026-09-28")
        manifest = json.loads((operation / "manifest.json").read_text())
        self.assertEqual(manifest["inputs"], [])
        prompt = op.worker_prompt(manifest, operation / "corpus")
        self.assertIn("compile by topic", prompt)
        self.assertNotIn("Read these inputs", prompt)
        with self.assertRaisesRegex(ValueError, "task"):
            op.stage(self.vault, "compile", [], None, self.config)

    def test_parse_proposal_formats(self):
        text = f"<<<FILE wiki/concepts/x.md>>>\nbody\n<<<END FILE>>>\n<<<LOG>>>\n{RECORD}\n<<<NOTES>>>\ncoverage"
        parsed = op.parse_proposal(text)
        self.assertEqual((parsed["files"], parsed["log"], parsed["notes"]),
                         ({"wiki/concepts/x.md": "body\n"}, RECORD, "coverage"))
        self.assertEqual(op.parse_proposal("<<<NOTES>>>\nunchanged repeat")["files"], {})
        indexed = text.replace("<<<LOG>>>", "<<<INDEX>>>\nConcepts | [[wiki/concepts/x|X]] — x.\n"
                                              "Gaps | - A gap.\n<<<END INDEX>>>\n<<<LOG>>>")
        self.assertEqual(op.parse_proposal(indexed)["index"],
                         [["Concepts", "- [[wiki/concepts/x|X]] — x."], ["Gaps", "- A gap."]])
        linked = text.replace("<<<LOG>>>", "<<<LINKS>>>\nwiki/sources/a.md | [[wiki/concepts/x|X]] — why.\n<<<LOG>>>")
        self.assertEqual(op.parse_proposal(linked)["links"], [["wiki/sources/a.md", "- [[wiki/concepts/x|X]] — why."]])
        both = text.replace("<<<LOG>>>", "<<<INDEX>>>\nConcepts | [[wiki/concepts/x|X]] — x.\n<<<LINKS>>>\n"
                                           "wiki/sources/a.md | [[wiki/concepts/x|X]]\n<<<LOG>>>")
        parsed = op.parse_proposal(both)
        self.assertEqual((len(parsed["index"]), len(parsed["links"])), (1, 1))
        skipped = op.parse_proposal(text.replace("<<<LOG>>>", "<<<LINKS>>>\nwiki/sources/a.md | no link\n"
                                                              "<<<INDEX>>>\nNowhere | x\n<<<LOG>>>"))
        self.assertEqual((skipped["links"], skipped["index"]), ([], []))
        self.assertEqual(len(skipped["warnings"]), 2)
        closed = text.replace("\n<<<NOTES>>>", "\n<<<LOG>>>\n<<<NOTES>>>") + "\n<<<END NOTES>>>"
        self.assertEqual(op.parse_proposal(closed)["log"], RECORD)
        self.assertEqual(op.parse_proposal(closed)["notes"], "coverage")
        mismatched = text.replace("\n<<<NOTES>>>", "\n<<<END FILE>>>\n<<<NOTES>>>")
        self.assertEqual(op.parse_proposal(mismatched)["log"], RECORD)
        # Formatting noise seen in live runs is tolerated.
        noisy = ("Here is the proposal.\n```\n<<<FILE wiki/concepts/x.md>>>\nbody\n"   # preamble, fence, no END FILE
                 "<<<INDEX>>>\n<<<INDEX>>>\n- Concepts | [[wiki/concepts/x|X]] — x.\n"   # repeated marker, bullet
                 "<<<LOG>>>\n" + RECORD + "\n<<<END FILE>>>\n```")                    # wrong closer, no NOTES
        parsed = op.parse_proposal(noisy)
        self.assertEqual(parsed["files"], {"wiki/concepts/x.md": "body\n"})
        self.assertEqual(parsed["index"], [["Concepts", "- [[wiki/concepts/x|X]] — x."]])
        self.assertEqual((parsed["log"], parsed["notes"]), (RECORD, ""))
        self.assertIn("duplicate FILE", " ".join(op.parse_proposal(
            "<<<FILE wiki/a.md>>>\none\n<<<FILE wiki/a.md>>>\ntwo\n<<<NOTES>>>\nx")["warnings"]))
        for bad in ("no markers at all", "<<<FILE >>>\nx\n<<<NOTES>>>\nx"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                op.parse_proposal(bad)

    def test_apply_writes_backs_up_and_undoes(self):
        operation = self.staged()
        self.proposal(operation)
        before = {p: op.file_hash(self.vault / p) for p in ("wiki/sources/trial-a.md", "wiki/index.md", "wiki/log.md")}
        dry = op.apply(operation, dry_run=True)
        self.assertEqual(dry["problems"], [])
        self.assertEqual({f["path"]: f["action"] for f in dry["files"]}["wiki/concepts/oven-airflow.md"], "create")
        self.assertFalse((self.vault / "wiki/concepts/oven-airflow.md").exists())
        result = op.apply(operation)
        self.assertTrue(result.get("applied"), result)
        self.assertTrue((self.vault / "wiki/concepts/oven-airflow.md").is_file())
        log = (self.vault / "wiki/log.md").read_text()
        self.assertTrue(log.endswith(RECORD + "\n"))
        self.assertEqual(op.link_check.check(self.vault)["errors"], [])
        with self.assertRaisesRegex(ValueError, "already applied"):
            op.apply(operation)
        undone = op.undo(operation)
        self.assertEqual(undone["skipped_changed_since"], [])
        self.assertFalse((self.vault / "wiki/concepts/oven-airflow.md").exists())
        self.assertEqual({p: op.file_hash(self.vault / p) for p in before}, before)

    def test_apply_refuses_unsafe_or_invalid_proposals(self):
        source = (self.vault / "wiki/sources/trial-a.md").read_text()
        cases = {
            "raw": ({"raw/trial-a.md": "x"}, RECORD, "not writable"),
            "log": ({"wiki/log.md": "x"}, RECORD, "not writable"),
            "instructions": ({"wiki/concepts/AGENTS.md": "x"}, RECORD, "not writable"),
            "traversal": ({"wiki/concepts/../../AGENTS.md": "x"}, RECORD, "not writable"),
            "cap": ({f"wiki/concepts/c{i}.md": CONCEPT for i in range(4)}, RECORD, "limit is 3"),
            "two records": ({"wiki/sources/trial-a.md": source}, RECORD + "\n## 2026-09-28 — x — partial", "single"),
            "checker": ({"wiki/concepts/oven-airflow.md": CONCEPT}, RECORD, "not_reciprocal"),
            "index file": ({"wiki/index.md": "# Index\n"}, RECORD, "must not be rewritten"),
            "dropped links": ({"wiki/sources/trial-a.md": "---\ntitle: \"x\"\n---\nshort\n"}, RECORD, "drops"),
            "empty": ({}, RECORD, "no pages"),
        }
        for name, (files, log, expected) in cases.items():
            with self.subTest(name=name):
                operation = self.staged()
                self.proposal(operation, files, log)
                result = op.apply(operation)
                self.assertTrue(any(expected in p for p in result["problems"]), result["problems"])
                self.assertFalse((operation / "receipt.json").exists())
                self.assertFalse((self.vault / "wiki/concepts/oven-airflow.md").exists())

    def test_drift_blocks_apply_and_undo_preserves_later_edits(self):
        operation = self.staged()
        self.proposal(operation)
        (self.vault / "wiki/log.md").write_text((self.vault / "wiki/log.md").read_text() + "\nHuman note.\n")
        self.assertIn("vault file changed since staging: wiki/log.md", op.apply(operation)["problems"])
        operation = self.staged()
        self.proposal(operation)
        self.assertTrue(op.apply(operation).get("applied"))
        edited = self.vault / "wiki/concepts/oven-airflow.md"
        edited.write_text(edited.read_text() + "Human addition.\n")
        undone = op.undo(operation)
        self.assertEqual(undone["skipped_changed_since"], ["wiki/concepts/oven-airflow.md"])
        self.assertIn("Human addition.", edited.read_text())

    def test_worker_evidence_verification(self):
        operation = self.staged()
        manifest = json.loads((operation / "manifest.json").read_text())
        corpus = operation / "corpus"

        def read(path, first=1, last=None, suffix=None):
            lines = (corpus / path).read_text().splitlines()
            last = len(lines) if last is None else last
            body = "\n".join(f"{n}: {lines[n - 1]}" for n in range(first, last + 1))
            end = suffix or (f"(End of file - total {len(lines)} lines)" if last == len(lines)
                             else f"(Output capped. Use offset={last + 1} to continue.)")
            return {"type": "tool_use", "part": {"tool": "read", "state": {
                "status": "completed", "input": {"filePath": str(corpus / path)},
                "output": f"<path>{path}</path>\n<content>\n{body}\n\n{end}\n</content>"}}}
        skill = {"type": "tool_use", "part": {"tool": "skill", "state": {
            "status": "completed", "input": {"name": "second-brain-ingest"}}}}
        text = {"type": "text", "part": {"text": "<<<NOTES>>>\nno-op"}}
        good = [skill, read("wiki/index.md"), read("instructions/wiki-contract.md"),
                read("wiki/sources/trial-a.md"), text]
        passed, evidence = op.verify_events(manifest, corpus, good, 0, {"a": 1}, {"a": 1})
        self.assertTrue(passed, evidence)
        half = len((corpus / "wiki/index.md").read_text().splitlines()) // 2
        chunked = [skill, read("wiki/index.md", 1, half), read("wiki/index.md", half + 1),
                   read("instructions/wiki-contract.md"), read("wiki/sources/trial-a.md"), text]
        self.assertTrue(op.verify_events(manifest, corpus, chunked, 0, {}, {})[0])  # large files in ranges
        gap = [skill, read("wiki/index.md", 1, half), read("instructions/wiki-contract.md"),
               read("wiki/sources/trial-a.md"), text]
        self.assertEqual(op.verify_events(manifest, corpus, gap, 0, {}, {})[1]["unread_required"], ["wiki/index.md"])
        truncated = good[:3] + [read("wiki/sources/trial-a.md", suffix="(line truncated to 2000)")] + [text]
        passed, evidence = op.verify_events(manifest, corpus, truncated, 0, {}, {})
        self.assertEqual(evidence["unread_required"], ["wiki/sources/trial-a.md"])
        outside = good + [{"type": "tool_use", "part": {"tool": "read", "state": {
            "status": "completed", "input": {"filePath": "/home/owner/AGENTS.md"}, "output": ""}}}]
        self.assertFalse(op.verify_events(manifest, corpus, outside, 0, {}, {})[1]["checks"]["reads_in_scope"])
        edit = good + [{"type": "tool_use", "part": {"tool": "edit", "state": {"status": "error"}}}]
        self.assertFalse(op.verify_events(manifest, corpus, edit, 0, {}, {})[1]["checks"]["only_reads"])
        self.assertFalse(op.verify_events(manifest, corpus, good, 0, {"a": 1}, {"a": 2})[0])

    def test_revise_only_for_a_failing_unapplied_proposal(self):
        query = op.stage(self.vault, "query", [], "What did Trial A find?", self.config)
        with self.assertRaisesRegex(ValueError, "revise needs"):
            op.revise(query)
        operation = self.staged()
        with self.assertRaisesRegex(ValueError, "revise needs"):
            op.revise(operation)
        self.proposal(operation)
        with self.assertRaisesRegex(ValueError, "already passes"):
            op.revise(operation)
        self.assertFalse((operation / "attempt-1").exists())

    def test_prompt_and_cli(self):
        operation = self.staged()
        prompt = op.worker_prompt(json.loads((operation / "manifest.json").read_text()), operation / "corpus")
        self.assertIn("at most 3 new or changed pages", prompt)
        self.assertNotIn("@", prompt)
        result = subprocess.run([sys.executable, str(CLI), "status", str(operation)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["kind"], "compile")
        result = subprocess.run([sys.executable, str(CLI), "apply", str(operation)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()


class SeriesTests(unittest.TestCase):
    """Series retry policy with a scripted worker in place of OpenCode."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.vault = base / "vault"
        for path in FIXTURE.rglob("*"):
            if path.is_file():
                target = self.vault / path.relative_to(FIXTURE)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(path.read_bytes())
        for n in (1, 2, 3):
            (self.vault / f"raw/book-part-{n}.md").write_text(f"Invented part {n}.\n")
        self.config = base / "operator.json"
        self.config.write_text(json.dumps({"agent": "a", "model": "p/m", "opencode_version": "0",
                                           "workdir": str(base / "ops")}))
        self.replies, self.prompts = [], []
        self.saved = (op.run, op.worker_prompt)

        def fake_run(operation, feedback=None, format_only=False):
            manifest = json.loads((operation / "manifest.json").read_text())
            self.prompts.append((manifest["series"], feedback, format_only))
            text = self.replies.pop(0)(manifest)
            (operation / "response.md").write_text(text)
            result = {"passed": True, "checks": {"run_completed": True}}
            try:
                (operation / "proposal.json").write_text(json.dumps(op.parse_proposal(text)))
            except ValueError as error:
                result.update(passed=False, proposal_error=str(error))
            (operation / "run.json").write_text(json.dumps(result))
            return result
        op.run = fake_run

    def tearDown(self):
        op.run, op.worker_prompt = self.saved
        self.tmp.cleanup()

    @staticmethod
    def good(manifest, extra=""):
        n = manifest["inputs"][0].rsplit("-", 1)[1][:-3]
        page = (f'---\ntitle: "Part {n}"\ntype: "source"\ncreated: "2026-09-28"\nupdated: "2026-09-28"\n'
                f'aliases: []\ntags: []\nurl: null\nauthor: null\npublished: null\ncaptured: "2026-09-28"\n'
                f'raw: "{manifest["inputs"][0]}"\n---\n\n# Part {n}\n\nInvented.{extra}\n')
        return (f"<<<FILE wiki/sources/book-part-{n}.md>>>\n{page}<<<END FILE>>>\n<<<INDEX>>>\n"
                f"Sources | - [[wiki/sources/book-part-{n}|Part {n}]] — part {n}.\n<<<LOG>>>\n"
                f"## 2026-09-28 — ingest part {n} — partial\n<<<NOTES>>>\nok")

    def test_series_applies_in_order_repairs_and_resumes(self):
        self.replies = [
            lambda m: self.good(m, " See [[wiki/sources/book-part-2|next part]]."),      # forward link: repaired
            lambda m: "I will now write the proposal.",                               # no markers: format revise
            lambda m: self.good(m),
            lambda m: "<<<NOTES>>>\nfront matter only",                               # no change: continue
        ]
        inputs = [f"raw/book-part-{n}.md" for n in (1, 2, 3)]
        lines = []
        result = op.series(self.vault, inputs, "Ingest {input} ({position}/{count})", self.config, emit=lines.append)
        self.assertEqual(result["status"], "completed", result)
        self.assertEqual([line["status"] for line in lines], ["applied", "applied", "no change"])
        self.assertIn("unlinked missing wiki/sources/book-part-2", " ".join(lines[0]["fixes"]))
        self.assertEqual(self.prompts[1][0]["previous_source"], "wiki/sources/book-part-1.md")
        self.assertTrue(self.prompts[2][2])  # the second item's retry was format-only
        self.assertTrue(self.prompts[0][0]["sources_only"])
        self.assertEqual(op.link_check.check(self.vault)["errors"], [])
        self.replies = [lambda m: "<<<NOTES>>>\nstill nothing"]
        again = op.series(self.vault, inputs, None, self.config, emit=lines.append)
        self.assertEqual((again["skipped"], again["no change"]), (2, 1))  # resumes past ingested parts

    def test_series_stops_after_bounded_retries(self):
        self.replies = [lambda m: "no markers"] * 4
        result = op.series(self.vault, ["raw/book-part-1.md"], None, self.config, emit=lambda line: None)
        self.assertEqual((result["status"], result["stopped_at"]), ("stopped", "raw/book-part-1.md"))
        self.assertEqual(len(self.prompts), 4)  # two operations, each with one format revision
        self.assertFalse((Path(json.loads(self.config.read_text())["workdir"]) / "series.lock").exists())

    def test_series_status_reads_background_log(self):
        workdir = Path(json.loads(self.config.read_text())["workdir"])
        workdir.mkdir(parents=True, exist_ok=True)
        log = workdir / "series-20260928-000000.jsonl"
        log.write_text(json.dumps({"input": "raw/book-part-1.md", "position": 1, "status": "applied"}) + "\n"
                       + json.dumps({"status": "completed", "applied": 1, "no change": 0, "skipped": 0}) + "\n")
        status = op.series_status(self.vault, self.config)
        self.assertEqual((status["running"], status["applied"], status["result"]["status"]), (False, 1, "completed"))
