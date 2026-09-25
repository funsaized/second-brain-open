"""Synthetic, read-only statistics contract checks; never use a personal vault."""

from datetime import date
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import vault_stats
from test_link_check import page


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/stats"
CLI = ROOT / "scripts/vault_stats.py"
AS_OF = date(2026, 9, 24)


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


def run_cli(root, *args, module=False):
    command = [sys.executable, "-m", "scripts.vault_stats"] if module else [sys.executable, str(CLI)]
    return subprocess.run([*command, str(root), *args], cwd=ROOT, capture_output=True, text=True)


class VaultStatsTests(unittest.TestCase):
    def test_exact_fixture_read_only_and_repeatable_cli(self):
        before = snapshot(FIXTURE)
        result = vault_stats.report(FIXTURE, as_of=AS_OF)
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["as_of"], "2026-09-24")
        self.assertIsInstance(result["scope"], dict)
        self.assertIsInstance(result["definitions"], dict)
        self.assertEqual(result["pages"], 4)
        self.assertEqual(result["by_type"], dict(source=1, concept=3, entity=0, synthesis=0, unknown=0))
        self.assertEqual(result["resolved_links"], 3)
        self.assertEqual(result["average_out_degree"], 0.75)
        self.assertEqual(result["average_total_degree"], 1.5)
        self.assertEqual(result["inbound_orphans"], {"count": 1, "rate": 0.25})
        self.assertEqual(result["weak_components"], {"count": 2, "largest_size": 3, "largest_share": 0.75})
        self.assertEqual(result["stale_concepts"], {"total": 3, "eligible": 2, "unknown": 1,
                                                    "count": 1, "rate": 0.5, "threshold_days": 90})
        self.assertEqual(result["update_dates"], {"valid": 3, "missing": 0, "invalid": 1, "future": 0})
        self.assertEqual(result["most_linked"], [
            {"path": "wiki/concepts/a.md", "inbound": 1},
            {"path": "wiki/concepts/b.md", "inbound": 1},
            {"path": "wiki/sources/s.md", "inbound": 1},
        ])
        self.assertIn({"page": "wiki/concepts/c.md", "kind": "metadata", "target": "",
                       "detail": "invalid updated date"}, result["diagnostics"])
        self.assertFalse(any(d["page"] in ("wiki/index.md", "wiki/log.md") for d in result["diagnostics"]))
        one = run_cli(FIXTURE, "--json", "--as-of", "2026-09-24")
        two = run_cli(FIXTURE, "--json", "--as-of", "2026-09-24", module=True)
        self.assertEqual((one.returncode, two.returncode), (0, 0), (one.stderr, two.stderr))
        self.assertEqual(one.stdout, two.stdout)
        self.assertEqual(json.loads(one.stdout), result)
        self.assertEqual(run_cli(FIXTURE, "--json", "--as-of", "2026-09-24").stdout, one.stdout)
        self.assertEqual(snapshot(FIXTURE), before)

    def test_empty_and_cli_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = vault_stats.report(root, as_of=AS_OF)
            self.assertEqual(report["pages"], 0)
            self.assertEqual(report["by_type"], dict(source=0, concept=0, entity=0, synthesis=0, unknown=0))
            self.assertEqual(report["resolved_links"], 0)
            self.assertIsNone(report["average_out_degree"])
            self.assertIsNone(report["average_total_degree"])
            self.assertEqual(report["inbound_orphans"], {"count": 0, "rate": None})
            self.assertEqual(report["weak_components"], {"count": 0, "largest_size": 0, "largest_share": None})
            self.assertEqual(report["stale_concepts"], {"total": 0, "eligible": 0, "unknown": 0,
                                                        "count": 0, "rate": None, "threshold_days": 90})
            self.assertEqual(report["update_dates"], {"valid": 0, "missing": 0, "invalid": 0, "future": 0})
            self.assertEqual(report["most_linked"], [])
            self.assertEqual(report["diagnostics"], [])
            self.assertEqual(run_cli(root, "--json", "--as-of", "2026-09-24").returncode, 0)
            for invalid, options in ((root / "missing", ()), (root / "../missing", ()),
                                      (root, ("--as-of", "2026-02-30")),
                                      (root, ("--as-of", "20260924")),
                                      (root, ("--as-of", "2026-W39-4")),
                                     (root, ("--as-of", "not-a-date"))):
                with self.subTest(invalid=invalid, options=options):
                    cli = run_cli(invalid, "--json", *options)
                    self.assertEqual(cli.returncode, 2)
                    self.assertEqual(cli.stdout, "")
            bad = root / "wiki/concepts/bad.md"
            bad.parent.mkdir(parents=True)
            bad.write_bytes(b"\xff")
            self.assertEqual(run_cli(root, "--json").returncode, 2)

    def test_only_leading_frontmatter_sets_type_and_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page(root, "wiki/sources/mismatched.md", type="concept", updated="2026-06-25")
            page(root, "wiki/concepts/not-concept.md", type="something-else")
            page(root, "wiki/concepts/not-string.md", type=["concept"])
            page(root, "wiki/concepts/missing-type.md").write_text(
                '---\ntitle: "Missing"\nupdated: "2026-06-25"\n---\n'
                'type: "concept"\nupdated: "2026-06-25"\n', encoding="utf-8")
            page(root, "wiki/concepts/body-only.md").write_text(
                'type: "concept"\nupdated: "2026-06-25"\n', encoding="utf-8")
            result = vault_stats.report(root, as_of=AS_OF)
            self.assertEqual(result["by_type"], dict(source=0, concept=1, entity=0, synthesis=0, unknown=4))
            self.assertEqual(result["stale_concepts"]["count"], 1)
            self.assertEqual(result["update_dates"], {"valid": 4, "missing": 1, "invalid": 0, "future": 0})
            self.assertTrue(all(isinstance(d, dict) for d in result["diagnostics"]))

    def test_disjoint_update_categories_and_stale_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            values = {"old": "2026-06-25", "boundary": "2026-06-26", "today": "2026-09-24",
                      "future": "2026-09-25", "null": None, "array": [], "number": 20260924,
                      "calendar": "2026-02-30", "format": "2026-9-24"}
            for name, value in values.items():
                page(root, f"wiki/concepts/{name}.md", updated=value)
            missing = page(root, "wiki/concepts/missing.md")
            missing.write_text(missing.read_text().replace('updated: "2026-01-02"\n', ''), encoding="utf-8")
            unquoted = page(root, "wiki/concepts/unquoted.md")
            unquoted.write_text(unquoted.read_text().replace('updated: "2026-01-02"', 'updated: 2026-06-25'), encoding="utf-8")
            result = vault_stats.report(root, as_of=AS_OF)
            self.assertEqual(result["pages"], 11)
            self.assertEqual(result["by_type"]["concept"], 11)
            self.assertEqual(result["update_dates"], {"valid": 3, "missing": 2, "invalid": 5, "future": 1})
            self.assertEqual(result["stale_concepts"], {"total": 11, "eligible": 3, "unknown": 8,
                                                        "count": 1, "rate": 1 / 3, "threshold_days": 90})
            self.assertTrue(any(d.get("detail") == "invalid JSON for updated" for d in result["diagnostics"]))

    def test_duplicate_fields_taint_even_if_valid_value_survives(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            duplicate_date = page(root, "wiki/concepts/duplicate-date.md", updated="2026-06-25")
            duplicate_type = page(root, "wiki/concepts/duplicate-type.md", updated="2026-06-25")
            invalid_json = page(root, "wiki/concepts/invalid-json.md", updated="2026-06-25")
            for path, line in ((duplicate_date, 'updated: "2026-06-26"\n'),
                               (duplicate_type, 'type: "source"\n'),
                               (invalid_json, 'updated: not-json\n')):
                path.write_text(path.read_text().replace('---\n', '---\n' + line, 1), encoding="utf-8")
            result = vault_stats.report(root, as_of=AS_OF)
            self.assertEqual(result["by_type"], dict(source=0, concept=2, entity=0, synthesis=0, unknown=1))
            self.assertEqual(result["update_dates"], {"valid": 1, "missing": 0, "invalid": 2, "future": 0})
            self.assertEqual(result["stale_concepts"], {"total": 2, "eligible": 0, "unknown": 2,
                                                        "count": 0, "rate": None, "threshold_days": 90})
            self.assertTrue({"duplicate updated", "duplicate type", "invalid JSON for updated"} <=
                            {d.get("detail") for d in result["diagnostics"]})

    def test_canonical_edges_diagnostics_and_control_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page(root, "wiki/sources/same.md", '[[wiki/concepts/same#Section|Label]] '
                 '[[wiki/concepts/same]] [[wiki/sources/same]] [[same]] [[wiki/index]] '
                 '[[wiki/log]] [[wiki/concepts/gone]] ![[wiki/concepts/same]] '
                 '[[wiki/concepts/same.md]] [[alias]] [[broken\n'
                 '```md\n[[wiki/concepts/gone]]\n```\n', aliases=["[[wiki/concepts/gone]]"])
            page(root, "wiki/concepts/same.md")
            page(root, "wiki/concepts/isolated.md")
            page(root, "wiki/index.md", "[[wiki/concepts/isolated]] [[wiki/sources/same]]\n")
            page(root, "wiki/log.md", "[[wiki/concepts/isolated]]\n")
            result = vault_stats.report(root, as_of=AS_OF)
            self.assertEqual(result["pages"], 3)
            self.assertEqual(result["resolved_links"], 1)
            self.assertEqual(result["inbound_orphans"], {"count": 2, "rate": 2 / 3})
            self.assertEqual(result["weak_components"], {"count": 2, "largest_size": 2, "largest_share": 2 / 3})
            self.assertEqual(result["most_linked"], [{"path": "wiki/concepts/same.md", "inbound": 1}])
            issues = result["diagnostics"]
            self.assertTrue({"anchor_unchecked", "ambiguous", "excluded_control", "missing", "malformed", "embed",
                             "unsupported_target", "bare_or_alias"} <= {d["kind"] for d in issues})
            self.assertEqual(next(d["candidates"] for d in issues if d["kind"] == "ambiguous"),
                             ["wiki/concepts/same.md", "wiki/sources/same.md"])
            self.assertEqual(sum(d["kind"] == "excluded_control" for d in issues), 2)
            self.assertFalse(any(d["page"] in ("wiki/index.md", "wiki/log.md") for d in issues))

    def test_most_linked_is_capped_and_sorted_by_canonical_path_on_ties(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            targets = [f"wiki/concepts/p{n:02}.md" for n in range(12)]
            for name in targets:
                page(root, name)
            page(root, "wiki/sources/links.md", " ".join(f"[[{name.removesuffix('.md')}]]" for name in targets))
            ranked = vault_stats.report(root, as_of=AS_OF)["most_linked"]
            self.assertEqual(ranked, [{"path": name, "inbound": 1} for name in targets[:10]])

    def test_excluded_files_and_symlink_controls_never_opened(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "vault"
            page(root, "wiki/concepts/a.md", "[[wiki/index]] [[wiki/log]]\n")
            outside = Path(tmp) / "outside.md"
            outside.write_text("Synthetic outside.\n", encoding="utf-8")
            for name in ("wiki/index.md", "wiki/log.md", "raw/input.md", "output/a.md",
                          "projects/p/Inputs/a.md", "templates/a.md", ".obsidian/settings.md",
                          "instructions/a.md", "wiki/concepts/AGENTS.md", "wiki/concepts/CLAUDE.md",
                          "wiki/concepts/CONTEXT.md"):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(outside)
            original_open = os.open
            with mock.patch("scripts.link_check.os.open", wraps=original_open) as spy:
                report = vault_stats.report(root, as_of=AS_OF)
            self.assertEqual(report["pages"], 1)
            self.assertEqual(report["resolved_links"], 0)
            self.assertEqual([d["kind"] for d in report["diagnostics"]], ["excluded_control"] * 2)
            self.assertEqual([Path(call.args[0]).relative_to(root).as_posix() for call in spy.call_args_list],
                             ["wiki/concepts/a.md"])

    def test_unsafe_adopted_scope_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "vault"
            original = page(root, "wiki/concepts/a.md")
            outside = base / "outside.md"
            outside.write_text("Synthetic outside.\n", encoding="utf-8")
            before = (original.read_bytes(), outside.read_bytes())
            hazards = ((root / "wiki/concepts/escape.md", lambda p: p.symlink_to(outside)),
                       (root / "wiki/concepts/inside.md", lambda p: p.symlink_to(original)),
                       (root / "wiki/concepts/hard.md", lambda p: os.link(original, p)),
                       (root / "wiki/concepts/dir", lambda p: p.symlink_to(base, target_is_directory=True)))
            for path, make in hazards:
                with self.subTest(path=path):
                    make(path)
                    self.assertEqual(run_cli(root, "--json").returncode, 2)
                    path.unlink()
            (root / "wiki/concepts").rename(root / "wiki/real")
            (root / "wiki/concepts").symlink_to("real", target_is_directory=True)
            self.assertEqual(run_cli(root, "--json").returncode, 2)
            (root / "wiki/concepts").unlink()
            (root / "wiki/real").rename(root / "wiki/concepts")
            linked_root = base / "linked-root"
            linked_root.symlink_to(root, target_is_directory=True)
            linked_parent = base / "linked-parent"
            linked_parent.symlink_to(base, target_is_directory=True)
            for invalid in (linked_root, linked_parent / "vault"):
                with self.subTest(invalid=invalid):
                    self.assertEqual(run_cli(invalid, "--json").returncode, 2)
            self.assertEqual((original.read_bytes(), outside.read_bytes()), before)


if __name__ == "__main__":
    unittest.main()
