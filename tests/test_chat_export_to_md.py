"""Synthetic contract checks for scripts/chat_export_to_md.py.

Only wholly synthetic records in temporary directories. Never private exports.
"""

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import chat_export_to_md as converter


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/chat_export_to_md.py"


def write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def run_cli(export, outdir, *args):
    return subprocess.run(
        [sys.executable, str(CLI), str(export), str(outdir), *args],
        capture_output=True, text=True, cwd=ROOT,
    )


def counts(stdout):
    return {key: int(value) for key, value in (token.split("=", 1) for token in stdout.split())}


def output_text(outdir):
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(outdir.glob("*.md")))


def snapshot(root):
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def frontmatter(text):
    lines = text.splitlines()
    end = lines.index("---", 1)
    return {line.split(": ", 1)[0]: json.loads(line.split(": ", 1)[1]) for line in lines[1:end]}


def claude_record(conv_id="c1", title="Synthetic", messages=None):
    return {
        "uuid": conv_id,
        "name": title,
        "created_at": 1700000000,
        "updated_at": "2026-01-02",
        "chat_messages": messages if messages is not None else [
            {"sender": "user", "created_at": 1700000001, "content": [{"type": "text", "text": "first"}]},
            {"sender": "assistant", "content": "second"},
        ],
    }


def simple_record(conv_id="s1", title="Simple", messages=None):
    return {
        "id": conv_id,
        "title": title,
        "messages": messages if messages is not None else [
            {"role": "user", "content": "hello there"},
            {"role": "assistant", "text": "general kenobi"},
        ],
    }


def mapping_record(conv_id="g1", current="n2", title="Branch"):
    return {
        "id": conv_id,
        "title": title,
        "create_time": 1700000000,
        "update_time": "2026-01-02T03:04:07Z",
        "current_node": current,
        "mapping": {
            "root": {"parent": None, "message": None},
            "n1": {"parent": "root", "message": {
                "author": {"role": "user"},
                "create_time": 1700000001,
                "content": {"content_type": "text", "parts": ["first question"]}}},
            "sibling": {"parent": "root", "message": {
                "author": {"role": "assistant"},
                "content": {"content_type": "text", "parts": ["sibling ignored branch"]}}},
            "n2": {"parent": "n1", "message": {
                "author": {"role": "assistant"},
                "content": {"content_type": "text", "parts": ["selected answer"]}}},
        },
    }


class FidelityTests(unittest.TestCase):
    def test_claude_and_simple_order_roles_and_text(self):
        items, provider, branch = converter.messages(claude_record())
        self.assertEqual((provider, branch), ("claude", None))
        self.assertEqual([item["sender"] for item in items], ["user", "assistant"])

        text = converter.render(claude_record(), "c1")[0].decode()
        self.assertLess(text.index("first"), text.index("second"))
        self.assertIn('Role: "user"', text)
        self.assertIn('Role: "assistant"', text)
        self.assertIn('format: "claude"', text)
        self.assertIn('conversation_id: "c1"', text)
        self.assertIn('title: "Synthetic"', text)

        items, provider, branch = converter.messages(simple_record())
        self.assertEqual((provider, branch), ("simple", None))
        self.assertEqual([item["role"] for item in items], ["user", "assistant"])
        text = converter.render(simple_record(), "s1")[0].decode()
        self.assertIn('format: "simple"', text)
        self.assertIn("hello there", text)
        self.assertIn("general kenobi", text)
        self.assertIn('Role: "assistant"', text)

    def test_mapping_walks_selected_branch_only_in_chronological_order(self):
        record = mapping_record()
        items, provider, branch = converter.messages(record)
        self.assertEqual((provider, branch), ("chatgpt", "n2"))
        self.assertEqual([item["content"]["parts"][0] for item in items],
                         ["first question", "selected answer"])

        text = converter.render(record, "g1")[0].decode()
        self.assertLess(text.index("first question"), text.index("selected answer"))
        self.assertNotIn("sibling ignored branch", text)
        self.assertIn('branch: "n2"', text)
        self.assertIn('format: "chatgpt"', text)

        # An unselected current node is still a valid, differently-scoped branch.
        sibling = dict(record, current_node="sibling")
        text = converter.render(sibling, "g1")[0].decode()
        self.assertIn("sibling ignored branch", text)
        self.assertNotIn("selected answer", text)
        self.assertIn('branch: "sibling"', text)

    def test_structural_null_nodes_are_skipped_not_rendered(self):
        record = {
            "id": "n", "title": "N", "current_node": "b",
            "mapping": {
                "root": {"parent": None, "message": None},
                "a": {"parent": "root", "message": None},
                "b": {"parent": "a", "message": {
                    "author": {"role": "user"},
                    "content": {"content_type": "text", "parts": ["only real node"]}}},
            },
        }
        items, provider, _ = converter.messages(record)
        self.assertEqual(len(items), 1)
        text = converter.render(record, "n")[0].decode()
        self.assertEqual(text.count("## Message "), 1)
        self.assertIn("only real node", text)


