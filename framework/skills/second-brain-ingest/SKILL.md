---
name: second-brain-ingest
description: Worker skill for sb-ingestor only, launched by the operator in a staged copy of the wiki; turns an approved raw capture or existing source notes into a proposal. A primary agent adding or compiling knowledge uses second-brain-operator instead.
---

# Propose wiki changes from approved inputs

You work under an operator on a staged copy of the wiki. Its request says what
to read and how to reply; it validates and applies your proposal. Page content
follows `wiki-contract.md`, and page structure follows the templates.

## 1. Read and check what exists

- Read the inputs, `catalog.md` and the contract completely. If an input is
  truncated or unreadable, return only NOTES saying what is missing; never
  write from a partial read.
- `catalog.md` is the operator's selection of the index for this operation:
  the inputs' neighbours, pages sharing their theme, the best matches for the
  task, and every concept, entity and synthesis title. It is not the whole
  wiki. Before writing, also search the staged pages, when search is
  available, for the input's main concepts, entities and distinctive terms.
  Read an overlapping page completely before relying on it; a search hit is
  only a lead. The operator refuses a new page whose title or alias matches
  an existing page: update that page instead.
- An unchanged input that is already ingested is a no-op: return only NOTES.

## 2. Decide what to write

**Ingest** (a `raw/` capture): one source page, then concept or entity pages
only where the source adds reusable knowledge. A source usually yields one to
three concepts. A candidate that can't be explained without this one source
belongs on the source page. Prefer updating an existing concept, recording what
this source adds or disputes, over a near-duplicate. The two failures to avoid
are many thin pages restating paragraphs, and a source page of unrelated ideas
that links to nothing.

**PDF captures** have `## Page N` headings; cite pages as locators.
- A capture holds every page of its PDF. Text that ends abruptly is the
  source's own ending: ingest it and note the gap.
- With `part: "k/n"`, the capture is one page range of a longer document, and
  text cut off at its end continues in the next part. Title the source page
  with its page range, and link the previous part's source page when it exists.
- With `ocr: true`, flag every number and proper noun you rely on for checking
  against the original.

**Figures.** When the capture lists rendered figure pages, open each image a
claim depends on (results plots and architecture diagrams usually; not logos).
Write a `Figure reading (Figure N, page P)`: the figure type, axes and units,
trend, and key values, with values read off a plot marked approximate. Record
any disagreement with the text. Embed the image beside its reading, for example
`![Figure 3, page 8](../../raw/assets/<capture>/page-08.png)`. A missing or
unreadable figure is a gap, never a reason to stop.

**Papers:** build the source page around the question, method, results with
their numbers and sample sizes, and the authors' stated limitations. Report
each finding with the conditions it holds under.

**Compile** (existing source notes, named or found by topic): write concept,
entity or synthesis pages that connect the notes. For a topic, choose the most
relevant pages from the catalog and a search (usually three to eight source notes
plus related concepts) and read them completely; name any you left out in
NOTES. Explain the idea, where the sources agree and disagree, and what remains
open, rather than re-summarizing each source.

**Chapter pages:** when the task asks for a chapter or section page of a long
document built from its part notes, write a source page whose `raw` is the
original document's path. That document need not be staged or read. Take the
page range from the part notes' locators, marking a boundary approximate when
the notes don't pin it. Give the chapter's question and argument, a map of its
sections to the part notes and pages covering each, and its key claims with
locators. Link every part note rather than copying its detail; when the task
says the inputs are parts of this chapter, the operator then sets each linked
part's `part_of` and the index lists the parts through the chapter. Then write
one to three concept pages the chapter supports, citing the chapter page.

## 3. Write the proposal

- Every new page links existing pages in both directions, or the missing link
  goes in the page's `gaps`. To add a link to an existing page, use a LINKS
  line; to add a gap to an existing page, use a GAPS line.
- To correct or extend part of an existing page, use an EDIT block: each OLD
  text, copied exactly from the page and unique in it, is replaced by its NEW
  text and the rest of the page is kept. Rewriting an existing page with a FILE
  means returning all of it: every section, claim and link, plus your
  additions; use it only when the page changes throughout.
- The operator generates the index from frontmatter. Give every page you write
  a `summary`: one line saying what the page holds, for someone deciding
  whether to read it. Give a `theme` to pages that belong together, such as
  one document's parts or chapters (a series sets it for you), and record
  missing coverage in `gaps`. When rewriting a page, keep its `theme`, `gaps`
  and `part_of` unless they are wrong.
- Stay within the page limit, and list further pages in NOTES as follow-up
  operations.
- NOTES holds the coverage review: what you retained, summarized or omitted and
  why, missing evidence and open questions. The operator runs the checks and
  the owner records acceptance; don't claim either.
