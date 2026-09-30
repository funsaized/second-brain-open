# Reference

Look up the operator CLI, the worker roles and the link checker. For the
content rules pages must follow, see the
[managed-wiki contract](../framework/instructions/wiki-contract.md).

## Operator CLI

`scripts/sb_operator.py` runs one operation at a time. Python 3 standard
library; `run` and `revise` need Linux and OpenCode.

```text
sb_operator.py capture VAULT URL | raw/<file>.pdf
sb_operator.py pending VAULT
sb_operator.py series VAULT (--input raw/<capture> ... | --glob 'raw/<stem>-part-*.md') [--task TEMPLATE]
                     [--with-concepts] [--theme TEXT] [--limit N] [--background]
sb_operator.py series VAULT --plan PLAN.json [--limit N] [--background]
sb_operator.py series-status VAULT
sb_operator.py accept VAULT --level technical|sampled|full --sample TEXT --defects TEXT [--match REGEX] [--dry-run]
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
| `revise` | Up to twice per operation: reruns the worker with feedback and its previous reply readable as `previous-proposal.md`; earlier attempts move to `attempt-N/`. A reply that could not be parsed gets a format-only revision, whose only required read is `previous-proposal.md`. Dry-run problems get a content revision, which rereads the inputs. |
| `accept` | Appends one owner acceptance record to `wiki/log.md` naming, one bullet each, every `partial` operation that no earlier acceptance record names (optionally filtered by `--match`). The owner states the level, the sample and the defects; `technical` keeps the operations partial, `sampled` and `full` complete them. The log is backed up to the workdir and restored if the checker fails afterwards. |
| `series` | Ingests inputs in order, one operation each. Retry policy: a reply that cannot be parsed gets one format-only `revise`; a failed run gets one fresh operation; dry-run problems get one `revise`. Items whose reply adds nothing are recorded as `no change`. Inputs already referenced by a source page are skipped, so rerunning the same command resumes. Workers are told their position, the previous item's source page, and that later items don't exist yet. Without `--with-concepts` they write source pages only. Each item's Sources index entry is filed under one theme: `--theme`, or else the first capture's `title`. `--plan` runs a JSON plan instead, `{"theme": ..., "items": [{"kind": "ingest"|"compile", "inputs": [...], "task": ..., "done_if": "wiki/...md", "file_inputs_under": ...}]}`: an item is skipped once its `done_if` page exists, and `file_inputs_under` makes the operator re-file the inputs' existing index entries, text unchanged, under that theme (for example, a book's part notes once chapter pages exist). `--background` detaches and logs one JSON line per item to `WORKDIR/series-*.jsonl`. One series runs per workdir at a time. |
| `series-status` | Shows the latest background series: whether it is running, the applied and no-change counts, the last item and the final result. |
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
| `max_pages` | Most pages one proposal may write whole (FILE); LINKS back-link lines don't count | `10` |
| `steps` | Worker turn limit; searches, figure reads and a synthesis's wide reading use turns too | `40` |
| `timeout` | Seconds per worker run. Separately, a worker with no output after 120 s is treated as an OpenCode startup stall: it is killed and relaunched once, and a second stall fails the run with "OpenCode did not start" | `600` |
| `auto_apply` | Whether the operator skill may apply a passing proposal without asking | `true` |
| `search` | Whether workers may use grep and glob over their staged copy | `true` |

Example: [`framework/operator.example.json`](../framework/operator.example.json).

### Worker run checks

`run` passes only when every check holds:

| Check | Passes when |
|---|---|
| `run_completed` | The worker exited 0 with a reply |
| `skill_loaded` | The worker loaded its designated skill with the skill tool |
| `only_reads` | Every tool call was a read or skill call, or a grep or glob when `search` is on |
| `searches_in_scope` | Every grep or glob path, if given, stays inside the staged copy |
| `citations_read` | Queries only: every `wiki/` page the answer cites was opened with the read tool; a search hit does not count. Failures list `unread_citations`, and `revise` gives the researcher one retry |
| `reads_in_scope` | Every completed read was a staged file |
| `required_full_reads` | Every line of the index, the contract and each input was read. A large file may be read in several offset/limit ranges; the reads together must show all of its lines, and none may be cut short at 2,000 characters |
| `zero_writes` | Staged files are byte-identical afterwards |

Before launching a worker with `search` on, `run` refuses a staged copy that
holds any file without a read grant. OpenCode checks a search against its
pattern, not the files it returns, and grep includes hidden folders, so the
staged copy must contain only files the worker may read.

Ingest workers, and compile workers given named inputs, get a compact copy of
`wiki/index.md`: headings, titles and paths, without descriptions or
frontmatter. Compile-by-topic and query workers choose pages by their
descriptions, so they get the full index. The vault's own index is never trimmed.

### Proposal format

```text
<<<FILE wiki/<folder>/<page>.md>>>
complete Markdown
<<<END FILE>>>
<<<INDEX>>>
Concepts | - [[wiki/concepts/<page>|Title]] — short description
Sources | <theme> | - [[wiki/sources/<page>|Title]] — short description
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
  `Synthesis`, `Sources` or `Gaps`), an optional theme, and an entry. `apply`
  merges the entries into `wiki/index.md`. A theme files the entry under a
  `### theme` heading in its section, created at the section's end if needed.
  Without a theme, an entry that replaces an existing one keeps its place, and
  a new one goes after the section's last unthemed entry. Theme headings left
  empty are removed, and a "No pages yet" line is replaced.
  Other entries are never removed, and the index's `updated` date is set. The
  worker never returns the whole index.
