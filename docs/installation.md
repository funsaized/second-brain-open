# Install or upgrade the framework in a separate vault

Use this guide to copy or merge selected roles, skills, the contract and templates
while preserving an existing vault and its primary agent. Copying definitions
does not verify the runtime or authorize source processing. Those checks follow
as separate steps.

This is a manual procedure, not an installer or a directory-sync operation.
For a first look without configuration or model calls, start with the
[read-only tutorial](tutorial.md).

## Before you copy files

- Keep this public checkout separate from the destination vault.
- Obtain approval for exact destinations, any merges, and the intended source.
- Before writes, approve the backup scope/retention, back up affected files and
  verify their restoration in a separate location. Check existing local evidence
  rather than assuming this work must be repeated. An explicit new-file-only
  exception covers only its named paths; the public rehearsal and earlier
  greenfield waiver are not a backup of your existing notes or settings.
- Choose and approve provider/model exposure, native authentication, session
  retention and budget before a live model reads source content.
- Prepare an isolated copy of the approved corpus. Do not mount the personal
  vault, home, settings, credential stores or personal `AGENTS.md` into it.
  Review any native authentication mechanism separately: it stays outside the
  agent-readable corpus and must not grant the role access to credential files.

The model-free Python tools need no OpenCode configuration. Agent operations
need OpenCode and a profile whose actual behavior has been checked. Public
native evidence covers OpenCode `1.18.32`; Linux namespace probes used Bubblewrap
`0.12.0`. These observations are not a compatibility guarantee for other versions
or platforms. Verify the actual environment before exposing data.

## 1. Define the file manifest

Record the chosen public commit locally:

```sh
git rev-parse HEAD
```

For each selected file, record its public source path, SHA-256, resolved local
destination, action, and the destination's preimage hash or absence. Include the
backup location or applicable scoped exception. Keep this manifest private; do
not put real destination paths or personal context in this checkout.

### File manifest

Destinations below are relative to the separately approved vault root. The table
is the distribution allowlist, not permission to overwrite every destination.

| Public source | Proposed local destination | Treatment |
|---|---|---|
| `framework/instructions/wiki-contract.md` | `.opencode/instructions/second-brain/wiki-contract.md` | Supplemental contract; never replace root `AGENTS.md`. |
| `framework/templates/source.md` | `templates/second-brain/source.md` | Copy new or review the local merge. |
| `framework/templates/concept.md` | `templates/second-brain/concept.md` | Copy new or review the local merge. |
| `framework/templates/entity.md` | `templates/second-brain/entity.md` | Copy new or review the local merge. |
| `framework/templates/synthesis.md` | `templates/second-brain/synthesis.md` | Copy new or review the local merge. |
| `framework/templates/index.md` | `templates/second-brain/index.md` | Template, not a replacement for a live index. |
| `framework/templates/log.md` | `templates/second-brain/log.md` | Template, not a replacement for a live log. |
| `framework/templates/project.md` | `templates/second-brain/project.md` | Brief template; no automatic project scaffolding. |
| `framework/agents/sb-ingestor.md` | `.opencode/agents/sb-ingestor.md` | Explicit ingest role; needs reviewed local grants. |
| `framework/agents/sb-researcher.md` | `.opencode/agents/sb-researcher.md` | Explicit query role; remains read-only. |
| `framework/skills/second-brain-ingest/SKILL.md` | `.opencode/skills/second-brain-ingest/SKILL.md` | Ingest procedure and coverage review. |
| `framework/skills/second-brain-query/SKILL.md` | `.opencode/skills/second-brain-query/SKILL.md` | Sourced-answer procedure. |
| `LICENSE` | `.opencode/second-brain/LICENSE` | Retain the downstream notice. |
| `THIRD_PARTY_NOTICES.md` | `.opencode/second-brain/THIRD_PARTY_NOTICES.md` | Retain upstream notices and the adaptation map. |

Do not copy this repository's `AGENTS.md`, fixtures or development history into
the vault. Run `scripts/link_check.py`, `scripts/vault_stats.py` and
`scripts/chat_export_to_md.py` from this checkout as an operator. They need no
agent shell grant or script installation in the vault.

