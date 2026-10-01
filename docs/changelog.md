# Changelog

> Dated results of each change, oldest first, moved from PLAN.md on
> 2026-09-30. Each entry records what changed and how it was verified; test
> counts appear only here, as of their date. Current state is in
> [STATUS.md](../STATUS.md).

## 2026-09-28 — Content-preservation policy follow-up

Implemented purpose-sensitive learning/reference content rules in the contract,
ingest skill, source template and manual request example. Source bodies support
complete Markdown, with retained/summarized/omitted coverage review in proposals;
no new metadata fields, page types, permissions or automated publication paths.
The adaptation map records these changes.

Verification: the focused contract suite passed 5 tests, and the offline
distribution suite passed 83 tests. The additional wholly invented template
case preserves a tree, code example and comparison table without introducing
metadata or concept-link requirements. `git diff --check` passed. These are
static/offline results, not proof of model selection quality or runtime adoption.

## 2026-09-28 — User documentation entry point

Reframed the README around the shipped manual source-to-wiki-to-answer capability
and the reader's next task. Diataxis navigation separates a model-free tutorial,
installation/operation how-tos, contract/tool reference and workflow explanation.
Installation details moved out of the overview; development evidence stays linked
as evidence, not mislabeled as a tutorial or private deployment certification.

The tutorial uses only the existing invented contract fixture. Its read-only
checker example reports five knowledge pages, two controls and 18 links without
diagnostics. Statistics on that same fixture at `2026-09-24` report one component,
zero inbound orphans and zero stale concepts out of one eligible concept. No
provider calls, private fixtures, runtime configuration or vault writes are needed.

Verification: all 83 offline tests pass. The documented tutorial commands produce
the expected results and preserve all fixture bytes and paths. Local documentation
links and referenced headings were checked. No native/model trials were rerun.

## 2026-09-28 — Review backlog: checker contract checks, acceptance, evaluation

Owner direction closed backlog items F1 (re-verify on OpenCode 1.18.33) and F2
(deployment recovery point) without further checks; native evidence stays dated
to 1.18.32 unless a run names another version.

- **C1:** `scripts/link_check.py` reports `placeholder`, `not_indexed` and
  `not_reciprocal` errors, which the contract already required but only the
  fixture tests checked. The contract fixture stays clean.
- **A3:** the contract, log template and ingest skill define `technical`,
  `sampled` and `full` owner acceptance. `completed` requires `sampled` or
  `full`, recorded as a new log record.
- **A2:** `tests/researcher_eval.py` stages a wiki copy without vault
  instructions, verifies exact read grants, asks each question in its own native
  run and scores index-first reads, cited-and-read pages, expected pages/terms,
  sections, abstention and zero writes. `docs/researcher-evaluation.md` explains
  it. A live run on the invented fixture passed 3/3 on OpenCode 1.18.33 through
  the previously approved route.
- **C2:** the fix is to bring a deployment's control pages up to the contract,
  not a legacy exception in the checker. Deployment edits are owner-local.

Verification: 93 offline tests pass; `git diff --check` passes. The helper
changes keep the earlier drivers' defaults (OpenCode 1.18.32, six steps).

## 2026-09-28 — Operator: autonomous ingest run by OpenCode

The owner chose "agent as operator": the primary agent runs the worker roles
through an operator skill and CLI. The workers stay deny-by-default and
proposal-only.

- **CLI:** `scripts/sb_operator.py` stages a copy outside the vault, runs the
  worker with exact read grants, and gives it one `revise` with the dry-run
  problems. `apply` writes only allowed `wiki/` pages and one `partial` log
  record, after drift and checker validation, with backups for `undo`.
- **Shared runtime:** helpers moved from the test drivers into
  `scripts/sb_runtime.py`.
- **Prompts:** the ingest skill gains a compile operation and a framed
  proposal format. The worker roles lose the per-edit approval text.
- **Docs:** follow Diataxis. `docs/operator.md` (how-to) and `docs/reference.md`
  (reference) replace `docs/manual-loop.md`, whose evidence sections moved to
  `docs/native-acceptance-trials.md`. Installation, how-it-works and the README
  are rewritten for the operator model.
- **Evidence:** live synthetic runs on OpenCode 1.18.33 are recorded in the
  trials doc, including a fully autonomous ingest by the primary agent from one
  request.