class MalformedInputTests(unittest.TestCase):
    BAD_MAPPINGS = {
        "missing_current": {"id": "x", "mapping": {"a": {"parent": None, "message": None}}},
        "empty_current": {"id": "x", "current_node": "", "mapping": {"a": {"parent": None, "message": None}}},
        "non_string_current": {"id": "x", "current_node": ["a"], "mapping": {"a": {"parent": None, "message": None}}},
        "absent_current_node": {
            "id": "x", "current_node": "ghost",
            "mapping": {"a": {"parent": None, "message": None}}},
        "non_list_messages": {"id": "x", "messages": "nope"},
        "non_list_chat_messages": {"id": "x", "chat_messages": "nope"},
        "missing_parent_reference": {
            "id": "x", "current_node": "a",
            "mapping": {"a": {"parent": "gone", "message": {"author": {"role": "user"}, "content": "hi"}}}},
        "missing_parent_key": {
            "id": "x", "current_node": "a",
            "mapping": {"a": {"message": {"author": {"role": "user"}, "content": "hi"}}}},
        "missing_message_key": {
            "id": "x", "current_node": "a", "mapping": {"a": {"parent": None}}},
        "node_not_object": {"id": "x", "current_node": "a", "mapping": {"a": "nope"}},
        "cyclic_ancestry": {
            "id": "x", "current_node": "a",
            "mapping": {"a": {"parent": "b", "message": None},
                        "b": {"parent": "a", "message": None}}},
        "multiple_parents_are_not_merged": {
            "id": "x", "current_node": "a",
            "mapping": {"a": {"parent": ["b", "c"], "message": {"author": {"role": "user"}, "content": "hi"}}}},
        "message_not_object": {
            "id": "x", "current_node": "a", "mapping": {"a": {"parent": None, "message": "nope"}}},
        "author_not_object": {
            "id": "x", "current_node": "a",
            "mapping": {"a": {"parent": None, "message": {"author": "nope", "content": "hi"}}}},
        "missing_role": {
            "id": "x", "current_node": "a",
            "mapping": {"a": {"parent": None, "message": {"author": {}, "content": "hi"}}}},
    }

    def test_bad_mappings_fail_explicitly_in_process(self):
        for name, record in self.BAD_MAPPINGS.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                converter.render(record, "x")

    def test_bad_mappings_fail_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for name, record in self.BAD_MAPPINGS.items():
                with self.subTest(name=name):
                    export = write_json(tmp / f"{name}.json", [record])
                    outdir = tmp / f"out-{name}"
                    result = run_cli(export, outdir, "--all", "--min-words", "0")
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(counts(result.stdout)["failed"], 1)
                    self.assertEqual(counts(result.stdout)["written"], 0)
                    self.assertFalse(outdir.exists())

    def test_non_object_and_duplicate_conversations_fail_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            cases = {
                "non_object": ["not an object"],
                "duplicate_ids": [{"id": "d", "chat_messages": []},
                                  {"id": "d", "chat_messages": []}],
                "duplicate_derived_ids": [
                    {"chat_messages": [{"sender": "user", "content": "same"}]},
                    {"chat_messages": [{"sender": "user", "content": "same"}]}],
            }
            for name, data in cases.items():
                with self.subTest(name=name):
                    export = write_json(tmp / f"{name}.json", data)
                    outdir = tmp / f"out-{name}"
                    result = run_cli(export, outdir, "--all", "--min-words", "0")
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(counts(result.stdout)["failed"], 1)
                    self.assertFalse(outdir.exists())

    def test_unsupported_shape_is_counted_separately_from_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            export = write_json(tmp / "u.json", [{"id": "u", "totally": "unknown"}])
            result = run_cli(export, tmp / "out", "--all", "--min-words", "0")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(counts(result.stdout)["unsupported"], 1)
            self.assertEqual(counts(result.stdout)["failed"], 0)
            self.assertFalse((tmp / "out").exists())

            unreadable = tmp / "bad.json"
            unreadable.write_text('[{"id": "u", "id": "v"}]', encoding="utf-8")
            result = run_cli(unreadable, tmp / "out2", "--all", "--min-words", "0")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(counts(result.stdout)["failed"], 1)
            self.assertFalse((tmp / "out2").exists())


