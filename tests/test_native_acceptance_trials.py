"""Offline recovery/protocol checks; simulated writes are not native evidence."""

from pathlib import Path
import tempfile
import unittest
from unittest import mock

from native_acceptance_trials import CHANGES, HUMAN_NOTE, ROLES, protected_inputs, reconcile
from native_chat_handoff import NativeServer, patch_for, validate_permission


class AcceptanceTrialTests(unittest.TestCase):
    def test_prepared_profile_mutation_is_in_the_protected_window(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            paths = [Path("export.json"), *[Path("profile") / name for role, skill in ROLES.items()
                     for name in (f"agents/{role}.md", f"skills/{skill}/SKILL.md")]]
            for path in paths:
                (base / path).parent.mkdir(parents=True, exist_ok=True)
                (base / path).write_text("Invented definition\n")
            before = protected_inputs(base)
            self.assertEqual(len(before), 5)
            (base / "profile/agents/sb-researcher.md").write_text("Unauthorized modification\n")
            self.assertNotEqual(before, protected_inputs(base))

    def test_compact_append_still_rejects_drift_outside_patch_context(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory)
            name = "wiki/log.md"
            path = corpus / name
            path.parent.mkdir()
            old = "Historical hash: abc123\n\nLast record\nTail\n"
            new = old + "\nVerification passed; acceptance pending.\n"
            text = patch_for(path, old, new)
            self.assertNotIn("abc123", text)
            self.assertIn("+Verification passed", text)
            path.write_text(old.replace("abc123", "human456"))
            request = {"permission": "edit", "patterns": [name], "tool": {"callID": "c", "messageID": "m"},
                       "metadata": {"files": [{"filePath": str(path)}]}}
            parts = [{"tool": "apply_patch", "callID": "c", "messageID": "m",
                      "state": {"status": "running", "input": {"patchText": text}}}]
            with self.assertRaises(RuntimeError):
                validate_permission(request, parts, corpus, {name: {"before": old, "after": new, "patchText": text}}, set())
            self.assertIn("human456", path.read_text())

    def test_confirmation_continuation_does_not_return_old_answer(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory)
            polls = []
            old = {"info": {"id": "old", "role": "assistant", "time": {"completed": 1}},
                   "parts": [{"type": "text", "text": "Please confirm."}]}
            new = {"info": {"id": "new", "role": "assistant", "time": {"completed": 2}},
                   "parts": [{"type": "text", "text": "New answer."}]}
            def api(method, path, data=None):
                if path == "/session/s":
                    return {"directory": str(corpus)}
                if path.endswith("/message"):
                    polls.append(path)
                    return [old, new] if len(polls) >= 3 else [old]
                if path.endswith("prompt_async"):
                    return None
                if path == "/permission":
                    return []
                if path == "/session/status":
                    return {}
                self.fail(f"Unexpected API call: {method} {path}")
            server = NativeServer.__new__(NativeServer)
            server.corpus, server.api = corpus, api
            with mock.patch("native_chat_handoff.time.sleep"):
                result = server.turn("sb-ingestor", "confirmed", session="s")
            self.assertEqual(result["text"], "New answer.")
            self.assertEqual(len(polls), 3)

    def test_partial_reconcile_refuses_drift_and_preserves_intervention(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory)
            approved = {p: {"before": "Before\n" if p in ("wiki/index.md", "wiki/log.md") else None,
                            "after": "After\n"} for p in CHANGES}
            for name, item in approved.items():
                if item["before"] is not None:
                    path = corpus / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(item["before"])
            self.assertEqual(reconcile(corpus, approved), (set(), CHANGES))
            source = corpus / "wiki/sources/lantern-chat.md"
            source.parent.mkdir()
            source.write_text("After\n")
            self.assertEqual(len(reconcile(corpus, approved)[0]), 1)
            index = corpus / "wiki/index.md"
            human = index.read_text() + HUMAN_NOTE
            index.write_text(human)
            with self.assertRaises(RuntimeError):
                reconcile(corpus, approved)
            self.assertEqual(index.read_text(), human)
            self.assertEqual(source.read_text(), "After\n")
            approved["wiki/index.md"].update(before=human, after="After\n" + HUMAN_NOTE)
            self.assertEqual(len(reconcile(corpus, approved)[1]), 3)
            source.unlink()
            source.symlink_to("absent")
            with self.assertRaises(RuntimeError):
                reconcile(corpus, approved)

    def test_native_protocol_aborts_at_next_permission_after_one_postimage(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory)
            names = ["wiki/sources/lantern-chat.md", "wiki/concepts/lantern-preferences.md"]
            approved = {p: {"before": None, "after": "Synthetic\n",
                            "patchText": patch_for(corpus / p, None, "Synthetic\n")} for p in names}
            parts = [{"type": "tool", "tool": "skill", "state": {"status": "completed", "input": {"name": "second-brain-ingest"}}}]
            requests = []
            for number, name in enumerate(names):
                pointer = {"callID": str(number), "messageID": "m"}
                parts.append({"type": "tool", "tool": "apply_patch", **pointer,
                              "state": {"status": "running", "input": {"patchText": approved[name]["patchText"]}}})
                requests.append({"id": str(number), "sessionID": "s", "permission": "edit", "patterns": [name],
                                 "tool": pointer, "metadata": {"files": [{"filePath": str(corpus / name)}]}})
            replies, aborts, polls = [], [], []
            def api(method, path, data=None):
                if path == "/session":
                    return {"id": "s"}
                if path.endswith("prompt_async"):
                    return None
                if path.endswith("/message"):
                    return [{"info": {"role": "assistant", "time": {}}, "parts": parts}]
                if path == "/permission":
                    polls.append(path)
                    # Native tool writes are asynchronous with the reply API.
                    if replies:
                        target = corpus / names[0]
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text(approved[names[0]]["after"])
                        parts[1]["state"]["status"] = "completed"
                    return requests
                if path == "/permission/0/reply":
                    replies.append(data)
                    return True
                if path == "/session/status":
                    return {"s": {"type": "busy"}}
                if path.endswith("/abort"):
                    aborts.append(path)
                    return True
                self.fail(f"Unexpected API call: {method} {path}")
            server = NativeServer.__new__(NativeServer)
            server.corpus, server.api = corpus, api
            result = server.turn("sb-ingestor", "synthetic test", approved, interrupt_after=1)
            self.assertTrue(result["interrupted"])
            self.assertEqual(result["approved_once"], [names[0]])
            self.assertEqual(result["pending_path"], names[1])
            self.assertEqual(replies, [{"reply": "once"}])
            self.assertEqual(aborts, ["/session/s/abort"])
            self.assertEqual(len(result["receipts"]), 1)
            self.assertEqual(len(polls), 2)
            self.assertFalse((corpus / names[1]).exists())


if __name__ == "__main__":
    unittest.main()
