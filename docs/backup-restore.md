# R6: synthetic backup and restore rehearsal

Status, 2026-09-25: the public filesystem rehearsal passes. **No private vault
has been backed up or restored.** This does not satisfy the private R6A policy or
R6C restore-proof gates for P3 installation.

The implementation is deliberately test-only:
`tests/test_r6_backup_restore.py`. It accepts no vault/source/destination CLI
arguments and runs only fixed public/invented inputs in temporary directories.
It reuses the existing link-rejecting scope check and wiki checker. It does not
start OpenCode, invoke a model, inspect owner configuration, configure sync/Git,
install framework files, or choose a backup product or encryption policy.

## Approved synthetic manifest and privacy assessment

The owner's authorization covers this invented/public rehearsal. Each run records
SHA-256 hashes for exactly **16 files**, not a discovered folder tree:

| Class | Exact paths in the prepared source |
|---|---|
| Wiki controls | `wiki/index.md`, `wiki/log.md` |
| Wiki content | `wiki/concepts/vent-choice.md`, `wiki/entities/aster-desk-lab.md`, `wiki/synthesis/vent-setting.md`, `wiki/sources/trial-a.md`, `wiki/sources/trial-b.md` |
| Raw records | `raw/trial-a.md`, `raw/trial-b.md` |
| Project brief | `projects/vent-repeat/brief.md` |
| Invented binary asset | `raw/assets/invented swatch.bin` |
| Inert public machinery | `templates/source.md`, `instructions/wiki-contract.md`, `local-framework/opencode.example.json` |
| Notices | `LICENSE`, `THIRD_PARTY_NOTICES.md` |

The first ten files come from the existing hand-authored contract fixture. The
asset is a short invented byte string containing non-text bytes, not real media.
Machinery/notices are per-file copies from this public repository. The config
example stays inert under `local-framework/`, not an active `.opencode/` folder.

Only harmless synthetic exclusion markers are created for `.obsidian/`, `.env`
and an unrelated file. They are not adopted into the backup. Reserved settings,
Git and credential-like path components are refused before file reads. **Filename
rules are not secret detection:** the fixed, reviewed public allowlist is what
makes this rehearsal safe. No real credential file is opened to decide exclusions.

## Procedure exercised

1. Prepare a frozen source and approve its exact relative-path/hash map. Keep a
   canonical `approved-manifest.json` outside the snapshot; do not take the
   snapshot's own possibly modified manifest as the authority for restoration.
2. Create a new, separate snapshot root. Copy only approved files into `files/`,
   exclusively create files, verify all copied hashes, then write `manifest.json`
   last. Existing/partial snapshot directories are not overwritten or resumed.
3. Restore from the snapshot into a **third, new root**, not the source or the
   snapshot. Compare the snapshot record with the separately retained approval
   and verify every payload before creating the restore root. A renamed/missing
   original source must not cause fallback to current source bytes.
4. Compare restored paths/hashes, binary asset bytes, and wiki structure. The
   restored graph matches the source fixture: five content pages, two controls,
   18 directed content links, no error/unsupported/unchecked diagnostics.
5. Rehearse a partial operation on the restored copy. A simulated human index
   addition makes the original multi-file recovery preconditions fail **before
   any file is changed**. The operator then preserves that index and narrows
   recovery to the interrupted concept page only. Restore from backup—not a
   subsequently changed source—and append a separately approved correction log.
   Unrelated work and the prior log prefix remain intact.

These are actual temporary filesystem operations, not merely schema assertions.
They are operator/test-harness operations, **not native-role edits** or proof of
real human concurrency. The native interruption tests are separate evidence.

## Checks and actual results

```sh
# Use an approved temporary location outside the checkout and any vault.
# This environment's pre-existing /tmp/opencode was used for the observed run:
TMPDIR=/tmp/opencode python3 -m unittest discover -s tests -p 'test_r6_backup_restore.py' -v
TMPDIR=/tmp/opencode python3 -m unittest discover -s tests -v
git diff --check
```

All **six R6 tests** and all **82 offline tests** pass. The R6 tests verify:

- Full restore and exclusive recreation of a missing asset with the original
  source path unavailable; separately retained approval is reloaded from disk.
- Selected recovery using backup bytes even when the source has a newer,
  different value. Backup/restore themselves leave source bytes alone; intentional
  source/human edits in the tests are explicitly simulated between operations.
- Corrupt payload refusal; altered manifest refusal with otherwise intact
  payloads; refusal when both payload and bundle manifest are rewritten to agree
  but differ from the retained approval. No restore root is created on failure.
- Source/snapshot/destination link and hardlink refusal, traversal and excluded
  path refusal, root-overlap/collision refusal and unapproved recovery-path refusal.
- Drift anywhere in the recovery plan prevents its first write. Preservation is
  an explicit replan that omits the human-edited path, not resetting the human edit
  or refreshing its hash merely to overwrite it.
- A failed backup copy leaves no complete manifest and cannot be restored or
  overwritten by a blind retry; a fresh bundle is required.
- A failed replacement preserves that target and removes its temporary file.
  A failure on the second file leaves the first restored and the second untouched:
  the old plan then refuses, and a new remaining-path-only plan completes recovery.

Test directories and generated manifests/backups are removed on exit. No backup,
private-derived fixture or transcript is committed. Hashes depend on the current
approved public file revisions; they are calculated and compared inside each run.

## Limits and private-use gate

This is not a production backup CLI, archive format commitment, scheduler or
general merge/rollback engine. Roots must be frozen against outside writers;
path preflight is not race-proof filesystem isolation. Fixture bytes are small
and held in memory. Restore files use owner-only modes, not preserved ACLs,
ownership, timestamps or extended attributes. Replacement is per-file, not
transactional across a batch. Failed new copies can leave partial directories;
inspect them rather than blindly retrying. No power-loss/fsync durability claim
is made.

The three roots are on the same temporary filesystem and are deleted after the
test: they provide **no independent storage, encryption, retention or disaster
recovery for the real vault**. Hash verification also depends on retaining a
trusted approval record; it is not a signature or protection if that record and
the backup are both replaced.

Next is **R6A policy approval**, before any private backup/restore or P3 install:

- Existing backup mechanism and approved destination/access, separate from sync.
- Exact private file scope and assets, with `.obsidian/` and credentials excluded
  from agent-driven backup. Secret/settings recovery stays owner-managed.
- Encryption and key recovery, retention/frequency and acceptable data-loss window.
- Approved alternate private restore location and verification procedure.
- Separate path/provider/first-source approval for eventual integration; no vault
  Git initialization, remote, publication or model exposure is implied.

Prefer a suitable existing backup mechanism once the owner identifies it. Do not
promote these internal test helpers to private use without that review and a real
restore drill. Owner content judgment for R8 remains a separate record.

## Upstream guidance

The pinned [backup guide](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/09-maintenance/backups-and-portability.md)
and [privacy guide](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/09-maintenance/privacy-and-secrets.md)
inform this procedure. Their private-Git/monthly-archive suggestions are not
adopted as owner policy. PLAN.md's explicit approvals, secrets boundary and
path-specific recovery rules take precedence over broad rollback examples.
