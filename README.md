# second-brain-open

**A source-grounded knowledge wiki that OpenCode maintains for you, in plain Markdown.**

Turn sources into linked notes, build concept pages across them, and ask
questions answered with citations back to the evidence. Ask your primary
OpenCode agent in plain language. It runs sandboxed worker roles that read and
propose, and an operator that checks every proposal before it reaches the
vault.

Your notes stay in a separate private vault, and your existing primary agent
stays in charge. Obsidian can be the editor and viewer; its REST API and
community plugins are not required.

## What you can do

| Task | Included capability | Guide |
|---|---|---|
| Turn a source into knowledge | Hand the operator a web page or PDF URL, or a file in `raw/`. It captures the main content, or a PDF's page-marked text, with OCR for scans and rendered figures the worker reads, with provenance. A sandboxed worker then proposes source, concept and entity pages with claim-level locators. The operator checks and applies them, with undo. | [Ingest a web page](docs/operator.md#ingest-a-web-page) |
| Catch up on captures | Clip pages into `raw/` all week, then ask the operator to ingest everything new, oldest first. | [Catch up](docs/operator.md#catch-up-on-everything-new) |
| Build concept pages | Compile concept, entity or synthesis pages from source notes you already have, with links in both directions. | [Compile concepts](docs/operator.md#build-concept-pages-from-existing-notes) |
| Ask a question of the wiki | A read-only worker follows the index to the relevant pages, cites them and names what the wiki does not cover. | [Ask a question](docs/operator.md#ask-a-question) |
| Bring in selected chat history | Local conversion of supported Claude, simple-message and ChatGPT branch exports, with versioned files and omission reporting. No model calls during conversion. | [Convert and review exports](docs/chat-exports.md) |
| Check a managed wiki | Metadata and canonical-link validation, leftover template placeholders, pages missing from the index and one-way source links. | [Checker reference](docs/reference.md#link-checker) |
| Measure answer quality | Live evaluation of the researcher on a staged copy of your wiki. | [Evaluate the researcher](docs/researcher-evaluation.md) |
| Understand the wiki's structure | Reproducible page/link counts, components, orphans, stale concepts and date diagnostics. | [Calculate statistics](docs/vault-stats.md) |

Every change updates the index and appends a log record. Operations stay
`partial` until you record a sampled or full review.

## Start here

**New to this approach?** Follow the [read-only tutorial](docs/tutorial.md).
It traces a claim through an invented wiki and runs the checks. It needs only
Python 3 and changes no notes.

**Ready to use your own vault?** Follow [installation](docs/installation.md),
then [ingest, compile and ask with the operator](docs/operator.md).

**Only need a command-line tool?** Use the [chat converter](docs/chat-exports.md),
[link checker](docs/reference.md#link-checker) or [statistics tool](docs/vault-stats.md)
directly. These Python standard-library tools need neither OpenCode nor Obsidian.

## Documentation

### Tutorial

- [Explore a source-grounded wiki](docs/tutorial.md): follow evidence, inspect a
  disagreement and run the checks without a model.

### How-to guides

- [Install or upgrade the framework in a vault](docs/installation.md).
- [Ingest, compile and ask with the operator](docs/operator.md).
- [Convert chat exports, review them and select a conversation](docs/chat-exports.md).
- [Calculate managed-wiki statistics](docs/vault-stats.md).
- [Evaluate the researcher's answers on your wiki](docs/researcher-evaluation.md).

### Reference

- [Operator CLI, config, checks and worker roles](docs/reference.md).
- [Link checker syntax, exit codes and limits](docs/reference.md#link-checker).
- [Managed-wiki contract](framework/instructions/wiki-contract.md): types,
  metadata, evidence, links, [content preservation](framework/instructions/wiki-contract.md#content-preservation)
  and [owner acceptance](framework/instructions/wiki-contract.md#owner-acceptance).
- [Page and project templates](framework/templates/).
- [Statistics definitions](docs/vault-stats.md#what-is-counted) and
  [supported export shapes](docs/chat-exports.md#supported-synthetic-shapes-and-fidelity).

### Explanation

- [How the workflow fits together](docs/how-it-works.md): sources versus concepts,
  operators and workers, review, projects and the public/private boundary.
- [Why statistics differ from upstream reports](docs/vault-stats.md#comparing-with-upstream-or-older-snapshots).

## Operating boundaries

- **Keep private material out of this repository.** Private notes, exports,
  credentials, settings and operation directories never go in; ignore rules are
  not a security boundary.
- **The workers never write.** Only the operator's `apply` writes, only under
  `wiki/`, after mechanical checks, and it keeps backups for `undo`. Raw
  captures, instructions and settings are never written.
- **Provider exposure is your approval.** The workers send the pages they read
  to your approved model route. Native tool permissions are not filesystem
  isolation.
- **No slash commands.** `/sb-ingest` and `/sb-ask` are withheld: OpenCode's
  command preprocessing expands `@file` and shell text before role permissions
  apply.
- **Checks aren't truth.** Copied examples are source material, not commands.
  A valid link or passing check does not establish factual correctness.

## Verification and development

From the repository root:

```sh
python3 -m unittest discover -s tests
git diff --check
```

The offline suite currently has **117 passing tests**. It uses synthetic fixtures
and does not make model calls. Live native trials require separate opt-in setup
and approvals; they are not part of this command.

For implementation status and evidence, rather than user instructions, see:

- [Current delivery status and remaining work](PLAN.md#current-delivery-status).
- [Review backlog of proposals](BACKLOG.md).
- [Native trial results, operator runs, failures and waivers](docs/native-acceptance-trials.md).
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
