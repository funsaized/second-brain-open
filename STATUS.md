# Status

> Current state of the public machinery, updated 2026-10-01. How it got here is
> in the [changelog](docs/changelog.md); what is planned in [PLAN.md](PLAN.md);
> proposals in [BACKLOG.md](BACKLOG.md); decisions in
> [docs/decisions.md](docs/decisions.md); what the machinery guarantees in
> [guarantees and limits](docs/guarantees-and-limits.md). A deployment's own results stay in
> that deployment's records, not here.

## Delivered

| Area | What works | Where |
|---|---|---|
| Distribution (P0) | MIT licence, upstream notices and adaptation map, per-file install and upgrade, the primary-agent permission profile | [Installation](docs/installation.md), [notices](THIRD_PARTY_NOTICES.md) |
| Contract (P1) | Page contract, seven templates, claim locators, contradictions kept side by side, owner acceptance levels, index theme headings | [Contract](framework/instructions/wiki-contract.md) |
| Operator and workers | `stage`, `run`, `revise`, `apply`, `undo`: deny-by-default workers in a staged copy with exact reads plus search, proposals applied only after checks, mechanical repairs, undo | [Operator guide](docs/operator.md), [reference](docs/reference.md) |
| Capture | Web pages by main content; PDFs with page markers, OCR, rendered figures and parts; `pending` catch-up | [Operator guide](docs/operator.md#ingest-a-pdf) |
| Long documents | Resumable background `series`; `series --plan` for chapter pages built from part notes | [Long documents](docs/operator.md#organize-a-long-document-by-chapter) |
| Answers | Index-first researcher with search; citations must be pages it read | [Ask a question](docs/operator.md#ask-a-question) |
| Acceptance | `accept` records the owner's stated review for every operation still waiting | [Record your review](docs/operator.md#record-your-review) |
| Generated index (P6) | `wiki/index.md` rebuilt from page `summary`, `theme`, `gaps` and `part_of` after every operation; workers read a bounded per-operation `catalog.md`; duplicate-page guard; `migrate-index` and `rebuild-index` | [Reference](docs/reference.md#generated-index) |
| Robustness | Exact read ranges for large required files, drift guards only on rewritten pages, startup-stall relaunch, retry policy for series and plans | [Reference](docs/reference.md) |
| Checker | Metadata, canonical links, placeholders, index coverage, source ↔ concept reciprocity | [Checker](docs/reference.md#link-checker) |
| Statistics (P2A) | Deterministic page/link statistics, including the knowledge-layer ratio and links by page type | [Statistics](docs/vault-stats.md) |
| Chat export (P2B) | Local conversion of supported exports with omission reporting | [Chat exports](docs/chat-exports.md) |
| Backup rehearsal (R6B–C) | Synthetic manifest backup and restore | [Backup and restore](docs/backup-restore.md) |
| Evaluation (optional) | Scored researcher runs on a staged wiki copy, index-only or with search | [Evaluation](docs/researcher-evaluation.md) |

## Verification

```sh
python3 -m unittest discover -s tests
git diff --check
```

The offline suite uses synthetic fixtures and makes no model calls. Each
change's result is recorded in its dated [changelog](docs/changelog.md) entry.

| Evidence class | What it establishes | Where |
|---|---|---|
| Offline suite | Static, CLI and guard behaviour on invented fixtures | `tests/` |
| Runtime probes | OpenCode loading, read and search boundaries with a fake provider, by version | `tests/live/runtime_*_probe.py`, [trials](docs/native-acceptance-trials.md) |
| Live synthetic runs | Worker behaviour on invented vaults, by date and OpenCode version | [Trials](docs/native-acceptance-trials.md), [synthetic acceptance](docs/synthetic-acceptance.md) |
| Owner acceptance | Whether a deployment's content is accepted | That deployment's `wiki/log.md`, never this repository |

## Outstanding, withheld and deferred

1. **P6 evaluation.** The deployment is migrated and compiles pass on the
   catalog; the researcher evaluation still needs a rerun on the catalog flow.
2. **P4/R5 project round trip.** Wiki context into a project and durable
   findings back, demonstrated with a real project when one needs it (backlog
   F5).
3. **Withheld: `/sb-ingest` and `/sb-ask`.** Command preprocessing exposed
   denied content and evaluated shell-like arguments, so the wrappers are not
   distributed. Use the operator.
4. **Deferred by need:** optional tracks T1–T5 (see the
   [planning history](docs/archive/planning-history.md)), extra agents, skills
   or wrappers, scheduling and publication.
5. **Owner-local:** deployment records, backup policy and restore proof,
   content acceptance.

## Closed without further work

- **Native variants for contradiction and ambiguous-link handling.** They keep
  their driver-applied and checker evidence; the operator's checks and repairs
  now cover these cases in daily use.
- **Missing-skill and nonexistent-agent negative scenarios.** Waived; the
  operator verifies the role and skill with `opencode debug` before every run,
  and the roles probe passes on 1.18.33.
- **The bootstrap metadata-audit caveat.** It concerned the first add-only
  install; later installs are per-file clean upgrades with backups.
- **Install planner (B3) and offline CI (E3).** Declined by the owner.
