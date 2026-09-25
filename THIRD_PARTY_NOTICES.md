# Third-party notices

This project builds on [second-brain-os](https://github.com/undefined-ui/second-brain-os)
at revision `347feee87b305b291f7264890e5024db422e3467`.
Original downstream work is licensed under the root MIT LICENSE.
Linked articles, chat exports, and other source material retain their own
licenses; neither project's MIT license grants rights to that content.

## Source and adaptation map

| Downstream file | Pinned upstream source | Use / changes |
|---|---|---|
| `PLAN.md` | Paths enumerated in its Upstream Inventory and Research Coverage | Research synthesis and proposed adaptations; not an installed catalog |
| `README.md` | `vault-template/README.md`, root `README.md` | Setup concepts replaced by an inert, approval-gated, one-way distribution procedure |
| `THIRD_PARTY_NOTICES.md` | `LICENSE` | Complete notice reproduced below, without adding a holder |
| `framework/instructions/wiki-contract.md` | `vault-template/CLAUDE.md`, `vault-template/projects/README.md`, and the four knowledge templates below | Reconciles schema, claim locators, unknown provenance, canonical paths, control types, isolated input scope and approved project promotion |
| `framework/templates/source.md` | `vault-template/templates/source.md` | Adds capture/archive fields and per-claim locators; unknown values explicit |
| `framework/templates/concept.md` | `vault-template/templates/concept.md` | Preserves support/opposition/questions; canonical source links and locators |
| `framework/templates/entity.md` | `vault-template/templates/entity.md` | Documents kind and source-backed identity/mentions |
| `framework/templates/synthesis.md` | `vault-template/templates/synthesis.md` | Separates source claims, author views and inference; preserves disagreement |
| `framework/templates/index.md` | `vault-template/wiki/index.md` | Common metadata and explicit control type; actual pages only, plain-text gaps |
| `framework/templates/log.md` | `vault-template/wiki/log.md` | Append-only dated records with changed paths, verification and partial/completed status; immutable header dates |
| `framework/templates/project.md` | `vault-template/projects/example-project/CLAUDE.md`, `vault-template/projects/README.md` | Lightweight owner-maintained brief; optional artifact folders and explicit reviewed promotion; no wiki type |
| `framework/agents/sb-ingestor.md` | `agents/ingestor.md` | Native primary role and designated skill; operator-preflight/manifest bootstrap; deny-default until exact local grants, approved per-edit requests |
| `framework/agents/sb-researcher.md` | `agents/researcher.md` | Native primary read-only role, operator-preflight/manifest bootstrap, scoped evidence reads and no delegated/network fallback |
| `framework/skills/second-brain-ingest/SKILL.md` | `skills/second-brain-ingest/SKILL.md` | Complete-read/proposal/approval flow, operator preflight distinguished from model access, source locators, raw immutability, repeat/recovery and honest status |
| `framework/skills/second-brain-query/SKILL.md` | `skills/second-brain-query/SKILL.md` | Index-first evidence retrieval, claim citations, abstention, Read/Not covered, no writes |
| `scripts/link_check.py` | `scripts/link_check.py` | Replaces basename guessing with exact managed paths; validates narrow metadata, reports ambiguity/unsupported forms/unchecked anchors, read-only stdlib CLI |
| `scripts/vault_stats.py` | `scripts/vault_stats.py`, `docs/05-graphs/metrics.md`, `skills/second-brain-metrics/SKILL.md`, `skills/second-brain-graph/SKILL.md` | Required stdlib port: content-only scope, canonical unique edges, explicit degrees/denominators, weak components, stale/unknown concepts, JSON/as-of and read-only reporting |
| `scripts/chat_export_to_md.py` | `scripts/chat_export_to_md.py` | Required stdlib port: explicit selection/dry-run, Claude/simple and ChatGPT active ancestry, preserved roles/text/UTC dates, quoted metadata, omissions, digest versions and no-overwrite descriptor-based writes |
| `docs/chat-exports.md` | `docs/03-ingestion/chat-exports.md`, `skills/second-brain-chat-import/SKILL.md`, `commands/ingest-chats.md` | Replaces direct-to-raw bulk conversion/agent triage with local staging, privacy approval and selected R3/R4 handoff; assistant assertions remain attributed; no wrapper port |

P2A extends the checker's shared scanner/resolver with optional control exclusion
and structured unusable-field diagnostics. Both consumers exclude reserved
instruction files. The statistics runbook documents intentional differences from
upstream rather than treating its numbers as equivalent snapshots.

Include this notice and the downstream LICENSE with any copied framework or
script distribution; placing them in a namespaced notices directory is fine.
Do not install unsafe command candidates: their argument-expansion tests live
only in the synthetic runtime probe, not in the framework's distribution list.

`AGENTS.md`, `.gitignore`, the inactive OpenCode example, and distribution
tests and wholly invented fixture content are original downstream material. Add a row when implementing each
substantial port; proposed files in PLAN.md are not delivered adaptations.
The selected lantern fixture, its acceptance packet and focused missing-resource
runtime checks and native proposal/handoff/recovery trial drivers are original downstream verification,
not new upstream ports. The acceptance packet links pinned OpenCode implementation
evidence for runtime-specific behavior; no OpenCode source is copied into the driver.

## Upstream MIT notice (verbatim)

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