class TimestampTests(unittest.TestCase):
    def test_epoch_zoned_date_unknown_and_invalid(self):
        self.assertIsNone(converter.timestamp(None))
        self.assertIsNone(converter.timestamp(""))
        self.assertEqual(converter.timestamp(1700000000), "2023-11-14T22:13:20Z")
        self.assertEqual(converter.timestamp(1700000000.5), "2023-11-14T22:13:20.500000Z")
        self.assertEqual(converter.timestamp("2026-01-02T03:04:05Z"), "2026-01-02T03:04:05Z")
        self.assertEqual(converter.timestamp("2026-01-02T03:04:05+02:00"), "2026-01-02T01:04:05Z")
        self.assertEqual(converter.timestamp("2026-01-02"), "2026-01-02")
        for invalid in (True, False, "2026-01-02T03:04:05", "2026-13-99", float("nan"),
                        float("inf"), float("-inf"), [1], {"a": 1}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                converter.timestamp(invalid)

    def test_render_keeps_known_and_unknown_dates_distinct(self):
        record = {
            "id": "t", "title": "T", "created_at": 1700000000, "updated_at": None,
            "chat_messages": [
                {"sender": "user", "created_at": "2026-01-02T03:04:05+02:00",
                 "updated_at": "2026-01-02", "content": "known"},
                {"sender": "assistant", "content": "no dates"},
            ],
        }
        text = converter.render(record, "t")[0].decode()
        meta = frontmatter(text)
        self.assertEqual(meta["created"], "2023-11-14T22:13:20Z")
        self.assertIsNone(meta["updated"])
        self.assertIn('Created: "2026-01-02T01:04:05Z"', text)
        self.assertIn('Updated: "2026-01-02"', text)
        self.assertEqual(text.count("Created: null"), 1)

    def test_invalid_message_timestamp_fails_conversion(self):
        record = claude_record(messages=[{"sender": "user", "created_at": "2026-01-02T03:04:05"}])
        with self.assertRaises(ValueError):
            converter.render(record, "c1")


class MetadataAndOmissionTests(unittest.TestCase):
    def test_text_variants_and_extra_payloads_are_not_silently_lost(self):
        for content, expected, omitted in (
            ({"type": "text", "text": "kept", "citations": [{"url": "synthetic"}],
              "image_url": "synthetic"}, "kept", 2),
            ({"content_type": "code", "text": "print('synthetic')", "language": "python"},
             "print('synthetic')", 1),
        ):
            with self.subTest(content=content):
                self.assertEqual(converter.text_content(content), (expected, omitted))
        for content in ({"content_type": "text", "parts": "invalid"},
                        {"type": "text"}, {"type": "text", "text": 3}):
            with self.subTest(content=content), self.assertRaises(ValueError):
                converter.text_content(content)
        for kind in ("execution_output", "tether_quote", "user_editable_context"):
            block = {"content_type": kind, "text": "unsupported text"}
            for content in (block, [block], {"content_type": "multimodal_text", "parts": [block]}):
                with self.subTest(content=content), self.assertRaises(converter.Unsupported):
                    converter.text_content(content)
        self.assertEqual(converter.text_content([{"content_type": "code", "text": "kept code"}]),
                         ("kept code", 0))
        record = simple_record(messages=[{"role": "user", "content": [], "text": "fallback"}])
        self.assertIn("fallback", converter.render(record, "s1")[0].decode())

    def test_titles_and_roles_are_quoted_and_never_forge_structure(self):
        record = {
            "id": "i",
            "name": 'a"\nRole: "admin"\n---',
            "chat_messages": [
                {"sender": 'evil"\nRole: "admin"', "content": "````\n## Message 99"},
            ],
        }
        text = converter.render(record, "i")[0].decode()
        # A run of four backticks needs a longer fence than any run inside the text.
        self.assertIn("`````text\n````\n## Message 99\n`````", text)
        meta = frontmatter(text)
        self.assertEqual(meta["title"], record["name"])
        role_lines = [line for line in text.splitlines() if line.startswith("Role: ")]
        self.assertEqual(len(role_lines), 1)
        self.assertEqual(json.loads(role_lines[0].split(": ", 1)[1]), record["chat_messages"][0]["sender"])
        # Only the real message heading exists outside the fenced payload.
        self.assertEqual(text.split("`````")[0].count("## Message "), 1)

    def test_non_text_and_tool_payloads_are_omitted_and_counted(self):
        record = {
            "id": "o", "name": "O",
            "chat_messages": [
                {"sender": "user", "content": [{"type": "text", "text": "alpha"},
                                                {"type": "image", "src": "SECRET-MEDIA"}],
                 "attachments": [{"a": 1}, {"b": 2}]},
                {"sender": "tool", "content": "SECRET-TOOL-TEXT", "tool_calls": [{"x": 1}]},
                {"sender": "assistant", "content": "beta"},
            ],
        }
        text = converter.render(record, "o")[0].decode()
        self.assertNotIn("SECRET-MEDIA", text)
        self.assertNotIn("SECRET-TOOL-TEXT", text)
        self.assertIn("alpha", text)
        self.assertIn("beta", text)
        self.assertIn('Role: "tool"', text)
        marker = [line for line in text.splitlines() if line.startswith("Omitted non-text/tool payloads:")]
        self.assertEqual(marker, ["Omitted non-text/tool payloads: 3",
                                  "Omitted non-text/tool payloads: 2",
                                  "Omitted non-text/tool payloads: 0"])
        self.assertEqual(frontmatter(text)["omitted_payloads"], 5)

        mapping = {
            "id": "m", "title": "M", "current_node": "n",
            "mapping": {"n": {"parent": None, "message": {
                "author": {"role": "user"},
                "content": {"content_type": "multimodal_text",
                            "parts": ["kept text", {"image": "SECRET-IMAGE"}]}}}},
        }
        text = converter.render(mapping, "m")[0].decode()
        self.assertIn("kept text", text)
        self.assertNotIn("SECRET-IMAGE", text)
        self.assertEqual(frontmatter(text)["omitted_payloads"], 1)


class CliSelectionTests(unittest.TestCase):
    def test_min_words_boundary_and_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            record = simple_record(messages=[{"role": "user", "content": "one two three"}])
            export = write_json(tmp / "e.json", [record])
            self.assertEqual(converter.render(record, "s1")[1], 3)

            exact = run_cli(export, tmp / "exact", "--all", "--min-words", "3")
            self.assertEqual(exact.returncode, 0)
            self.assertEqual(counts(exact.stdout)["written"], 1)

            over = run_cli(export, tmp / "over", "--all", "--min-words", "4")
            self.assertEqual(over.returncode, 0)
            self.assertEqual(counts(over.stdout)["too_short"], 1)
            self.assertFalse((tmp / "over").exists())

            defaulted = run_cli(export, tmp / "default", "--all")
            self.assertEqual(defaulted.returncode, 0)
            self.assertEqual(counts(defaulted.stdout)["too_short"], 1)

            negative = run_cli(export, tmp / "neg", "--all", "--min-words", "-1")
            self.assertEqual(negative.returncode, 2)

    def test_explicit_selection_all_and_deduplication(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            export = write_json(tmp / "e.json", [
                simple_record("a", messages=[{"role": "user", "content": "alpha alpha"}]),
                simple_record("b", messages=[{"role": "user", "content": "beta beta"}]),
            ])
            every = run_cli(export, tmp / "all", "--all", "--min-words", "0")
            self.assertEqual(counts(every.stdout)["written"], 2)
            self.assertEqual(len(list((tmp / "all").glob("*.md"))), 2)

            chosen = run_cli(export, tmp / "one", "--conversation-id", "a", "--min-words", "0")
            self.assertEqual(counts(chosen.stdout)["selected"], 1)
            text = output_text(tmp / "one")
            self.assertIn("alpha", text)
            self.assertNotIn("beta", text)

            repeat = run_cli(export, tmp / "dup", "--conversation-id", "a",
                             "--conversation-id", "a", "--min-words", "0")
            self.assertEqual(counts(repeat.stdout)["written"], 1)
            self.assertEqual(len(list((tmp / "dup").glob("*.md"))), 1)

            missing = run_cli(export, tmp / "missing", "--conversation-id", "zz", "--min-words", "0")
            self.assertEqual(missing.returncode, 2)
            self.assertEqual(counts(missing.stdout)["failed"], 1)
            self.assertEqual(json.loads(missing.stderr)["failures"],
                             [["zz", "selected conversation ID not found"]])
            self.assertFalse((tmp / "missing").exists())

            for args in ((), ("--all", "--conversation-id", "a")):
                with self.subTest(args=args):
                    result = run_cli(export, tmp / "arg", *args, "--min-words", "0")
                    self.assertEqual(result.returncode, 2)


class DryRunAndRerunTests(unittest.TestCase):
    def test_omitted_payload_revisions_still_version_the_artifact(self):
        record = simple_record(messages=[{"role": "user", "content": "kept",
                                          "attachments": ["synthetic-a"]}])
        before = converter.render(record, "s1")[0]
        record["messages"][0]["attachments"] = ["synthetic-b"]
        after = converter.render(record, "s1")[0]
        self.assertNotEqual(before, after)
        self.assertNotIn(b"synthetic-b", after)

    def test_dry_run_creates_nothing_and_leaves_input_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "src"
            source.mkdir()
            export = write_json(source / "e.json", [simple_record()])
            before = snapshot(source)

            result = run_cli(export, tmp / "absent" / "out", "--all", "--min-words", "0", "--dry-run")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(counts(result.stdout)["would_write"], 1)
            self.assertEqual(counts(result.stdout)["written"], 0)
            self.assertFalse((tmp / "absent").exists())
            self.assertFalse((tmp / "absent" / "out").exists())
            self.assertEqual(snapshot(source), before)

    def test_identical_rerun_new_version_and_same_title_distinct_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "src"
            source.mkdir()
            export = write_json(source / "e.json", [simple_record("a", messages=[
                {"role": "user", "content": "alpha beta"}])])
            before = snapshot(source)
            outdir = tmp / "out"

            first = run_cli(export, outdir, "--all", "--min-words", "0")
            self.assertEqual(counts(first.stdout)["written"], 1)
            files = sorted(path.name for path in outdir.glob("*.md"))
            original_bytes = (outdir / files[0]).read_bytes()

            for _ in range(2):
                again = run_cli(export, outdir, "--all", "--min-words", "0")
                self.assertEqual(counts(again.stdout)["identical"], 1)
                self.assertEqual(counts(again.stdout)["written"], 0)
            self.assertEqual(sorted(path.name for path in outdir.glob("*.md")), files)
            self.assertEqual((outdir / files[0]).read_bytes(), original_bytes)
            self.assertEqual(snapshot(source), before)

            changed = write_json(source / "e.json", [simple_record("a", messages=[
                {"role": "user", "content": "gamma delta"}])])
            revised = run_cli(changed, outdir, "--all", "--min-words", "0")
            self.assertEqual(counts(revised.stdout)["written"], 1)
            self.assertEqual(len(list(outdir.glob("*.md"))), 2)
            self.assertTrue((outdir / files[0]).exists())
            self.assertEqual((outdir / files[0]).read_bytes(), original_bytes)
            self.assertIn("gamma", output_text(outdir))

            titled = write_json(tmp / "titled.json", [
                simple_record("x", title="Shared Title", messages=[{"role": "user", "content": "x1"}]),
                simple_record("y", title="Shared Title", messages=[{"role": "user", "content": "y2"}]),
            ])
            both = run_cli(titled, tmp / "titled-out", "--all", "--min-words", "0")
            self.assertEqual(counts(both.stdout)["written"], 2)
            self.assertEqual(len(list((tmp / "titled-out").glob("*.md"))), 2)
            self.assertEqual(output_text(tmp / "titled-out").count('title: "Shared Title"'), 2)


class PathSafetyTests(unittest.TestCase):
    def test_export_path_hazards_and_traversal_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "src"
            source.mkdir()
            real = write_json(source / "e.json", [simple_record()])
            real_hash = hashlib.sha256(real.read_bytes()).hexdigest()

            symlink = tmp / "linked.json"
            symlink.symlink_to(real)
            hardlink = tmp / "hard.json"
            os.link(real, hardlink)
            directory = tmp / "adir"
            directory.mkdir()
            linked_source = tmp / "linked-src"
            linked_source.symlink_to(source, target_is_directory=True)

            cases = {
                "symlink_export": symlink,
                "hardlink_export": hardlink,
                "directory_export": directory,
                "parent_traversal": source / ".." / "src" / "e.json",
                "symlink_export_ancestor": linked_source / "e.json",
            }
            for name, export in cases.items():
                with self.subTest(name=name):
                    outdir = tmp / f"out-{name}"
                    result = run_cli(export, outdir, "--all", "--min-words", "0")
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(counts(result.stdout)["written"], 0)
                    self.assertFalse(outdir.exists())
            self.assertEqual(hashlib.sha256(real.read_bytes()).hexdigest(), real_hash)

    def test_output_path_hazards_and_traversal_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            export = write_json(tmp / "e.json", [simple_record()])

            traversal = run_cli(export, tmp / "sub" / ".." / "escape", "--all", "--min-words", "0")
            self.assertEqual(traversal.returncode, 2)
            self.assertFalse((tmp / "escape").exists())

            real_dir = tmp / "realdir"
            real_dir.mkdir()
            linked_ancestor = tmp / "linked" / "child"
            (tmp / "linked").symlink_to(real_dir, target_is_directory=True)
            ancestor = run_cli(export, linked_ancestor, "--all", "--min-words", "0")
            self.assertEqual(ancestor.returncode, 2)
            self.assertFalse((real_dir / "child").exists())

            linked_outdir = tmp / "outlink"
            linked_outdir.symlink_to(real_dir, target_is_directory=True)
            direct = run_cli(export, linked_outdir, "--all", "--min-words", "0")
            self.assertEqual(direct.returncode, 2)
            self.assertEqual(list(real_dir.iterdir()), [])

            blocked = tmp / "blocked"
            blocked.write_text("not a directory", encoding="utf-8")
            as_file = run_cli(export, blocked, "--all", "--min-words", "0")
            self.assertEqual(as_file.returncode, 2)

    def test_existing_destination_links_and_corruption_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            export = write_json(tmp / "e.json", [simple_record("keep")])

            outdir = tmp / "out"
            self.assertEqual(run_cli(export, outdir, "--all", "--min-words", "0").returncode, 0)
            artifact = next(outdir.glob("*.md"))
            good = artifact.read_bytes()

            elsewhere = tmp / "elsewhere.md"
            elsewhere.write_bytes(good)
            artifact.unlink()
            artifact.symlink_to(elsewhere)
            linked = run_cli(export, outdir, "--all", "--min-words", "0")
            self.assertEqual(linked.returncode, 2)
            self.assertEqual(counts(linked.stdout)["failed"], 1)
            self.assertEqual(artifact.read_bytes(), good)

            artifact.unlink()
            artifact.write_bytes(good)
            os.link(artifact, tmp / "hard-other.md")
            hard = run_cli(export, outdir, "--all", "--min-words", "0")
            self.assertEqual(hard.returncode, 2)
            self.assertEqual(counts(hard.stdout)["failed"], 1)

            os.unlink(tmp / "hard-other.md")
            artifact.write_bytes(b"corrupt bytes")
            corrupt = run_cli(export, outdir, "--all", "--min-words", "0")
            self.assertEqual(corrupt.returncode, 2)
            self.assertEqual(counts(corrupt.stdout)["failed"], 1)
            self.assertEqual(artifact.read_bytes(), b"corrupt bytes")


class PartialFailureAndDiagnosticsTests(unittest.TestCase):
    def test_partial_write_failure_reports_written_and_failed_ids_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            export = write_json(tmp / "e.json", [
                simple_record("a", messages=[{"role": "user", "content": "alpha"}]),
                simple_record("b", messages=[{"role": "user", "content": "beta"}]),
                simple_record("c", messages=[{"role": "user", "content": "gamma"}]),
            ])
            outdir = tmp / "out"
            real_save = converter.save
            calls = {"n": 0}

            def flaky(fd, name, content, dry_run):
                calls["n"] += 1
                if calls["n"] == 2:
                    raise OSError("synthetic disk failure")
                return real_save(fd, name, content, dry_run)

            stdout, stderr = io.StringIO(), io.StringIO()
            with mock.patch.object(converter, "save", side_effect=flaky), \
                    contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = converter.main([str(export), str(outdir), "--all", "--min-words", "0"])

            self.assertEqual(code, 2)
            self.assertEqual(counts(stdout.getvalue())["written"], 1)
            self.assertEqual(counts(stdout.getvalue())["failed"], 1)
            report = json.loads(stderr.getvalue())
            self.assertEqual(report["written_ids"], ["a"])
            self.assertEqual(report["unattempted_ids"], ["c"])
            self.assertEqual(report["failures"], [["b", "destination write/verification failed"]])
            self.assertEqual(len(list(outdir.glob("*.md"))), 1)

    def test_diagnostics_never_include_titles_or_message_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            secret_title = "SECRET-TITLE-9f2a"
            secret_body = "SECRET-BODY-9f2a"

            malformed = write_json(tmp / "bad.json", [
                {"id": "bad", "name": secret_title,
                 "chat_messages": [{"sender": "user", "content": secret_body, "created_at": "not-a-date"}]},
            ])
            result = run_cli(malformed, tmp / "out", "--all", "--min-words", "0")
            self.assertEqual(result.returncode, 2)
            self.assertNotIn(secret_title, result.stdout + result.stderr)
            self.assertNotIn(secret_body, result.stdout + result.stderr)

            unsupported = write_json(tmp / "unsup.json", [{"id": "u", "name": secret_title, "other": 1}])
            result = run_cli(unsupported, tmp / "out2", "--all", "--min-words", "0")
            self.assertEqual(result.returncode, 2)
            self.assertNotIn(secret_title, result.stdout + result.stderr)

            broken = tmp / "broken.json"
            broken.write_text('["' + secret_body + '",', encoding="utf-8")
            result = run_cli(broken, tmp / "out3", "--all", "--min-words", "0")
            self.assertEqual(result.returncode, 2)
            self.assertNotIn(secret_body, result.stdout + result.stderr)
            self.assertNotIn(str(broken), result.stderr)

            # A successful default run prints counts only, not converted content.
            good = write_json(tmp / "good.json", [simple_record("g", title=secret_title, messages=[
                {"role": "user", "content": secret_body}])])
            result = run_cli(good, tmp / "out4", "--all", "--min-words", "0")
            self.assertEqual(result.returncode, 0)
            self.assertNotIn(secret_title, result.stdout + result.stderr)
            self.assertNotIn(secret_body, result.stdout + result.stderr)
            self.assertIn(secret_title, output_text(tmp / "out4"))


if __name__ == "__main__":
    unittest.main()
