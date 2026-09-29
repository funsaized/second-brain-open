# Review backlog

> Proposals from a review on 2026-09-28 of commit `f6786d2` and a read-only look
> at one owner deployment. Nothing here is approved work. PLAN.md's gates still
> apply. **Owner decision** marks items that change a recorded policy or need
> approval before anyone acts on them.

## Status update (2026-09-28)

- **Closed by the owner without further checks:** F1 and F2.
- **Implemented:**
  - C1: the checker now reports leftover template placeholders, pages missing
    from the index, and one-way source ↔ concept/entity links.
  - A3: owner acceptance levels.
  - A2: the researcher evaluation. It passed 10/10 on the deployment wiki.
- **C2 and A3 on the deployment:** cleaned control pages and a `sampled`
  acceptance record are prepared and verified against a staged copy. The owner
  applies them locally.
- **Operator (B1, B2):** delivered on the "agent as operator" model. The
  owner's primary agent ingests autonomously through the
  `second-brain-operator` skill and the `sb_operator.py` CLI. E1 and D4 are
  partly done: shared helpers moved to `scripts/`, and the worker prompts were
  rewritten for the operator flow.
- **URL ingest (2026-09-29):** delivered. The operator captures a URL's main
  content without a model, and a sandboxed worker ingests it. `pending` plus
  catch-up processes new clips. The ingest skill adopts upstream's calibration.
- **PDF ingest (2026-09-29):** delivered. Covers URLs or dropped files, page
  locators, OCR for scans, automatic parts for long documents, and paper mode.
- **Figures (2026-09-29):** delivered. Pages with figure captions are rendered
  and read by the vision-capable worker. Captures of any kind split within
  OpenCode's read limits.
- **Concept compile hardening (2026-09-29):** delivered. Index changes are
  merged entries, back-links are LINKS patches, drop/shrink guards are in
  place, compile works by topic, and workers read by relative path.
- **New item H1:** `opencode run` occasionally stalls before starting a
  session (no events, no database writes, no operation staged). Seen twice, in
  runs without `--print-logs`, once while another session of yours was active.
  Next: reproduce it and add a startup timeout to the operator skill's
  guidance.
- **Long-document ingest (2026-09-29):** made reliable with the tolerant
  parser, format-only revise, mechanical repairs, and a resumable,
  backgroundable `series` command.
- **Large-file reads (2026-09-29):** delivered. Workers read files over the
  read cap in ranges, and coverage is checked line by line.
- **New item H2:** index growth. Every operation reads the whole index, so
  token cost grows with the wiki. Options: split the index into per-type
  pages behind a short hub, or stage a compact index (titles and paths) for
  workers.
- **Suggested next step:** A1. Compile the first concept pages in the
  deployment with the operator, then rerun the A2 evaluation.

## Status update (2026-09-29, later)

- **Owner decisions.** Keep `wiki/index.md` as one page; no split into
  per-type or topic pages. No cap on notes per operation (A4), but notes
  should follow the source's logical structure. Let the running textbook
  series finish on the current code.
- **H2: delivered without a split.** Ingest workers read a compact staged
  index (titles and paths only). On the deployment that is 57.5 KB → 32.0 KB
  with all 183 entries, back under the single-read cap. INDEX lines can name a
  theme, filed as a `### theme` heading inside the section, and a series
  files its parts under the document's title.
- **B5: delivered, in the staged copy.** Workers get grep and glob over the
  staged copy. A Bubblewrap probe shows they can't leave it. Grep sees every
  file there, hidden ones included, so `run` refuses a copy with ungranted
  files. A2 had found search unnecessary at 110 notes; it is now in place for
  the larger wiki and for the "does this page already exist?" check.
- **B4: narrowed.** The staged copy plus the corpus check is the practiced
  confinement for workers; OS isolation remains probe-only.
- **Primary-agent permissions.** Installation step 2 and
  `framework/vault-opencode.example.json` define the operator agent's vault
  permissions. The deployment still has only the `external_directory` allow.
