# Manual ingest/query operation

Status: native four-file edits, sourced queries, write-enabled repeat, bounded
source injection and operator-mediated interruption/recovery now have synthetic
runtime evidence. See the [native trial report](native-acceptance-trials.md) for
actual results versus limitations. Missing-resource cases were owner-waived, not
passed. Owner content judgment remains separate from technical verification.
Do not install into a personal vault until PLAN.md's P3 entry gate passes,
including both required CLI ports and private backup/restore proof.

## 1. Prepare the isolated profile

The operator, outside the agent runtime, selects a small approved corpus and
records its paths and preimage hashes. Reject linked files/ancestors, hardlinks
and traversal; freeze the prepared corpus against outside writers. Do not mount
the personal vault, home, settings, credentials or personal AGENTS.md. Native
tool permissions cannot protect the destination of an allowed symlink.

Copy only the four reviewed files into the isolated profile's native agents and
skills directories. The test uses a disposable clean home; real distribution
uses the approved local manifest, never a recursive vault sync:

- `agents/sb-ingestor.md`
- `agents/sb-researcher.md`
- `skills/second-brain-ingest/SKILL.md`
- `skills/second-brain-query/SKILL.md`

Retain the root LICENSE and THIRD_PARTY_NOTICES.md in a namespaced notices
directory alongside the copied machinery; the disposable test does this too.

Keep the public checkout inert. The roles are primary but do not replace the
owner's default agent. They intentionally grant **no file access** until the
operator supplies exact local rules; skill and question tools are available.

Supply role-specific grants from the reviewed manifest:

| Resource | Read | Edit |
|---|---|---|
| Approved contract/templates, index, candidate pages, selected source | Both roles, only as needed | None by default |
| Approved changed wiki pages, index and log | Both roles when approved | Ingestor `ask` on exact files; researcher `deny` |
| Raw captures, role/config/skill files, settings, unrelated files | No additional access beyond the selected input/resources | Deny |
| Designated skill resource directory outside cwd | Precisely scoped external-directory rule if needed | Deny |

Broad denials precede exact grants; final sensitive-path denials follow. Do not
grant shell, broad search, network or delegation to make setup errors disappear.
Native `read` permission keys are **worktree-relative**, not necessarily relative
to cwd. In the tested non-Git `/workspace`, the reported worktree was `/` and a
file's key was `workspace/wiki/index.md`. Determine the actual worktree locally;
do not copy this synthetic prefix into another profile.

Before any live model call, approve provider/model, authentication mechanism,
data classes, retention and cost cap, including auxiliary model routes. Do not
import the owner's ordinary configuration to shortcut authentication. Inspect
only an allowlisted effective summary, never a complete config or environment.
Restart after configuration changes and verify the selected role really loaded.
`tests/runtime_roles_probe.py` demonstrates the disposable install and checks,
not a production installer or a private-provider profile.

## 2. Invoke the role directly, not a slash wrapper

`/sb-ingest` and `/sb-ask` are **withheld**. In OpenCode 1.18.32, native command
preprocessing expands `@file` and shell-interpolation-like text inside
`$ARGUMENTS` before role tool permissions constrain it. Both candidate wrappers
attached denied synthetic file content and evaluated a harmless shell snippet.
Literal arguments correctly selected the intended role and skill, but that is
not sufficient safety. The failing characterizations remain visible in the probe.

Select `sb-ingestor` or `sb-researcher` explicitly. Use a plain, vetted request
with ordinary approved paths—no `@file`, shell snippets or pasted untrusted
source content. This fallback does not claim that arbitrary prompt text is
immune to OpenCode preprocessing. Read source content through the scoped read
tool, not by interpolating it into a command.

Example request after local setup (replace paths with approved local paths):

> Load your designated skill using the skill tool. Read the approved contract,
> index and source at the paths in this operation's manifest. Propose claims
> and exact changed paths only; do not write before I approve the proposal.

For queries:

> Load your designated query skill. Starting from the approved index, explain
> the recorded disagreement about vent choice with source locators. End with
> Read and Not covered. Do not edit files or substitute outside knowledge.

These are operator request examples, not evidence of completed ingestion/query.

## 3. Approve a bounded patch, then verify

For ingestion, read the entire input before the proposal. The owner checks
source identity/locators, complete reading, existing-page candidates, competing
claims, exact paths, raw hash and preimages. Reject unrelated edits. The ingestor
must request each permitted edit; never choose a broad **always** approval.
Never use `--auto`. The live driver now verifies exact native `once` replies,
preimages and postimages, including recovery and a log-only append. It does not
test or authorize persistent `always` grants. A conversational confirmation may
be answered once under explicit owner delegation; each tool request still needs
its own exact-patch validation and `once` reply.

Update source/concept/entity pages and reciprocal links, update the index in
the same operation, and append truthful log status. The log header stays fixed.
Until the owner reviews the changed set and checks, the operation is partial.
Repeating unchanged input must not duplicate pages/claims. On interruption or
preimage drift, preserve human work, reconcile only approved paths against the
backup, and append a correction/completion record. Never broad-reset.

The owner runs the read-only checker on the approved frozen corpus:

```sh
python3 scripts/link_check.py tests/fixtures/contract
python3 scripts/link_check.py tests/fixtures/contract --json
```

The shipped synthetic fixture reports five content pages, two control pages,
18 unique directed content links and no diagnostics. Substitute a real approved
scope only locally; paths/titles in its report may be private.

### Checker contract

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
- Strips fragments only to check the file; heading/block validity is **unchecked**.
  A zero exit with unchecked anchors is not proof that those anchors exist.