- **Unattended use:** needs an `external_directory` allow for the CLI and
  workdir in the vault's `opencode.json`.

Verification: 102 offline tests pass; `git diff --check` passes.

## 2026-09-29 — URL capture and catch-up ingest

The operator now takes a URL.

- **Capture.** `sb_operator.py capture` (and `stage ... --url`) fetches the page
  with the standard library, keeps its main content as Markdown with
  provenance frontmatter, and refuses fragments, overlong pages and non-text
  types. No model reads the page before the sandboxed ingest worker.
- **Rejected alternative.** A webfetch-only worker was tried and dropped:
  OpenCode's webfetch converts the whole page, navigation and comments
  included, and truncated a real gist at 32 KB of 143 KB.
- **Catch-up.** `pending` lists captures without a source page, oldest first,
  and the operator skill ingests them one operation at a time, up to 20 per
  request.
- **Calibration.** The ingest skill adopts upstream's link-before-done rule and
  its one-to-three-concepts guidance.

A live run on OpenCode 1.18.33 had the primary agent ingest a public URL
end-to-end in a synthetic vault; see `docs/native-acceptance-trials.md`.
Verification: 109 offline tests pass; `git diff --check` passes.

## 2026-09-29 — PDF capture

- **Capture.** A PDF by URL, or dropped into `raw/`, keeps its original and
  gains page-marked Markdown from Poppler: reading order first, `-layout` as a
  fallback, and `ocrmypdf` for scans. A quality check refuses interleaved or
  garbled text. Long documents split on page boundaries into parts that are
  ingested in order.
- **Metadata.** A PDF's creation date is recorded as `pdf_created`, never as
  the publication date.
- **Ingest skill.** Gains upstream-derived paper rules (question, method,
  results with numbers, limitations) and OCR verification caveats.
- **Live run.** The primary agent ingested arXiv 1706.03762 from its URL
  alone; see the trials doc.

Verification: 114 offline tests pass, including an OCR run on a generated
scan; `git diff --check` passes.

## 2026-09-29 — Figures and reliable parts

- **Figures.** PDF capture renders every page with a figure caption (up to 12)
  to `raw/assets/<capture>/`, links it under the page text and stages the
  images for the worker. A vision check confirmed the worker model reads
  images through OpenCode's read tool.
- **Figure readings.** The ingest skill writes labelled figure readings with
  approximate values and embeds the image. Figures never block an ingest.
- **Parts.** Every capture, web or PDF, now splits within 1,850 lines and
  45 KB, because OpenCode's read tool truncates at about 50 KB. Web pages split
  before headings.
- **Manifest.** The operation manifest lists exact readable paths.
- **Live run.** A 12-page arXiv paper was ingested end-to-end in two parts,
  with six figure readings; see the trials doc for the failures found and
  fixed.

Verification: 117 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Index merge, back-link patches and compile by topic

A deployment compile request exposed three failures: the worker rewrote the
142-line index down to 2 entries (the checker blocked it), fetched an
unrequested URL, and could not return long notes whole.

- **Index merge.** Index changes are INDEX entries that `apply` merges;
  `wiki/index.md` can no longer be a FILE.
- **Back-link patches.** LINKS lines append to a page's Links section, so no
  long note is retyped.
- **Guards.** `apply` refuses updates that drop existing links or shrink a
  page by half.
- **Compile by topic.** `compile` with no inputs lets the worker choose notes
  from the index. The operator skill routes concept requests there and never
  captures a URL it wasn't given.
- **Paths.** Workers read by relative path and retry denied optional reads.

A rerun of the same request on a copy of the deployment wiki succeeded on the
first attempt. Verification: 120 offline tests pass; `git diff --check`
passes.

## 2026-09-29 — Reliable long-document ingest

A 90-part textbook ingest stopped about once every five parts. The causes were
worker formatting drift, a page both rewritten and link-patched, a forward
link to a later part, and ad-hoc agent-written retry loops.

- **Tolerant parser.** The proposal parser reads marked sections and ignores
  noise.
- **Format-only `revise`.** `revise` handles unparseable replies with a
  format-only rerun, up to two revisions per operation.
- **Mechanical repairs.** `apply` merges links into rewrites, unlinks missing
  targets, drops dangling entries and fills in the log heading, reporting
  each repair.
