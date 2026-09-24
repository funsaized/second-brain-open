"""Static schema/link/evidence checks for wholly invented P1 pages, not ingestion proof."""

from datetime import date
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/contract"
COMMON = {"title", "type", "created", "updated", "aliases", "tags"}
EXTENSIONS = {
    "source": {"url", "author", "published", "captured", "raw"},
    "entity": {"kind"}, "concept": set(), "synthesis": set(), "index": set(), "log": set(),
}
LINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def metadata(text):
    header, body = text.removeprefix("---\n").split("\n---\n", 1)
    result = {}
    for line in header.splitlines():
        key, value = line.split(": ", 1)
        if key in result:
            raise ValueError("Duplicate fixture field")
        result[key] = json.loads(value)
    return result, body


class ContractTests(unittest.TestCase):
    def test_templates_and_populated_metadata_agree(self):
        templates = ROOT / "framework/templates"
        self.assertEqual({p.stem for p in templates.glob("*.md")}, {*EXTENSIONS, "project"})
        seen_types = set()
        for path in (FIXTURE / "wiki").rglob("*.md"):
            with self.subTest(path=path.relative_to(FIXTURE)):
                text = path.read_text()
                self.assertTrue(text.startswith("---\n"))
                fields, _ = metadata(text)
                kind = fields["type"]
                seen_types.add(kind)
                self.assertIn(kind, EXTENSIONS)
                self.assertTrue(COMMON <= fields.keys())
                self.assertTrue(fields.keys() <= COMMON | EXTENSIONS[kind])
                template_fields, _ = metadata((templates / f"{kind}.md").read_text())
                self.assertEqual(template_fields["type"], kind)
                self.assertTrue(fields.keys() <= template_fields.keys())
                self.assertIsInstance(fields["title"], str)
                self.assertTrue(fields["title"])
                self.assertLessEqual(date.fromisoformat(fields["created"]), date.fromisoformat(fields["updated"]))
                for name in ("aliases", "tags"):
                    self.assertIsInstance(fields[name], list)
                    self.assertTrue(all(isinstance(item, str) for item in fields[name]))
                if kind == "source":
                    self.assertTrue({"author", "published", "captured", "raw"} <= fields.keys())
                    date.fromisoformat(fields["captured"])
                    if fields["published"] is not None:
                        date.fromisoformat(fields["published"])
                    self.assertTrue((FIXTURE / fields["raw"]).is_file())
                if kind == "entity":
                    self.assertEqual(fields["kind"], "org")
                if kind == "log":
                    self.assertEqual(fields["created"], fields["updated"])
        self.assertEqual(seen_types, set(EXTENSIONS))

    def test_no_residue_canonical_links_index_and_reciprocals(self):
        graph = {}
        for path in FIXTURE.rglob("*.md"):
            text = path.read_text()
            self.assertNotRegex(text, r"\{\{[^}]*\}\}")
            body = metadata(text)[1] if text.startswith("---\n") else text
            targets = set(LINK.findall(body))
            for target in targets:
                self.assertTrue(target.startswith("wiki/"), target)
                self.assertNotIn("..", Path(target).parts)
                self.assertTrue((FIXTURE / (target + ".md")).is_file(), target)
            graph[path.relative_to(FIXTURE).with_suffix("").as_posix()] = targets
        content = {key for key in graph if key.startswith("wiki/") and key not in ("wiki/index", "wiki/log")}
        self.assertEqual(graph["wiki/index"], content)
        for source in ("wiki/sources/trial-a", "wiki/sources/trial-b"):
            for related in ("wiki/concepts/vent-choice", "wiki/entities/aster-desk-lab"):
                self.assertIn(related, graph[source])
                self.assertIn(source, graph[related])
        index = (FIXTURE / "wiki/index.md").read_text()
        self.assertNotIn("[[", index.split("## Gaps", 1)[1])

    def test_fixed_claim_source_matrix_and_unknown_provenance(self):
        # This is a hand-reviewed fixture oracle, not automated fact verification.
        matrix = [
            ("trial-a", "A1", "Measurements", "18 minutes", "24 minutes"),
            ("trial-a", "A2", "Recommendation", "recommend the open vent", "single trial"),
            ("trial-b", "B1", "Measurements", "25 minutes", "19 minutes"),
            ("trial-b", "B2", "Recommendation", "recommend the closed vent", "single trial"),
        ]
        for source, claim, section, first, second in matrix:
            with self.subTest(claim=claim):
                page = (FIXTURE / f"wiki/sources/{source}.md").read_text()
                archive = (FIXTURE / f"raw/{source}.md").read_text()
                self.assertIn(claim, page)
                self.assertIn(f"`raw/{source}.md`, {section}", page)
                bullets = re.findall(r"(?m)^- .*(?:\n(?!\n|- |#).+)*", page)
                self.assertTrue(any(claim in bullet and f"`raw/{source}.md`, {section}" in bullet for bullet in bullets))
                evidence = archive.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
                normalized = " ".join(evidence.split())
                self.assertIn(first, normalized)
                self.assertIn(second, normalized)
                for related in ("concepts/vent-choice", "synthesis/vent-setting"):
                    text = (FIXTURE / f"wiki/{related}.md").read_text()
                    bullets = re.findall(r"(?m)^- .*(?:\n(?!\n|- |#).+)*", text)
                    self.assertTrue(any(
                        f"[[wiki/sources/{source}|" in bullet and claim in bullet and f"raw {section}" in bullet
                        for bullet in bullets
                    ), (related, claim))
        fields, body = metadata((FIXTURE / "wiki/sources/trial-b.md").read_text())
        self.assertIsNone(fields["published"])
        self.assertIn("publication date is unknown", " ".join(body.split()))
        for path in ("concepts/vent-choice", "synthesis/vent-setting"):
            text = (FIXTURE / f"wiki/{path}.md").read_text()
            for item in ("wiki/sources/trial-a", "wiki/sources/trial-b", "A1", "A2", "B1", "B2"):
                self.assertIn(item, text)
            self.assertIn("Agent inference", text)

    def test_project_and_control_status_are_honest(self):
        brief = (FIXTURE / "projects/vent-repeat/brief.md").read_text()
        self.assertFalse(brief.startswith("---"))
        for term in ("Inputs", "Process", "Outputs", "Feedback", "Nothing has been promoted", "wiki/index"):
            if term == "wiki/index":
                self.assertNotIn(term, brief)  # a project is not a second index
            else:
                self.assertIn(term, brief)
        self.assertEqual(len(list((FIXTURE / "projects").rglob("*.md"))), 1)
        log = (FIXTURE / "wiki/log.md").read_text()
        self.assertIn("not evidence of a runtime ingest", " ".join(log.split()))
        for path in (FIXTURE / "wiki").rglob("*.md"):
            self.assertIn(path.relative_to(FIXTURE).as_posix(), log)


if __name__ == "__main__":
    unittest.main()
