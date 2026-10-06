"""Offline operator checks on invented vaults; `run` is covered by its event verifier only."""

import json
import os
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

    def test_workers_get_a_catalog_not_the_index(self):
        index = (self.vault / "wiki/index.md").read_text()
        for kind, inputs, task in (("ingest", ["raw/trial-b.md"], "Ingest trial B"),
                                   ("compile", ["wiki/sources/trial-a.md"], "t"), ("compile", [], "vent setting"),
                                   ("query", [], "Which vent setting?")):
            with self.subTest(kind=kind, inputs=inputs):
                operation = self.staged(kind, inputs, task)
                manifest = json.loads((operation / "manifest.json").read_text())
                self.assertFalse((operation / "corpus/wiki/index.md").exists())
                catalog = (operation / "corpus/catalog.md").read_text()
                self.assertIn("# Catalog for this operation", catalog)
                self.assertIn("catalog.md", manifest["reads"])
                prompt = op.worker_prompt(manifest, operation / "corpus")
                self.assertIn("Read catalog.md first", prompt)
                self.assertNotIn("<<<INDEX>>>", prompt)
        named = self.staged("compile", ["wiki/sources/trial-a.md"], "t")
        catalog = (named / "corpus/catalog.md").read_text()
        related = catalog.split("## Related pages", 1)[1]
        self.assertIn("[[wiki/concepts/vent-choice|Vent choice]] — competing evidence", related)  # linked from the input
        self.assertEqual((self.vault / "wiki/index.md").read_text(), index)

    def test_stage_refuses_a_hand_written_index_until_migrated(self):
        index = self.vault / "wiki/index.md"
        index.write_text(index.read_text().replace(op.wiki_index.MARKER, ""))
        with self.assertRaisesRegex(ValueError, "migrate-index"):
            self.staged()
        self.assertTrue(op.stage(self.vault, "query", [], "Which vent setting?", self.config).is_dir())

    def test_apply_regenerates_the_index_from_frontmatter(self):
        operation = self.staged()
        concept = CONCEPT.replace('tags: []\n', 'tags: []\nsummary: "How airflow changes tray drying."\n'
                                  'theme: "Tray trials"\ngaps: ["No humidity readings."]\n')
        self.proposal(operation, files={"wiki/concepts/oven-airflow.md": concept},
                      index=[["Concepts", "- [[wiki/concepts/oven-airflow|Wrong]] — ignored."]])
        result = op.apply(operation)
        self.assertTrue(result.get("applied"), result)
        self.assertIn("ignored 1 INDEX line(s): the operator generates the index", result["fixes"])
        index = (self.vault / "wiki/index.md").read_text()
        concepts = index.split("## Concepts", 1)[1].split("\n## ", 1)[0]
        self.assertIn("### Tray trials\n\n- [[wiki/concepts/oven-airflow|Oven airflow]] — How airflow changes", concepts)
        self.assertIn("- [[wiki/concepts/oven-airflow|Oven airflow]]: No humidity readings.", index.split("## Gaps")[1])
        self.assertFalse(op.link_check.check(self.vault)["errors"])
        op.undo(operation)
        self.assertNotIn("oven-airflow", (self.vault / "wiki/index.md").read_text())

    def test_a_missing_summary_is_filled_and_rewrites_keep_catalog_fields(self):
        operation = self.staged()
        page = (self.vault / "wiki/sources/trial-a.md").read_text()
        rewritten = "\n".join(line for line in page.splitlines() if not line.startswith(("summary:", "gaps:")))
        self.proposal(operation, files={"wiki/sources/trial-a.md": rewritten + "\n", "wiki/concepts/oven-airflow.md": CONCEPT})
        fixed, fixes = op.normalize(json.loads((operation / "manifest.json").read_text()),
                                    json.loads((operation / "proposal.json").read_text()))
        self.assertIn("added a summary to wiki/sources/trial-a.md from its previous version", fixes)
        self.assertIn("added a summary to wiki/concepts/oven-airflow.md from its first sentence", fixes)
        self.assertEqual(op.wiki_index.get_field(fixed["files"]["wiki/concepts/oven-airflow.md"], "summary"),
                         "Trial A timed the open vent at 18 minutes (Trial A, raw Measurements).")
        self.assertTrue(op.apply(operation).get("applied"))

    def test_gaps_lines_add_to_existing_pages(self):
        operation = self.staged()
        self.proposal(operation, files={})
        proposal = json.loads((operation / "proposal.json").read_text())
        proposal["gaps"] = [["wiki/sources/trial-b.md", "Oven model is not stated."],
                            ["wiki/sources/missing.md", "dropped"]]
        (operation / "proposal.json").write_text(json.dumps(proposal))
        result = op.apply(operation)
        self.assertTrue(result.get("applied"), result)
        self.assertIn("dropped a gap for missing page wiki/sources/missing.md", result["fixes"])
        self.assertEqual(op.wiki_index.get_field((self.vault / "wiki/sources/trial-b.md").read_text(), "gaps"),
                         ["Oven model is not stated."])
        self.assertIn("[[wiki/sources/trial-b|Tray trial B]]: Oven model is not stated.",
                      (self.vault / "wiki/index.md").read_text())
        empty = self.staged()
        self.proposal(empty, files={})
        self.assertIn("proposal changes no pages", op.apply(empty, dry_run=True)["problems"])

    def test_a_new_page_that_duplicates_an_existing_one_is_refused(self):
        operation = self.staged()
        twin = CONCEPT.replace('title: "Oven airflow"', 'title: "Vent Choice"')
        self.proposal(operation, files={"wiki/concepts/vent-selection.md": twin})
        problems = op.apply(operation, dry_run=True)["problems"]
        self.assertTrue(any("duplicates existing page wiki/concepts/vent-choice.md" in p for p in problems), problems)
        alias = CONCEPT.replace('aliases: []', 'aliases: ["Tray trial A"]')
        other = self.staged()
        self.proposal(other, files={"wiki/concepts/oven-airflow.md": alias})
        self.assertFalse(any("duplicates" in p for p in op.apply(other, dry_run=True)["problems"]))  # source vs concept

    def test_migrate_index_stages_for_review_then_applies_and_undoes(self):
        index = self.vault / "wiki/index.md"
        pages = {key: (self.vault / key).read_text() for key in op.link_check.collect(self.vault)[0]
                 if key != "wiki/index.md"}
        for key, text in pages.items():
            if key != "wiki/log.md":
                (self.vault / key).write_text("\n".join(line for line in text.splitlines()
                                                         if not line.startswith(("summary:", "gaps:"))) + "\n")
        index.write_text("# Index\n\n## Concepts\n\n- [[wiki/concepts/vent-choice|Vent choice]] — two settings.\n\n"
                         "## Sources\n\n### Trials\n\n- [[wiki/sources/trial-a|Trial A]] — open vent.\n\n"
                         "## Gaps\n\n- Humidity was not measured in the trials.\n- Humidity was not measured in the trials.\n")
        before = {key: (self.vault / key).read_text() for key in [*pages, "wiki/index.md"]}
        with self.assertRaisesRegex(ValueError, "migrate-index"):
            self.staged()
        staged = op.migrate_index(self.vault, self.config, today="2026-10-01")
        operation = Path(staged["operation"])
        self.assertEqual(staged["gaps"], 1)  # duplicates collapsed
        self.assertEqual(staged["summary from index"], 2)
        self.assertEqual(staged["theme from index"], 1)
        self.assertEqual({key: (self.vault / key).read_text() for key in before}, before)  # staging writes nothing
        gaps = json.loads((operation / "gaps.json").read_text())
        self.assertEqual(gaps[0]["gap"], "Humidity was not measured in the trials.")
        gaps[0]["page"] = "wiki/sources/trial-a"
        (operation / "gaps.json").write_text(json.dumps(gaps))
        result = op.apply_migration(operation)
        self.assertTrue(result["applied"], result)
        trial = (self.vault / "wiki/sources/trial-a.md").read_text()
        self.assertEqual(op.wiki_index.get_field(trial, "summary"), "open vent.")
        self.assertEqual(op.wiki_index.get_field(trial, "theme"), "Trials")
        self.assertEqual(op.wiki_index.get_field(trial, "gaps"), ["Humidity was not measured in the trials."])
        self.assertIn('updated: "2026-09-24"', trial)  # metadata only: the content date is kept
        self.assertTrue(op.wiki_index.is_generated(index.read_text()))
        self.assertFalse(op.link_check.check(self.vault)["errors"])
        self.assertIn("migrate index to the generated form — partial", (self.vault / "wiki/log.md").read_text())
        self.assertTrue(self.staged().is_dir())
        with self.assertRaisesRegex(ValueError, "already applied"):
            op.apply_migration(operation)
        op.undo(operation)
        self.assertEqual({key: (self.vault / key).read_text() for key in before}, before)

    def test_rebuild_index_after_a_hand_edit(self):
        page = self.vault / "wiki/sources/trial-b.md"
        page.write_text(op.wiki_index.set_fields(page.read_text(), {"summary": "Hand-written summary."}))
        self.assertIn("index_stale", {d["kind"] for d in op.link_check.check(self.vault)["errors"]})
        self.assertTrue(op.rebuild_index(self.vault, self.config, dry_run=True)["changed"])
        result = op.rebuild_index(self.vault, self.config)
        self.assertTrue(Path(result["backup"]).is_file())
        self.assertIn("Hand-written summary.", (self.vault / "wiki/index.md").read_text())
        self.assertEqual(op.link_check.check(self.vault)["errors"], [])
        self.assertFalse(op.rebuild_index(self.vault, self.config)["changed"])
        index = self.vault / "wiki/index.md"
        index.write_text(index.read_text().replace(op.wiki_index.MARKER, ""))
        with self.assertRaisesRegex(ValueError, "migrate-index"):
            op.rebuild_index(self.vault, self.config)

    def test_migration_finds_capture_parts_through_their_chapter(self):
        raw = self.vault / "raw"
        for n in (1, 2):
            (raw / f"book-part-{n}.md").write_text(f'---\ntitle: "Book"\npart: "{n}/2"\n---\n\n## Page {n}\n\nText.\n')
        def source(slug, title, raw_path, body):
            return (f'---\ntitle: "{title}"\ntype: "source"\ncreated: "2026-09-24"\nupdated: "2026-09-24"\n'
                    f'aliases: []\ntags: []\nsummary: "{title}."\nauthor: null\npublished: null\n'
                    f'captured: "2026-09-24"\nraw: "{raw_path}"\n---\n\n# {title}\n\n{body}\n')
        wiki = self.vault / "wiki/sources"
        (wiki / "book-part-1.md").write_text(source("book-part-1", "Book, part 1", "raw/book-part-1.md",
                                                    "Next: [[wiki/sources/book-part-2|Part 2]]."))
        (wiki / "book-part-2.md").write_text(source("book-part-2", "Book, part 2", "raw/book-part-2.md",
                                                    "Previous: [[wiki/sources/book-part-1|Part 1]]."))
        (wiki / "book-chapter-1.md").write_text(source("book-chapter-1", "Book, chapter 1", "raw/trial-a.md",
            "Built from [[wiki/sources/book-part-1|part 1]] and [[wiki/sources/book-part-2|part 2]]."))
        index = self.vault / "wiki/index.md"
        index.write_text(index.read_text().replace(op.wiki_index.MARKER, ""))
        operation = Path(op.migrate_index(self.vault, self.config)["operation"])
        values = json.loads((operation / "manifest.json").read_text())["values"]
        self.assertEqual(values["wiki/sources/book-part-1.md"]["part_of"], "wiki/sources/book-chapter-1")
        self.assertNotIn("part_of", values.get("wiki/sources/book-chapter-1.md", {}))
        (operation / "gaps.json").write_text("[]")
        self.assertTrue(op.apply_migration(operation)["applied"])
        text = index.read_text()
        self.assertIn("[[wiki/sources/book-chapter-1|Book, chapter 1]] — Book, chapter 1. (2 parts)", text)
        self.assertNotIn("[[wiki/sources/book-part-1|", text)
        self.assertFalse(op.link_check.check(self.vault)["errors"])

    def test_parse_index_themes(self):
        text = ("<<<INDEX>>>\nSources | Distributed systems: concepts | - [[wiki/sources/p1|Part 1]] — one.\n"
                "Concepts | [[wiki/concepts/x|X]] — no theme, pipe in link.\nSources | Book | [[wiki/sources/p2|P2]]\n"
                "<<<LOG>>>\n" + RECORD)
        self.assertEqual(op.parse_proposal(text)["index"], [
            ["Sources", "- [[wiki/sources/p1|Part 1]] — one.", "Distributed systems: concepts"],
            ["Concepts", "- [[wiki/concepts/x|X]] — no theme, pipe in link."],
            ["Sources", "- [[wiki/sources/p2|P2]]", "Book"]])

    def test_search_calls_are_verified_and_confined(self):
        operation = self.staged()
        manifest = json.loads((operation / "manifest.json").read_text())
        corpus = operation / "corpus"
        self.assertTrue(manifest["config"]["search"])

        def read(path):
            lines = (corpus / path).read_text().splitlines()
            body = "\n".join(f"{n}: {line}" for n, line in enumerate(lines, 1))
            return {"type": "tool_use", "part": {"tool": "read", "state": {
                "status": "completed", "input": {"filePath": path},
                "output": f"<content>\n{body}\n\n(End of file - total {len(lines)} lines)\n</content>"}}}

        def search(tool, path=None):
            return {"type": "tool_use", "part": {"tool": tool, "state": {
                "status": "completed", "input": {"pattern": "vent", **({"path": path} if path else {})}}}}
        skill = {"type": "tool_use", "part": {"tool": "skill", "state": {
            "status": "completed", "input": {"name": "second-brain-ingest"}}}}
        base = [skill, read("catalog.md"), read("instructions/wiki-contract.md"), read("wiki/sources/trial-a.md"),
                {"type": "text", "part": {"text": "<<<NOTES>>>\nno-op"}}]
        passed, evidence = op.verify_events(manifest, corpus, [search("grep"), search("glob", "wiki")] + base, 0, {}, {})
        self.assertTrue(passed, evidence)
        self.assertEqual(evidence["searches"], 2)
        for path in ("/home/owner", "../outside", str(corpus / "../x")):
            with self.subTest(path=path):
                checks = op.verify_events(manifest, corpus, [search("grep", path)] + base, 0, {}, {})[1]["checks"]
                self.assertFalse(checks["searches_in_scope"])
        manifest["config"]["search"] = False
        self.assertFalse(op.verify_events(manifest, corpus, [search("grep")] + base, 0, {}, {})[1]["checks"]["only_reads"])
        self.assertIn("directory listings are not available", op.worker_prompt(manifest, corpus))
        manifest["config"]["search"] = True
        self.assertIn("grep and glob", op.worker_prompt(manifest, corpus))
        self.assertIn("operation.md (the operation manifest, optional", op.worker_prompt(manifest, corpus))

    def test_run_refuses_a_corpus_with_ungranted_files(self):
        operation = self.staged()
        (operation / "corpus/stray.md").write_text("not granted\n")
        with self.assertRaisesRegex(ValueError, "without read grants: stray.md"):
            op.run(operation)

    def test_accept_appends_one_record_for_unaccepted_operations(self):
        log = self.vault / "wiki/log.md"
        log.write_text(log.read_text().rstrip("\n") + "\n\n## 2026-09-28 — Book part 1 ingest — partial\n- x\n\n"
                       "## 2026-09-28 — Owner acceptance (sampled) — completed\n- Accepted operations: "
                       "2026-09-28 book part 1 ingest.\n\n## 2026-09-29 — Book part 2 ingest — partial\n- y\n\n"
                       "## 2026-09-29 — Chapter 1 compile — partial\n- z\n")
        self.assertEqual(op.unaccepted(log.read_text())[-2:], ["2026-09-29 Book part 2 ingest", "2026-09-29 Chapter 1 compile"])
        with self.assertRaisesRegex(ValueError, "needs --sample"):
            op.accept(self.vault, "sampled", " ", "none", config_path=self.config)
        preview = op.accept(self.vault, "sampled", "not itemized", "none", match="book part", config_path=self.config,
                            dry_run=True, today="2026-09-30")
        self.assertEqual((preview["operations"], preview["first"]), (1, "2026-09-29 Book part 2 ingest"))
        before = log.read_text()
        done = op.accept(self.vault, "sampled", "chapter 1 page, not itemized otherwise", "none",
                         config_path=self.config, today="2026-09-30")
        text = log.read_text()
        self.assertTrue(text.startswith(before.rstrip("\n")))
        self.assertIn("## 2026-09-30 — Owner acceptance (sampled) — completed\n- Accepted operations:\n"
                      "  - 2026-09-29 Book part 2 ingest\n  - 2026-09-29 Chapter 1 compile", text)
        self.assertTrue(Path(done["backup"]).is_file())
        self.assertNotIn("2026-09-29 Chapter 1 compile", op.unaccepted(text))
        with self.assertRaisesRegex(ValueError, "no unaccepted"):
            op.accept(self.vault, "full", "all", "none", match="Chapter 1", config_path=self.config)
        self.assertEqual(op.link_check.check(self.vault)["errors"], [])

    def test_page_limit_counts_written_pages_not_links(self):
        operation = self.staged()
        manifest = json.loads((operation / "manifest.json").read_text())
        links = [[f"wiki/sources/trial-{x}.md", "- [[wiki/concepts/oven-airflow|Oven airflow]] — cites"] for x in "ab"]
        links += [["wiki/concepts/vent-choice.md", "- [[wiki/concepts/oven-airflow|Oven airflow]] — related"],
                  ["wiki/entities/aster-desk-lab.md", "- [[wiki/concepts/oven-airflow|Oven airflow]] — related"]]
        proposal = {"files": {"wiki/concepts/oven-airflow.md": CONCEPT}, "links": links, "index": [], "log": RECORD}
        self.assertFalse([p for p in op.check_proposal(manifest, proposal) if "limit" in p])  # 1 page + 4 links, limit 3

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

    def test_edit_blocks_change_part_of_an_existing_page(self):
        reply = ("<<<EDIT wiki/sources/trial-a.md>>>\n<<<OLD>>>\nopen reached the target in\n  18 minutes\n"
                 "<<<NEW>>>\nopen reached the target in\n  19 minutes\n<<<OLD>>>\nwith a single-trial\n<<<NEW>>>\n"
                 "with a one-trial\n<<<END EDIT>>>\n<<<EDIT wiki/sources/trial-b.md>>>\n<<<OLD>>>\ndangling\n"
                 f"<<<END EDIT>>>\n<<<LOG>>>\n{RECORD}\n<<<NOTES>>>\nTwo corrections.")
        parsed = op.parse_proposal(reply)
        self.assertEqual(parsed["edits"], [["wiki/sources/trial-a.md", "open reached the target in\n  18 minutes",
                                            "open reached the target in\n  19 minutes"],
                                           ["wiki/sources/trial-a.md", "with a single-trial", "with a one-trial"]])
        self.assertIn("skipped an EDIT of wiki/sources/trial-b.md with OLD but no NEW", parsed["warnings"])
        operation = self.staged()
        before = (self.vault / "wiki/sources/trial-a.md").read_text()
        (operation / "run.json").write_text(json.dumps({"passed": True}))
        op.write_json(operation / "proposal.json", parsed)
        result = op.apply(operation)
        self.assertTrue(result.get("applied"), result)
        self.assertEqual(result["edits_applied"], ["wiki/sources/trial-a.md: 2"])
        after = (self.vault / "wiki/sources/trial-a.md").read_text()
        expected = (before.replace("18 minutes and", "19 minutes and").replace("single-trial", "one-trial")
                    .replace('updated: "2026-09-24"', 'updated: "2026-09-28"'))
        self.assertEqual(after, expected)
        op.undo(operation)
        self.assertEqual((self.vault / "wiki/sources/trial-a.md").read_text(), before)
        for edits, expected in (([["wiki/sources/trial-a.md", "no such text", "x"]], "was not found"),
                                ([["wiki/sources/trial-a.md", "raw/trial-a.md", "x"]], "occurs 3 times"),
                                ([["wiki/sources/trial-a.md", "", "x"]], "is empty"),
                                ([["wiki/sources/missing.md", "a", "b"]], "not an existing wiki page"),
                                ([["wiki/concepts/oven-airflow.md", "Trial A", "x"]], "both rewritten and edited")):
            operation = self.staged()
            self.proposal(operation, files={"wiki/concepts/oven-airflow.md": CONCEPT})
            proposal = json.loads((operation / "proposal.json").read_text())
            proposal["edits"] = edits
            (operation / "proposal.json").write_text(json.dumps(proposal))
            problems = op.apply(operation, dry_run=True)["problems"]
            self.assertTrue(any(expected in p for p in problems), problems)
        manifest = json.loads((self.staged() / "manifest.json").read_text())
        prompt = op.worker_prompt(manifest, Path(manifest["vault"]))
        self.assertIn("<<<EDIT path>>>", prompt)
        self.assertIn("never completing or correcting it", prompt)

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
        self.assertEqual(fixed["index"], [])
        self.assertIn("ignored 2 INDEX line(s): the operator generates the index", fixes)
        self.assertTrue(fixed["log"].startswith("## 2026-09-28 — compile wiki/sources/trial-a.md — partial"))
        self.assertEqual(len(fixes), 4)
        self.assertIn("added the back-link wiki/sources/trial-a -> wiki/concepts/new", fixes)
        completed = dict(proposal, log="## 2026-09-28 — x — completed\n- y")
        self.assertTrue(op.normalize(manifest, completed)[0]["log"].startswith("## 2026-09-28 — x — partial"))

    def test_prompt_lists_read_ranges_for_files_over_the_cap(self):
        operation = self.staged()
        manifest = json.loads((operation / "manifest.json").read_text())
        corpus = operation / "corpus"
        self.assertNotIn("size cap", op.worker_prompt(manifest, corpus))
        (corpus / "catalog.md").write_text("".join(f"- entry {i} {'x' * 200}\n" for i in range(1, 501)))
        ranges = op.read_ranges(corpus / "catalog.md")
        self.assertGreater(len(ranges), 1)
        self.assertEqual(ranges[0][0], 1)
        self.assertEqual(sum(count for _, count in ranges), 500)
        self.assertTrue(all(a + n == b for (a, n), (b, _) in zip(ranges, ranges[1:])))
        self.assertIn(f"offset=1 limit={ranges[0][1]}", op.worker_prompt(manifest, corpus))

    def test_normalize_turns_markdown_page_links_into_wikilinks(self):
        operation = self.staged()
        manifest = json.loads((operation / "manifest.json").read_text())
        body = ("After [Trial A](wiki/sources/trial-a), [again](../sources/trial-a.md), [gone](wiki/sources/gone), "
                "[web](https://example.com), [anchor](#x) and ![fig](../../raw/assets/a.png).\n"
                "```\n[code](wiki/sources/trial-a)\n```\n")
        proposal = {"files": {"wiki/concepts/new.md": body}, "links": [], "index": [], "log": RECORD, "notes": ""}
        fixed, fixes = op.normalize(manifest, proposal)
        text = fixed["files"]["wiki/concepts/new.md"]
        self.assertIn("After [[wiki/sources/trial-a|Trial A]], [[wiki/sources/trial-a|again]], gone, "
                      "[web](https://example.com), [anchor](#x)", text)
        self.assertIn("[code](wiki/sources/trial-a)", text)
        self.assertEqual(sum("into a wikilink" in f for f in fixes), 3)

    def test_normalize_adds_missing_concept_back_links(self):
        operation = self.staged("ingest", ["raw/trial-b.md"], "Ingest trial B")
        manifest = json.loads((operation / "manifest.json").read_text())
        page = ('---\ntitle: "New | trial"\ntype: "source"\n---\n\n# New\n\nSee '
                '[[wiki/concepts/vent-choice|Vent choice]] and [[wiki/sources/trial-a|Trial A]].\n')
        proposal = {"files": {"wiki/sources/new.md": page}, "links": [], "index": [], "log": RECORD, "notes": ""}
        fixed, fixes = op.normalize(manifest, proposal)
        self.assertEqual(fixed["links"], [["wiki/concepts/vent-choice.md",
                                           "- [[wiki/sources/new|New   trial]] — source that cites this page"]])
        self.assertIn("added the back-link wiki/concepts/vent-choice -> wiki/sources/new", fixes)
        again, _ = op.normalize(manifest, fixed)
        self.assertEqual(len(again["links"]), 1)  # not added twice
        concept = CONCEPT.replace("[[wiki/sources/trial-a|Trial A]]", "[[wiki/sources/trial-b|Trial B]]")
        cited, fixes = op.normalize(manifest, dict(proposal, files={"wiki/concepts/oven-airflow.md": concept}))
        self.assertEqual(cited["links"], [["wiki/sources/trial-b.md",
                                           "- [[wiki/concepts/oven-airflow|Oven airflow]] — page that cites this source"]])
        # A LINKS line from an existing source to a concept the proposal writes: the back-link goes into the page.
        patched, fixes = op.normalize(manifest, dict(proposal, files={"wiki/concepts/oven-airflow.md": CONCEPT},
                                                     links=[["wiki/sources/trial-b.md",
                                                             "- [[wiki/concepts/oven-airflow|Oven airflow]] — concept"]]))
        self.assertIn("[[wiki/sources/trial-b|", patched["files"]["wiki/concepts/oven-airflow.md"])
        self.assertIn("added the back-link wiki/concepts/oven-airflow -> wiki/sources/trial-b", fixes)

    def test_normalize_repairs_missing_images(self):
        operation = self.staged("ingest", ["raw/trial-b.md"], "Ingest trial B")
        manifest = json.loads((operation / "manifest.json").read_text())
        (self.vault / "raw/assets/cap").mkdir(parents=True)
        (self.vault / "raw/assets/cap/page-01.png").write_bytes(b"x")
        body = ("![Figure 1, page 1](../../raw/assets/cap/page-01.png)\n![Figure 2, page 2](../../raw/assets/cap/page-02.png)\n"
                "![Figure 3](../../raw/raw/assets/cap/page-01.png)\n![web](https://example.com/x.png)\n")
        fixed, fixes = op.normalize(manifest, {"files": {"wiki/sources/new.md": body}, "links": [], "index": [],
                                               "log": RECORD, "notes": ""})
        text = fixed["files"]["wiki/sources/new.md"]
        self.assertIn("![Figure 1, page 1](../../raw/assets/cap/page-01.png)", text)
        self.assertIn("Figure 2, page 2 (image not rendered)", text)
        self.assertIn("![Figure 3](../../raw/assets/cap/page-01.png)", text)
        self.assertIn("![web](https://example.com/x.png)", text)
        self.assertEqual(sum("image" in f for f in fixes), 2)

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
            "checker": ({"wiki/concepts/oven-airflow.md": CONCEPT.replace("# Oven airflow", "# {{TITLE}}")}, RECORD,
                        "placeholder"),
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

    def test_only_problems_a_proposal_adds_block_it(self):
        # A hand edit leaves a problem in the vault: an unrelated operation still applies.
        source = self.vault / "wiki/sources/trial-b.md"
        source.write_text(source.read_text() + "\nSee [[vent choice]] and ![fig](../../raw/assets/missing.png).\n")
        existing = op.link_check.check(self.vault)
        self.assertTrue(existing["errors"] and existing["unsupported"])
        operation = self.staged()
        self.proposal(operation)
        result = op.apply(operation)
        self.assertTrue(result.get("applied"), result["problems"])
        self.assertEqual(result["checker"]["existing"], 2)
        self.assertTrue(json.loads((operation / "receipt.json").read_text())["post_check_clean"])
        # A proposal that adds its own broken evidence link is refused (images are repaired instead).
        operation = self.staged()
        concept = CONCEPT.replace("# Oven airflow", "# Airflow two").replace("Oven airflow", "Airflow two")
        self.proposal(operation, {"wiki/concepts/airflow-two.md": concept + "See [the capture](../../raw/missing.md).\n"},
                      index=[["Concepts", "- [[wiki/concepts/airflow-two|Airflow two]] — two."]])
        problems = op.apply(operation, dry_run=True)["problems"]
        self.assertTrue(any("missing_evidence wiki/concepts/airflow-two.md" in p for p in problems), problems)
        self.assertFalse(any("trial-b" in p for p in problems), problems)

    def test_drift_blocks_apply_and_undo_preserves_later_edits(self):
        operation = self.staged()
        self.proposal(operation)
        # Another operation's log record and gap land in between: the log appends and the index regenerates.
        (self.vault / "wiki/log.md").write_text((self.vault / "wiki/log.md").read_text() + "\nHuman note.\n")
        index, other = self.vault / "wiki/index.md", self.vault / "wiki/sources/trial-b.md"
        other.write_text(op.wiki_index.set_fields(other.read_text(), {"gaps": ["A concurrent gap."]}))
        index.write_text(op.rebuilt_index(self.vault))
        self.assertTrue(op.apply(operation).get("applied"))
        self.assertIn("Human note.", (self.vault / "wiki/log.md").read_text())
        self.assertIn("A concurrent gap.", index.read_text())
        self.assertIn("[[wiki/concepts/oven-airflow|", index.read_text())
        # A later change to the index does not leave it stale when the earlier operation is undone.
        other.write_text(op.wiki_index.set_fields(other.read_text(), {"gaps": ["A later gap."]}))
        index.write_text(op.rebuilt_index(self.vault))
        undone = op.undo(operation)
        self.assertTrue(undone["index_rebuilt"])
        self.assertNotIn("oven-airflow", index.read_text())
        self.assertFalse(op.link_check.check(self.vault)["errors"])
        # A page the proposal rewrites that changed since staging is refused, and revise won't retry it.
        operation = self.staged()
        self.proposal(operation)
        source = self.vault / "wiki/sources/trial-a.md"
        source.write_text(source.read_text() + "Human edit.\n")
        self.assertIn("vault file changed since staging: wiki/sources/trial-a.md", op.apply(operation)["problems"])
        with self.assertRaisesRegex(ValueError, "stage the operation again"):
            op.revise(operation)
        source.write_text(source.read_text().replace("Human edit.\n", ""))
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
        good = [skill, read("catalog.md"), read("instructions/wiki-contract.md"),
                read("wiki/sources/trial-a.md"), text]
        passed, evidence = op.verify_events(manifest, corpus, good, 0, {"a": 1}, {"a": 1})
        self.assertTrue(passed, evidence)
        half = len((corpus / "catalog.md").read_text().splitlines()) // 2
        chunked = [skill, read("catalog.md", 1, half), read("catalog.md", half + 1),
                   read("instructions/wiki-contract.md"), read("wiki/sources/trial-a.md"), text]
        self.assertTrue(op.verify_events(manifest, corpus, chunked, 0, {}, {})[0])  # large files in ranges
        gap = [skill, read("catalog.md", 1, half), read("instructions/wiki-contract.md"),
               read("wiki/sources/trial-a.md"), text]
        self.assertEqual(op.verify_events(manifest, corpus, gap, 0, {}, {})[1]["unread_required"], ["catalog.md"])
        truncated = good[:3] + [read("wiki/sources/trial-a.md", suffix="(line truncated to 2000)")] + [text]
        passed, evidence = op.verify_events(manifest, corpus, truncated, 0, {}, {})
        self.assertEqual(evidence["unread_required"], ["wiki/sources/trial-a.md"])
        outside = good + [{"type": "tool_use", "part": {"tool": "read", "state": {
            "status": "completed", "input": {"filePath": "/home/owner/AGENTS.md"}, "output": ""}}}]
        self.assertFalse(op.verify_events(manifest, corpus, outside, 0, {}, {})[1]["checks"]["reads_in_scope"])
        edit = good + [{"type": "tool_use", "part": {"tool": "edit", "state": {"status": "error"}}}]
        self.assertFalse(op.verify_events(manifest, corpus, edit, 0, {}, {})[1]["checks"]["only_reads"])
        self.assertFalse(op.verify_events(manifest, corpus, good, 0, {"a": 1}, {"a": 2})[0])

    def test_query_citations_must_be_read(self):
        query = op.stage(self.vault, "query", [], "What did Trial A find?", self.config)
        manifest, corpus = json.loads((query / "manifest.json").read_text()), query / "corpus"

        def read(path):
            lines = (corpus / path).read_text().splitlines()
            body = "\n".join(f"{n}: {line}" for n, line in enumerate(lines, 1))
            return {"type": "tool_use", "part": {"tool": "read", "state": {
                "status": "completed", "input": {"filePath": path},
                "output": f"<content>\n{body}\n\n(End of file - total {len(lines)} lines)\n</content>"}}}
        skill = {"type": "tool_use", "part": {"tool": "skill", "state": {
            "status": "completed", "input": {"name": "second-brain-query"}}}}
        grep = {"type": "tool_use", "part": {"tool": "grep", "state": {"status": "completed", "input": {"pattern": "vent"}}}}
        answer = ("Trial A timed 18 minutes (wiki/sources/trial-a.md, Measurements); Trial B differed "
                  "([[wiki/sources/trial-b|Trial B]]).\nRead: ...\nNot covered: none")
        base = [skill, read("catalog.md"), read("instructions/wiki-contract.md"), read("wiki/sources/trial-a.md"), grep]
        text = {"type": "text", "part": {"text": answer}}
        passed, evidence = op.verify_events(manifest, corpus, base + [text], 0, {}, {})
        self.assertFalse(passed)
        self.assertEqual(evidence["unread_citations"], ["wiki/sources/trial-b.md"])
        self.assertTrue(op.verify_events(manifest, corpus, base + [read("wiki/sources/trial-b.md"), text], 0, {}, {})[0])
        (query / "run.json").write_text(json.dumps({"passed": False, "checks": dict(evidence["checks"]),
                                                    "unread_citations": evidence["unread_citations"]}))
        (query / "response.md").write_text(answer + "\n")
        calls = []
        saved = op.run
        op.run = lambda operation, feedback=None, format_only=False: calls.append(feedback) or {"passed": True}
        try:
            op.revise(query)
        finally:
            op.run = saved
        self.assertIn("wiki/sources/trial-b.md", calls[0][0])
        self.assertIn("previous-proposal.md", json.loads((query / "manifest.json").read_text())["reads"])
        ingest = self.staged("ingest", ["raw/trial-b.md"], "Ingest trial B")
        imanifest = json.loads((ingest / "manifest.json").read_text())
        self.assertNotIn("citations_read", op.verify_events(imanifest, ingest / "corpus", [text], 0, {}, {})[1]["checks"])

    def test_operation_paths_resolve_before_use(self):
        operation = self.staged()
        seen = {}
        saved = op.configure_worker
        op.configure_worker = lambda corpus, profile, *rest: seen.update(corpus=corpus, profile=profile) or (_ for _ in ()).throw(RuntimeError("stop"))
        try:
            relative = Path(os.path.relpath(operation, Path.cwd()))
            with self.assertRaisesRegex(RuntimeError, "stop"):
                op.run(relative)
        finally:
            op.configure_worker = saved
        self.assertTrue(seen["profile"].is_absolute() and seen["corpus"].is_absolute())

    def test_revise_only_for_a_failing_unapplied_proposal(self):
        query = op.stage(self.vault, "query", [], "What did Trial A find?", self.config)
        with self.assertRaisesRegex(ValueError, "revise a query only"):
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
        self.assertIn("wiki/log.md, may be read in part", prompt)
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
                proposal = op.parse_proposal(text)
                (operation / "proposal.json").write_text(json.dumps(proposal))
                result.update(proposed_files=sorted(proposal["files"]), proposed_links=len(proposal["links"]))
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

    def test_series_files_source_entries_under_a_theme(self):
        (self.vault / "raw/book-part-1.md").write_text('---\ntitle: "Invented [Book] | Two"\n---\n\nPart 1.\n')
        self.assertEqual(op.series_theme(self.vault, ["raw/book-part-1.md"]), "Invented Book Two")
        self.assertEqual(op.series_theme(self.vault, ["raw/book-part-2.md"]), None)
        self.replies = [self.good, self.good]
        inputs = [f"raw/book-part-{n}.md" for n in (1, 2)]
        lines = []
        result = op.series(self.vault, inputs, None, self.config, emit=lines.append, theme="Invented book")
        self.assertEqual(result["status"], "completed", result)
        self.assertEqual(self.prompts[0][0]["theme"], "Invented book")
        self.assertIn("set the series theme on wiki/sources/book-part-1.md", lines[0]["fixes"])
        index = (self.vault / "wiki/index.md").read_text()
        themed = index.split("### Invented book", 1)[1].split("\n## ", 1)[0]
        self.assertIn("book-part-1|", themed)
        self.assertIn("book-part-2|", themed)
        self.assertEqual(op.link_check.check(self.vault)["errors"], [])

    def test_plan_series_compiles_chapters_and_marks_their_parts(self):
        self.replies = [self.good, self.good, self.good]
        lines = []
        op.series(self.vault, [f"raw/book-part-{n}.md" for n in (1, 2, 3)], None, self.config,
                  emit=lines.append, theme="Invented book")

        def chapter(manifest):
            page = ('---\ntitle: "Chapter 1"\ntype: "source"\ncreated: "2026-09-29"\nupdated: "2026-09-29"\n'
                    'aliases: []\ntags: []\nurl: null\nauthor: null\npublished: null\ncaptured: "2026-09-28"\n'
                    'raw: "raw/book.pdf"\n---\n\n# Chapter 1\n\nParts: [[wiki/sources/book-part-1|Part 1]], '
                    '[[wiki/sources/book-part-2|Part 2]].\n')
            return ("<<<FILE wiki/sources/book-ch1.md>>>\n" + page + "<<<END FILE>>>\n<<<INDEX>>>\n"
                    "Sources | - [[wiki/sources/book-ch1|Chapter 1]] — chapter one.\n"
                    "Sources | - [[wiki/sources/book-part-1|Part 1]] — worker's own line.\n<<<LINKS>>>\n"
                    "wiki/sources/book-part-1.md | - [[wiki/sources/book-ch1|Chapter 1]] — its chapter\n"
                    "<<<LOG>>>\n## 2026-09-29 — compile chapter 1 — partial\n<<<NOTES>>>\nok")
        (self.vault / "raw/book.pdf").write_bytes(b"%PDF-1.4 invented")
        plan_file = Path(self.tmp.name) / "plan.json"
        plan_file.write_text(json.dumps({"theme": "Invented book", "items": [
            {"kind": "compile", "inputs": ["wiki/sources/book-part-1.md", "wiki/sources/book-part-2.md"],
             "task": "Chapter 1 page", "done_if": "wiki/sources/book-ch1.md", "parts": True}]}))
        plan = op.load_plan(self.vault, plan_file)
        self.replies = [chapter]
        result = op.series(self.vault, [], None, self.config, emit=lines.append, plan=plan)
        self.assertEqual(result["status"], "completed", (result, lines[-1]))
        series_info = self.prompts[-1][0]
        self.assertEqual((series_info["parts"], series_info["sources_only"]), (True, False))
        index = (self.vault / "wiki/index.md").read_text()
        book = index.split("### Invented book\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("[[wiki/sources/book-ch1|Chapter 1]] — Parts: Part 1, Part 2. (2 parts)", book)
        self.assertIn("book-part-3|", book)  # not in the chapter: still listed itself
        self.assertNotIn("book-part-1|", book)
        self.assertNotIn("worker's own line", index)
        part = (self.vault / "wiki/sources/book-part-1.md").read_text()
        self.assertIn("book-ch1", part)
        self.assertEqual(op.wiki_index.get_field(part, "part_of"), "wiki/sources/book-ch1")
        self.assertEqual(op.link_check.check(self.vault)["errors"], [])
        again = op.series(self.vault, [], None, self.config, emit=lines.append, plan=plan)
        self.assertEqual(again["skipped"], 1)
        plan["items"][0]["done_if"] = "wiki/sources/book-ch2.md"
        self.replies = [lambda m: "<<<NOTES>>>\ncannot map the chapter"] * 2
        declined = op.series(self.vault, [], None, self.config, emit=lines.append, plan=plan)
        self.assertEqual(self.replies, [])  # declined twice: one fresh operation, then stop
        self.assertEqual(declined["status"], "stopped")  # a plan page that was not created is not a no-op
        self.assertIn("cannot map", declined["reason"])
        for bad in ({"items": []}, {"items": [{"kind": "query", "task": "t"}]},
                    {"items": [{"kind": "ingest", "task": "t", "parts": True}]},
                    {"items": [{"kind": "compile", "task": "t", "parts": True}]},
                    {"items": [{"kind": "compile", "task": "t", "done_if": "raw/x.md"}]}):
            plan_file.write_text(json.dumps(bad))
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                op.load_plan(self.vault, plan_file)

    def test_series_does_not_count_an_empty_format_revision_as_no_change(self):
        self.replies = [lambda m: "Maximum steps reached before the proposal.",   # status message, no markers
                        lambda m: "<<<NOTES>>>\nnothing to restate",               # format revision: notes only
                        self.good]                                                 # fresh operation succeeds
        lines = []
        result = op.series(self.vault, ["raw/book-part-1.md"], None, self.config, emit=lines.append)
        self.assertEqual((result["status"], lines[0]["status"]), ("completed", "applied"))
        self.assertIn("no proposal to restate", " ".join(lines[0]["retries"]))

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