- **Done since:** installed on the deployment; the textbook finished and was
  reorganized into 21 chapter pages plus back matter with 30 concepts (A1 for
  the textbook, A4 per-chapter notes); A2 rerun: 9/10 index-only (effectively
  10/10 after a scorer fix), 8/10 with search.
- **Query citations:** delivered. `run` now fails a query whose answer cites
  pages the researcher never opened (`citations_read`), and `revise` gives it
  one retry. The evaluation stays an optional, manually run check; extending
  its question set was dropped by the owner.
- **Next.**
  1. Series-level acceptance record, and a series startup timeout (H1).
  2. The first synthesis page (still 0).

## How the review was done

- Read README, PLAN.md, all of `docs/`, `framework/` and `scripts/`, and the
  layout and interfaces of `tests/`. Ran `python3 -m unittest discover -s tests`:
  83 tests pass.
- Deployment (read-only): compared the installed machinery hashes with
  `framework/`, read the control pages and one source note, and ran
  `link_check.py` and `vault_stats.py`. There were no OpenCode or model runs and
  no writes. Below are aggregate facts about an ingest of the public upstream
  guide. No personal content is included.
- Not covered: a line-by-line audit of `docs/synthetic-acceptance.md` and of
  the live drivers' internals.

## Summary

The public machinery is careful, well tested and unusually honest about what its
evidence proves. The real loop is the weak side: it has barely run. When it did
run, it skipped most of the prescribed ceremony, and it produced only source
notes. The next stage should focus on real use (a concept layer, real queries,
acceptance that can finish) and on turning the procedures people actually
followed into supported tools. More safety campaigns and more prose should
wait.

Deployment facts (sanitized):

- One capture of the upstream public guide became **110 source notes (~93k
  words)**. There are **0 concept, 0 entity and 0 synthesis pages**.
- The checker reports 110 pages, 247 links (source→source navigation carried
  over from the guide) and 2 errors: the pre-existing index and log have no
  frontmatter. The checker will exit 1 on every run until that changes.
- Both logged operations are `partial`. Owner content acceptance is pending
  for all 110 notes.
- The operator assembled and applied the proposals, with native edit tools
  denied. So the per-edit `once` approval path, which the docs describe as the
  write path, was not used.
- The installed machinery matches HEAD. OpenCode is now **1.18.33**, but all
  native evidence is for 1.18.32.
- There is no version control in the vault root. Backup status can't be
  verified from this side.

## What works well (keep)

1. **Public/private boundary.** Framework files stay inert, distribution is
   one-way and per file, and notices plus the adaptation map are preserved.
   Tests enforce the ignore rules and the notice text.
2. **Deterministic stdlib tools with real safety engineering.** Descriptor walks
   use `O_NOFOLLOW`, hardlinks are refused, files are created exclusively,
   converter output is versioned by digest, and every tool has a dry run. JSON
   reports are stable and carry `schema_version`, definitions and as-of.
3. **Evidence taxonomy.** Static, driver-applied, native and owner-accepted
   results are kept apart, and failures stay on the record. This is rare and
   worth protecting.
4. **Empirical OpenCode findings.**
   - Command preprocessing expands `@file` and shell text before role
     permissions apply.
   - Permission keys are worktree-relative.
   - A PWD/cwd mismatch can make OpenCode inspect one directory and run in
     another.
   - A nonexistent `--agent` falls back to another agent without an error.

   These findings are worth more than most of the code.
5. **The contract.** It requires claim-level locators, keeps contradictions,
   separates source/author/inference, and keeps unknowns unknown. The
   vent-trial fixture plus the tutorial teach all of this in ten minutes
   without a model.
6. **Feedback from real use.** The content-preservation follow-up (`415d72b`)
   came from actual use. That is the right loop.
7. **Precise raw evidence in the deployment.** Each note locates its source by
   embedded-JSON selector plus heading, backed by a SHA-256 capture manifest.

## Where it is overcomplicated

- **Ceremony that real use skips.** Per-edit `once` approvals and an
  OS-isolated frozen corpus are documented as the path. The actual ingests used
  operator application and ordinary-auth overlays. See B2 and B4.
