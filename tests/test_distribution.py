"""Offline distribution checks; not runtime permission or sandbox tests."""

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DistributionTests(unittest.TestCase):
    def test_inert_deny_default_example(self):
        config = json.loads((ROOT / "framework/opencode.example.json").read_text())
        self.assertEqual(config["permission"], {"*": "deny"})
        self.assertEqual(config["share"], "disabled")
        for key in ("snapshot", "autoupdate", "formatter", "lsp"):
            self.assertIs(config[key], False)
        for key in ("enabled_providers", "plugin", "instructions"):
            self.assertEqual(config[key], [])
        self.assertEqual(config["mcp"], {})
        self.assertNotIn("default_agent", config)
        for path in ("opencode.json", "opencode.jsonc", ".opencode"):
            self.assertFalse((ROOT / path).exists(), path)

    def test_upstream_notice_preserves_blank_holder(self):
        downstream = (ROOT / "LICENSE").read_text()
        expected = downstream.replace("Copyright (c) 2026 Funsaized", "Copyright (c) 2026")
        notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text()
        self.assertEqual(notice.split("```text\n", 1)[1].split("```", 1)[0], expected)

    def test_private_paths_ignored_without_hiding_synthetic_pages(self):
        blocked = [
            "raw/capture.md", "wiki/index.md", "projects/example/brief.md",
            "output/report.md", "backups/snapshot.md", "sessions/session.json",
            "transcripts/run.json", "runtime/trace.json", ".obsidian/settings.json",
            "nested/.obsidian/settings.json", ".env", "nested/.env.local",
            "credentials.json", "nested/auth.json", "key.pem", "key.key",
            ".opencode/agents/probe.md", "opencode.json", "opencode.jsonc",
        ]
        public = [
            "tests/fixtures/wiki/sources/example.md", "tests/fixtures/raw/example.md",
            "framework/opencode.example.json", "LICENSE", "PLAN.md",
        ]
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin"],
            input="\n".join(blocked + public) + "\n", text=True,
            capture_output=True, cwd=ROOT, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(result.stdout.splitlines()), set(blocked))


if __name__ == "__main__":
    unittest.main()
