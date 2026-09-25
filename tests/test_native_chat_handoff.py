"""Exact per-call approval regressions; no server/provider or native writes."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from native_chat_handoff import ARTIFACT_NAME, CHANGES, digest, patch_for, query, validate_permission, write_local


class NativeApprovalTests(unittest.TestCase):
    def test_repeat_uses_ingestor_reads_log_and_preserves_corpus(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            corpus = base / "corpus"
            names = CHANGES | {"operation.md", "instructions/wiki-contract.md", f"raw/{ARTIFACT_NAME}"}
            for name in names:
                path = corpus / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("Invented content\n")
            calls = [{"tool": "skill", "state": {"input": {"name": "second-brain-ingest"}}}]
            calls += [{"tool": "read", "state": {"input": {"filePath": str(corpus / name)},
                       "output": "(End of file - total 1 lines)"}} for name in names]
            with mock.patch("native_chat_handoff.configure", return_value={}) as configure, \
                    mock.patch("native_chat_handoff.NativeServer") as server, \
                    mock.patch("native_chat_handoff.ARTIFACT_SHA256", digest(b"Invented content\n")), \
                    mock.patch("builtins.print"):
                server.return_value.turn.return_value = {"text": "Unchanged source: no-op; owner acceptance pending.", "calls": calls}
                query(base, repeat=True)
                configure.assert_called_once_with(base, editing=False)
                self.assertEqual(server.return_value.turn.call_args.args[0], "sb-ingestor")
                server.return_value.close.assert_called_once()
            evidence = json.loads((base / "native-repeat-evidence.json").read_text())
            self.assertEqual(evidence["required_full_reads"], 7)
            self.assertTrue(evidence["corpus_bytes_and_file_set_unchanged"])
            self.assertFalse((base / "native-query.txt").exists())

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
