# second-brain-open

**A manual, source-grounded knowledge workflow for OpenCode and plain Markdown.**

Turn approved sources into useful, linked notes, then ask questions with citations
back to the evidence. The repository provides the ingest/query roles and skills,
page contracts, templates, local conversion tools and read-only checks for that loop.

Keep your notes in a separate private folder and retain your existing primary
assistant. Obsidian can be the editor and viewer; its REST API and community
plugins are not required. The workflow is reviewed and operator-controlled, not
an unattended capture or publishing service.

## What you can do

| Task | Included capability | Guide |
|---|---|---|
| Turn a source into knowledge | Complete-source reading, full Markdown proposals, useful source/concept/entity/synthesis pages, provenance and coverage review. | [Ingest and query](docs/manual-loop.md) |
| Ask a question of the wiki | A read-only researcher follows approved pages and evidence, cites supporting passages and names coverage gaps. | [Sourced-query operation](docs/manual-loop.md#2-invoke-the-role-directly-not-a-slash-wrapper) |
| Bring in selected chat history | Local conversion of supported Claude, simple-message and ChatGPT branch exports, with versioned files and omission reporting. No model calls during conversion. | [Convert and review exports](docs/chat-exports.md) |
| Check a managed wiki | Read-only metadata and canonical-link validation, plus leftover template placeholders, pages missing from the index and one-way source links. Explicit errors and unsupported/unchecked cases. | [Checker reference](docs/manual-loop.md#checker-contract) |
| Measure answer quality | Opt-in live evaluation of the researcher on a staged copy of your wiki: index-first reads, citations it actually read, expected pages and abstention. | [Evaluate the researcher](docs/researcher-evaluation.md) |
| Understand the wiki's structure | Reproducible page/link counts, components, orphans, stale concepts and date diagnostics. No automatic repairs. | [Calculate statistics](docs/vault-stats.md) |

Ingestion maintains the index and append-only log alongside approved page changes.
Project briefs can consume wiki knowledge; promoting project findings is a separate
reviewed decision. No particular folder tree, optional learning track or extra
agent catalog must be installed to use the core workflow.

## Start here

**New to this approach?** Follow the [read-only tutorial](docs/tutorial.md).
Trace a claim through an invented wiki and run the checks. It needs Python 3,
uses no provider credentials and changes no notes.

**Ready to use your own vault?** Follow [installation and upgrades](docs/installation.md),
then [operate one approved ingest and sourced query](docs/manual-loop.md).
The supplied roles deny access until exact local grants and the runtime are prepared.

**Only need a command-line tool?** Use the [chat converter](docs/chat-exports.md),
[link checker](docs/manual-loop.md#checker-contract) or [statistics tool](docs/vault-stats.md)
directly. These Python standard-library tools do not require OpenCode or Obsidian.

## Documentation

Choose the reader job, rather than working through development phases.

### Learn by doing

- [Explore a source-grounded wiki](docs/tutorial.md): follow evidence, inspect a
  disagreement and check the same synthetic corpus without a model.

### Complete a task

- [Install, upgrade or recover framework files](docs/installation.md).
- [Run an approved ingest and read-only query](docs/manual-loop.md).
- [Convert chat exports, review them and select a conversation](docs/chat-exports.md).
- [Calculate managed-wiki statistics](docs/vault-stats.md).
- [Evaluate the researcher's answers on your wiki](docs/researcher-evaluation.md).

### Look up the contract

- [Wiki types, metadata, evidence and links](framework/instructions/wiki-contract.md).
- [Content-preservation rules](framework/instructions/wiki-contract.md#content-preservation).
- [Owner acceptance levels](framework/instructions/wiki-contract.md#owner-acceptance).
- [Seven page and project templates](framework/templates/).
- [Distribution file manifest](docs/installation.md#file-manifest).
- [Checker syntax, exit codes and limits](docs/manual-loop.md#checker-contract).
- [Statistics definitions](docs/vault-stats.md#what-is-counted) and
  [supported export shapes](docs/chat-exports.md#supported-synthetic-shapes-and-fidelity).

### Understand the design

- [How the workflow fits together](docs/how-it-works.md): sources versus concepts,
  raw evidence, project work, review and the public/private boundary.
- [Why statistics differ from upstream reports](docs/vault-stats.md#comparing-with-upstream-or-older-snapshots).

## Operating boundaries

- Keep private notes, exports, credentials, settings and receipts out of this
  repository. Ignore rules are not a security boundary.
- Approve source/provider exposure and exact changed paths. Preserve raw captures,
  local edits and the existing default agent; do not grant blanket approval.
- Native tool permissions are not filesystem isolation. Prepare and verify an
  appropriately confined runtime before exposing private data.
- Invoke the named roles directly. `/sb-ingest` and `/sb-ask` are withheld because
  tested command preprocessing could bypass the intended argument boundary.
- Treat copied examples as source material, not commands to run. A valid link,
  copied code block or passing test does not establish factual correctness.

The [installation guide](docs/installation.md) and [manual runbook](docs/manual-loop.md)
explain these requirements in execution order. There is no automatic installer,
global configuration replacement, scheduled writer or publication step.

## Verification and development

From the repository root:

```sh
python3 -m unittest discover -s tests
git diff --check
```

The offline suite currently has **93 passing tests**. It uses synthetic fixtures
and does not make model calls. Live native trials require separate opt-in setup
and approvals; they are not part of this command.

For implementation status and evidence, rather than user instructions, see:

- [Current delivery status and remaining work](PLAN.md#current-delivery-status).
- [Review backlog of proposals](BACKLOG.md).
- [Native synthetic trial results, failures and waivers](docs/native-acceptance-trials.md).
- [Selected-conversation acceptance packet](docs/synthetic-acceptance.md).
- [Synthetic backup and restore rehearsal](docs/backup-restore.md).

These records distinguish shipped tools, static checks, observed native behavior
and owner acceptance. They do not certify a particular private deployment.
Use wholly synthetic fixtures when contributing; never copy private-derived
examples or runtime transcripts into the repository.

## Attribution and license

Adapted from [second-brain-os](https://github.com/undefined-ui/second-brain-os)
at revision `347feee87b305b291f7264890e5024db422e3467`. See [LICENSE](LICENSE) and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for notices and the adaptation map.
Linked third-party material retains its own licensing terms.