- **The `series` command.** Runs items in order with one fixed retry policy,
  resumes by skipping ingested items, runs in the background and has
  `series-status`. Workers are told their position, the previous item's
  source page, and to write source pages only.
- **Local PDFs.** `capture` also extracts a PDF already in `raw/`.
- **Live run.** The primary agent ingested an invented 4-part PDF through a
  background series with no retries.

Verification: 125 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Large files read in ranges

Once `wiki/index.md` passed OpenCode's roughly 50 KB read cap, every
operation failed its full-read check, which stalled the textbook series at
part 47.

- **Coverage check.** The check now accepts a file read in several
  offset/limit ranges when the reads together show every line and none was
  cut short. The worker prompt says to keep reading in ranges.
- **Stop reasons.** Series stops name the file not read in full.
- **Live check.** Part 47's run passed on the deployment.

Verification: 125 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Worker search, compact staged index and index themes

The owner kept `wiki/index.md` as one page and set no cap on notes per
operation. Three changes address index growth (backlog H2) within that.

- **Worker search (B5).** Workers get grep and glob over their staged copy
  (`search`, on by default). A fake-provider Bubblewrap probe on OpenCode
  1.18.33 showed that `external_directory` confines both to the worktree,
  including against traversal and outside symlinks. It also showed that grep
  sees every worktree file, granted or not, hidden folders included. `run`
  therefore refuses a staged copy holding any file without a read grant, and
  a new check, `searches_in_scope`, verifies search paths. Prompts treat
  search hits as leads that must be read before use, and ingest searches for
  existing pages before creating new ones (upstream's "check what already
  exists").
- **Compact staged index.** Ingest workers read a copy of the index with
  headings, titles and paths only. On the deployment it measured 57.5 KB →
  32.0 KB, all 183 entries kept. Compile and query workers still get the full
  index, and the vault's index is unchanged.
- **Themes.** INDEX lines may name a theme, which `apply` files under a
  `### theme` heading in the section. A replacement without a theme keeps its
  place, and emptied themes are dropped. A series files its source entries
  under the capture's title, or `--theme`.
- **Primary-agent permissions.** `framework/vault-opencode.example.json`
  and installation step 2 give the operator agent path-scoped reads of
  `wiki/` and `raw/`, no edits to managed folders, CLI-only shell without a
  prompt, and grep and glob on ask, because a vault-root search reaches
  `.obsidian`. `opencode debug` resolves the example as intended.

Live evidence (OpenCode 1.18.33, previously approved route, synthetic fixture)
is in `docs/native-acceptance-trials.md`: the search probe passed 8/8 cases,
worker permission verification passed with search on and off, and a synthetic
ingest and query each passed every run check while using search. Not yet done:
installing the changed framework files and the permission profile into the
deployment (after its running textbook series), rerunning the researcher
evaluation there, and logically structured notes for long documents (A4).

Verification: 131 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Plan series for chapter compiles

The owner chose to reorganize long documents by chapter while keeping their
part notes as page-level evidence.

- **`series --plan`.** Runs an ordered JSON plan of ingest and compile items
  with the series retry policy. It resumes by skipping items whose `done_if`
  page exists. `file_inputs_under` re-files the inputs' existing index entries
  under a theme, keeping their text; the worker gives no INDEX lines for them.
- **Chapter pages.** The ingest skill's compile section defines a chapter
  source page: `raw` is the original document, the body holds the chapter's
  argument and a section map to its part notes, with one to three concepts and
  an up-link on each part note.

Verification: 132 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Automatic concept back-links

The deployment's textbook series stopped at part 79: its source page linked
the book's hub concept, a sources-only item may not touch concept pages, so the
back-link was missing (`not_reciprocal`), and the revision then failed the full
read of the 57 KB index. `normalize` now adds a LINKS back-link on an existing
concept or entity page that a proposed source page links, and reports it. The
compact staged index addresses the second failure.

Verification: 133 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Step budget and empty format revisions

Resuming the textbook series on the new code, parts 79 and 80 were recorded as
`no change` without source pages. The worker ran out of its 12 steps (search,
six figure reads and related pages). Its reply was a status message, and the
format-only revision had no proposal to restate, so it replied with NOTES only.
A format revision without a proposal now counts as a failed run, which gets a
fresh operation and otherwise stops the series. The default `steps` is 20,
because searches and figure reads use turns.

Verification: 134 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Compact index for named-input compiles; evaluation search

The deployment's first chapter compile failed twice on the full-read check of
the 66 KB index, although its second attempt produced a chapter proposal. A
compile given named inputs now gets the compact index like an ingest; compile
by topic and query keep the full index because they choose pages by
description. `tests/researcher_eval.py --search` grants the researcher grep
and glob on its staged copy and scores those calls, so evaluations can
compare index-only and search-enabled retrieval.

Verification: 134 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Chapter pages without the raw document

The first chapter compile on the deployment replied NOTES only: it treated the
unstaged PDF named as the chapter page's `raw` as a required read and would not
infer the chapter's page range. The series recorded it as `no change` and moved
on. The ingest skill now says the raw document need not be staged or read and
that the range comes from the part notes, marked approximate where needed. A
plan item whose `done_if` page was not created now stops the series.

Verification: 134 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Only required files must be read in full

The deployment's chapter plan applied chapters 1–7 and stopped at chapter 8:
the worker read the 100 KB log, which is optional, hit the read cap and treated
the prompt's complete-read rule as covering every file. The prompt now limits
that rule to the index, the contract and the inputs, which are what the
operator checks; other files, such as the log, may be read in part.

Verification: 134 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Two-way back-link repair

Chapter 8's compile cited individual part notes from a new concept page; the
part notes lacked the back-links, so the checker refused it after a revision.
The back-link repair now also covers concept and entity pages that link an
existing source page the proposal does not rewrite.

Verification: 134 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Declined plan items get one fresh attempt

Chapter 8 was declined again: the worker judged a 42-line concept page
"capped" and stopped. The prompt now says a capped read means continuing from
the next offset, never stopping, and a plan item that declines without
creating its `done_if` page gets one fresh operation before the series stops.

Verification: 134 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Back-links for every new source ↔ concept edge

Chapters 8–14 applied; chapter 15 stopped because the worker's LINKS lines
added part → concept links while its new concept page did not link those
parts. The repair now covers every source ↔ concept/entity link a proposal
adds, from pages or LINKS lines, and writes the back-link into the proposed
page when the proposal writes it.

Verification: 134 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Deployment follow-through and evaluation

Installed the changed framework files and the primary-agent permission profile
in the deployment (clean per-file upgrades, backups and a receipt kept
locally), finished the textbook's last 12 parts, and ran a private 22-item
chapter plan: 21 chapter pages and a back-matter page, 30 concepts, checker
clean. The researcher evaluation on the same 10 questions scored 9/10
index-only (the miss a scorer false negative, now fixed) and 8/10 with search
(two real misses: citing grep hits without reading them, and answering from
the contract without the index). Details are in the trials document.

Verification: 134 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Query citations must be read

The deployment evaluation found a search-enabled answer citing pages it had
seen only in grep output. `run` now checks every query: each `wiki/` page the
answer cites must have been opened with the read tool (`citations_read`,
failures listed as `unread_citations`), and `revise` gives the researcher one
retry to read those pages or drop the claims. The citation extractor moved
from the evaluation harness into `scripts/sb_runtime.py`, which both share.

Verification: 135 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Owner acceptance command

`sb_operator.py accept` appends one owner acceptance record naming, one bullet
each, every partial operation no earlier acceptance record names, with the
owner-stated level, sample and defects; `technical` keeps them partial. It
backs up the log and restores it if the checker fails. On the deployment the
owner recorded `sampled` acceptance (pages not itemized, no defects reported)
for all 130 pending operations; none remain partial and unaccepted.

Verification: 136 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Primary agent cannot load worker skills

Asked "what does the wiki say about…", the deployment's primary agent loaded
`second-brain-query` directly instead of the operator skill. In the vault root
that worker skill found no staged copy or contract and asked for a read scope.
The permission profile now denies both worker skills to the primary agent
(workers load them from their own profile), the worker skill descriptions say
they are worker-only, and the operator skill's description covers any question
about the wiki.

Verification: 136 offline tests pass; `git diff --check` passes; `opencode
debug agent` resolves the operator skill as allowed and both worker skills as
denied for the example profile.

## 2026-09-29 — Startup timeout for worker runs (H1)

`opencode run` occasionally stalls before starting a session and emits
nothing; the operator used to wait out the full per-run timeout (900 s on the
deployment) and then count a failed run. `run_role` now watches the event
stream: no output after 120 s means a startup stall, so the process is killed
and relaunched once, and a second stall raises "OpenCode did not start". A run
that has started keeps the normal timeout. Three offline tests use a fake
`opencode` script.

Verification: 139 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Drift guards only rewritten pages

The deployment's first synthesis was refused because another compile applied
while it ran: `apply` required the log and index to match their staged hashes,
though it appends the log record and merges index entries against the current
files anyway. A revision could not fix that and returned no pages. The drift
check now covers only pages a proposal rewrites whole, and `revise` refuses
when drift is the only problem, asking for a new stage.

Verification: 139 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Page limit counts written pages

The deployment's first synthesis (after a rerun with a 40-step budget for the
reading it needed) wrote one page plus 25 LINKS back-links and was refused as
26 pages over the limit of 20. Back-link lines are one-line appends, not pages
to review, and the owner set no per-operation cap on notes, so `max_pages` now
counts only pages a proposal writes whole.

