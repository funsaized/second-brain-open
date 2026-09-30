# How the knowledge workflow fits together

second-brain-open separates captured evidence, maintained knowledge and project
work. OpenCode supplies the model and tools. This repository supplies the worker
roles, the operator, the contract, templates and checks that run them.

```text
URL ---> operator capture (no model: main content + provenance) ---> raw/
                                                                       |
capture in raw/  (or existing source notes, for a compile)  <----------+
        |
        v
operator stages a copy  --->  sb-ingestor reads it and proposes pages
        |                                   |
        v                                   v
operator checks the proposal (paths, drift, checker), applies it, keeps undo
        |
        v
wiki pages, index and a partial log record  --->  owner review: sampled / full
        |
        +----> operator stages a query ---> sb-researcher answers with citations
        |
        +----> project work uses knowledge; durable findings may be compiled back
```

## Evidence is not the same as a note

`raw/` preserves the captured source version. A source note explains that
artifact and identifies where its claims came from. Editing the explanation does
not authorize editing the original. A changed source gets distinct provenance.

A **source locator** identifies a passage within a source: a heading, page,
timestamp or preserved excerpt. A hash identifies captured bytes; it does not
identify a passage or establish truth. A link checker can check a destination
without checking whether the evidence supports a statement.

## Source notes and concept notes serve different jobs

| Page type | Reader question | Relationship to evidence |
|---|---|---|
| Source | What does this particular artifact teach or claim? | Retains its identity, useful detail, qualifications and locators. |
| Concept | What is this idea, how does it work, and where does it apply? | Connects relevant source claims, examples, disagreements and open questions. |
| Entity | Who or what is this person, organization, product or tool? | Records source-backed identity and mentions. |
| Synthesis | What can we conclude about a question across these sources? | Separates evidence, disagreement and the current interpretation. |

One source can support several concepts, and one concept can use several
sources. A concept may begin with one source, but it should not imply independent
corroboration. Create pages for a useful explanation or relationship, not merely
to fill every template. Source-to-concept/entity links are reciprocal where
those relationships exist.

For learning material, a source note may retain a directory tree, worked example
or full code block. A comparison should retain the benefits as well as the costs.
There is no universal claim count or required length. The model drafts according
to the agreed purpose; a coverage review makes consequential omissions visible.

The [content-preservation contract](../framework/instructions/wiki-contract.md#content-preservation)
defines that rule. It does not make the model an infallible editor or turn copied
code into tested software.

## Knowledge and projects have different lifecycles

The wiki organizes reusable knowledge by idea. Projects organize work toward a
goal, including inputs, work in progress, outputs and feedback. A project can
start with one brief; unused folders are not a setup requirement.

A project may reference wiki knowledge. Its drafts and generated outputs do not
automatically become established knowledge. Promotion is a separate proposal
that preserves evidence, context and limitations. The
[project brief template](../framework/templates/project.md) and
[handoff contract](../framework/instructions/wiki-contract.md#project-handoff)
describe that boundary.

## Operators and workers

Two tiers of agent do the work.

- **Workers** (`sb-ingestor`, `sb-researcher`) read sources and wiki pages and
  produce proposals or answers. They are the only agents that read untrusted
  source text, so they get the least access. Their role files deny every tool.
  When launched, they get exact read grants on a staged copy of the wiki, plus
  grep and glob inside that copy, and nothing else: no edits, shell or network.
  The copy holds only files they may read, so search can't reach anything else.
- **The operator** is your primary agent, using the `second-brain-operator`
  skill, or you at a terminal. It stages each operation, launches a worker,
  checks the result mechanically and applies it. It never edits pages itself;
  the operator CLI is the only writer, and only under `wiki/`.

Web pages and PDFs enter the same way. When you give the operator a URL, the
CLI fetches the document itself, with no model reading it. It keeps a web
page's main content, or a PDF's original plus page-marked text (OCR for scans,
split when long), with provenance. Untrusted page text therefore reaches only the sandboxed
worker, never your primary agent, which holds shell access. Upstream
second-brain-os instead lets one agent fetch, read and write everything. That
is simpler, but a page's injected instructions would then run with full vault
access.

The split puts the trust where it can be checked. A hostile source can
influence what a worker proposes, but a proposal only reaches the vault after
`apply` confirms:

- the paths are allowed pages
- the page count is within the limit
- no target changed since staging
- the log gains exactly one `partial` record, index entries are merged and
  back-links are appended, never rewritten by the model
- no updated page loses its existing links
- the managed checker passes on the result

Formatting slips and links to pages that don't exist yet are repaired
mechanically, and each repair is reported. Anything that changes what a page
claims goes back to the worker or stops. Every applied operation keeps backups
for `undo`. The staged copy also keeps
the vault's `AGENTS.md`, which holds your personal instructions, out of the
workers' provider context.

This makes ingest autonomous without giving any model standing write access.
What the checks cannot establish is whether each claim is faithful to its
source. That is the owner's review.

## Review is part of the capability

The ingestor reads an approved source and proposes complete pages. The
operator's checks catch metadata and link problems, leftover template
placeholders, pages missing from the index and one-way source links. When a
proposal fails them, the worker gets one chance to revise. Purely mechanical
gaps, such as a missing back-link, the operator repairs itself and reports.

The researcher reads pages and evidence, then answers with citations and
coverage limits. The operator rejects an answer that cites a page the
researcher never opened. It writes no files, including the log. Saving an answer
requires a separate compile operation.

Editorial review asks whether a note is faithful, sufficiently detailed and
useful. Applied operations stay `partial` until the owner records `sampled` or
`full` acceptance. A passing check does not establish every claim's truth or
grant permission to publish.

## Why the public repository stays separate

This checkout contains reusable machinery and invented fixtures. The private
vault contains the owner's captures, notes and project material. Installation
is a one-way copy of framework files, not synchronization between the two.

Native permissions restrict tools, but they are not filesystem isolation. The
staged copy refuses symlinks and hardlinks. Provider exposure, authentication
and local session retention still need your approval, even with sharing
disabled. Slash-command wrappers are withheld because OpenCode's command
preprocessing expands `@file` and shell text before role permissions apply.

## Related documentation

- [Explore an invented wiki without a model](tutorial.md).
- [Install or upgrade the framework](installation.md).
- [Ingest, compile and ask with the operator](operator.md).
- [Reference: CLI, checks and roles](reference.md).
- [Look up the managed-wiki contract](../framework/instructions/wiki-contract.md).
- [Inspect public delivery status and evidence limits](../STATUS.md).