- **Documentation mass and hedging.**
  - PLAN.md is 1,085 lines.
  - Docs, skills and the contract total about 16k words, with about 370
    occurrences of "not".
  - The test count appears in five places with three different values.

  See D1–D3.
- **Prompts state the rules three times.** They also include filesystem duties
  the model cannot perform. See D4.
- **Operational tooling lives in `tests/`.** It is bound to one owner's agent,
  model and temp directory. See B1, E1 and D6.
- **Scenario-specific trial modes** preserve evidence but can't be reused. See
  E2.

## Backlog index

| ID | Title | Type | Pri | Size | Owner decision |
|---|---|---|---|---|---|
| A1 | Compile a first concept layer from existing sources | Implement | P0 | M | — |
| A2 | ✅ Evaluate the researcher on the real wiki | Verify | P0 | S | — |
| A3 | ✅ Define owner acceptance that can finish — deployment record awaits owner | Decide | P0 | S | Yes |
| A4 | Collection captures — decided: no cap, logical notes; themes delivered, per-chapter notes pending | Decide | P1 | S | Yes |
| A5 | Ingest one non-meta source tied to actual goals | Verify | P1 | S | Yes |
| B1 | ✅ Ship an operator launcher (manifest → overlay → verify → run) — `sb_operator.py` | Implement | P0 | M | — |
| B2 | ✅ Make "propose → operator apply" the primary write path — agent as operator | Simplify | P0 | M | Yes |
| B3 | Install/upgrade planner | Implement | P1 | M | Yes |
| B4 | Reconcile the isolation requirement with practice — narrowed by the staged-copy corpus check | Decide | P1 | S | Yes |
| B5 | ✅ Scoped search inside a confined corpus — grep/glob in the staged copy | Decide | P2 | M | Yes |
| C1 | ✅ Residue, index-completeness and reciprocity checks | Implement | P0 | S | — |
| C2 | ✅ Stop permanent exit 1 on legacy controls — deployment cleanup awaits owner | Improve | P0 | S | — |
| C3 | Validate raw evidence links; report Markdown links | Improve | P1 | S | — |
| C4 | Stats that tell a mirror from a knowledge graph | Improve | P1 | S | — |
| C5 | Advisory log-record linter | Improve | P2 | S | — |
| D1 | Split PLAN.md | Simplify | P1 | M | — |
| D2 | One place for test counts and status | Simplify | P1 | S | — |
| D3 | Cut hedging; move evidence narrative out of how-tos | Simplify | P1 | M | — |
| D4 | Prompts: one rule, one place, no operator-only content | Simplify | P1 | M | — |
| D5 | Obsidian link-format guidance | Improve | P1 | S | — |
| D6 | Generalize owner-specific identifiers | Simplify | P2 | S | — |
| E1 | Separate the live harness from unit tests | Simplify | P1 | S | — |
| E2 | Freeze scenario-specific driver modes | Simplify | P2 | S | — |
| E3 | Offline CI | Implement | P2 | S | Yes |
| F1 | ✅ Re-verify runtime behavior on OpenCode 1.18.33 — closed by owner | Verify | P0 | S | — |
| F2 | ✅ Confirm a deployment recovery point — closed by owner | Verify | P0 | S | Yes |
| F3 | Report the two OpenCode safety issues upstream | Decide | P2 | S | Yes |
| F4 | Retire caveats that will not be acted on | Simplify | P2 | S | — |
| F5 | Decide how to do the P4 project round trip | Decide | P1 | S | Yes |
| G1 | Explicit chat selection vs `--min-words` | Improve | P2 | S | — |

Sizes are rough: S is under a day and M is one to three days.

## Suggested order

1. **F1, F2.** Cheap checks that protect what already exists.
2. **C1, C2.** The checker catches what no human will check across 110 notes.
3. **A3 → A2 → A1.** Let acceptance close, measure retrieval, then build the
   concept layer.
4. **B1 + B2.** Make the loop runnable without test code, before the next
   batch of ingests.
5. **D1–D4.** Simplify docs and prompts. Do D4 after B2 so the prompts change
   (and native evidence resets) only once.

Take everything else as needed.

---

## A. Close the real-use loop