Verification: 140 offline tests pass; `git diff --check` passes.

## 2026-09-29 — Default step limit 40

The first synthesis needed about 40 reads, so the default worker `steps` is
now 40 (and on the deployment). A worker that finishes earlier is unaffected.

Verification: 140 offline tests pass; `git diff --check` passes.

## 2026-09-30 — Status split, one place for test counts, knowledge-layer statistics

- **Split PLAN.md (D1).** Current state moved to a one-screen `STATUS.md`;
  dated entries to `docs/changelog.md`; the design decisions and decision
  register to `docs/decisions.md`; the execution history, upstream inventory,
  research coverage, planning notes and optional tracks T1–T5 to
  `docs/archive/planning-history.md`. `PLAN.md` keeps the objective,
  requirements, delivery approach, phases, validation and runbooks R0–R8.
  Section text moved unchanged.
- **One place for test counts (D2).** The README and PLAN.md no longer state a
  count; each change's result is recorded only in its changelog entry.
- **Statistics that tell a mirror from a knowledge graph (C4).**
  `vault_stats.py` (definitions v2) reports the knowledge-layer ratio
  (concept + entity + synthesis pages per source page) and links by type pair,
  first in the human report.

Verification: 140 offline tests pass; `git diff --check` passes.

## 2026-09-30 — One rule, one place; guarantees and limits

