# Ingest, compile and ask with the operator

Use this guide to add a source to your wiki, build concept pages from notes you
already have, or ask a question, and to undo a change you don't want. It
assumes the framework and operator are installed; if not, start with
[installation](installation.md).

Most of the time you ask your primary agent in plain language, and it runs the
operator for you through the `second-brain-operator` skill. You can run the same
steps yourself with the CLI.

## Ingest a web page

Give your primary agent the URL:

> Use the second-brain-operator skill to ingest https://example.com/post as a
> learning reference and connect it to related pages.

The operator does the rest:

1. **Capture.** It fetches the page itself, with no model involved. It keeps
   the main content (headings, text, lists, tables and code, verbatim), drops
   navigation, headers and footers, and saves the result to
   `raw/<date>-<title>.md` with the URL, title, author, publication date,
   capture time and a hash.
2. **Ingest.** The sandboxed `sb-ingestor` reads the capture and the index and
   proposes a source page, plus concept and entity pages where the source adds
   something reusable. Every new page is linked in both directions.
3. **Apply.** The operator checks the proposal, gives the worker one revision
   if needed, and applies it with backups.
4. **Report.** You get the pages created or updated, the checker result, the
   operation directory and the undo command.

A long page is split between headings into parts the worker can read in full.
The operator then ingests the parts in order, each as its own source page. A
capture is refused when the page yields fewer than 150 words of main content,
which is common for pages that need JavaScript, a login or a subscription. In
that case, save the page with the
[Obsidian Web Clipper](https://obsidian.md/clipper) into `raw/` and ingest the
file instead.

## Ingest a PDF

Give the URL of a PDF (a paper, report or manual), or save the file into `raw/`
and name it:

> Use the second-brain-operator skill to ingest the paper at
> https://arxiv.org/pdf/1706.03762 and connect it to related pages.

The operator does the rest:

1. **Keep the original.** It saves the PDF unchanged next to the extracted
   text.
2. **Extract.** It extracts the text in reading order, with a `## Page N`
   heading per page, so claims cite page numbers. If the text looks garbled
   (interleaved columns, broken characters), it retries with layout
   extraction.
3. **OCR scans.** A scan without a text layer goes through `ocrmypdf`. The
   pages are then marked as OCR text, and the worker flags any numbers it
   relies on for checking against the original.
4. **Split long documents.** A document too long for one read is split on page
   boundaries into parts. The operator ingests the parts in order, each as its
   own source page, linked to the previous part.
5. **Capture figures.** Every page with a `Figure N` caption is rendered to
   an image in `raw/assets/<capture>/` (up to 6 per part) and linked under that
   page's text, so you see the figures in Obsidian.
6. **Read the figures.** The worker looks at the figures the paper relies on.
   It writes a labelled "Figure reading" (type, axes, trend, key values, with
   plotted values marked approximate) and embeds the image on the source page
   next to it.
7. **Read papers as papers.** A paper's source page is built around its
   question, method, results with numbers and sample sizes, and stated
   limitations.

Tables come through as text but lose their layout. A rendered figure page shows
the whole page, not a neat crop, and figure pages beyond the first 12 are
listed as not rendered. An extraction that fails the quality check is refused with the
reason. In that case, export the text another way (for example, Zotero's
Markdown export) into `raw/` and ingest that file.

## Ingest a whole book or long document

Long PDFs and pages are split into parts. Ask for all of them:

> Use the second-brain-operator skill to ingest all parts of raw/2026-09-29-book.pdf in order.

The operator extracts the parts if needed, then runs a **series** in the
background, one operation per part:
- A reply the parser can't read gets one formatting retry.
- A failed run gets one fresh attempt.
- Failed checks get one revision.

Each part becomes a source page linked to the previous part. Concept pages
are compiled after the series, so the same concept isn't rewritten for every
part. A part with nothing reusable, such as front matter, is recorded and
skipped. The operator checks progress every few minutes and reports when the
series finishes or stops.

To resume after a stop, ask again ("continue ingesting the book"): parts
that are already ingested are skipped. From a terminal:

```sh
python3 "$CLI" series . --glob 'raw/2026-09-29-book-part-*.md' --background
python3 "$CLI" series-status .
```

## Ingest a file you saved

Save the source into `raw/` (clipped article, extracted PDF text, a converted
chat) and name it:

> Use the second-brain-operator skill to ingest raw/2026-10-01-article.md as a
> learning reference.

A large source may need more pages than `max_pages` allows. The worker then
proposes the most important pages and lists the rest as follow-up operations.

## Catch up on everything new

Clip pages into `raw/` as you find them, then:

> Use the second-brain-operator skill to catch up on new captures.

The operator lists every capture no source page references yet, including
PDFs you dropped into `raw/`, oldest first,
and ingests them one by one, up to 20 per request. It stops at the first failure
it cannot fix, and reports what it did and what is left.

## Build concept pages from existing notes

Describe the concept; the worker finds the relevant notes itself:

> Use the second-brain-operator skill to create a concept around the structure
> of the wiki filesystem and how it plays into usage.

The worker reads the index, picks the most relevant notes (usually three to
eight), reads them in full, and writes the concept page. Every claim links to
the note that supports it, and each note gets a link back to the concept. The
operator merges the new index entry; nothing is fetched from the web. To choose
the notes yourself, name them: "…from wiki/sources/a.md and wiki/sources/b.md".

## Ask a question

> Use the second-brain-operator skill to answer: how should the log differ from
> the index?

The answer cites the pages it read and ends with `Read:` and `Not covered:`. Asking
writes nothing. To keep an answer, ask for a compile operation.

## Run the steps yourself

From the vault root, with `CLI` set to the `sb_operator.py` path in your
operator config:

```sh
python3 "$CLI" stage . ingest --url https://example.com/post --task "Ingest as a learning reference"
python3 "$CLI" run   OPERATION        # OPERATION is the directory stage printed
python3 "$CLI" apply OPERATION --dry-run
python3 "$CLI" apply OPERATION
```

Use `--input raw/<file>` instead of `--url` for a file you saved.
`python3 "$CLI" capture . URL` only captures a page, and
`python3 "$CLI" pending .` lists captures waiting to be ingested.

For a question, use `stage . query --question "..."` and `run`; the answer is in
the operation's `response.md`.

## When a step fails

- **The worker run fails verification.** `run` prints the failed checks and
  any required input it did not read completely. A capture too long to read in
  one pass has to be split into smaller captures first. Stage a new operation
  afterwards.
- **The dry run lists problems.** Run `revise OPERATION` once. The worker gets
  the problems and its previous reply, and returns a corrected proposal. Check
  it with `apply --dry-run` again. The operator skill does this for you. If the
  problems remain, stage a new operation with a narrower task.
- **A vault file changed since staging.** `apply` refuses rather than
  overwrite your edit. Stage the operation again.

## Undo an operation

```sh
python3 "$CLI" undo OPERATION
```

`undo` restores every file the operation changed, including the log. It keeps
any file you edited after the operation and names it under
`skipped_changed_since`.

## Record your review

Applied operations are logged as `partial`. After you review the changes,
append an acceptance record to `wiki/log.md` in the form the
[log template](../framework/templates/log.md) shows. Use `sampled` for a
reviewed sample or `full` for every page; see
[Owner acceptance](../framework/instructions/wiki-contract.md#owner-acceptance).
The operator never records acceptance for you.

## Related

- [Reference: CLI commands, checks, config and roles](reference.md).
- [Why operators and workers are separate](how-it-works.md#operators-and-workers).
- [Measure the researcher's answers](researcher-evaluation.md).