The separate [configuration example](../framework/opencode.example.json) is an
inactive deny-default fragment for isolated setup. It is not part of the
14-file payload, a ready-to-use profile or an isolation mechanism. Do not copy it
over an ordinary `opencode.json`: it deliberately permits no tools or providers,
and empty collections do not erase inherited configuration.

## 2. Copy or merge only the approved files

Pause edits to affected paths. Reject traversal, symlinks, linked ancestors and
hardlinks; use regular, explicitly named files rather than directories or globs.
Verify each preimage immediately before writing.

- For a new destination, create it exclusively. A collision requires review.
- For an existing destination, compare the old installed revision, the new
  public revision and local contents. Approve a per-file merge that preserves
  local customizations.
- Record and verify postimage hashes. Keep the preimages needed for recovery.

Do not replace root instructions, alter Obsidian settings or change the default
agent. Copying these roles does not restrict or confine that existing default
agent; their rules apply when the named role is actually selected.
No recursive copy, reverse sync, blanket overwrite or `rsync --delete` is
part of this procedure. On drift, stop and reconcile the affected file.

## 3. Prepare and verify the scoped runtime

Follow [Prepare the isolated profile](manual-loop.md#1-prepare-the-isolated-profile).
The operation manifest must name the actual contract, index, source and candidate
page paths. Merely placing the contract under `.opencode/instructions/` does not
make it an automatic global instruction; give the role its permitted path.

Keep the default-deny rules. Grant exact reads for the operation. Only after a
patch is approved should the ingestor receive per-file ask-to-edit grants. The
researcher must not gain write access. Native permissions do not prevent an
allowed filename from referring through a symlink, and preflight alone does not
freeze files against concurrent replacement. Use appropriately confined,
regular-file inputs and preserve that boundary for the whole operation.

Review authentication separately from source access. Stop if its bootstrap adds
unreviewed tools, plugins or provider routes. Inspect only a sanitized, allowlisted
effective summary, never a complete configuration or environment. Account for
inherited instructions, MCP, auxiliary model routes and local retention. Model
step/request targets are not a guaranteed spend ceiling.

Running with the personal vault as the working directory is a different,
separately reviewed choice. Vault and global instructions may be sent to the
provider regardless of read-tool denials. Do not substitute that mode for the
isolated procedure without explicit acceptance of the exposure and the applicable
permission checks.

Quit and restart OpenCode after changing loaded configuration, agents or skills.
Verify the actual named role, designated skill, provider route and permissions.
Running sessions may retain old definitions. Missing-role fallback is not fixed;
do not infer correct loading from process exit code alone. Verify actual resources
without restarting the owner-waived missing-resource negative campaign.

**Checkpoint:** copied files match the approved manifest, local work is preserved,
and the selected runtime has been verified. Copying definitions alone establishes
neither runtime confinement nor successful ingestion.

## 4. Ingest one approved source, then ask a sourced question

Continue with [Manual ingest/query operation](manual-loop.md). Select the role
directly with a vetted request. `/sb-ingest` and `/sb-ask` are intentionally not
distributed because their tested command preprocessing was unsafe.

Review the complete Markdown proposal and its coverage, then apply only the
approved changes. Check evidence, index/log consistency and links. A read-only
query should cite the consulted pages and sources and disclose what is not covered.

Do not treat copying files, a checker pass or a model's success statement as
owner content acceptance. Keep real captures, notes, reports, receipts and
backups outside this public repository.

## Upgrade or recover a previous installation

For an upgrade, repeat the manifest and three-way review using the recorded
installed revision. Never assume local files still match their original copy.

For rollback, obtain approval for the exact paths. Restore preimages only when
current hashes match the installed postimages. Remove a newly created file only
with explicit approval and a matching hash. If a path drifted, preserve human
work and replan; never broad-reset or recursively delete a vault tree.

The [distribution rehearsal](../tests/test_scope_and_distribution.py) exercises
synthetic copy/collision/rollback behavior. The [backup/restore report](backup-restore.md)
documents a separate synthetic recovery rehearsal. Neither is a production backup
CLI, authorization to run internal test helpers on a vault, or proof of a private restore.

## Related documentation

- [Why evidence, notes and project work are separate](how-it-works.md).
- [Managed-wiki contract](../framework/instructions/wiki-contract.md).
- [Documented native behavior and failures](native-acceptance-trials.md).
- [Current public delivery status and historical checkpoints](../PLAN.md#current-delivery-status).