- **Prompts (D4).** The contract now holds content rules only; its file-safety
  and approval-workflow text moved to the operator, which enforces them. The
  ingest and query skills hold the procedure without restating the contract,
  the agent files bind the role and stop conditions, and the operator's
  generated prompt keeps read mechanics, operation facts and the reply format
  while dropping rules the skill owns. Worker instructions per ingest fell from
  about 4,560 to 2,650 words (the four worker files from 3,920 to 2,102).
- **Docs (D3).** New `docs/guarantees-and-limits.md` states once what checks,
  permissions and evidence establish. The chat-export guide is now a
  step-by-step how-to (1,662 to 429 words), with the converter specification
  moved unchanged to `docs/reference.md`. The statistics guide and
  `how-it-works.md` link the new page instead of repeating caveats.
- **Fixes.** Operation paths resolve before use (a relative path broke
  `revise`); the evaluation scorer accepts "does not answer" and "found no"
  abstentions; a duplicated closing sentence in the reference was removed.
- **Installed** on the deployment: both agent files, both worker skills, the
  contract and the notices, each a clean upgrade with a local backup.
- **Checks.** Synthetic ingest, compile (one revise) and query passed; search
  probe 8/8 in a traced rerun; deployment evaluation 9/10 index-only and 8/10
  with search, with no answer-quality regressions. Details in the trials
  document.

Verification: 141 offline tests pass; `git diff --check` passes.

## 2026-09-30 — Evidence links, hand editing and the live harness

- **Raw evidence is checked (C3).** The checker confirms with `lstat`, never
  opening a file, that each source's `raw` exists (`missing_raw`) and that local
  Markdown links, images and Obsidian embeds into `raw/` resolve
  (`missing_evidence`); other local Markdown links are unsupported
  (`markdown_link`). `normalize` turns an embedded image that does not exist
  into its caption and fixes a doubled `raw/raw/`.
