"""Exact per-call approval regressions; no server/provider or native writes."""

import copy
from pathlib import Path
import tempfile
import unittest

from native_chat_handoff import patch_for, validate_permission, write_local


class NativeApprovalTests(unittest.TestCase):
    def test_only_exact_patch_preimage_path_and_once(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory)
            name = "wiki/log.md"
            path = corpus / name
            path.parent.mkdir()
            path.write_text("Original\n")
            patch = patch_for(path, "Original\n", "Original\nPartial record\n")
            approved = {name: {"before": "Original\n", "after": "Original\nPartial record\n", "patchText": patch}}
            request = {"permission": "edit", "patterns": [name],
                       "tool": {"callID": "c1", "messageID": "m1"},
                       "metadata": {"files": [{"filePath": str(path)}]}}
            parts = [{"callID": "c1", "messageID": "m1", "tool": "apply_patch",
                      "state": {"status": "running", "input": {"patchText": patch}}}]
            self.assertEqual(validate_permission(request, parts, corpus, approved, set()), name)
            for changed in (dict(request, patterns=["raw/source.md"]), dict(request, permission="read"),
                            dict(request, patterns=[name, "wiki/index.md"]),
                            dict(request, tool={"callID": "wrong", "messageID": "m1"})):
                with self.assertRaises(RuntimeError):
                    validate_permission(changed, parts, corpus, approved, set())
            with self.assertRaises(RuntimeError):
                validate_permission(request, parts, corpus, approved, {name})
            modified = copy.deepcopy(parts)
            modified[0]["state"]["input"]["patchText"] += "\n*** Delete File: raw/source.md"
            with self.assertRaises(RuntimeError):
                validate_permission(request, modified, corpus, approved, set())
            path.write_text("Concurrent human work\n")
            with self.assertRaises(RuntimeError):
                validate_permission(request, parts, corpus, approved, set())
            self.assertEqual(path.read_text(), "Concurrent human work\n")

    def test_new_file_is_exclusive_and_links_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory)
            name = "wiki/sources/lantern-chat.md"
            path = corpus / name
            path.parent.mkdir(parents=True)
            patch = patch_for(path, None, "Synthetic\n")
            approved = {name: {"before": None, "after": "Synthetic\n", "patchText": patch}}
            request = {"permission": "edit", "patterns": [name], "tool": {"callID": "c", "messageID": "m"},
                       "metadata": {"files": [{"filePath": str(path)}]}}
            parts = [{"callID": "c", "messageID": "m", "tool": "apply_patch",
                      "state": {"status": "running", "input": {"patchText": patch}}}]
            self.assertEqual(validate_permission(request, parts, corpus, approved, set()), name)
            path.write_text("Existing\n")
            with self.assertRaises(RuntimeError):
                validate_permission(request, parts, corpus, approved, set())
            path.unlink()
            path.symlink_to("absent")
            with self.assertRaises(RuntimeError):
                validate_permission(request, parts, corpus, approved, set())
            with self.assertRaises(RuntimeError):
                write_local(path, "Do not follow link\n")
            self.assertFalse((path.parent / "absent").exists())
            evidence = corpus / "evidence.json"
            write_local(evidence, "{}\n")
            self.assertEqual(evidence.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
