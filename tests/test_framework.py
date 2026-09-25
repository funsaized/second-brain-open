"""Offline distribution invariants; native loading is tested by runtime_roles_probe."""

from pathlib import Path
import json
import re
import unittest


FRAMEWORK = Path(__file__).resolve().parents[1] / "framework"


class FrameworkTests(unittest.TestCase):
    def test_primary_roles_are_inert_and_skill_scoped(self):
        for role, skill in (("sb-ingestor", "second-brain-ingest"), ("sb-researcher", "second-brain-query")):
            text = (FRAMEWORK / f"agents/{role}.md").read_text()
            header, body = text.removeprefix("---\n").split("\n---\n", 1)
            self.assertIn("mode: primary", header)
            self.assertIn("permission:\n  '*': deny", header)
            self.assertIn("  read:\n    '*': deny", header)
            self.assertIn(f"  skill:\n    '*': deny\n    {skill}: allow", header)
            self.assertIn("  question: allow", header)
            self.assertNotIn("tools:", header)
            self.assertIn(skill, body)
            self.assertIn("fails closed", body)

    def test_native_skill_names_and_descriptions(self):
        paths = list((FRAMEWORK / "skills").glob("*/SKILL.md"))
        self.assertEqual({path.parent.name for path in paths}, {"second-brain-ingest", "second-brain-query"})
        for path in paths:
            header, body = path.read_text().removeprefix("---\n").split("\n---\n", 1)
            fields = dict(line.split(": ", 1) for line in header.splitlines())
            self.assertEqual(fields["name"], path.parent.name)
            self.assertRegex(fields["name"], re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$"))
            self.assertLessEqual(len(fields["name"]), 64)
            self.assertTrue(1 <= len(fields["description"]) <= 1024)
            self.assertIn("wiki-contract.md", body)

    def test_unsafe_wrappers_are_not_distributed(self):
        commands = json.loads((FRAMEWORK / "opencode.example.json").read_text()).get("command", {})
        for name in ("sb-ingest", "sb-ask"):
            self.assertFalse((FRAMEWORK / f"commands/{name}.md").exists())
            self.assertNotIn(name, commands)


if __name__ == "__main__":
    unittest.main()