- **Hand editing (D5).** `apply`, its post-apply check and `accept` now refuse
  only checker problems a proposal adds; problems already in the vault are
  counted as `existing`. Installation step 4 gives the Obsidian settings (absolute
  paths, wikilinks, attachments under `raw/`, frontmatter in source mode) and the
  operator guide a hand-editing section. Embeds of `raw/` files count as evidence.
- **Live harness (E1, E2).** The nine live drivers and probes moved to
  `tests/live/` with a README labelling them opt-in evidence and the native-trial
  drivers frozen. The probes close stdin for every subprocess, which was the
  cause of their "intermittent" timeouts, and the sandbox mounts `scripts/` and
  `tests/` under `/src`, which fixes the roles probe. Read 16/16, roles 25/25 and
  search 8/8 on OpenCode 1.18.33.
- **Deployment findings.** Three part notes have broken figure links, reported
  by the checker for the owner to fix.

Verification: 144 offline tests pass; `git diff --check` passes.


## 2026-09-30 — Owner identifiers out of the public repo; chat selection; closures

- **Identifiers (D6).** The frozen live drivers take the owner's primary agent
  and route from `SB_AGENT` and `SB_MODEL` and refuse to run without them, the
  trial folder from `SB_TRIAL_ROOT` (default: a folder in the system temp
  directory), and the OpenCode release from `SB_OPENCODE_VERSION` (default: the
  recorded 1.18.32). Docs, records and tests name "the owner's primary agent"
  and "approved route" instead. Checked locally: without the settings the
  drivers refuse; with the owner's values the full no-model preflight (staged
  corpus, profile, route, version and permission checks) passes. Older commits
  still contain the identifiers.
- **Chat selection (G1).** A conversation chosen with `--conversation-id` is
  converted whatever its length unless `--min-words` is given; the 150-word
  default applies to `--all`.
- **Closed:** B4 (practice documented in guarantees and limits), F4 (retired
  caveats listed under "Closed without further work" in STATUS.md); B3 and E3
  declined by the owner.

Verification: 145 offline tests pass; `git diff --check` passes.

## 2026-09-30 — OpenCode issues reproduced and drafted (F3)

Both behaviours reproduce on OpenCode 1.18.33 with a fake provider: `opencode
run --agent` with an unknown name runs the default agent and exits 0, and
custom-command arguments are expanded (`@file` inlined, `` !`cmd` `` executed)
regardless of the command agent's `read` and `bash` permissions. OpenCode's
security policy bans AI-generated security reports and puts permission bypasses
out of scope, so both are drafted as ordinary bug reports for the owner to
review and post; the drafts are kept outside this repository. The operator is
unaffected: it verifies the role with `opencode debug` before each run and never
uses command wrappers.

## 2026-09-30 — Two series stoppages fixed

A live source-page series stopped twice on predictable worker slips.

- **Manifest path.** The worker prompt listed "the manifest" as readable
  without a path; a worker guessed `raw/manifest.json`, was denied, and
  returned no change. The prompt now names `operation.md` and marks it
  optional.
- **Markdown page links.** A worker linked the previous series item as
  `[Title](wiki/sources/x)`; the checker rejects Markdown links to pages, and
  the retry repeated the mistake. `apply` now converts such links into
  wikilinks before checking and reports each under `fixes`.

Verification: 146 offline tests pass; a dry-run apply of the failed live
proposal passes with the one conversion reported. The worker's other slip,
inferring a domain ID from the series position, is a task-wording issue and
is not changed here.

## 2026-09-30 — Index-only proposals

A compile whose only change was a Gaps entry in the index was refused as
"proposal has no pages", and a revision could not change that. `apply` now
accepts a proposal with INDEX entries and no pages; one with neither is still
refused. The index and log are written and undone as with any operation.

Verification: 147 offline tests pass; a dry-run apply of the refused live
proposal passes with no problems.

## 2026-10-01 — Exact read ranges for large files

The compact staged index reached 54.9 KB on the deployment (423 lines), over
OpenCode's roughly 50 KB read cap again. Some workers read it once, got a
capped output and did not continue, so a concept series stopped after two
failed attempts. The prompt now gives the exact `offset`/`limit` calls for
any required file over 40 KB, instead of relying on the worker to page.

Verification: 148 offline tests pass. For the failed live operation the
prompt now lists `offset=1 limit=350, offset=351 limit=73`. Not yet
confirmed in a live run.