- **LINKS.** Optional. Each line names an existing page and a link entry.
  `apply` appends the entry to that page's `## Links` (or `## Related`)
  section, creating `## Links` at the end if needed. Links the page already
  has are skipped, and the page's `updated` date is set. This is how
  back-links reach long notes without the worker retyping them. A page may be
  rewritten with FILE or patched with LINKS, not both.
- **Tolerance.** Text outside sections, repeated section markers, missing
  or mismatched closing markers, a missing NOTES section and an outer code
  fence are all ignored. Malformed INDEX or LINKS lines are skipped and
  reported under `parse_warnings`. Only a reply with no markers, or a FILE
  marker without a path, fails to parse.

### Repairs before checking

`apply` repairs these mechanically and lists every repair under `fixes`:

- A LINKS entry for a page that is also rewritten is merged into the rewrite.
- A wikilink to a page that doesn't exist becomes its plain label. Code blocks
  are left alone.
- INDEX and LINKS entries that point at missing pages are dropped.
- Every source ↔ concept/entity link the proposal adds, in a page or a LINKS
  line, gets its missing back-link: inside the page when the proposal writes
  it, otherwise as a LINKS entry on the existing page.
- A missing log record is written from the changed paths. A record without a
  proper heading gets one, and a record claiming a status other than
  `partial` is set to `partial`.

### Apply checks

`apply` refuses the whole proposal, writing nothing, when any of these fail:

- **Pages:** at least one page changed (FILE or LINKS), and no more than
  `max_pages` pages written whole with FILE.
- **Paths:** only `wiki/{sources,concepts,entities,synthesis}/**.md`; never
  `wiki/index.md` or `wiki/log.md` as a page, `raw/`, instruction filenames or
  traversal.
- **Updates keep content:** an update may not drop any wikilink the page
  already has, and may not shrink a page of 20 or more lines to under half its
  length. These catch a model summarizing a page it was asked to extend.
- **Log record:** a single record whose heading is
  `## YYYY-MM-DD — operation — partial`.
