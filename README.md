# second-brain-open

Reusable OpenCode machinery for a separate Obsidian vault, based on
[second-brain-os](https://github.com/undefined-ui/second-brain-os) at
`347feee87b305b291f7264890e5024db422e3467`.
See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

**Status: P0 baseline verified; P1 contracts and examples delivered.**
Not ready for personal-vault installation. Next is P2: the ingest/query roles,
skills, commands and link checker. The required statistics and chat converter
ports follow in P2A/P2B; they are not optional. See [PLAN.md](PLAN.md).

## Content contract and examples

- [Wiki contract](framework/instructions/wiki-contract.md): four knowledge types,
  source locators, competing claims, index/log maintenance and project promotion.
- [Seven plain-text templates](framework/templates/): no Obsidian plugins needed.
- [Synthetic index](tests/fixtures/contract/wiki/index.md): two invented trial
  records with conflicting recommendations, a concept, entity and synthesis.
- [Synthetic project brief](tests/fixtures/contract/projects/vent-repeat/brief.md):
  consumes wiki evidence; promotion remains a separate approved operation.

Generated metadata uses a flat JSON-value YAML subset. All six wiki types have
common metadata; source and entity fields are documented in the contract.
The append-only log keeps its creation-time header dates, with operation dates
in appended entries. Existing notes are not automatically normalized.
These examples are hand-authored fixtures, **not a demonstrated agent ingest**.

## Current distribution allowlist

No file is currently approved for installation into a personal vault.
Destinations below are candidates, relative to an approved isolated workspace
unless noted. Collision status must be checked locally; every copy/merge is
reviewed. P1 template/contract review does not waive the P3 entry gate.

| Public source | Proposed destination | Action |
|---|---|---|
| `framework/opencode.example.json` | `opencode.json` | Isolated test starting fragment only; review/instantiate, never overwrite |
| `framework/instructions/wiki-contract.md` | `.opencode/instructions/second-brain/wiki-contract.md` | Approved supplemental instruction reference, never root AGENTS replacement |
| `framework/templates/source.md` | `templates/second-brain/source.md` | Copy new or review local merge |
| `framework/templates/concept.md` | `templates/second-brain/concept.md` | Copy new or review local merge |
| `framework/templates/entity.md` | `templates/second-brain/entity.md` | Copy new or review local merge |
| `framework/templates/synthesis.md` | `templates/second-brain/synthesis.md` | Copy new or review local merge |
| `framework/templates/index.md` | `templates/second-brain/index.md` | Template only, not an overwrite of a live index |
| `framework/templates/log.md` | `templates/second-brain/log.md` | Template only, not an overwrite of a live log |
| `framework/templates/project.md` | `templates/second-brain/project.md` | Brief template; no project scaffolding |

Root documentation, license notices, development instructions, tests, and
PLAN.md stay in this public repository. Do not copy its AGENTS.md into a vault.
The example has no roles, read grants, provider, credential, or private path.
It is a deny-default starting fragment, **not an isolation mechanism**. Empty
plugin/MCP/instruction collections do not erase inherited configuration.
No root default agent is changed. Do not activate this fragment in an ordinary
session: it intentionally grants no tools or providers.
P2 roles will grant scoped reads, their designated skill and questions; the
ingestor will additionally ask before approved wiki edits. The research role
will remain read-only. This does not disable ordinary development tools in
the owner's existing OpenCode setup.

## Reviewed install, upgrade, and rollback

1. Pass the phase's gates before copying anything. Real integration additionally
   requires P2/P2A/P2B and R6 backup/isolated-restore proof.
2. In a private local manifest record the reviewed public commit SHA, each
   allowlisted source and its SHA-256, resolved destination, action (copy or
   merge), destination's preimage hash or absence, and private backup location.
   Reject traversal and symlinked sources/destinations/ancestors. Do not use
   directories or globs as manifest entries. No private paths belong here.
3. Pause edits to affected files; verify preimages immediately before each
   write. A collision or changed hash stops that file for owner review.
   Preserve existing root instructions and settings. No blanket overwrite.
4. Copy only individually approved new files. For existing files, review the
   old installed revision → new public revision → local contents, then approve
   a per-file merge. Record postimage hashes and retain local customizations.
5. Quit/restart the isolated OpenCode instance after config changes, inspect
   its sanitized effective policy, and repeat enforcement probes. Existing
   sessions keep old policy. No restart is needed for this inert checkout.
6. Roll back only manifest paths whose current hashes still match installed
   postimages. Restore their private preimages; remove newly created files
   only with owner approval and matching hashes. On drift, preserve human work
   and ask. Never broad-reset, recursively sync, or delete a vault tree.

The synthetic rehearsal in `tests/test_scope_and_distribution.py` preserves
conflicting instructions/config/templates, copies one approved new file,
refuses rollback on drift, and removes only a matching approved postimage.
It tests this manual procedure, not a production installer or a private restore.

## Approved R0 distribution / R1A runtime scope

The owner approved this distribution method and synthetic-only runtime rehearsal
on 2026-09-24, then approved the corpus/permissions distinction and continuing
in logical increments:

- Disposable Linux namespace/container with a clean home/XDG environment;
  mount only runtime dependencies and synthetic test data. No home/vault mount,
  credential import, personal AGENTS.md, or host configuration inheritance.
- Begin network-disabled with no provider and no authentication. Use a local
  deterministic fake provider if needed for tool-enforcement probes. This
  tests runtime behavior, not model quality or successful ingestion.
- No plugins/MCP/custom tools or remote instructions; disable compatibility
  skill/instruction discovery using settings verified for the installed
  release. Disable formatters/LSP, sharing, snapshots, and auto-update.
- Add a disposable deny-default probe role with exact synthetic read grants;
  test allowed reads, forbidden tools/writes, fake sensitive paths, traversal,
  symlinks, and approval rejection. No auto-approval. Later P2 must repeat the
  matrix for the actual named roles and command entry points.
- Inspect only allowlisted effective settings: permissions, selected roles,
  share/snapshot, plugin/MCP presence, instruction paths, formatter/LSP, and all
  provider/model routes. Never print a full effective config or environment.
- Keep runtime artifacts outside this checkout. The test namespace's fixtures
  and sessions disappear on exit; retain only sanitized results. Real data,
  backups and session-retention policy remain separately approved.

### Runtime baseline: actual results (2026-09-24)

Tested OpenCode `1.18.32`, Bubblewrap `0.12.0`, Python 3, in a cleared-environment
network namespace with a fresh home/XDG profile. Read-only `/usr` supplies
dependencies; the executable and probe are single-file read-only mounts.
No host home, vault, settings or credentials are mounted. A deterministic local
fake provider forces calls instead of relying on a model promising refusal.

| Check | Actual result |
|---|---|
| Approved exact read | Pass; source marker returned |
| Fake settings, `.env`, unrelated, traversal, outside reads | Five passes; permission refusal, no forbidden marker in events/provider requests |
| Edit/write/bash/grep/glob/webfetch/task/unapproved skill | Eight passes; runtime rejects calls to unavailable tools |
| Ask-scoped edit | Pass; noninteractive CLI rejects permission request; fixture unchanged |
| Symlink in approved input scope | Pass at **preflight**; no runtime/provider call |

All 16 cases pass. Each native case uses a fresh OpenCode process. Hash checks
cover the five named synthetic files' contents, not every runtime/session file.
The probe checks share/snapshot, formatter/LSP, plugin/MCP/instruction absence
and main/auxiliary fake-model routing without printing unrestricted config.
No live provider is involved; these tests do not prove ingestion quality.
The ask-edit case verifies rejection, not interactive approval persistence.
Never select a broad “always” grant; P2 must inspect the actual offered patterns
and prove that the named roles stay scoped after approved edits.

The original path mismatch is resolved: `read` asks on **worktree-relative**
paths. `debug scrap` reports `/` as this non-Git project's worktree, so the exact
grant is `workspace/wiki/index.md`, not `/workspace/wiki/index.md` or a wildcard.
Do not assume cwd equals worktree. HTTP inspection timed out (even on a health
request); we use the working CLI instead and do not claim the server was fixed.
OpenCode can exit 0 on tool denial, so assertions inspect actual tool outcomes.

### Boundary: permissions are not a filesystem sandbox

The initial native symlink characterization **did return denied synthetic data**
through an allowed filename. This runtime behavior has not been fixed upstream.
The adopted profile rejects symlinked files/ancestors, hardlinks, traversal and
non-files before launch; `validate_scope` in the probe and its unit tests make
that check explicit. It is not a lock against concurrent replacement.

For real use, the owner must prepare and freeze a regular-file-only approved
corpus with no outside writers, expose inputs read-only where practical, and
never mount personal settings/credentials or the vault/home wholesale. Tool
permissions then restrict actions within that isolated corpus. A preflight
followed by an ordinary mutable shared folder is **not** an acceptable substitute.
The named-role/command matrix and live-source/provider/backup gates still apply.

## Checks

```sh
python3 -m unittest discover -s tests -v
git diff --check
# Manual Linux runtime probe; requires the reviewed OpenCode release and bwrap:
python3 tests/runtime_read_probe.py
```

The offline suite has 13 passing checks: distribution, scope preflight,
synthetic copy/rollback, and P1 schema/link/claim fixtures. The separate runtime
probe exits 0 on acceptance, 1 on a failed check, 2 on setup/runtime failure.
No unisolated fallback is provided. P2 must repeat and extend these checks for
the actual ingest/query roles, designated skills, commands, interactive approvals,
source injection and recovery. No file here has been installed into a vault.
