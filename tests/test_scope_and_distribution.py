"""Synthetic preflight and manual distribution rehearsal; not runtime enforcement."""

import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from runtime_read_probe import validate_scope


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ScopeTests(unittest.TestCase):
    def test_regular_relative_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "corpus"
            (root / "pages").mkdir(parents=True)
            (root / "pages/ok.md").write_text("Synthetic page\n")
            self.assertIsNone(validate_scope(root, ["pages/ok.md"]))

    def test_absolute_and_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "corpus"
            root.mkdir()
            (root / "ok.md").write_text("Synthetic page\n")
            for path in (root / "ok.md", "../ok.md", "pages/../ok.md"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    validate_scope(root, [path])

    def test_file_and_ancestor_links_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "corpus"
            (root / "pages").mkdir(parents=True)
            (root / "pages/ok.md").write_text("Synthetic page\n")
            (root / "link.md").symlink_to("pages/ok.md")
            (root / "linked-pages").symlink_to("pages", target_is_directory=True)
            (base / "linked-root").symlink_to(root, target_is_directory=True)
            (base / "linked-parent").symlink_to(base, target_is_directory=True)
            for scope, path in (
                (root, "link.md"),
                (root, "linked-pages/ok.md"),
                (base / "linked-root", "pages/ok.md"),
                (base / "linked-parent/corpus", "pages/ok.md"),
            ):
                with self.subTest(scope=scope, path=path), self.assertRaises(ValueError):
                    validate_scope(scope, [path])

    def test_hardlinks_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "ok.md").write_text("Synthetic page\n")
            os.link(root / "ok.md", root / "alias.md")
            for path in ("ok.md", "alias.md"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    validate_scope(root, [path])

    def test_missing_and_directory_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "pages").mkdir()
            for path in ("pages/missing.md", "pages"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    validate_scope(root, [path])


class DistributionRehearsalTests(unittest.TestCase):
    def test_approved_new_file_and_hash_gated_rollback(self):
        # Manual, path-specific rehearsal only: no installer, merge, vault, or runtime proof.
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source_dir = base / "public"
            workspace = base / "workspace"
            source_dir.mkdir()
            (workspace / ".opencode/templates").mkdir(parents=True)
            source = source_dir / "candidate.json"
            source.write_text('{"permission":{"*":"deny"}}\n')
            protected = {
                workspace / "AGENTS.md": "Synthetic local instructions\n",
                workspace / "opencode.json": '{"local":"synthetic"}\n',
                workspace / ".opencode/templates/capture.md": "Synthetic local template\n",
                workspace / "unrelated.md": "Synthetic unrelated page\n",
            }
            for path, content in protected.items():
                path.write_text(content)
            preimages = {path: sha256(path) for path in protected}

            # Collisions have no merge approval; approve only this NEW namespaced file.
            destination = workspace / ".opencode/second-brain.json"
            validate_scope(source_dir, ["candidate.json"])
            source_hash = sha256(source)
            self.assertFalse(destination.exists())  # destination preimage: absent
            with destination.open("xb") as output:
                output.write(source.read_bytes())
            postimage_hash = sha256(destination)
            self.assertEqual(postimage_hash, source_hash)
            self.assertEqual({path: sha256(path) for path in protected}, preimages)

            destination.write_text("Synthetic local edit\n")
            drift_hash = sha256(destination)
            self.assertNotEqual(drift_hash, postimage_hash)
            if sha256(destination) == postimage_hash:
                destination.unlink()
            self.assertEqual(sha256(destination), drift_hash)  # drift blocks rollback

            # Owner resolves the synthetic drift back to the recorded postimage.
            destination.write_bytes(source.read_bytes())
            self.assertEqual(sha256(destination), postimage_hash)
            if sha256(destination) == postimage_hash:
                destination.unlink()  # approved removal of the newly created file only
            self.assertFalse(destination.exists())
            self.assertEqual({path: sha256(path) for path in protected}, preimages)


if __name__ == "__main__":
    unittest.main()