### A1. Compile a first concept layer from existing sources — P0

**Problem.** The deployment's wiki is a faithful Markdown mirror of one guide.
The contract's main value has not been tested on real data: concepts that
connect sources, disagreements kept side by side, and synthesis. The ingest
skill takes one raw capture as input. No documented operation derives concepts
from source notes that already exist.

**Proposal.** Add a *compile* operation as a section of the ingest skill, not a
new role.

- **Input:** owner-selected existing source notes plus a concept question.
- **Output:** proposed concept, entity or synthesis pages that link claims into
  the source notes, reciprocal links added to those notes, and index/log
  updates.

Run it on 5–8 core ideas from the guide, such as the two layers, source versus
concept, contradiction handling, index/log and linking rules.

**Done when.** At least five concept pages exist with claim-level links, and
the reciprocity check passes (C1). If the guide contains a real internal
disagreement, one synthesis page records it.

### A2. Evaluate the researcher on the real wiki — P0 · ✅ Done

**Resolution (2026-09-28).** `tests/researcher_eval.py` stages a copy of the
wiki without vault instructions and verifies exact read grants. It asks each
question in its own native run and scores:

- index-first reads
- whether every cited page was actually read
- expected pages and terms
- `Read:` / `Not covered:` sections
- abstention on unsupported questions
- zero writes

See `docs/researcher-evaluation.md`. Both runs used OpenCode 1.18.33 through
the previously approved route:

- **Invented fixture:** 3/3 passed.
- **Deployment wiki:** 10/10 passed. The set covered six single-page, two
  cross-page and two unanswerable questions.

On the deployment, the researcher read a mean of 1.1 content pages per
question, took about 27 s and used 13k–27k input tokens. Index-only routing
works at 110 notes, so B5 (search) is not needed now. The question set and
answers stay local. Rerun the same set after A1 to measure the concept
layer's effect.

**Problem.** Nothing shows that index-first retrieval works at 110 notes and
~93k words. All public query evidence uses a five-page fixture. The researcher
cannot search, so its recall depends on the index descriptions.

**Proposal.** Write 8–10 questions whose answers are known: single-page,
cross-page and unsupported. For each, record:

- whether each citation is correct
- which pages were read
- time and tokens used
- whether it abstained where it should

Keep transcripts local.

**Done when.** A local scorecard exists and settles B5, the search decision.

### A3. Define owner acceptance that can finish — P0 · Owner decision · ✅ Done (deployment step pending)

**Resolution (2026-09-28).** The contract, log template and ingest skill define
three acceptance levels: `technical`, `sampled` and `full`. `completed` requires
`sampled` or `full`, recorded as a new log record naming the accepted
operations, the sample and any defects. The owner reports a partial review with
no defects. The prepared deployment log appends a `sampled` acceptance record
that completes the three pending operations; it is applied with the C2 files.

**Problem.** Both deployment operations are `partial` while they wait for
claim-by-claim owner acceptance. For 110 notes that review will not happen, so
nothing ever reaches `completed` and the status turns into noise.

**Proposal.** Define three acceptance levels in the contract and log template:

- **technical:** checker passes and hashes match
- **sampled:** the owner reads k random notes plus every note involved in a
  contradiction, and records the defects found
- **full:** every note is reviewed

For learning or reference sources, let `completed` follow sampled acceptance.
Record it in the log with the sample list and defect rate.

**Done when.** The deployment's first operation can close honestly.

### A4. Collection captures and batch size — P1 · Owner decision

**Problem.** The plan says to process one real source and stop before backfill.
The first real ingest turned one capture into 110 source notes in a single
operation. The contract says a source page identifies "one artifact/version".
It doesn't say how one capture holding many articles maps to notes.

**Proposal.** Document a *collection* pattern: one raw capture with its
manifest, and one source note per sub-article carrying a sub-locator. A hub
note is optional. Cap each proposal at about ten notes so review stays
feasible, which matches upstream's batch guidance.

**Done when.** The contract and skill include the rule, and the next bulk
capture follows it.

### A5. Ingest one non-meta source tied to actual goals — P1 · Owner decision