- **Drift:** every page it rewrites with a FILE still has its staged hash. The
  log record is appended, INDEX entries merged and LINKS lines patched against
  the vault's current files, so another operation applied in between doesn't
  block it. `revise` refuses when drift is the only problem: stage again.
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
| `sb-ingestor` | `second-brain-ingest` | Exact reads on the staged files, including rendered figure images, plus grep and glob inside the staged copy; no edits, shell, network or delegation. Returns a proposal. |
| `sb-researcher` | `second-brain-query` | Exact reads plus grep and glob inside the staged copy; nothing else. Returns an answer ending with `Read:` and `Not covered:`. |
| Your primary agent | `second-brain-operator` | The vault's `opencode.json` ([installation step 2](installation.md#2-configure-the-operator)): reads `wiki/` and `raw/`, runs the operator CLI, never edits managed folders. |

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

## Chat export converter

`python3 scripts/chat_export_to_md.py EXPORT STAGING (--conversation-id ID ... | --all) [--min-words N] [--dry-run]`

How to use it is in [the chat-export guide](chat-exports.md); this is its
specification.

### Options, output and exit status

`--min-words N` defaults to 150; nonnegative thresholds count only retained text
using whitespace splitting, not role labels or metadata. Exactly N words passes.
Short filtering is **not** privacy review. `--dry-run` validates and checks
existing output bytes but creates no directories or files.

Successful stdout is counts only, for example:

```text
selected=1 written=1 would_write=0 identical=0 too_short=0 unsupported=0 omitted_payloads=0 failed=0
```

Exit 0 means successful conversion/filtering (or dry-run), not factual acceptance.
Exit 2 means invalid CLI/input, unsupported format, unsafe path, or output failure.
Errors print JSON-escaped source IDs and fixed reasons to stderr, never titles,
message text, exception bodies or file paths. IDs themselves can be sensitive;
keep error reports local. Invalid top-level input uses a null ID. `unsupported`
is separate from `too_short`. Omission counts include supported selected records
even if filtered as short.

### Supported shapes and fidelity

Top level is a list or `{"conversations": [...]}`. Every record must be an object;
duplicate JSON keys and duplicate conversation identities are errors. Unknown
vendor variants require compatibility review; these fixtures are not proof that
every current vendor export works.

| Shape | Ordered messages and roles |
|---|---|
| Claude | `chat_messages` list; `sender` (including `human`/`assistant`) |
| Simple | `messages` list; `sender`, then `role`, then `author.role` |
| ChatGPT | `mapping` object and nonempty string `current_node`; walk `parent` to explicit null, reverse; role from `author.role` |

Mapping nodes require explicit `parent` and `message`. Structural null messages
are skipped. Unselected sibling branches are ignored, not merged or validated.
The selected walk rejects cycles, absent nodes/parents, non-string parents
(including multiple-parent arrays), and malformed messages. `current_node`
selects the endpoint; descendants are not silently substituted. List shapes
retain list order; timestamps never reorder messages.

Example invented inputs (word filter must be lowered for these tiny examples):

```json
[
  {"uuid":"synthetic-chat-a","name":"Invented vent trial","created_at":"2026-09-24T09:00:00Z",
   "chat_messages":[
     {"sender":"human","text":"I preferred the wider vent in this invented trial."},
     {"sender":"assistant","content":[{"type":"text","text":"That is an unverified preference, not a measured result."}]}]},
  {"id":"synthetic-chat-b","title":"Invented branch","create_time":0,"current_node":"chosen",
   "mapping":{
     "root":{"parent":null,"message":null},
     "question":{"parent":"root","message":{"author":{"role":"user"},"content":{"content_type":"text","parts":["Which trial?"]}}},
     "chosen":{"parent":"question","message":{"author":{"role":"assistant"},"content":{"content_type":"text","parts":["The synthetic trial; evidence is still missing."]}}},
     "sibling":{"parent":"question","message":{"author":{"role":"assistant"},"content":{"content_type":"text","parts":["Not selected."]}}}
   }}
]
```

