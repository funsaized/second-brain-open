"""Offline R6 filesystem rehearsal, not a private-vault backup CLI.

Only fixed public/invented inputs are used, under three temporary sibling roots.
Preflight assumes frozen roots; it is not a lock against concurrent replacement.
No models, runtime profiles, encryption policy, sync, vault Git or live restore.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import link_check
from runtime_read_probe import validate_scope


FIXTURE = ROOT / "tests/fixtures/contract"
FIXTURE_PATHS = (
    "wiki/index.md", "wiki/log.md", "wiki/concepts/vent-choice.md",
    "wiki/entities/aster-desk-lab.md", "wiki/synthesis/vent-setting.md",
    "wiki/sources/trial-a.md", "wiki/sources/trial-b.md",
    "raw/trial-a.md", "raw/trial-b.md", "projects/vent-repeat/brief.md",
)
PUBLIC_COPIES = {
    "templates/source.md": ROOT / "framework/templates/source.md",
    "instructions/wiki-contract.md": ROOT / "framework/instructions/wiki-contract.md",
    "local-framework/opencode.example.json": ROOT / "framework/opencode.example.json",
    "LICENSE": ROOT / "LICENSE",
    "THIRD_PARTY_NOTICES.md": ROOT / "THIRD_PARTY_NOTICES.md",
}
ASSET = "raw/assets/invented swatch.bin"
ASSET_BYTES = b"Wholly invented R6 binary asset\x00\xff\n"
APPROVED = (*FIXTURE_PATHS, *PUBLIC_COPIES, ASSET)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_names(names):
    names = tuple(names)
    if not names or len(set(names)) != len(names):
        raise ValueError("Expected a nonempty, unique approved file list")
    for name in names:
        if not isinstance(name, str):
            raise ValueError("Expected canonical relative names")
        path = Path(name)
        if (path.is_absolute() or ".." in path.parts or path.as_posix() != name
                or name == "." or "\\" in name or ":" in name
                or any(ord(c) < 32 or ord(c) == 127 for c in name)
                or any(p in (".obsidian", ".git", "auth.json")
                       or p.startswith((".env", "credentials")) or p.endswith((".pem", ".key"))
                       for p in path.parts)):
            raise ValueError("Unapproved path form or excluded resource")
    return tuple(sorted(names))


def distinct_roots(*roots):
    for root in roots:
        if not root.is_absolute() or ".." in root.parts or any(p.is_symlink() for p in (root, *root.parents)):
            raise ValueError("Roots must be absolute, unlinked and non-traversing")
        if root.exists() and not root.is_dir():
            raise ValueError("Existing root is not a directory")
    for index, root in enumerate(roots):
        if any(root == other or root in other.parents or other in root.parents for other in roots[index + 1:]):
            raise ValueError("Source, snapshot and restore roots must not overlap")


def manifest_for(root, names):
    names = checked_names(names)
    validate_scope(root, names)
    return {name: digest((root / name).read_bytes()) for name in names}


def manifest_bytes(manifest):
    checked_names(manifest)
    if any(not isinstance(h, str) or not re.fullmatch(r"[0-9a-f]{64}", h) for h in manifest.values()):
        raise ValueError("Invalid approved digest")
    return (json.dumps({"version": 1, "files": manifest}, sort_keys=True, indent=2) + "\n").encode()


def verified_bytes(root, manifest):
    manifest_bytes(manifest)
    validate_scope(root, manifest)
    # ponytail: tiny fixed fixture is held in RAM; real large-asset backup needs
    # a separately reviewed streaming implementation/tool and frozen-source policy.
    data = {name: (root / name).read_bytes() for name in sorted(manifest)}
    if {name: digest(body) for name, body in data.items()} != manifest:
        raise ValueError("Snapshot/source content differs from the approved manifest")
    return data


def exclusive_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as stream:
        stream.write(data)


def backup(source, bundle, manifest):
    distinct_roots(source, bundle)
    data = verified_bytes(source, manifest)
    bundle.mkdir(mode=0o700)  # Existing or partially written bundles are not reused.
    for name, body in data.items():
        exclusive_file(bundle / "files" / name, body)
    verified_bytes(bundle / "files", manifest)
    # A failed copy has no complete manifest; never restore an incomplete bundle.
    exclusive_file(bundle / "manifest.json", manifest_bytes(manifest))


def load_backup(bundle, approved_manifest):
    validate_scope(bundle, ["manifest.json"])
    if (bundle / "manifest.json").read_bytes() != manifest_bytes(approved_manifest):
        raise ValueError("Bundle manifest differs from separately retained approval")
    return verified_bytes(bundle / "files", approved_manifest)


def restore_new(source, bundle, target, manifest):
    distinct_roots(source, bundle, target)
    data = load_backup(bundle, manifest)
    target.mkdir(mode=0o700)
    for name, body in data.items():
        exclusive_file(target / name, body)
    if manifest_for(target, manifest) != manifest:
        raise ValueError("Restored hashes differ")


def restore_selected(source, bundle, target, manifest, preimages):
    distinct_roots(source, bundle, target)
    if not target.is_dir():
        raise ValueError("Selected recovery requires an existing alternate restore root")
    checked_names(preimages)
    if not set(preimages) <= set(manifest):
        raise ValueError("Recovery may touch only approved manifest files")
    data = load_backup(bundle, manifest)
    # Validate the whole recovery plan before the first mutation.
    for name, expected in preimages.items():
        path = target / name
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError("Linked recovery destination")
        actual = None
        if path.exists():
            validate_scope(target, [name])
            actual = digest(path.read_bytes())
        if actual != expected:
            raise ValueError("Recovery drift: preserve human work and replan")
    for name in sorted(preimages):
        path = target / name
        if preimages[name] is None:
            exclusive_file(path, data[name])
        else:
            # Per-file atomic replacement; the batch is deliberately not atomic.
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".r6-", delete=False) as stream:
                temporary = Path(stream.name)
                try:
                    stream.write(data[name])
                    stream.flush()
                except BaseException:
                    temporary.unlink()
                    raise
            try:
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
        if digest(path.read_bytes()) != manifest[name]:
            raise ValueError("Recovered file hash differs")


class R6BackupRestoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sb-r6-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.source, self.bundle, self.target = (self.base / name for name in ("source", "snapshot", "restored"))
        self.source.mkdir(mode=0o700)
        inputs = {name: FIXTURE / name for name in FIXTURE_PATHS} | PUBLIC_COPIES
        for name, original in inputs.items():
            validate_scope(ROOT, [original.relative_to(ROOT)])
            exclusive_file(self.source / name, original.read_bytes())
        exclusive_file(self.source / ASSET, ASSET_BYTES)
        # Wholly invented exclusions; never inspect real credentials to filter them.
        for name in (".obsidian/ignored.md", ".env", "unrelated.md"):
            exclusive_file(self.source / name, b"Unselected synthetic marker\n")
        self.manifest = manifest_for(self.source, APPROVED)
        self.approval_file = self.base / "approved-manifest.json"
        exclusive_file(self.approval_file, manifest_bytes(self.manifest))
        self.approval_file.chmod(0o400)

    def assert_clean(self, root):
        report = link_check.check(root)
        self.assertEqual((report["pages"], len(report["links"])), (5, 18))
        self.assertEqual((report["errors"], report["unsupported"], report["unchecked"]), ([], [], []))
        return report

    def test_separate_snapshot_and_restore_without_live_source(self):
        original_read = Path.read_bytes
        def selected_only(path):
            self.assertNotIn(".obsidian", path.parts)
            self.assertNotIn(path.name, (".env", "unrelated.md"))
            return original_read(path)
        with mock.patch.object(Path, "read_bytes", selected_only):
            backup(self.source, self.bundle, self.manifest)
        before_report = self.assert_clean(self.source)
        offline_source = self.base / "offline-source"
        self.source.rename(offline_source)  # Prove restoration does not fall back to source bytes.
        retained_manifest = json.loads(self.approval_file.read_bytes())["files"]
        restore_new(self.source, self.bundle, self.target, retained_manifest)
        self.assertEqual(len(self.manifest), 16)
        self.assertEqual(manifest_for(self.target, APPROVED), self.manifest)
        self.assertEqual(manifest_for(offline_source, APPROVED), self.manifest)
        self.assertEqual(self.assert_clean(self.target), before_report)
        self.assertEqual((self.target / ASSET).read_bytes(), ASSET_BYTES)
        (self.target / ASSET).unlink()
        restore_selected(self.source, self.bundle, self.target, retained_manifest, {ASSET: None})
        self.assertEqual(manifest_for(self.target, APPROVED), self.manifest)
        self.assertEqual({p.relative_to(self.target).as_posix() for p in self.target.rglob("*") if p.is_file()}, set(APPROVED))
        self.assertEqual(self.bundle.stat().st_mode & 0o777, 0o700)
        self.assertTrue(all((self.target / p).stat().st_mode & 0o777 == 0o600 for p in APPROVED))

    def test_partial_operation_drift_refuses_all_then_preserves_human_work(self):
        backup(self.source, self.bundle, self.manifest)
        restore_new(self.source, self.bundle, self.target, self.manifest)
        concept, index, log = "wiki/concepts/vent-choice.md", "wiki/index.md", "wiki/log.md"
        before_concept = (self.target / concept).read_bytes()
        partial = before_concept + b"\nUnfinished synthetic operation.\n"
        (self.target / concept).write_bytes(partial)
        # This simulated later source revision must not replace the backup's bytes.
        (self.source / concept).write_bytes(b"Source changed after snapshot\n")
        source_after_simulation = manifest_for(self.source, APPROVED)
        intended_preimages = {concept: digest(partial), index: self.manifest[index], log: self.manifest[log]}
        human = (self.target / index).read_bytes() + b"\nHuman review: preserve this synthetic paragraph.\n"
        (self.target / index).write_bytes(human)
        exclusive_file(self.target / "unrelated.md", b"Preserve unselected human work\n")
        before_refusal = manifest_for(self.target, APPROVED)
        with self.assertRaises(ValueError):
            restore_selected(self.source, self.bundle, self.target, self.manifest, intended_preimages)
        self.assertEqual(manifest_for(self.target, APPROVED), before_refusal)
        # Operator chooses preservation, not resetting the human edit to make a check pass.
        restore_selected(self.source, self.bundle, self.target, self.manifest, {concept: digest(partial)})
        self.assertEqual((self.target / concept).read_bytes(), before_concept)
        self.assertEqual((self.target / index).read_bytes(), human)
        old_log = (self.target / log).read_bytes()
        self.assertEqual(digest(old_log), self.manifest[log])
        with (self.target / log).open("ab") as stream:
            stream.write(b"\n## 2026-09-25 - Synthetic recovery\nRestored only the interrupted concept change from verified backup; preserved human index and unrelated work.\n")
        self.assertTrue((self.target / log).read_bytes().startswith(old_log))
        self.assertEqual((self.target / "unrelated.md").read_bytes(), b"Preserve unselected human work\n")
        unaffected = set(APPROVED) - {concept, index, log}
        self.assertEqual(manifest_for(self.target, unaffected), {p: self.manifest[p] for p in unaffected})
        self.assertEqual(manifest_for(self.source, APPROVED), source_after_simulation)
        load_backup(self.bundle, self.manifest)
        self.assert_clean(self.target)

    def test_corrupt_payload_and_rewritten_bundle_manifest_cannot_restore(self):
        backup(self.source, self.bundle, self.manifest)
        # Intact payloads: this specifically exercises the external-manifest check.
        original_record = (self.bundle / "manifest.json").read_bytes()
        (self.bundle / "manifest.json").write_bytes(original_record + b"\n")
        with self.assertRaises(ValueError):
            restore_new(self.source, self.bundle, self.target, self.manifest)
        self.assertFalse(self.target.exists())
        (self.bundle / "manifest.json").write_bytes(original_record)
        name = "raw/trial-a.md"
        (self.bundle / "files" / name).write_bytes(b"Corrupted synthetic backup\n")
        with self.assertRaises(ValueError):
            restore_new(self.source, self.bundle, self.target, self.manifest)
        self.assertFalse(self.target.exists())
        forged = dict(self.manifest, **{name: digest(b"Corrupted synthetic backup\n")})
        (self.bundle / "manifest.json").write_bytes(manifest_bytes(forged))
        with self.assertRaises(ValueError):
            restore_new(self.source, self.bundle, self.target, self.manifest)
        self.assertFalse(self.target.exists())

    def test_links_hardlinks_and_excluded_manifest_entries_are_refused(self):
        for name in ("../outside.md", "/absolute.md", "wiki/../outside.md", ".obsidian/never-read.json", ".env", "auth.json",
                     ".env/secret.md", "nested/.env.local/secret.md", "credentials.txt", "credentials/secret.md",
                     "key.pem", "nested/id_rsa.key", "bad\nname.md", "bad\x00name.md"):
            # Check the lexical gate itself, not just a later missing-file error.
            with self.subTest(path=name, gate="names"), self.assertRaises(ValueError):
                checked_names([name])
            with self.subTest(path=name), self.assertRaises(ValueError):
                manifest_for(self.source, [name])
        source_file = self.source / "raw/trial-a.md"
        alias = self.base / "alias.md"
        os.link(source_file, alias)
        with self.assertRaises(ValueError):
            backup(self.source, self.bundle, self.manifest)
        self.assertFalse(self.bundle.exists())
        alias.unlink()
        backup(self.source, self.bundle, self.manifest)
        copied = self.bundle / "files/raw/trial-a.md"
        copied.unlink()
        copied.symlink_to(source_file)
        with self.assertRaises(ValueError):
            restore_new(self.source, self.bundle, self.target, self.manifest)
        self.assertFalse(self.target.exists())
        copied.unlink()
        exclusive_file(copied, source_file.read_bytes())
        restore_new(self.source, self.bundle, self.target, self.manifest)
        target_file = self.target / "wiki/index.md"
        target_alias = self.base / "target-alias.md"
        os.link(target_file, target_alias)
        with self.assertRaises(ValueError):
            restore_selected(self.source, self.bundle, self.target, self.manifest, {"wiki/index.md": self.manifest["wiki/index.md"]})
        target_alias.unlink()
        target_file.unlink()
        target_file.symlink_to(self.source / "wiki/index.md")
        with self.assertRaises(ValueError):
            restore_selected(self.source, self.bundle, self.target, self.manifest, {"wiki/index.md": self.manifest["wiki/index.md"]})
        linked = self.base / "linked"
        linked.symlink_to(self.target, target_is_directory=True)
        with self.assertRaises(ValueError):
            restore_new(self.source, self.bundle, linked / "new", self.manifest)
        self.assertEqual(manifest_for(self.source, APPROVED), self.manifest)

    def test_root_overlap_collisions_and_unapproved_recovery_are_refused(self):
        for destination in (self.source, self.source / "nested", self.base):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                backup(self.source, destination, self.manifest)
        backup(self.source, self.bundle, self.manifest)
        with self.assertRaises(FileExistsError):
            backup(self.source, self.bundle, self.manifest)
        for destination in (self.source, self.source / "nested", self.bundle / "nested"):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                restore_new(self.source, self.bundle, destination, self.manifest)
        restore_new(self.source, self.bundle, self.target, self.manifest)
        with self.assertRaises(FileExistsError):
            restore_new(self.source, self.bundle, self.target, self.manifest)
        with self.assertRaises(ValueError):
            restore_selected(self.source, self.bundle, self.target, self.manifest, {"unlisted.md": None})
        self.assertEqual(manifest_for(self.target, APPROVED), self.manifest)
        (self.source / ASSET).write_bytes(b"Source drift\n")
        with self.assertRaises(ValueError):
            backup(self.source, self.base / "new-snapshot", self.manifest)
        self.assertFalse((self.base / "new-snapshot").exists())

    def test_write_failures_preserve_data_and_require_remaining_path_replan(self):
        original_copy = exclusive_file
        copies = []
        def fail_second_copy(path, data):
            if copies:
                raise OSError("synthetic backup write failure")
            copies.append(path)
            original_copy(path, data)
        with mock.patch(f"{__name__}.exclusive_file", side_effect=fail_second_copy), self.assertRaises(OSError):
            backup(self.source, self.bundle, self.manifest)
        self.assertTrue(copies[0].exists())
        self.assertFalse((self.bundle / "manifest.json").exists())
        with self.assertRaises(ValueError):
            restore_new(self.source, self.bundle, self.target, self.manifest)
        self.assertFalse(self.target.exists())
        with self.assertRaises(FileExistsError):
            backup(self.source, self.bundle, self.manifest)
        # The operator chooses a fresh bundle; never overwrite the partial copy.
        self.bundle = self.base / "complete-snapshot"
        backup(self.source, self.bundle, self.manifest)
        restore_new(self.source, self.bundle, self.target, self.manifest)
        name = "wiki/concepts/vent-choice.md"
        path = self.target / name
        path.write_bytes(b"Synthetic interrupted write\n")
        preimage = digest(path.read_bytes())
        before_names = set(path.parent.iterdir())
        with mock.patch("os.replace", side_effect=OSError("synthetic replacement failure")), self.assertRaises(OSError):
            restore_selected(self.source, self.bundle, self.target, self.manifest, {name: preimage})
        self.assertEqual(digest(path.read_bytes()), preimage)
        self.assertEqual(set(path.parent.iterdir()), before_names)
        other = self.target / "wiki/index.md"
        other.write_bytes(b"Second interrupted path\n")
        preimages = {name: preimage, "wiki/index.md": digest(other.read_bytes())}
        original_replace = os.replace
        calls = []
        def fail_second(source, destination):
            calls.append(destination)
            if len(calls) == 2:
                raise OSError("synthetic second replacement failure")
            return original_replace(source, destination)
        with mock.patch("os.replace", side_effect=fail_second), self.assertRaises(OSError):
            restore_selected(self.source, self.bundle, self.target, self.manifest, preimages)
        self.assertEqual(digest(path.read_bytes()), self.manifest[name])
        self.assertEqual(digest(other.read_bytes()), preimages["wiki/index.md"])
        with self.assertRaises(ValueError):
            restore_selected(self.source, self.bundle, self.target, self.manifest, preimages)
        restore_selected(self.source, self.bundle, self.target, self.manifest, {"wiki/index.md": preimages["wiki/index.md"]})
        self.assertEqual(manifest_for(self.target, APPROVED), self.manifest)
        self.assertFalse(list(self.target.rglob(".r6-*")))
        load_backup(self.bundle, self.manifest)
        self.assertEqual(manifest_for(self.source, APPROVED), self.manifest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