**Problem.** The only real source is this framework's own upstream guide. That
is good for dogfooding, but it tests nothing about the owner's domain.

**Proposal.** Pick one short source from current work or learning priorities.
Run the full loop, ending with a query that combines it with guide-derived
concepts from A1.

**Done when.** One domain source exists with at least one concept linking it.

## B. Make the workflow operable without the test harness

### B1. Ship an operator launcher — P0 · ✅ Done

**Resolution (2026-09-28).** `scripts/sb_operator.py` handles `stage`, `run`,
`revise`, `apply`, `undo` and `status`. The shared runtime helpers moved from
the test drivers into `scripts/sb_runtime.py`:

- the tool-denying overlay
- `opencode debug` verification
- `validate_scope`
- native runs

The worker's route, version and limits come from the vault's
`.opencode/second-brain/operator.json`, not hard-coded values.

**Problem.** The installed roles deny all reads. The grants come from pieces
that live only in test code:

- an `OPENCODE_CONFIG_CONTENT` overlay, composed and checked with
  `opencode debug` in `tests/native_chat_proposal.py:130-211`
- `validate_scope` in `tests/runtime_read_probe.py:19`

`docs/manual-loop.md` gives a table of grants but no syntax. A new user can't
run the loop, and the owner depends on test code to run it.

**Proposal.** Add `scripts/sb_run.py`, stdlib only:

1. Read a small operation manifest: role, model, read paths and optional edit
   paths.
2. Validate the scope: no links, hardlinks or traversal.
3. Build the overlay.
4. Check the effective permissions and confirm that the agent and skill exist.
5. Launch `opencode run --agent`.

Pass the agent and model as arguments; don't hard-code them. `--dry-run` prints
the overlay without credentials.

**Done when.**

- `docs/manual-loop.md` uses the launcher.
- The existence check blocks the missing-agent fallback. That scenario is
  waived today but cheap to prevent.
- Unit tests run against a fake `opencode` binary.

### B2. Make "propose → operator apply" the primary write path — P0 · Owner decision · ✅ Done

**Resolution (2026-09-28).** The owner chose option 1: the agent is the
operator. The owner's primary agent uses the new `second-brain-operator` skill
to run the CLI. The workers stay deny-by-default and proposal-only.

`apply` refuses the whole proposal unless every check passes:

- allowed `wiki/` paths only
- the page cap
- no drift since staging
- a single `partial` log record
- the checker clean on the result

It backs up replaced files for `undo` and undoes itself if the post-write check
fails. `revise` gives the worker one retry with the refusal reasons.
Unattended runs need an `external_directory` allow for the CLI and workdir in
the vault's `opencode.json`.

**Problem.** Every real and synthetic ingest wrote through an operator or
driver. The one exception is the bounded four-file native trial, which needed a
custom approval handler (`tests/native_chat_handoff.py`). The per-edit `once`
flow can't handle 10–110 files, and it requires the ingestor to hold edit
grants.

**Proposal.** Make the ingestor read-only by design (`edit: deny`). It emits a
framed-Markdown proposal packet; `native_chat_proposal.py` already defines that
format. A new `scripts/sb_apply.py`:

- validates paths against the manifest
- checks preimage hashes
- writes with exclusive create or atomic replace
- runs the checker
- appends a log record with receipts

Keep native edits as an optional, documented mode.

**Done when.** One real ingest uses this path end to end. The ingestor's
permissions shrink, and per-edit approval leaves the main path in the docs.

### B3. Install/upgrade planner — P1 · Owner decision

**Problem.** Installation is a manual per-file procedure: hashes, exclusive
create and three-way review. The bootstrap and a later upgrade were done by
ad hoc means; the installed files match HEAD while the public record names
`1e987fd`.

**Proposal.** Add `scripts/sb_install.py` with two modes:

- **`plan`** prints each manifest row with its status: absent, identical,
  locally modified, upstream changed or conflict.
- **`apply`** only creates absent files, or replaces files whose hash equals
  the recorded installed postimage. It writes a local install manifest.

This is not a sync: it never deletes, never copies directories and never works
in reverse.

