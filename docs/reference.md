# Reference

Look up the operator CLI, the worker roles and the link checker. For the
content rules pages must follow, see the
[managed-wiki contract](../framework/instructions/wiki-contract.md).

## Operator CLI

`scripts/sb_operator.py` runs one operation at a time. Python 3 standard
library; `run` and `revise` need Linux and OpenCode.

```text
sb_operator.py capture VAULT URL
sb_operator.py pending VAULT
sb_operator.py stage VAULT ingest  --url URL --task TEXT
sb_operator.py stage VAULT ingest  --input raw/<capture> [--input ...] --task TEXT
sb_operator.py stage VAULT compile --task TEXT                      # worker picks notes from the index
sb_operator.py stage VAULT compile --input wiki/sources/<note>.md [--input ...] --task TEXT
sb_operator.py stage VAULT query   --question TEXT
sb_operator.py run    OPERATION
sb_operator.py revise OPERATION
sb_operator.py apply  OPERATION [--dry-run]
sb_operator.py undo   OPERATION
sb_operator.py status OPERATION
```

`stage` accepts `--config FILE`; the default is
`VAULT/.opencode/second-brain/operator.json`. Every command prints JSON.

| Command | What it does |
|---|---|
| `capture` | Fetches one http(s) URL with no model involved. A web page's main content goes to `raw/<date>-<slug>.md` (see [Web capture](#web-capture)). A PDF is kept as `raw/<date>-<slug>.pdf` beside its extracted text (see [PDF capture](#pdf-capture)). Never overwrites: repeats get `-2`, `-3`. |
| `pending` | Lists `.md`, `.txt` and `.html` files under `raw/` that no source page's `raw` field references, plus PDFs no capture's `source_pdf` names, oldest first. Skips `raw/assets/`, hidden files, and subfolders where any file is already referenced (multi-file captures). |
| `stage` | Writes `operation.md`, listing the exact contract, index, log, template, input and figure paths the worker may read. With `--url`, runs `capture` first and ingests the result. An ingest `--input` ending in `.pdf` is extracted first. Either way, the printed `capture` lists every part, and the operation ingests part 1. Creates `WORKDIR/<date>-<kind>-<id>/` holding `corpus/` (a copy of every adopted wiki page, the contract, the four content templates and the inputs), `profile/` (the worker role and skill) and `manifest.json` (every vault wiki file's SHA-256, the inputs and the config). Refuses symlinks, hardlinks and traversal. Never copies the vault's `AGENTS.md`, settings or other folders. |
| `run` | Grants the worker exact reads on the staged files, denies every other tool, verifies the effective configuration with `opencode debug`, then runs the worker once. Saves `response.md`, `run.json` and, for ingest and compile, `proposal.json`. |
| `revise` | Once per operation: reruns the worker with the dry-run problems as feedback and its previous reply readable as `previous-proposal.md`. The first attempt moves to `attempt-1/`. |
| `apply` | Validates the proposal (below), backs up every file it replaces to `backup/`, writes the pages and appends the log record, then runs the checker on the vault. If that check fails, it undoes the write. `--dry-run` validates without writing. |
| `undo` | Restores the files an applied operation changed, and removes files it created, when each still matches what `apply` wrote. Files changed since are listed in `skipped_changed_since` and left alone. |
| `status` | Shows the operation's kind, task, inputs and completed stages. |

Exit codes: `0` success; `1` the worker run failed verification, `apply`
found problems, or `undo` skipped changed files; `2` invalid input or setup.

### Operator config

| Key | Meaning | Default |
|---|---|---|
| `cli` | Path to `sb_operator.py`; read by the operator skill | — |
| `agent` | Existing primary agent whose provider authentication is reused | required |
| `model` | Worker route as `provider/model`; must match that agent's route | required |
| `opencode_version` | Installed OpenCode version you approved | required |
| `workdir` | Where operations are staged; must be outside the vault | required |
| `max_pages` | Most pages one proposal may change | `10` |
| `steps` | Worker turn limit | `10` |
| `timeout` | Seconds per worker run | `600` |
| `auto_apply` | Whether the operator skill may apply a passing proposal without asking | `true` |

Example: [`framework/operator.example.json`](../framework/operator.example.json).

### Worker run checks

`run` passes only when every check holds:

| Check | Passes when |
|---|---|
| `run_completed` | The worker exited 0 with a reply |
| `skill_loaded` | The worker loaded its designated skill with the skill tool |
| `only_reads` | Every tool call was a read or skill call |
| `reads_in_scope` | Every completed read was a staged file |
| `required_full_reads` | The index, the contract and every input were read completely (no offset, limit or truncation) |
| `zero_writes` | Staged files are byte-identical afterwards |

### Proposal format

```text
<<<FILE wiki/<folder>/<page>.md>>>
complete Markdown
<<<END FILE>>>
<<<INDEX>>>
Concepts | - [[wiki/concepts/<page>|Title]] — short description
Gaps | - plain-text gap
<<<LINKS>>>
wiki/sources/<note>.md | - [[wiki/concepts/<page>|Title]] — how they relate
<<<LOG>>>
## YYYY-MM-DD — operation — partial
- bullets
<<<NOTES>>>
coverage review
```

A reply with only `<<<NOTES>>>` is a valid no-op.

- **INDEX.** Optional. Each line names a section (`Concepts`, `Entities`,
  `Synthesis`, `Sources` or `Gaps`) and an entry. `apply` merges the entries
  into `wiki/index.md`: an entry replaces any existing entry for the same page,
  goes after the section's last entry, and replaces a "No pages yet" line.
  Other entries are never removed, and the index's `updated` date is set. The
  worker never returns the whole index.
- **LINKS.** Optional. Each line names an existing page and a link entry.
  `apply` appends the entry to that page's `## Links` (or `## Related`)
  section, creating `## Links` at the end if needed. Links the page already
  has are skipped, and the page's `updated` date is set. This is how
  back-links reach long notes without the worker retyping them. A page may be
  rewritten with FILE or patched with LINKS, not both.
- **Markers.** A final closing marker line on a section (any `<<<…>>>`) is
  ignored. Any other marker line inside a page or the log record is an error.

### Apply checks

`apply` refuses the whole proposal, writing nothing, when any of these fail:

- **Pages:** at least one page changed (FILE or LINKS) and no more than
  `max_pages` distinct pages.
- **Paths:** only `wiki/{sources,concepts,entities,synthesis}/**.md`; never
  `wiki/index.md` or `wiki/log.md` as a page, `raw/`, instruction filenames or
  traversal.
- **Updates keep content:** an update may not drop any wikilink the page
  already has, and may not shrink a page of 20 or more lines to under half its
  length. These catch a model summarizing a page it was asked to extend.
- **Log record:** a single record whose heading is
  `## YYYY-MM-DD — operation — partial`.
- **Drift:** every file it touches, the log, and the index when it has INDEX
  entries, still has its staged hash.
- **Checker:** the managed checker reports no errors or unsupported forms on a
  copy of the wiki with the proposal applied.

### Web capture

`capture` uses the standard library only:

- **Content.** It keeps the richest `<article>`, else `<main>` or
  `[role=main]`, else `<body>`. Scripts, navigation, headers, footers, asides
  and forms are dropped.
- **Markdown.** Headings, paragraphs, lists, links (made absolute), emphasis,
  inline code, quotes, tables, images and code blocks (verbatim, with the
  language when marked) are converted. `text/plain` and `text/markdown` are
  saved unchanged.
- **Metadata.** `og:title` or `<title>`; the `author` meta tag, ignoring
  profile URLs and numeric IDs; `article:published_time`, similar tags or
  `<time datetime>`.
- **Line length.** Prose lines over 1,500 characters are wrapped so a worker
  can read every line; code is never rewrapped.
- **Parts.** A capture too long for one full read is split into
  `-part-1.md`, `-part-2.md`, and so on. Splits fall before headings, then at
  blank lines, never inside code, and the `part` field records `k/n`. A full
  read means at most 1,850 lines and 45 KB, because OpenCode's read tool
  truncates at about 50 KB.
- **Refusals.** Fewer than 150 words of main content, a download over 50 MB,
  or another content type. A refusal writes nothing.

Capture frontmatter, one JSON value per line:

| Field | Meaning |
|---|---|
| `url` | The URL you gave |
| `final_url` | Where redirects ended, or `null` if the same |
| `part` | `k/n` when the page was split, otherwise `null` |
| `title`, `author`, `published` | From the page; `null` when absent, never guessed |
| `captured` | UTC capture time |
| `fetched_with` | Records that no model produced the text |
| `body_sha256` | Hash of the Markdown body |

### PDF capture

Requires Poppler's `pdftotext` and `pdfinfo`. OCR requires `ocrmypdf` with
Tesseract.

- **Extraction order.** Reading order first. If the quality check fails,
  `pdftotext -layout`. If there is no text layer (fewer than 150 words),
  `ocrmypdf --skip-text` and then reading order. Encrypted PDFs are refused.
- **Quality check.** Fails when any of these hold:
  - under 150 words
  - more than 35% of lines are one to three characters (interleaved columns)
  - under 60% of visible characters are letters
  - more than 1 in 200 characters are unreadable
- **Figures.** Pages whose text has a line starting `Figure N` or `Fig. N`
  followed by `.`, `:` or `|` are rendered with `pdftoppm` at 110 dpi to
  `raw/assets/<capture>/page-NN.png`. That covers embedded images and vector
  charts alike. Up to 6 such pages are rendered per part, so long books keep figures throughout. Each rendered page
  gets a `![Figure N (page P)](...)` line under its text. `stage` copies the
  input capture's figure images into the staged copy, so the worker can read
  them; image reads are optional, not required full reads.
- **Pages and parts.** Each page becomes `## Page N`. Parts break only
  between pages, and each part stays within one full read (1,850 lines and
  45 KB). A single-part
  capture is named after the PDF; parts are named `-part-1`, `-part-2`, and
  so on.

PDF capture frontmatter:

| Field | Meaning |
|---|---|
| `url` | Source URL, or `null` for a file you saved |
| `source_pdf`, `pdf_sha256` | The original PDF in `raw/` and its hash |
| `title`, `author` | From the PDF's metadata when set; `null` otherwise |
| `published` | Always `null`; the worker takes it from the text if the document states it |
| `pdf_created` | The file's creation date, which is not the publication date |
| `pages`, `page_range`, `part` | Total pages, this capture's pages, and `k/n` for parts (`null` if one part) |
| `extracted_with`, `ocr`, `quality` | Extraction mode, whether OCR produced the text, and the quality metrics |
| `figures` | Rendered figure pages in this capture: page, figure numbers and image path |
| `figures_not_rendered` | Count of caption pages in this part beyond the per-part limit |
| `captured`, `body_sha256` | UTC capture time and the hash of the Markdown body |

## Worker roles

| Role | Skill | Access when launched by the operator |
|---|---|---|
| `sb-ingestor` | `second-brain-ingest` | Exact reads on the staged files, including rendered figure images; no edits, shell, search, network or delegation. Returns a proposal. |
| `sb-researcher` | `second-brain-query` | Exact reads on the staged files; nothing else. Returns an answer ending with `Read:` and `Not covered:`. |
| Your primary agent | `second-brain-operator` | Its own permissions; it needs shell access to run the CLI. |

The role files deny every tool on their own. Selecting them in an ordinary
OpenCode session without the operator gives them no file access.

## Link checker

`python3 scripts/link_check.py VAULT [--json]`

- Reads only `wiki/{sources,concepts,entities,synthesis}/` Markdown and optional
  `wiki/index.md`/`wiki/log.md`. Other root folders are not scanned. Protected
  `.obsidian`/`.opencode`/`.git` entries inside the adopted content tree cause refusal.
  Reserved `AGENTS.md`, `CLAUDE.md` and `CONTEXT.md` instruction files are excluded;
  links to them are unsupported, not knowledge edges.
- Validates the contract's flat JSON-valued frontmatter, not arbitrary YAML.
  Source `raw` paths are format-checked but never opened. A valid root without
  `wiki/` is an empty corpus, not an invalid directory.
- Resolves exact extensionless vault-relative wikilinks, with optional labels
  and spaces. Repeated links are deduplicated; self/control edges are not content
  edges. Controls are still checked, but are not counted as knowledge pages.
- Reports missing/malformed/ambiguous targets, and unsupported embeds, bare
  basenames, aliases or out-of-scope forms. It does not guess a unique basename.
- Reports contract errors: `placeholder` for leftover `{{...}}` text in metadata
  or in the body outside code (HTML comments included); `not_indexed` for a
  content page that `wiki/index.md` does not link, when the index exists; and
  `not_reciprocal` for a source ↔ concept/entity link without its back-link,
  reported on the page that lacks it.
- Strips fragments only to check the file; heading/block validity is **unchecked**.
  A zero exit with unchecked anchors is not proof that those anchors exist.
- Excludes leading frontmatter, ordinary fenced code and simple inline-code
  spans. An unclosed fence suppresses the rest of the page. This is not a full
  Markdown/Obsidian parser: HTML comments, indented code, blockquote fences and
  complex inline spans are not normalized.
- Exit 0: no error/unsupported form (review unchecked items separately).
  Exit 1: errors or unsupported forms. Exit 2: invalid/unsafe scope or read failure.

The checker does not establish factual support, whether a link's meaning is
right, or transaction completion. Review those separately.

The checker does not establish factual support, whether a link's meaning is
right, or transaction completion.
