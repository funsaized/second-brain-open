"""Offline checks for live-test guards. These never call a model or inspect auth."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ingest_rehearsal import CONCEPT, apply_proposal
from semantic_probe import ROOT, call_model, semantic_checks


class LiveDriverTests(unittest.TestCase):
    def test_preprocessing_tokens_rejected_before_invocation(self):
        with patch("semantic_probe.subprocess.run") as invoked:
            for prompt in ("read @file", "use !`command`", "use !  `command`"):
                with self.subTest(prompt=prompt), self.assertRaises(RuntimeError):
                    call_model({}, prompt)
            invoked.assert_not_called()

    def test_missing_or_invented_answers_do_not_pass(self):
        self.assertFalse(all(semantic_checks({}).values()))
        self.assertFalse(semantic_checks({"preferred_vent": "closed"})["preferred_vent"])
        self.assertFalse(semantic_checks({})["trial_b_publication_date"])
        self.assertTrue(semantic_checks({"trial_b_publication_date": None})["trial_b_publication_date"])

    def test_manifest_log_and_input_preservation(self):
        fixture = ROOT / "tests/fixtures/contract"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for source in fixture.rglob("*.md"):
                destination = root / source.relative_to(fixture)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read_bytes())
            expected = {"wiki/sources/trial-a.md", CONCEPT, "wiki/index.md", "wiki/log.md"}
            files = {name: (root / name).read_text() for name in expected}
            files["wiki/sources/trial-a.md"] += "\n## Preserved evidence excerpts\n\n" + (fixture / "raw/trial-a.md").read_text()
            before = (root / "raw/trial-a.md").read_bytes()
            with self.assertRaises(RuntimeError):
                apply_proposal(root, {"files": {"../escape.md": "outside"}}, expected)
            with self.assertRaises(RuntimeError):
                apply_proposal(root, {"files": {**files, "wiki/log.md": "rewritten"}}, expected)
            files["wiki/log.md"] += "\n## 2026-09-24 — synthetic rehearsal — partial\nVerification pending.\n"
            report = apply_proposal(root, {"files": files}, expected)
            self.assertEqual(report["errors"], [])
            self.assertEqual((root / "raw/trial-a.md").read_bytes(), before)
            self.assertFalse((root.parent / "escape.md").exists())
            current_log = (root / "wiki/log.md").read_text()
            with self.assertRaisesRegex(RuntimeError, "partial"):
                apply_proposal(root, {"files": {**files, "wiki/log.md": current_log + "\nimpartial review completed\n"}}, expected)
            files["wiki/log.md"] = current_log + "\n## Another operation — partial\nChecks pending.\n"
            files[CONCEPT] = files[CONCEPT].replace("[[wiki/sources/trial-b|Trial B]]", "Trial B")
            with self.assertRaisesRegex(RuntimeError, "reciprocal"):
                apply_proposal(root, {"files": files}, expected)


if __name__ == "__main__":
    unittest.main()