Content can be a string, a list of strings/`{"type":"text","text":"..."}`
blocks, a single typed text block, or a ChatGPT `content_type: text` /
`multimodal_text` object with a `parts` list. `content` takes precedence over
`text`, except an empty string/list content falls back to `text`; malformed text
blocks fail rather than being stringified. ChatGPT `content_type: code` with a
string `text` is also retained. Other content types carrying a `text` string are
unsupported (not silently filtered as short). Separate text
blocks are joined with two newlines; text within each block is unchanged.
Each message has a numbered heading, quoted original role and timestamps, and a
backtick fence longer than any run in its text. Text is archived literally, not
rendered as executable instructions or trusted Markdown headings.

Unknown non-text blocks count as omitted payloads. Additional populated fields
on text blocks (including citation/media fields) count as omitted units too.
Attachments/files and explicit
tool-call/use/result/function-call fields also count; text of `tool`/`function`
messages is omitted and counted, while their role, position and dates remain.
Counts represent encountered payload units, not attachment bytes or unique assets.
Both message sections and frontmatter record omissions, including tool-only
messages. This is **not lossless media/tool conversion**; retain the original
export separately. Incidental vendor metadata is not reproduced.

Supported creation keys are `created_at`, then `create_time`; update keys are
`updated_at`, then `update_time`,
at conversation and message level. A present key wins, even if null. Values are
epoch **seconds** (not milliseconds), `YYYY-MM-DD`, or
`YYYY-MM-DDTHH:MM:SS[.fraction](Z|±HH:MM)`. Zoned times normalize to UTC, retaining
time to microsecond precision; date-only stays a date. Missing/null/empty values
remain JSON null (unknown), never today's date. Invalid values and zone-less
datetimes fail; no timezone is guessed. Dates and all other metadata values use
JSON quoting in flat YAML frontmatter, including hostile titles/newlines.

### Identity, safe paths and recovery

Identity is `uuid`, then `id`, then `conversation_id`, if present: a nonempty
string. Otherwise it is `derived-` plus SHA-256 of the record's sorted-key,
ASCII JSON serialization (Python's default separators, finite JSON values).
An absent ID cannot establish continuity across content changes; a revised
ID-less record gets a new derived identity. Original IDs, title, format, branch,
known conversation/message dates and omission counts are retained in the artifact.
`source_record_sha256` hashes that same canonical JSON representation of the full
record, so revisions to omitted payloads or sibling branches also produce a new
version without exposing their content in Markdown.

Filename: `chat-<24 hex ID hash>-<24 hex artifact hash>.md`. Titles and raw IDs
never become path components. Same-title conversations remain distinct. Identical
reruns verify the complete existing bytes and skip; changed output gets a new
digest path without removing the old version. A truncated-digest collision or
tampered existing file is an error, not permission to overwrite or add a suffix.

Input and existing output must be unique regular files (no hardlinks). Traversal,
symlinks in inputs/destinations/ancestors and non-directory ancestors are refused.
New directories use mode 0700 and artifacts 0600 subject to umask. Existing
directory permissions are not changed. Exclusive creation prevents overwrites;
the output file is flushed/fsynced. No shared scanner semantics were changed:
the wiki scanner's preflight helpers do not supply the converter's descriptor-based
write boundary.

All selected records are validated before writes. One invalid/unsupported selected
record blocks the whole batch, including otherwise valid records. Short records
are still validated. Unselected record bodies are not converted, but envelope/ID
validation applies to the whole export. On an output failure, writing stops;
stderr reports written IDs, the failed ID and unattempted IDs. Later planned
records were not attempted. Handled write errors remove the just-created incomplete file, not
earlier successful outputs. A process kill/power loss may leave an incomplete
file: an identical rerun refuses it, rather than silently accepting it. Inspect
locally, preserve evidence and remove only that verified incomplete artifact
before rerunning. No transactional batch, directory-fsync durability, database,
automatic cleanup of old versions, or sync service is promised.