**Done when.** An upgrade between two revisions is one plan plus one apply,
with a receipt.

### B4. Reconcile the isolation requirement with practice — P1 · Owner decision

**Problem.** The docs require a frozen, link-rejecting, OS-isolated corpus
before any private data is processed. The Bubblewrap profile exists only in
the probes. The live trials ran under ordinary authentication with an overlay,
and their report says "This is not filesystem isolation". The deployment
ingest's own log doesn't show isolation either.

**Proposal.** Choose one:

- **(a)** Ship the isolation launcher as part of B1.
- **(b)** Document two tiers:
  - *overlay mode* uses tool permissions only and is acceptable for public or
    low-sensitivity sources.
  - *isolated mode* is required for sensitive sources.

  State which tier each deployment uses.

**Done when.** The docs describe what is actually practiced, and no stated
requirement goes unmet.

### B5. Scoped search inside a confined corpus — P2 · Owner decision

**Problem.** `grep` and `glob` are denied because their permissions match the
pattern, not the files returned. Retrieval is therefore index-only.

**Proposal.** If A2 shows misses, allow search only in isolated mode (B4a).
There the corpus contains nothing secret, so pattern-level permission is
enough.

**Done when.** A rerun of A2 shows better recall, and the confinement test is
repeated.

## C. Deterministic checks the contract already requires

### C1. Residue, index-completeness and reciprocity checks — P0 · ✅ Done

**Resolution (2026-09-28).** `scripts/link_check.py` now reports three new
error kinds:

- `placeholder`: leftover `{{…}}` text in metadata, or in the body outside code.
  HTML comments count.
- `not_indexed`: a content page that `wiki/index.md` doesn't link. Checked only
  when the index exists.
- `not_reciprocal`: a source ↔ concept/entity link without its back-link,
  reported on the page that lacks it.

Four new tests cover them. The contract fixture stays clean, and the deployment
has no new findings.

**Problem.** The contract requires three things:

- no placeholder residue
- every page listed in the index
- reciprocal source ↔ concept/entity links

These are checked only against the fixtures (`tests/test_contract.py:92`). No
human will check them across 110 notes.

**Proposal.** Add them to `link_check.py`:

- **Errors:** `{{…}}` residue outside fences and comments, and pages missing
  from the index.
- **Warnings:** missing reciprocal links.

**Done when.** The fixture assertions move into the checker's tests, and a
deployment run reports these diagnostics.

### C2. Stop permanent exit 1 on legacy controls — P0 · ✅ Done (deployment step pending)

**Resolution (2026-09-28).** By owner direction, non-conforming historical
control pages are cleaned up rather than excused, so the checker stays strict.
Normalized `wiki/index.md` and `wiki/log.md` were prepared for the deployment:

- contract frontmatter on both pages
- `date — operation — status` log headings
- index sections in template order
- stale gap notes removed

A staged copy with those files checks clean (exit 0). Writing them into the
private vault was blocked by the session's permission guard, so the owner
applies them locally.

**Problem.** The contract says not to rewrite pre-existing notes. The checker
still reports an error when a pre-existing index or log has no frontmatter
(`scripts/link_check.py:60`, `:157`). The deployment therefore exits 1 on every
run, and people learn to ignore exit 1.

**Proposal.** Report missing control frontmatter as a `legacy_control` warning.
Keep the error when frontmatter is present but malformed. An owner-approved
one-time normalization is the alternative.

**Done when.** A clean deployment can reach exit 0.

### C3. Validate raw evidence links; report Markdown links — P1

**Problem.** Two evidence gaps:

- The `raw` field is only format-checked.
- Relative Markdown links, which deployment source notes use to point at raw
  captures, are silently ignored: the `TOKEN` regex only matches wikilinks
  (`scripts/link_check.py:29`). They are neither validated nor reported.

**Proposal.**

- Check that `raw` exists using `lstat` only; never open the capture.
- Report local `[text](path)` links: validate them when they point under
  `raw/`, otherwise flag `unsupported_markdown_link`.

### C4. Stats that tell a mirror from a knowledge graph — P1