- Excludes leading frontmatter, ordinary fenced code and simple inline-code
  spans. An unclosed fence suppresses the rest of the page. This is not a full
  Markdown/Obsidian parser: HTML comments, indented code, blockquote fences and
  complex inline spans are not normalized.
- Exit 0: no error/unsupported form (review unchecked items separately).
  Exit 1: errors or unsupported forms. Exit 2: invalid/unsafe scope or read failure.

The checker does not establish factual support, index completeness, reciprocal
meaning or transaction completion. Review those separately. Query role writes
zero files, including the log; persisting an answer is another approved operation.

## Remaining proof and installation gates

See the [dated acceptance matrix and selected-conversation packet](synthetic-acceptance.md).
The focused `python3 tests/runtime_roles_probe.py --missing-only` currently exits
**1**: a nonexistent role still causes fake-provider requests (CLI exit 0), while
both missing designated skills error. Do not rely on `--agent` or exit status
alone to fail closed. Verify the exact primary prompt, skill and effective scoped
grants before live launch; missing/mismatched resources must prevent the call.
This historical result is native runtime evidence, not model-level refusal.
The owner subsequently waived missing-role/skill scenarios as acceptance blockers
and will ensure they exist. Retain inexpensive preflight checks; do not describe
the waived runtime behavior as fixed or passing.

The native proposal helper, `python3 tests/native_chat_proposal.py --live`, now
produces a valid framed-Markdown proposal. Effective-config inspection belongs to
the operator, not the model before its initial permitted manifest read.
Keep `PWD`, process cwd and `run --dir`
aligned; OpenCode 1.18.32 otherwise may inspect one directory but run in another.
Never fix that mismatch by widening permissions. Native edits remain denied
until a valid exact patch reaches the applicable approval gate.

For this invented four-file slice only, the owner authorized operator patch
validation and one-time native edit approvals. `native_chat_handoff.py` checks
exact patch arguments, tool-call identity, paths and preimages before `once`,
never `always`. The retry with absolute manifest/patch paths now has live evidence:
four accepted native edits, exact postimages, passing checker, unchanged protected
inputs, and a native applied-wiki query with no writes. `--live-repeat-only` adds
a read-only unchanged-source no-op assessment, including a full log read. It does
not replay the old patch over changed preimages. The separate acceptance trial now
also tests no-op behavior with four edit ask gates available, a native interruption,
stale-patch refusal, and operator-rebased native recovery preserving a simulated
human edit. See the trial report; this is not an autonomous conflict-resolution engine.
Owner content acceptance was not delegated by the edit authorization.

### Optional live semantic rehearsal

The owner approved the existing `dingus` primary agent, whose inspected routing
was `openai/gpt-6-luna`, for synthetic provider calls. The observed four-turn run:

1. Proposed and staged trial A: two content pages, two reciprocal edges.
2. Proposed and staged conflicting trial B: three content pages, four reciprocal
   edges; old source/raw bytes and the old log prefix were preserved.
3. Repeated unchanged trial B: empty change set, no duplicate pages/claims/log.
4. Queried the generated wiki plus raw evidence: measured values and attribution
   correct, publication date unknown retained, preferred setting not established,
   unexplained cause reported not covered, four valid source/section citations.

All four calls reported one model step, zero tool events and exit 0. Eleven final
semantic/state checks passed. This is an observed run, not a guarantee about every
future model response. The test driver—not the model's edit tools—applied only
four exact synthetic paths per ingest. It validates metadata/links/provenance,
verbatim evidence excerpts for both source sections, all source/concept
reciprocals, canonical index entries, append-only partial logs
and unchanged inputs. It does not automate human factual acceptance of every sentence.

The live helpers are opt-in and require an explicitly approved primary and route:

```sh
python3 tests/semantic_probe.py --live --agent APPROVED_AGENT --model PROVIDER/MODEL
python3 tests/ingest_rehearsal.py --live --agent APPROVED_AGENT --model PROVIDER/MODEL
```

These Linux-only helpers use the owner's existing authentication and normal
OpenCode profile context/session retention, **not the isolated fake-provider
profile**. Config-directory AGENTS.md may still be sent; this is not instruction
isolation or approval for private notes. External plugins/project configuration
are disabled; native authentication remains available. Tool-deny and one-step
settings, provider routing, disabled MCPs, sharing, snapshots, formatters and LSP
are inspected using the same environment as inference. Intermediate config output
stays in anonymous RAM and is never printed. No credentials are copied into this
repository. Untrusted `@`/shell preprocessing tokens are rejected before calls.

Only fixed public synthetic inputs are supported. Generated staging is removed;
the CLI's ordinary session store can retain prompts/replies. No generated page,
transcript, or owner configuration is published by these helpers. Logs remain
partial because that older rehearsal did not test native edits or owner content
acceptance. The later native trial report is separate evidence.

The actual named-role trials now cover accepted edits, sourced answers,
edit-capable injection, repeat and operator-mediated interruption/recovery.
Missing-role/skill scenarios are owner-waived. Neither those scoped successes nor
the older rehearsal imply universal attack resistance, an autonomous merger,
private restore proof or owner content judgment.

Before personal installation: P2B conversion and selected native R8 ingest/query
are evidenced; owner content judgment remains separate. P2A statistics
is delivered with its [local report approval procedure](vault-stats.md).
Approve exact paths/provider/source and R6 backup policy/isolated restore.
No personal installation has been performed. Existing approved authentication was
used only for the synthetic live checks above; no private-source approval is implied.
