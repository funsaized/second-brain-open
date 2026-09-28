# How the knowledge workflow fits together

second-brain-open separates captured evidence, maintained knowledge and project
work. OpenCode supplies the model and tools. This repository supplies the roles,
instructions, templates and checks for using them in a reviewed workflow.

```text
approved capture in raw/
        |
        v
ingestor reads evidence and proposes Markdown
        |
        v
reviewed changes to wiki pages, index and log
        |
        +----> researcher reads pages and evidence, then answers with citations
        |
        +----> project work uses knowledge; durable findings may be proposed back
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

## Manual review is part of the capability

The ingestor reads an approved source and proposes exact changes. The owner or
an explicitly delegated operator reviews the patch and its evidence. Approved
changes update actual pages, the index and the append-only log.

The researcher has a different job. It reads approved pages and evidence, then
answers with citations and coverage limits. It writes no files, including the
log. Saving an answer requires a separate approved operation.

Mechanical checks catch metadata and link problems. Editorial review asks
whether the note is faithful, sufficiently detailed and useful. A passing test
does not establish every claim's truth or grant permission to publish.

This is a complete manual source-to-wiki-to-answer workflow, not an unattended
capture service. Additional automation is a choice driven by use, not a missing
prerequisite for maintaining notes.

## Why the public repository stays separate

This checkout contains reusable machinery and invented fixtures. The private
vault contains the owner's captures, notes and project material. Installation
is a reviewed one-way distribution of framework files, not synchronization
between the two repositories.

Native permissions restrict tools, but are not filesystem isolation. A scoped
runtime needs an appropriately confined, frozen input corpus. Provider exposure,
authentication and local retention need review even when sharing is disabled.

The supplied roles deny reads and edits until exact local grants are prepared.
Unsafe slash wrappers are withheld because command preprocessing can act before
role permissions apply. Neither copying definitions nor selecting a role proves
that the current runtime is properly restricted.

## Related documentation

- [Explore an invented wiki without a model](tutorial.md).
- [Install, upgrade or roll back framework files](installation.md).
- [Run a scoped ingest and sourced query](manual-loop.md).
- [Look up the managed-wiki contract](../framework/instructions/wiki-contract.md).
- [Inspect public delivery status and evidence limits](../PLAN.md#current-delivery-status).