## 2026-10-01 — Generated index and worker catalogs (P6)

Owner-approved after the deployment's index passed the read cap a second
time and its hand-merged Gaps section had accumulated stale and repeated
lines. The index stays one page.

- **Generated index.** `scripts/wiki_index.py` builds `wiki/index.md` from each
  page's `title`, `summary`, `theme`, `gaps` and `part_of`; `apply` rebuilds it
  after every operation and `undo` rebuilds it after restoring. Workers no
  longer send INDEX lines (old ones are ignored and reported); a GAPS section
  adds a gap to an existing page. The checker reports `index_stale`,
  `missing_summary` and invalid `part_of`, and no longer requires a part that
  its chapter links to be listed itself.
- **Catalog.** Workers read `catalog.md` (at most 24 KB: the inputs'
  neighbours, their theme, task matches, then every concept, entity and
  synthesis title) instead of the index, which is no longer staged. The
  researcher evaluation does the same, with `--full-index` for comparison.
- **Guards and repairs.** A new page duplicating an existing title or alias is
  refused. A missing summary is filled from the previous version or first
  sentence; rewrites keep `theme`, `gaps` and `part_of`; a plan item with
  `parts` sets `part_of` (replacing `file_inputs_under`).
- **Migration.** `migrate-index` stages summaries, themes and `part_of` from a
  hand-written index plus `gaps.json` for the owner; `--apply` writes it with a
  receipt for `undo`. `rebuild-index` regenerates after hand edits. The
  contract fixture was converted with it.

Verification: 161 offline tests pass; `git diff --check` passes. No live
worker run has used the catalog yet, and the deployment is not migrated.

## 2026-10-01 — P6 on the deployment

- **Install.** The 12 installed framework files matched earlier public
  versions (no local edits) and were replaced per file, with backups and a
  hash manifest outside the vault.
- **Migration.** 296 pages gained summaries from their index entries, 172
  their theme, and 90 capture parts `part_of` their chapter; 7 parts of a
  book without chapter pages stay listed. Of 89 distinct Gaps lines, the owner
  kept 11 on their pages and dropped 78 stale "parts N–90 remain uncovered"
  lines. Checker clean afterwards; the index went from 92.6 KB to 54.7 KB.
- **First live runs on the catalog.** The three concept items of a plan that
  had stopped on the index read cap ran on the new flow: 3/3 applied on the
  first attempt, no retries, checker clean (299 pages, 1,291 links). Their
  catalogs were about 20 KB, read in one call.

Not yet done: the researcher evaluation rerun (its private question file is
no longer available), and ingest and query runs on the catalog.

## 2026-10-01 — Researcher evaluation on the catalog; synthesis on the deployment

- **Evaluation.** A new private set of 14 questions (10 to answer across
  four documents, 4 to abstain on, one of them about the unresearched D-12
  domain) ran in catalog mode with search, 12 steps, on OpenCode 1.18.33:
  12/14 after a scorer fix. Every answer question found its expected page and
  terms (10/10), all abstentions were correct, and the catalog was read first
  14/14; mean 1.9 content pages and about 20 s per question. The two failures:
  one failed tool call during a correct answer (`tools_ok`), and one correct
  abstention citing a page seen only in search results (`citations_read`,
  which operator query runs retry). Not comparable with the 2026-09-29 set.
- **Scorer fix.** Emphasis is dropped before the abstention check, so "does
  **not** provide" counts; "provide" joins the abstention verbs.
- **Invalid comparison.** A `--full-index` run is not reported: the installed
  query skill tells the researcher to read `catalog.md`, which that mode does
  not stage, so several runs stopped. A fair comparison needs the pre-P6 skill.
- **Synthesis.** The owner's primary agent compiled six synthesis pages
  through the operator in one non-interactive run: 6/6 applied with no
  revisions, checker clean (305 pages, 1,396 links).
- **Found: vault permission patterns.** In a vault that is not a git
  repository, OpenCode's worktree is `/`, so the relative read and edit rules
  from `framework/vault-opencode.example.json` never match: reads fall through
  to `ask`, and the `edit` denials for `wiki/**`, `raw/**` and `.opencode/**`
  fall through to `ask` instead of `deny`. Not yet fixed; needs a runtime probe.
