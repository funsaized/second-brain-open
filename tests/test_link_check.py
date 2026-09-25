"""Synthetic managed-wiki checker checks; no private vault inputs."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import link_check


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/link_check.py"


def page(root, name, body="", **changes):
    kind = {"sources": "source", "concepts": "concept", "entities": "entity", "synthesis": "synthesis"}
    category = name.split("/")[1]
    kind = {"wiki/index.md": "index", "wiki/log.md": "log"}.get(name, kind.get(category))
    fields = dict(title=Path(name).stem, type=kind, created="2026-01-01",
                   updated="2026-01-02", aliases=[], tags=[])
    if kind == "log":
        fields["updated"] = fields["created"]
    if kind == "source":
        fields.update(url=None, author=None, published=None, captured="2026-01-01", raw="raw/item.txt")
    if kind == "entity":
        fields["kind"] = "unknown"
    fields.update(changes)
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + "".join(f"{k}: {json.dumps(v)}\n" for k, v in fields.items())
                    + "---\n" + body, encoding="utf-8")
    return path


class LinkCheckTests(unittest.TestCase):
    def test_contract_fixture_clean_and_controls_separate(self):
        report = link_check.check(ROOT / "tests/fixtures/contract")
        self.assertEqual((report["errors"], report["unsupported"], report["unchecked"]), ([], [], []))
        self.assertEqual(report["pages"], 5)
        self.assertEqual(report["controls"], ["wiki/index.md", "wiki/log.md"])
        self.assertTrue(report["links"])
        self.assertTrue(all("wiki/index.md" not in edge for edge in report["links"]))

    def test_paths_labels_fragments_and_basename_collisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = page(root, "wiki/sources/same.md")
            page(root, "wiki/concepts/same.md")
            page(root, "wiki/entities/space name.md")
            source.write_text(source.read_text() +
                              "[[wiki/concepts/same|Same]] [[wiki/concepts/same]]\n"
                              "[[wiki/entities/space name#Heading|Nice]]\n")
            pages, diagnostics = link_check.collect(root)
            edges, link_diagnostics = link_check.resolve_links(pages)
            self.assertEqual(diagnostics, [])
            self.assertEqual(edges, {("wiki/sources/same.md", "wiki/concepts/same.md"),
                                     ("wiki/sources/same.md", "wiki/entities/space name.md")})
            self.assertEqual([d["kind"] for d in link_diagnostics], ["anchor_unchecked"])
            self.assertEqual(link_check.check(root)["pages"], 3)

    def test_invalid_links_and_examples_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = page(root, "wiki/concepts/one.md", aliases=["[[wiki/concepts/missing]]"])
            source.write_text(source.read_text() + "```md\n[[wiki/concepts/missing]]\n```\n"
                              + "`[[wiki/concepts/missing]]`\n"
                              + "[[wiki/concepts/gone]] [[oops [[wiki/concepts/one]]\n"
                              + "[[one]] [[alias]] ![[wiki/concepts/one]] [[wiki/concepts/one#block^id]]\n")
            page(root, "wiki/sources/one.md")
            report = link_check.check(root)
            self.assertEqual([d["kind"] for d in report["errors"]],
                             ["missing", "malformed", "ambiguous"])
            self.assertEqual(report["errors"][-1]["candidates"],
                             ["wiki/concepts/one.md", "wiki/sources/one.md"])
            self.assertEqual([d["kind"] for d in report["unsupported"]], ["bare_or_alias", "embed"])
            self.assertEqual([d["kind"] for d in report["unchecked"]], ["anchor_unchecked"])
            self.assertEqual(report["links"], [])

    def test_metadata_diagnostics_preserve_fields_for_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page(root, "wiki/concepts/valid.md")
            page(root, "wiki/concepts/bad.md", updated="2026-19-99", aliases="bad")
            page(root, "wiki/sources/bad-raw.md", raw="raw/../other.txt")
            no_header = root / "wiki/concepts/no-header.md"
            no_header.write_text("[[wiki/concepts/valid]]\n")
            legacy = root / "wiki/concepts/legacy.md"
            legacy.write_text('---\ntitle: legacy\n---\n[[wiki/concepts/valid]]\n')
            pages, diagnostics = link_check.collect(root)
            self.assertEqual(pages["wiki/concepts/bad.md"]["metadata"]["updated"], "2026-19-99")
            self.assertEqual(pages["wiki/concepts/no-header.md"]["metadata"], {})
            self.assertEqual({d["page"] for d in diagnostics},
                             {"wiki/concepts/bad.md", "wiki/concepts/no-header.md", "wiki/concepts/legacy.md",
                              "wiki/sources/bad-raw.md"})
            self.assertEqual({d["kind"] for d in diagnostics}, {"metadata"})
            self.assertIn("invalid raw path", {d["detail"] for d in diagnostics})
            self.assertEqual(len(link_check.resolve_links(pages)[0]), 2)

    def test_unsupported_schema_and_out_of_scope_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page(root, "wiki/entities/one.md", kind="robot", type="concept")
            wrong = root / "wiki/entities/one.md"
            wrong.write_text(wrong.read_text().replace('"2026-01-02"', '"2026-13-02"')
                             .replace('aliases: []', 'aliases: []\nnested: {"a": 1}'))
            for dirname in ("raw", "projects", "output", ".obsidian", "wiki/other"):
                path = root / dirname / "unread.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("[[wiki/concepts/missing]]")
            (root / "wiki/other/linked.md").symlink_to(root / "raw/unread.md")
            inputs = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*.md") if not p.is_symlink()}
            pages, issues = link_check.collect(root)
            self.assertEqual(list(pages), ["wiki/entities/one.md"])
            self.assertTrue({"invalid kind", "type does not match path", "invalid updated date",
                             "unsupported nested"} <= {d["detail"] for d in issues})
            self.assertEqual(link_check.resolve_links(pages), (set(), []))
            self.assertEqual({p: hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}, inputs)

    def test_refuse_links_and_nonregular_adopted_scope_without_reading_them(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "vault"
            original = page(root, "wiki/concepts/ok.md")
            outside = base / "outside.md"
            outside.write_text("Synthetic outside\n")
            hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (original, outside)}
            cases = [
                (root / "wiki/concepts/link.md", lambda p: p.symlink_to(outside)),
                (root / "wiki/concepts/inside.md", lambda p: p.symlink_to(original)),
                (root / "wiki/concepts/escape", lambda p: p.symlink_to(base, target_is_directory=True)),
                (root / "wiki/concepts/hard.md", lambda p: os.link(original, p)),
                (root / "wiki/concepts/fifo.md", lambda p: os.mkfifo(p)),
            ]
            for path, make in cases:
                with self.subTest(path=path):
                    make(path)
                    with self.assertRaises(ValueError):
                        link_check.collect(root)
                    path.unlink()
            (root / "wiki/index.md").symlink_to(outside)
            with self.assertRaises(ValueError):
                link_check.collect(root)
            (root / "wiki/index.md").unlink()
            (root / "wiki/concepts").rename(root / "wiki/real")
            (root / "wiki/concepts").symlink_to("real", target_is_directory=True)
            with self.assertRaises(ValueError):
                link_check.collect(root)
            (root / "wiki/concepts").unlink()
            (root / "wiki/real").rename(root / "wiki/concepts")
            (root / "wiki").rename(root / "real-wiki")
            (root / "wiki").symlink_to("real-wiki", target_is_directory=True)
            with self.assertRaises(ValueError):
                link_check.collect(root)
            (root / "wiki").unlink()
            (root / "real-wiki").rename(root / "wiki")
            for linked_root in (base / "linked-root", base / "linked-parent"):
                linked_root.symlink_to(root if linked_root.name == "linked-root" else base, target_is_directory=True)
                with self.subTest(linked_root=linked_root), self.assertRaises(ValueError):
                    link_check.collect(linked_root if linked_root.name == "linked-root" else linked_root / "vault")
            self.assertEqual({p: hashlib.sha256(p.read_bytes()).hexdigest() for p in hashes}, hashes)

    def test_empty_invalid_root_traversal_and_cli_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(link_check.check(root)["pages"], 0)
            self.assertEqual(link_check.check(root)["errors"], [])
            for invalid in (root / "missing", root / "wiki", root / "../missing"):
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    link_check.collect(invalid)
            page(root, "wiki/concepts/a.md", "[[wiki/concepts/missing]]\n")
            result = subprocess.run([sys.executable, str(CLI), str(root), "--json"],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["errors"][0]["kind"], "missing")
            clean = subprocess.run([sys.executable, str(CLI), str(ROOT / "tests/fixtures/contract"), "--json"],
                                   capture_output=True, text=True)
            self.assertEqual(clean.returncode, 0, clean.stderr)
            invalid = subprocess.run([sys.executable, str(CLI), str(root / "missing"), "--json"],
                                     capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 2)
            self.assertEqual(invalid.stdout, "")

    def test_invalid_fence_anchor_and_path_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page(root, "wiki/concepts/index.md", "``` ```\n[[wiki/concepts/missing]]\n")
            page(root, "wiki/concepts/one.md", "[[one#Heading]] [[wiki/concepts/one.md#Heading]]\n")
            report = link_check.check(root)
            self.assertEqual([d["kind"] for d in report["errors"]], ["missing"])
            self.assertEqual([d["kind"] for d in report["unsupported"]], ["bare_or_alias", "unsupported_target"])
            self.assertEqual(report["unchecked"], [])
            for raw in ("raw/a\x00.md", "raw/a\nb.md", "raw/a\rb.md"):
                with self.subTest(raw=raw):
                    page(root, "wiki/sources/bad.md", raw=raw)
                    self.assertIn("invalid raw path", {d.get("detail") for d in link_check.check(root)["errors"]})

    def test_nested_settings_are_rejected_not_adopted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page(root, "wiki/concepts/.obsidian/settings.md")
            with self.assertRaisesRegex(ValueError, "protected entry"):
                link_check.collect(root)

    def test_log_header_date_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page(root, "wiki/log.md", updated="2026-01-02")
            self.assertIn("log header dates must remain equal", {d.get("detail") for d in link_check.check(root)["errors"]})

    def test_instruction_files_are_not_managed_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page(root, "wiki/concepts/a.md", "[[wiki/concepts/AGENTS]]\n")
            for name in ("AGENTS.md", "CLAUDE.md", "CONTEXT.md"):
                page(root, f"wiki/concepts/{name}", "[[wiki/concepts/missing]]\n")
            report = link_check.check(root)
            self.assertEqual(report["pages"], 1)
            self.assertEqual(report["errors"], [])
            self.assertEqual([d["kind"] for d in report["unsupported"]], ["unsupported_target"])
            protected = root / "wiki/concepts/.opencode"
            protected.mkdir()
            with self.assertRaisesRegex(ValueError, "protected entry"):
                link_check.collect(root)
            protected.rmdir()
            (root / "wiki/concepts/AGENTS.md").unlink()
            page(root, "wiki/concepts/AGENTS.md/note.md", "[[wiki/concepts/a]]\n")
            page(root, "wiki/concepts/a.md", "[[wiki/concepts/AGENTS.md/note]]\n")
            report = link_check.check(root)
            self.assertEqual((report["pages"], len(report["links"])), (2, 2))
            (root / "wiki/concepts/AGENTS.md/.git").mkdir()
            with self.assertRaisesRegex(ValueError, "protected entry"):
                link_check.collect(root)


if __name__ == "__main__":
    unittest.main()
