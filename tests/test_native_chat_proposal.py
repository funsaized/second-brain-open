"""Offline fail-closed guards; no provider calls or profile inspection."""

import copy
from pathlib import Path
import unittest
from unittest import mock
import subprocess

from native_chat_proposal import CHANGES, ROLES, native_run, parse_proposal, verify_agent, verify_skills


class NativePreflightTests(unittest.TestCase):
    def test_edit_gates_require_default_deny_and_exact_asks(self):
        agent = {"name": "sb-ingestor", "mode": "primary", "prompt": "exact", "steps": 6,
                 "model": {"providerID": "openai", "modelID": "gpt-6-luna"},
                 "permission": [{"permission": "*", "pattern": "*", "action": "deny"},
                                {"permission": "edit", "pattern": "wiki/log.md", "action": "ask"}]}
        verify_agent(agent, "sb-ingestor", "exact", set(), edits={"wiki/log.md"})
        for extra in ({"permission": "edit", "pattern": "*", "action": "ask"},
                      {"permission": "edit", "pattern": "wiki/log.md", "action": "allow"}):
            changed = copy.deepcopy(agent)
            changed["permission"].append(extra)
            with self.assertRaises(RuntimeError):
                verify_agent(changed, "sb-ingestor", "exact", set(), edits={"wiki/log.md"})
        agent["permission"].pop(0)
        with self.assertRaises(RuntimeError):
            verify_agent(agent, "sb-ingestor", "exact", set(), edits={"wiki/log.md"})

    def test_unescaped_proposal_requires_exact_unique_complete_files(self):
        text = "".join(f'<<<FILE {p}>>>\nA "quoted" line.\n<<<END FILE>>>\n' for p in sorted(CHANGES))
        self.assertEqual(set(parse_proposal(text + "<<<NOTES>>>\nPending.")["files"]), CHANGES)
        with self.assertRaises(RuntimeError):
            parse_proposal(text)
        for bad in ("", text.replace("<<<END FILE>>>", "", 1),
                    text.replace("wiki/log.md", "raw/other.md"), text + text):
            with self.subTest(text=bad), self.assertRaises(RuntimeError):
                parse_proposal(bad + "<<<NOTES>>>\nPending.")

    def test_missing_changed_or_overgranted_role_fails(self):
        agent = {"name": "sb-ingestor", "mode": "primary", "prompt": "exact prompt", "steps": 6,
                 "model": {"providerID": "openai", "modelID": "gpt-6-luna"},
                 "permission": [{"permission": "*", "pattern": "*", "action": "deny"}]}
        verify_agent(agent, "sb-ingestor", "exact prompt", set())
        for field, value in (("name", "build"), ("prompt", "changed"), ("model", {}),
                             ("permission", []), ("steps", 7)):
            changed = copy.deepcopy(agent)
            changed[field] = value
            with self.subTest(field=field), self.assertRaises(RuntimeError):
                verify_agent(changed, "sb-ingestor", "exact prompt", set())
        agent["permission"].append({"permission": "read", "pattern": "*", "action": "allow"})
        with self.assertRaises(RuntimeError):
            verify_agent(agent, "sb-ingestor", "exact prompt", set())
        agent["permission"] = [{"permission": "*", "pattern": "*", "action": "allow"},
                               {"permission": "*", "pattern": "*", "action": "deny"},
                               {"permission": "read", "pattern": "operation.md", "action": "allow"}]
        verify_agent(agent, "sb-ingestor", "exact prompt", {("read", "operation.md")})
        agent["permission"].append({"permission": "external_directory", "pattern": "*tool-output*", "action": "allow"})
        with self.assertRaises(RuntimeError):
            verify_agent(agent, "sb-ingestor", "exact prompt", {("read", "operation.md")})

    def test_missing_shadowed_or_duplicate_skill_fails(self):
        profile = Path("/synthetic/profile")
        skills = [{"name": skill, "location": str(profile / f"skills/{skill}/SKILL.md")} for skill in ROLES.values()]
        verify_skills(skills, profile)
        for changed in ([], skills[:1], skills + skills, [dict(s, location="/elsewhere/SKILL.md") for s in skills]):
            with self.subTest(skills=changed), self.assertRaises(RuntimeError):
                verify_skills(changed, profile)

    def test_run_directory_stdin_and_timeout(self):
        corpus = Path("/synthetic/corpus")
        with mock.patch("native_chat_proposal.subprocess.Popen") as popen:
            with self.assertRaises(RuntimeError):
                native_run({"PWD": "/wrong"}, corpus, "synthetic prompt", None)
            popen.assert_not_called()
            process = popen.return_value.__enter__.return_value
            process.returncode = 0
            self.assertEqual(native_run({"PWD": str(corpus)}, corpus, "synthetic prompt", None), 0)
            args, kwargs = popen.call_args
            self.assertEqual(args[0][args[0].index("--dir") + 1], str(corpus))
            self.assertEqual(kwargs["cwd"], corpus)
            self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
            self.assertTrue(kwargs["start_new_session"])
            process.communicate.assert_called_once_with(timeout=180)
            process.communicate.side_effect = [subprocess.TimeoutExpired("opencode", 180), (None, None)]
            with mock.patch("native_chat_proposal.os.killpg") as kill, self.assertRaises(RuntimeError):
                native_run({"PWD": str(corpus)}, corpus, "synthetic prompt", None)
            kill.assert_called_once()


if __name__ == "__main__":
    unittest.main()