**Problem.** The deployment's metrics look respectable: 247 links, 13.6% inbound
orphans and a largest component holding 67% of pages. Yet there are zero
concepts, and every edge is source→source navigation copied from the guide.

**Proposal.** Add edge counts by type pair and a knowledge-layer ratio:
(concept + entity + synthesis) / source. Show both first in the human report.

### C5. Advisory log-record linter — P2

**Problem.** The deployment log mixes three formats: one-liners, `##` records,
and a `###` record nested under the previous `##`. That makes parsing for
reconciliation unreliable.

**Proposal.** Add an advisory check for the heading
`## YYYY-MM-DD — operation — status`, using the status words from A3. It never
rewrites the log.

## D. Simplify docs and prompts

### D1. Split PLAN.md — P1

**Problem.** PLAN.md is 1,085 lines. It mixes current status, the execution
history, a research inventory of 18 skills and 72 commands, eight runbooks,
five optional-track runbooks and the decision register. Current status fills
the first 75 lines; the rest is rarely needed.

**Proposal.** Split it three ways:

- **`STATUS.md`:** current status plus this backlog, 150 lines or fewer.
- **`docs/decisions.md`:** the decision register and technical gates.
- **`docs/archive/`:** the execution history, upstream inventory and T1–T5
  runbooks. Alternatively, drop T2–T5 and link to upstream.

**Done when.** A new contributor finds the current status on one screen.

### D2. One place for test counts and status — P1

**Problem.** The test count appears in five files with three values:

| File | Count |
|---|---|
| `README.md:101` | 83 |
| `PLAN.md` (three places) | 83 |
| `docs/backup-restore.md` | 82 |
| `docs/native-acceptance-trials.md` | 76 |

Every change needs four or five edits.

**Proposal.** Record counts only in dated evidence entries. The README should
just say to run the suite.

### D3. Cut hedging; move evidence narrative out of how-tos — P1

**Problem.** About 370 uses of "not" across roughly 16k words. Most paragraphs
end by listing what something isn't, which buries the instructions. Evidence
history also sits inside how-to guides: the `dingus` live rehearsal and the
bootstrap record are in `docs/manual-loop.md`.

**Proposal.** Write one *Guarantees and limits* reference page. How-to guides
state their steps positively and link to that page once. Move the evidence
narrative into the evidence docs.

**Done when.** `docs/manual-loop.md` is a step list of about two screens.

### D4. Prompts: one rule, one place, no operator-only content — P1

**Problem.** The agent, skill and contract (about 2,900 words together) each
restate the same rules: raw immutability, grants, preflight, and
symlink/hardlink/frozen-corpus handling. The model cannot check hardlinks or
freeze a corpus. Those are operator duties, so in the prompt they cost tokens
and dilute attention.

**Proposal.** Give each file one job:

- **Agent:** the role binding, "load the skill", and stop conditions, in about
  ten lines.
- **Skill:** the procedure.
- **Contract:** the content rules.

Move the filesystem-preparation text to the operator docs. Changing the prompts
resets native evidence, so re-run one synthetic ingest and query afterwards.

**Done when.** Prompt word count drops about 40%, and a synthetic trial passes
again.

### D5. Obsidian link-format guidance — P1

**Problem.** The checker accepts only `[[wiki/…|Label]]` links, which use the
path from the vault root. Obsidian's default for new links is the shortest
path, usually a bare basename, which the checker reports as unsupported.
`docs/installation.md` doesn't mention the setting.

**Proposal.** Document the Obsidian settings under Files & links: set *New link
format* to "Absolute path in vault" and turn on *Use [[Wikilinks]]*. The other
option is to let the checker accept unique basenames with a warning.

### D6. Generalize owner-specific identifiers — P2

**Problem.** Public code and docs contain one owner's primary-agent name, model
route and `/tmp/opencode/...` trial directories:

- `tests/native_chat_proposal.py:26,164,346`
- `docs/native-acceptance-trials.md:5,72-78`

The drivers refuse to run from any other base directory.

**Proposal.** Take these values from CLI arguments or environment variables,
with no defaults. Move trial paths into local records.

## E. Test and harness hygiene

### E1. Separate the live harness from unit tests — P1

**Problem.** `tests/` mixes 13 unit-test modules with about 2,200 lines of live
drivers and probes. Unit tests import from the probes:
`test_scope_and_distribution.py` gets `validate_scope` from
`runtime_read_probe.py`.

**Proposal.** Move the shared safety helpers into `scripts/` as part of B1.
Move the drivers to `tests/live/` or `harness/`, and label them evidence-only.

### E2. Freeze scenario-specific driver modes — P2

**Problem.** Some driver modes fit exactly one scenario:

- `--resume-trial` accepts only a one-edit interruption with exactly three
  pending patches.
- `--assess-only` and `--verification-only` replay a single trial.

They preserve evidence, but nothing else can reuse them.

**Proposal.** Mark these drivers as frozen evidence harnesses that get no new
features. Build future recovery on B2's apply tool.

### E3. Offline CI — P2 · Owner decision

**Problem.** There is no CI, even though the offline suite needs no secrets.

**Proposal.** Add a GitHub Actions workflow with read-only permissions and no
secrets. It runs `unittest` and `git diff --check` on push and on pull
requests.

## F. Verify

### F1. Re-verify runtime behavior on OpenCode 1.18.33 — P0 · ✅ Closed

**Resolution (2026-09-28).** Closed by the owner without re-verification. The
recorded native evidence remains dated to 1.18.32; later runs on 1.18.33 must
name the version they used.

**Problem.** OpenCode 1.18.33 is installed. All native evidence was gathered on
1.18.32: worktree-relative keys, wrapper preprocessing and the missing-agent
fallback.

**Proposal.** Re-run `tests/runtime_read_probe.py` and
`tests/runtime_roles_probe.py`. They use a fake provider, so they make no
provider calls. Record the results. If behavior changed, pin the version or
turn off autoupdate in the operator profile.

### F2. Confirm a deployment recovery point — P0 · Owner decision · ✅ Closed

**Resolution (2026-09-28).** Closed by owner decision. No backup requirement is
added for the deployment; this is recorded as an accepted risk, not as a
verified backup.

**Problem.** Two operations wrote or rewrote more than 100 notes. There is no
version control in the vault root, and the status of the R6A backup policy
isn't visible from the public side.

**Proposal.** Confirm locally that a restorable backup exists. Consider a
local-only private Git repository for the vault, with no remote. It is the
cheapest way to diff and roll back agent-generated bulk changes. This is
decision D6 in PLAN.md's register.

### F3. Report the two OpenCode safety issues upstream — P2 · Owner decision

**Problem.** Two OpenCode behaviors are safety issues:

- Command preprocessing runs before permissions apply.
- A nonexistent `--agent` falls back silently.

Together they make slash wrappers unusable.

**Proposal.** File minimal synthetic reproductions with OpenCode. If they are
fixed, reconsider `/sb-ingest` and `/sb-ask`. Filing publishes information, so
it needs approval.

### F4. Retire caveats that will not be acted on — P2

**Problem.** Status still carries items nobody plans to act on:

- the bootstrap metadata-audit caveat
- the waived missing-resource scenarios
- the unclaimed native variants for contradiction and ambiguous links

**Proposal.** Move them to a "closed / won't do" list with a reason for each.
B1's existence check covers the missing-resource case technically.

### F5. Decide how to do the P4 project round trip — P1 · Owner decision

**Problem.** P4/R5 is the only outstanding public item, and the deployment has
no project yet.

**Proposal.** Do the round trip with the first real project that needs wiki
context. Add one small synthetic test for the promotion mechanics, or skip the
synthetic demonstration. Don't build a larger fixture ahead of real need.

## G. Small tool fixes

### G1. Explicit chat selection vs `--min-words` — P2

**Problem.** `--conversation-id X` still drops X when it has fewer than 150
words (`scripts/chat_export_to_md.py:293`). The only feedback is
`too_short=1`.

**Proposal.** Explicit IDs imply `--min-words 0` unless the flag is given.
Otherwise, print a stderr note naming the filtered ID.
