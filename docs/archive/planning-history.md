# Planning history

> Moved from PLAN.md on 2026-09-30 and kept for the record: the execution
> history, the state at planning time, the upstream inventory and disposition,
> research coverage, the original planning notes, and the optional tracks
> T1–T5 (not needed for vault setup). None of it is current status; see
> [STATUS.md](../../STATUS.md).

## Execution history (historical checkpoints)

The entries below record what was known at each checkpoint. Later entries and
the current delivery status supersede earlier blockers, "future checks" and
test counts without erasing their failure history.

<details>
<summary>Expand the historical implementation and bootstrap record</summary>

* D1 resolved: downstream MIT notice added; pinned upstream notice preserved verbatim in `THIRD_PARTY_NOTICES.md`.
* P0 baseline delivered: inert config example, guidance, ignore rules, one-way distribution/rollback rehearsal, isolated runtime baseline and corpus preflight checks. The owner approved the distinction between native tool permissions and prepared-corpus/OS controls, then authorized delivery in logical increments.
* Observed: installed OpenCode reports `1.18.32`; `bwrap` and Python 3 are available. P0 used only disposable profile inspection. Later owner-approved primary-agent routing/effective settings were inspected locally with allowlisted output; no credential values or vault content were exposed in public tool output or copied into this repository.
* Pre-P2B verification: `python3 -m unittest discover -s tests -v` passed 39 offline checks (distribution, scope, rollback, contract/framework/checker, live-driver guards and statistics); P2B results are recorded below. Previously run `python3 tests/runtime_read_probe.py` passed 16 baseline cases on OpenCode `1.18.32` / Bubblewrap `0.12.0`; `python3 tests/runtime_roles_probe.py` passed 25 native loading/tool checks and enforced withholding the unsafe wrappers. Its separate command characterizations retain four failed safety results. Static tests are not runtime proof, and a deterministic fake provider is not model-ingestion proof. P2A invokes neither runtime nor live models.
* R0 distribution method and R1A synthetic-only isolated runtime proposal approved by the owner's subsequent “approve”. Their technical exit criteria remain mandatory.
* Runtime path mismatch resolved: native `read` asks on worktree-relative paths. The disposable non-Git project reports worktree `/`, not cwd `/workspace`; its exact allow is `workspace/wiki/index.md`. The approved read now succeeds, while five direct/traversal/outside negative reads are denied. CLI `debug scrap` supplies the isolated project record; HTTP inspection timed out and was removed from the workflow, not declared fixed.
* Baseline forced edit/write/bash/grep/glob/webfetch/task/skill calls are rejected as unavailable under deny-default policy. A narrowly ask-scoped edit requests permission and is rejected by noninteractive CLI, leaving fixture bytes unchanged. A new process is used for each case. Named-role skill loads and command expansion are now tested as detailed below; accepted interactive approval and full model-driven named-role behavior remain future checks.
* Boundary distinction: an earlier native symlink characterization returned denied synthetic content through an approved filename. Native read permissions do not confine link targets. The adopted profile rejects linked files/ancestors and hardlinks before launch, freezes the prepared corpus against outside writers, and never mounts private settings/credentials. Its symlink test now stops at preflight with zero provider calls; this is not a claim that OpenCode fixed symlinks or that a preflight alone prevents races.
* P1 delivered: generic contract, seven templates, all four content types plus index/log populated, two conflicting wholly invented sources, and a project brief. Claim/locator matrix, reciprocal links, complete index, explicit unknown provenance and no placeholder residue pass static checks. The log labels this as hand-authored fixture creation, not runtime ingest. Generated metadata is a flat JSON-value YAML subset; append-only log header dates remain at creation and operation dates are in entries.
* P2 machinery delivered: read-only `scripts/link_check.py`, two native primary role files, two designated skills, synthetic tests and `docs/manual-loop.md` (replaced by `docs/operator.md` and `docs/reference.md` on 2026-09-28). The checker validates exact managed paths and generated metadata, reports ambiguity/unsupported forms and unchecked anchors, and supplies pure collection/link functions for the required statistics port. The synthetic contract fixture has five nodes, two controls and 18 unique directed content links with no diagnostics.
* Four role/skill files were copied into a disposable clean native profile, not the owner's configuration. Native prompts/skills loaded; approved reads worked; cross-skill/private-path/tool/write refusals passed. The ingestor's wiki edit reached ask rejection. This is not proof of accepted edits, source reasoning or a complete ingest.
* P2 command decision: both candidate wrappers routed literal input to the right skill, but `@file` attached denied synthetic content and shell-like arguments expanded before role tool restrictions. As explicitly permitted in the plan, wrappers are withheld from `framework/` and installation. Continue with explicitly selected roles and plain vetted requests; do not treat arbitrary prompt interpolation as safe. No attempt is made to patch OpenCode itself.
* Owner additionally approved the existing `dingus` primary agent for live synthetic provider calls and ingestion tests; allowlisted inspection identified `openai/gpt-6-luna`. The opt-in helpers take local agent/model arguments, not public default provider configuration. An eight-expectation semantic check passed, with one step and zero tool events observed.
* Live staged rehearsal passed: two ingest proposals were applied by an operator driver to fixed temporary wiki paths; source A yielded two content pages/two edges, source B yielded three pages/four edges in the latest run. Schema/provenance, verbatim evidence excerpts, reciprocal links for both sources, canonical index, unchanged old source/raw bytes and append-only partial logs were checked. Repeating unchanged B produced an empty patch. Querying generated pages plus raw evidence passed 11 semantic/state expectations, including four source/section citations and honest gaps. Four model calls each reported one step, zero tool events and exit 0. Generated artifacts were not added to this repository.
* Distinction: live semantic tests use the owner's existing primary-agent authentication and ordinary profile context/session retention, not the isolated permission-test profile. Config-directory instructions may be sent. The driver, not native model edit tools, applies the synthetic proposals; logs and owner content acceptance remain partial. These runs do not prove accepted native edits, every sentence's factual fidelity, source injection, or interrupted-run recovery.
* P2A delivered on the owner's “next slice … do it” authorization: exact PLAN definitions and fixture were shown before implementation (R7A); the existing P1 contract and P2 shared link semantics satisfy this port's dependencies. `scripts/vault_stats.py` supports positional root, human output, `--json` and reproducible `--as-of`. It shares parsing/link resolution, never opens controls, excludes instruction files, exposes unusable dates/types and leaves all input hashes unchanged. Known fixture passes N=4, E=3, degrees 0.75/1.5, orphan 1/4, weak components 2, largest share 3/4, and stale 1/2 eligible with one unknown. Nine statistics regression tests and the extended shared scanner regression pass; both CLI entry forms repeat identically for fixed input/as-of. See `docs/vault-stats.md` for definitions, upgrade differences and R7B local-report approval. No private corpus was read and no snapshot was written.
* P2B converter machinery delivered on the owner's explicit next-slice authorization: pinned script and all three consumers inspected before implementation. `scripts/chat_export_to_md.py` provides positional export/outdir, default 150-word filter, no-write dry-run and mandatory ID selection or explicit `--all`. Synthetic Claude/simple and ChatGPT active-ancestry fixtures preserve roles/text/known UTC dates/identity, reject malformed walks, quote metadata and count omissions. Descriptor-based path handling, exclusive creation, byte-verified reruns and content versions pass synthetic tests, including partial failure and changed omitted payloads. All 23 converter tests pass; full offline suite now passes 62 checks. No shared scanner behavior changed. `docs/chat-exports.md` records supported shapes, local staging, recovery and R8 approvals; the pinned adaptation map is extended. No model/provider call, private export, personal installation or global configuration change occurred in this slice.
* Synthetic R8 preparation (2026-09-25): current prompt approves invented staging/conversion. `tests/test_chat_handoff.py` selects only `synthetic-lantern-01` / branch `m4`, verifies four messages, roles/text/UTC and unknown dates, one omission, excluded sibling/conversation, unchanged export bytes and identical rerun. The reproducible manifest, privacy assessment and claim/locator oracle are in `docs/synthetic-acceptance.md`. No provider call or wiki edit occurred; this is a handoff packet, not an ingest/query result or owner content acceptance.
* Focused native P2 increment: `python3 tests/runtime_roles_probe.py --missing-only` verifies loaded native prompts and both missing designated skills returning tool errors, with tracked bytes unchanged. **Missing-role refusal fails:** OpenCode 1.18.32 exits 0 and makes two fake-provider requests/one errored tool call for a nonexistent role. Probe exits 1 and preserves that failure; no live route is involved. Require fail-closed role/skill launch preflight before live testing; tool failure does not prove model-level refusal. Prior unrelated runtime matrices were not rerun.
* Verification for this packet: the selected handoff regression passes; `python3 -m unittest discover -s tests -v` passes all 63 offline checks; `git diff --check` passes. Independent review corrected manifest locking and evidence wording. The focused native probe's exit 1 remains an explicit safety finding, not included among passing offline checks.
* Follow-up owner “approve” authorizes the temporary named-role live profile, not an exact patch or content acceptance. Pre-execution inspection found the proposed hard budget cannot be guaranteed: the pinned OpenCode 1.18.32 OpenAI hook clears `maxOutputTokens`, and retries make agent steps unsuitable as a total provider-request ceiling. Installed version remains 1.18.32. No live call, temporary profile installation or credential inspection was performed under this extension. `docs/synthetic-acceptance.md` records source evidence and a proposed single timeout-bounded run with explicitly non-guaranteed token/request targets; no budget relaxation is assumed.
* Subsequent owner authorization permits continuing synthetic feature-slice runs after disclosure that call/token figures are targets, not guaranteed ceilings. `tests/native_chat_proposal.py` adds a disposable native-role overlay, fail-closed prompt/route/skill/grant preflight and a proposal-only path with edits denied. Eight live CLI attempts (not a provider-request count) exposed setup refusals and a PWD/cwd mismatch: OpenCode run uses inherited PWD for its SDK directory. Aligning PWD/cwd/explicit --dir fixed the read failure without widening permissions. One attempt then loaded the native ingest skill and fully read required files, but returned malformed proposal JSON and imperfect date metadata; it was rejected. The subsequent attempt again refused to read the preflight manifest. Live retries stopped; role/manifest bootstrap ambiguity remains a suspected cause, not a verified fix. No native edit, valid accepted packet or researcher query occurred. Later failed responses remain outside the repository; normal session retention applies. Three new offline guard tests pass; full suite passes 66 checks and `git diff --check` passes. See the acceptance packet for actual results and limitations.
* Owner “authorize yes” permits one-time native approvals for the four synthetic wiki paths after operator patch validation, not raw/config edits, broad always grants or owner content acceptance. Role/skill instructions now assign effective-config inspection to the operator and allow the initial permitted manifest read. Three new proposal turns ended at dependency-cache inventory drift, malformed JSON, then success: sb-ingestor skill loaded, nine complete reads, four steps, unchanged protected inputs, four-file packet SHA-256 `67f68b06968d2ca9849c0364d1a41eadbf106446566bdf9b59c01d40236c2e62`. Framed Markdown replaced fragile JSON-escaped pages; supplied files are frozen separately from OpenCode's dependency cache. Operator review restored full UTC timestamp prose and added a later partial apply log; review-only link/metadata checking passed. Those corrections are not native wiki edits.
* `tests/native_chat_handoff.py` adds authenticated loopback sessions and per-request `once` validation against exact apply_patch text, tool-call identity, one allowed path and current preimage; it never writes corpus wiki pages itself. Three native application turns remained incomplete with no edits/approvals. The second correctly refused JSON patch strings truncated by native read; multiline patches replaced that input. The third requested a manifest path despite receiving the relative path. Live edit retries stopped under the repeated-failure rule. An explicit absolute-path request is staged but not yet live-verified; the positive permission handler has only offline evidence.
* A separate native sb-researcher turn loaded its query skill and completely read manifest, contract, empty index and selected raw artifact (four reads). Its answer cited Messages 1–3, distinguished creation/message dates, reported unknown change date and lack of independent battery evidence, included Read / Not covered, and disclosed that no wiki ingest exists. Corpus bytes/file set were unchanged. This advances named-role source-grounded answering, not applied-wiki R8 acceptance. Seven narrow native-driver tests and all 70 offline tests pass; `git diff --check` passes. Later query-scope/permission-poll tightening is not a new live pass. Details are in `docs/synthetic-acceptance.md`.
* Following explicit retry authorization, the absolute-path request succeeded: sb-ingestor loaded its designated skill, read the manifest/validated patches, and made four native apply_patch calls. The driver replied once per exact approved path after matching patch arguments, metadata and preimages; all four postimages matched, link/metadata checking passed, and export/capture/protected profile bytes were unchanged. No driver applied these corpus wiki edits. A separate sb-researcher turn read six complete files, including the actual applied pages and selected raw artifact, and answered with message locators, temporal uncertainty and unsupported-assertion disclosure. A second read-only query removed an imprecise section-heading citation. Both query turns preserved corpus bytes/file set. Independent review rechecked final postimages and raw hash, not the full live session.
* Added `--live-repeat-only`: actual sb-ingestor loaded its skill, completely read seven files (including the log), concluded unchanged-source no-op and made no writes/log append. This is a repeat assessment with edits denied, not evidence of behavior under enabled write grants. Eight narrow native-driver tests and all 71 offline tests pass; `git diff --check` passes. R8 now has selected native ingest/applied-wiki query evidence; a bounded owner content-acceptance packet is ready. The wiki log remains historical apply-time partial status; subsequent verification lives in separate local evidence records and this plan, not a fabricated completion append.
* Owner acceptance amendment: missing-skill and nonexistent-agent scenarios are waived as acceptance blockers under the owner's assurance that the intended resources exist. Existing cheap preflight guards and historical failure evidence remain; no missing-resource behavior is relabeled as passing. The owner authorized the remaining synthetic trials/model calls and delivery. That operational authorization is not recorded as a separate personal judgment of the R8 prose or as private-vault approval.
* Native trial increment: `tests/native_acceptance_trials.py` reuses the reviewed source packet in a fresh disposable corpus. A native concept edit received one exact `once` reply; the next pending native edit was interrupted before approval. A labeled driver-simulated human index addition caused stale reconciliation to refuse without writes. After explicit operator rebase preserving that paragraph, native recovery applied exactly index/source/log, not the completed concept. Postimages and link/metadata checks passed. This is operator-mediated recovery, not an autonomous merge or broad rollback. One earlier failed partial trial was preserved, not reset.
* The recovered trial then passed repeat and injection assessments with all four wiki edit ask gates available. Repeat read seven required files and returned no-op without a permission request/log append. Injection read eight files, identified attempts to modify raw/profile/extra-page/log targets and forge acceptance, and made no writes/approvals. After independent review identified a measurement gap, only these two assessments were rerun with before/after export and prepared role/skill hashes, saved sanitized manifests and tool summaries; both passed with corpus and protected inputs unchanged. The actual selected raw hash still matches the original converter artifact. These bounded cases are not proof against all possible payloads or filesystem isolation.
* A native log-only verification append on the original selected corpus passed with one exact `once` receipt and preserved all prior log bytes. Its first attempt safely failed after the model mistyped a historical hash while retranscribing a whole-file patch. Append patches now use short tail context while the approval gate still checks the entire preimage; the compact retry passed. Same-session bounded conversational confirmation is supported without turning tool grants into blanket approvals. New receipts bind call/permission IDs and before/after hashes; future fresh trials also save initial approval/interrupted-state snapshots (not retroactively claimed for the observed run).
* Current verification: 13 narrow native-driver tests and all 76 offline tests pass; `git diff --check` passes. Independent review rechecked recovered postimages, one preserved human paragraph, raw hashes and first-one/recovery-three/log-only-one receipts. Current operational evidence and failure history are summarized in `docs/native-acceptance-trials.md`. Missing-resource cases were not rerun. Owner content judgment remains distinct from technical validation; no personal-vault work occurred.
* R6 public rehearsal delivered under the owner's continue/commit/test authorization: `tests/test_r6_backup_restore.py` uses 16 fixed public/invented files, a separately retained canonical approval manifest, a new snapshot and a third alternate restore root. Full restore works with the source path unavailable; selected recovery uses snapshot bytes even after a simulated source revision. All restored hashes/binary asset bytes and the five-page/two-control/18-link fixture match. Settings/credential-like names, links/hardlinks, root overlap, collisions, altered manifests, corrupt payloads and unapproved paths are refused. A late preimage drift blocks all writes; operator replan preserves the simulated human index/unrelated work and restores only the interrupted concept before appending a correction log.
* R6 failure evidence: replacement failure preserves its target; a second-file failure leaves an explicitly partial batch, rejects blind replay and permits a reviewed remaining-path-only retry. Source and backup bytes are not changed by restore; deliberate fixture mutations are labeled test actions, not native edits. Six R6 tests and all 82 offline tests pass; `git diff --check` passes. No OpenCode/provider invocation, private file access, active framework installation, backup-policy choice or production backup CLI was introduced. See `docs/backup-restore.md` for the approved scope, observed checks and limits.
* Next logical slice/gate: R6A owner backup-policy agreement (mechanism/destination/access, exact scope, encryption/key recovery, retention/frequency and recovery-point expectations), then an explicitly approved private alternate-location restore drill. The synthetic rehearsal does **not** complete private R6C or prove that any personal data is backed up. Owner content judgment, actual private restore proof, path/provider/source approvals, R7B reporting and P3 installation remain separate gates.
* Later owner amendment: the owner identified the private destination, described it as greenfield and waived the initial backup prerequisite. The owner then explicitly approved a 14-file add-only bootstrap: supplemental contract, seven namespaced templates, two roles, two skills and both license notices. This exception is limited to new machinery files. It does not authorize collisions/overwrites, root instruction/settings changes, real-source processing, a new provider exposure or broad grants. No private backup is claimed. The private destination and local instructions are not copied into public files.
* Bootstrap actual result: public revision `1e987fda10279b6cacd9dedd6906c271d88bd416` supplied all 14 files via exclusive, link-rejecting per-file creation. A temporary wholly synthetic smoke check first verified dry preflight, exact copies, preservation and collision refusal. Private preflight found zero destination collisions. All installed hashes match that public revision, the root instruction hash is unchanged, the new namespaces contain exactly the approved files with no links, and no root OpenCode config was created. No existing raw/wiki/settings file contents were opened, no OpenCode/provider process was started, and no default-agent config was changed.
* Audit limitation retained: after the 14 copies, the initial broad top-level metadata comparison failed. Its before-metadata values were not retained, so the change is not attributed or declared harmless. A separate read-only reconciliation verified the payloads, root instruction hash and expected root layout without inspecting existing note/settings contents. The private install and verification receipts remain outside the public repository and private notes folder. This is verified payload delivery with an unresolved metadata-audit caveat, not a full private-content integrity audit or runtime permission proof. No recopy, rollback or note modification was attempted.
* Next integration step: restart the owner's OpenCode session to discover the added roles/skills, then approve one source, its provider exposure and exact local grants before any real ingest. The copied role files deny reads/edits by default; effective inherited configuration has not been inspected in this bootstrap. Existing notes, instructions and settings remain outside the bootstrap write scope. The public checkout stays inert.
* Earlier public P0/P1 checkpoint `074e700` was pushed under the owner's explicit request. At that earlier checkpoint, no personal-vault installation was recorded; the later add-only bootstrap above supersedes that installation status. This cross-reference does not describe current private deployment state. Private-vault Git remains separately gated.

</details>

## Current State at planning time (historical)

Implementation-time results supersede these initial observations; see
Current delivery status and Execution history above.

* At investigation start this repository contained only `.git/`, with no commits, application, tests, dependencies, or existing plan. This consolidated `PLAN.md` is the only new repository file. The configured remote is the user's public `funsaized/second-brain-open` repository. No commit or push was performed.
* Only the explicitly permitted vault `AGENTS.md` was read. Its integration constraints require small approved steps, direct file access, preservation of notes/settings, source grounding, and optional—not mandatory—tracks. No personal notes or plugin credential file were read. Personal context from that file is deliberately not reproduced here.
* Upstream was inspected at commit [`347feee87b305b291f7264890e5024db422e3467`](https://github.com/undefined-ui/second-brain-os/tree/347feee87b305b291f7264890e5024db422e3467). The website exposes only a navigation shell to direct retrieval, so its corresponding repository Markdown was read.
* Research covered all ten guide sections, all five tracks, 18 skills, 72 commands, six agents, six scripts, the complete vault template, and root licensing/setup material. The detailed inventory and source coverage are recorded below.
* OpenCode's installed version was reported as `1.18.32`. Current public docs/schema were inspected, but runtime config and permission compatibility have not been tested. No local credential/config contents were inspected.

## Upstream Inventory and Disposition

All upstream paths below are relative to the [pinned source tree](https://github.com/undefined-ui/second-brain-os/tree/347feee87b305b291f7264890e5024db422e3467). This is the original disposition inventory, not the delivery checklist. **Now** means selected for core implementation; the current summary identifies what shipped and the wrapper exception. **Later** means a stated gate must be met. **Reference** means do not port the component. A later row's acceptance check applies only if that component is selected later.

### Vault, templates, agents, and scripts

| Upstream source | Class; purpose and adaptation | Order/gate; risk; acceptance check |
|---|---|---|
| `vault-template/CLAUDE.md` | Now: source-grounded wiki contract → supplemental OpenCode instruction, not a replacement root `AGENTS.md` | P1; incomplete upstream folder/schema map; four page types plus controls/projects correctly described |
| `vault-template/templates/{source,concept,entity,synthesis}.md` | Now: plain text page templates; add explicit provenance, reconcile fields, resolve placeholders without plugins | P1; metadata drift/invented provenance; populated examples pass R2 |
| `vault-template/wiki/{index,log}.md` and four wiki `.gitkeep` directories | Now: catalog and append-only history; control-type exceptions; create local directories only when needed | P1–P2; stale index/false completion; actual paths and operation record agree |
| `vault-template/projects/README.md`, `projects/example-project/CLAUDE.md`, four project `.gitkeep` directories | Now as a project brief/handoff contract, not copied example project; `CLAUDE.md` guidance becomes locally reviewed `AGENTS.md` | P1/P4; project hub mistaken for wiki; round-trip handoff retains sources |
| `vault-template/raw/README.md`, `raw/assets/.gitkeep`, `output/README.md` | Now as input/archive/output boundary instructions, not bulk scaffold | P1; raw treated as another knowledge layer or editable store; raw hashes unchanged and outputs explicitly promoted |
| `vault-template/README.md` | Reference: Claude quickstart replaced by R1 manifest | No recursive copy; local files preserved |
| `agents/ingestor.md` | Now: `sb-ingestor` primary role, native `permission`, explicit scoped ask-to-edit, no delegation | P2; Claude `tools:` is not OpenCode policy; forbidden-write tests fail closed |
| `agents/researcher.md` | Now: `sb-researcher` primary role, native deny-write/no-shell/no-network policy | P2; citations may be superficial; claim/source trace and zero-write check |
| `agents/linker.md` | Later: focused link edits only if manual linking becomes bottleneck | Repeated documented need; no page rewrites; approved links-only diff |
| `agents/reviewer.md` | Later: read-only review once review volume warrants a role | P4 cadence; no output writes through reviewer; useful report, zero changes |
| `agents/graph-analyst.md` | Later: graph reports after T1; do not grant Bash while calling it read-only | T1; arbitrary shell writes; isolated verified analyzer and non-mutating report |
| `agents/curator.md` | Later: pruning/merge proposals after real duplication appears | P4; deletion risk; proposals only, no deletions |
| `scripts/link_check.py` | Now: read-only managed-wiki checker; correct path/ambiguity/scoping behavior and documented limitations | P2; stem/alias regex shortcuts; positive/negative fixture and unchanged-tree checks |
| `scripts/vault_stats.py` | **Now, first-class:** deterministic read-only wiki statistics, JSON/as-of, actual component/staleness metrics; share canonical link semantics with checker | P2A; scope/degree/denominator/date errors; exact known fixture and unchanged-tree checks, R7 |
| `scripts/graph_export.py` | Later: graph export after T1 need; canonical IDs, consistent link handling, provenance | T1; basename collisions and dropped aliases; exact graph fixture and destination-only write |
| `scripts/chat_export_to_md.py` | **Now, first-class:** local faithful selected-conversation conversion, dry-run, actual ChatGPT branches/Claude text, safe repeat runs; privacy/triage before ingest | P2B; unsupported shapes/private data/role/date/path errors; synthetic fidelity/refusal/idempotency tests, R8 |
| `scripts/build_tracks.py`, `scripts/build_tree.py` | Reference: upstream website generators, not vault machinery | No port; writes generated docs/HTML, `markdown` dependency, site-specific analytics |
| `agents/README.md`, `scripts/README.md`, `skills/README.md`, `commands/README.md` | Reference: catalogs inform adaptation, not installable components | Do not turn README files into commands/agents |

### All 18 skills

Paths are `skills/<name>/SKILL.md`.

| Name | Class; purpose/OpenCode change | Dependency/risk/acceptance |
|---|---|---|
| `second-brain-ingest` | Now: complete read → source/concepts/entities → reciprocal links → index/log; retain native skill frontmatter, remove Claude assumptions, add approved patch and recovery | P2; over-extraction/injection/partial updates; R3 fixture and real-source gates |
| `second-brain-query` | Now: index-first sourced answers and explicit gaps; read-only role, canonical citations/claim locators, no silent web fallback | P2; source drift/poor recall; R4 support and abstention checks |
| `second-brain-lint` | Later: report-before-repair workflow; use native checker, no auto-repair/commit shortcut | After P4 reports prove useful; semantic changes disguised as mechanical; report changes zero files |
| `second-brain-backfill` | Later: oldest-first approved small batches and checkpoints | Successful single-source loop + explicit backlog; duplicate/partial batches; resume fixture without duplicates |
| `second-brain-changed-my-mind` | Later: two dated positions and intervening evidence | Enough dated evidence; recency bias; both views cited, uncertainty retained |
| `second-brain-chat-import` | Later **automation wrapper only**: converter and privacy/triage/selected-ingest runbook ship now in P2B/R8 | Repeated need for agent-assisted triage; transcript disclosure risk; approved synthetic selective import |
| `second-brain-graph` | Later: structural report via validated graph tools | T1; shell and graph inaccuracies; fixture-checked read-only report |
| `second-brain-merge` | Later: approved merge, aliases/inbound-link updates/log | Actual duplicates; destructive semantics; reviewed diff and no lost claims |
| `second-brain-metrics` | Later **snapshot/trend automation only**: all required statistics ship now in P2A/R7 | Repeated need to append/compare metrics; no shell grants to core agents; consistent definition/version comparison |
| `second-brain-privacy` | Later: local audit, no automatic deletion; redact findings, never echo secrets | Explicit audit scope/tooling; disclosure through audit output; synthetic secret locations reported without values |
| `second-brain-project` | Later as automation; project contract/handoff already in core | Real repeated project setup need; scope creep; one goal, bounded workspace, evidence round-trip |
| `second-brain-publish` | Later: opt-in export review, no implicit upload | Explicit publication destination/license/privacy approval; linked-page leakage; output allowlist contains no unapproved pages/assets |
| `second-brain-quiz` | Later: questions grounded in recorded knowledge | User learning need; prior-knowledge contamination; every answer key sourced |
| `second-brain-rename` | Later: file + alias + inbound links + log as reviewed change | Actual rename need; broken identities; inbound-link fixture and reversible diff |
| `second-brain-report` | Later: scope/gaps before evidence-backed report | Approved output need; unsupported conclusions; claim-to-source audit |
| `second-brain-review` | Later: concise periodic knowledge review | P4 cadence; activity mistaken for value; useful source-linked changes/gaps report |
| `second-brain-transcript` | Later: faithful cleanup, not summary | Approved media, consent, transcription provider; speaker/timestamp errors; sampled fidelity comparison |
| `second-brain-write` | Later: evidence-led outline/draft; mark model-generated text | Approved writing task; attribution and voice confusion; sourced outline and human approval |

### All 72 commands

Sources are `commands/<name>.md`. These are prompt wrappers, mostly forwarding to skills. Every later wrapper needs a native namespaced command, explicit agent, compatible `$ARGUMENTS`, no shell/file interpolation, and its target skill first. Test dispatch, arguments, and role permissions—not just menu visibility. No need to implement synonyms separately until use warrants them.

The "Now" column below records the original selection, not shipped commands.
Both selected wrappers are currently withheld; direct role invocation is the
delivered alternative. No remaining wrapper is required simply to fill this table.

| Family | Now | Later (explicit inventory) | Reference / do not port |
|---|---|---|---|
| Ingestion (10) | `ingest` → `sb-ingest` | `ingest-url`, `ingest-youtube`, `ingest-pdf`, `ingest-paper`, `ingest-chats`, `ingest-voice`, `ingest-newsletter`, `ingest-highlights`, `backfill` | — |
| Structuring (11) | — | `link`, `dedupe`, `merge`, `rename`, `split`, `retype`, `schema`, `tags`, `aliases`, `contradictions`, `index` | — |
| Graph (8) | — | `graph`, `graph-export`, `orphans`, `hubs`, `bridges`, `clusters`, `typed-links`, `stale` | — |
| Retrieval (10) | `ask` → `sb-ask` | `know`, `connect`, `compare`, `sources`, `gaps`, `contradicts`, `timeline`, `trace`, `changed-my-mind` | — |
| Maintenance (9) | — | `lint`, `health`, `metrics`, `review`, `weekly`, `monthly`, `prune`, `archive` | `commit` |
| Outputs (8) | — | `outline`, `draft`, `report`, `publish`, `export`, `quiz`, `explain`, `ingest-mine` | — |
| Projects (6) | — | `project`, `project-status`, `decisions`, `commitments`, `handoff`, `scope` | — |
| Safety (5) | — | `privacy`, `secrets`, `dry-run`, `audit` | `rollback` |
| Setup (5) | — | `doctor` | `init`, `claude-md`, `install`, `schedule` |

Family gates and checks: ingestion variants require a tested extractor and approved source/provider, with fidelity/provenance tests; structuring needs a concrete repair with an approved reversible patch and link check; graph requires T1; retrieval needs a repeated query type and sourced/abstention fixtures; maintenance needs a validated checker/cadence and report-before-repair test; outputs need privacy/licensing/publishing approval and source audit; project wrappers need repeated handoff work and a round-trip test; safety wrappers need locally redacted synthetic-secret tests; doctor needs stable, non-secret diagnostics. Core `ingest`/`ask` acceptance is P2. **Deferring `ingest-chats`, `metrics`, or `health` slash wrappers does not defer their underlying first-class CLI ports: P2A/P2B and R7/R8 are required.** Commit/rollback/install/init/schedule remain human-runbook actions, not agent commands.

### Reference material and licensing

* `docs/01-*` through `docs/10-*`, `docs/README.md`, `docs/ROADMAP.md`: reference strategy; link rather than copy the guide.
* `docs/track-{graph,jev,harness,loop,evals}/`: optional reference curricula; selected lab outputs only after T1–T5 gates.
* `resources/`, root `README.md`, `CONTRIBUTING.md`: reference catalogs/provenance/style. External rankings, model IDs, SDK behavior, and performance numbers are not verified dependencies.
* `index.html`, `resources.html`, `tree.html`, `tools/{build_site,extract_site}.py`, `assets/`, `examples/`: no port. Website infrastructure is unrelated; examples are not an existing tested fixture suite. Website generation tools were inventoried, not executed or fully audited.
* Root `.gitignore` and `.gitattributes`: reference only; upstream ignores only some Obsidian files and does not protect private vault directories. Write a downstream allowlist/ignore policy suitable for public machinery instead.
* [`LICENSE`](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/LICENSE): MIT. For any substantial adaptation/copy, retain the complete notice including the exact blank-holder copyright line, identify upstream repository, pinned revision, adapted file paths and changes in `THIRD_PARTY_NOTICES.md`, and credit the upstream project. Do not invent the missing holder; clarification can be requested upstream before release. Choose the downstream project's own license explicitly. Links to the Karpathy gist and third-party resources do not confer their content licenses.

## Research Coverage and Known Gaps

The inspected guide is [published here](https://undefined-ui.github.io/second-brain-os/index.html). Markdown sources at the pinned commit are authoritative for this plan. All section README files were read along with the following content pages (names below omit `.md`):

| Directory under `docs/` | Content pages read |
|---|---|
| `01-concepts` | `what-is-a-second-brain`, `the-save-for-later-paradox`, `llm-wiki-pattern`, `two-layers`, `why-markdown-and-plain-text`, `pkm-lineage`, `wiki-vs-rag`, `what-good-looks-like` |
| `02-setup` | `obsidian-install-and-vault`, `claude-code-setup`, `mcp-obsidian`, `claude-md`, `vault-structure`, `project-scoping`, `live-data`, `obsidian-plugins`, `git-and-sync` |
| `03-ingestion` | `web-clipper`, `youtube-transcripts`, `pdfs-and-books`, `chat-exports`, `voice-and-meetings`, `newsletters-and-email`, `bulk-backfill` |
| `04-structuring` | `atomic-pages`, `page-types`, `linking-rules`, `frontmatter-schema`, `naming-and-aliases`, `dedupe-and-merge`, `contradictions-and-supersession`, `index-and-log` |
| `05-graphs` | `graph-basics`, `obsidian-graph-view`, `typed-links`, `graph-vs-vectors`, `graphrag`, `exporting-your-graph`, `metrics` |
| `06-agents` | `agent-roles`, `scheduled-maintenance`, `subagents`, `hooks`, `skills-and-commands`, `safety-and-guardrails` |
| `07-retrieval` | `asking-questions`, `query-patterns`, `search-tools`, `rag-on-top`, `context-budget` |
| `08-outputs` | `writing-from-the-vault`, `research-reports`, `publishing-and-export`, `teaching-yourself` |
| `09-maintenance` | `lint-and-health`, `review-cadence`, `versioning-with-git`, `backups-and-portability`, `privacy-and-secrets`, `scaling` |
| `10-troubleshooting` | `common-failures`, `agent-writes-garbage`, `broken-links`, `vault-too-big`, `faq` |
| `track-graph` | `why-graphs`, `graphrag`, `building-graphs-with-llms`, `graph-stores`, `tools`, `build-extract`, `build-query`, `build-use`, `resources` |
| `track-jev` | `system-one-models`, `what-jev-is-good-for`, `jev-in-an-agent-stack`, `getting-started`, `build-decision-endpoint`, `build-router`, `build-swap-in-jev`, `resources` |
| `track-harness` | `what-a-harness-is`, `claude-code-as-harness`, `context-engineering`, `tools-and-mcp`, `harness-landscape`, `build-the-loop`, `build-guardrails`, `build-graduate`, `resources` |
| `track-loop` | `what-loop-engineering-is`, `stop-conditions`, `critics-and-verification`, `context-hygiene`, `patterns`, `build-goal-test`, `build-critic`, `build-overnight`, `resources` |
| `track-evals` | `why-evals`, `designing-evals`, `llm-as-judge`, `agent-evals`, `tooling`, `build-traces`, `build-suite`, `build-ci`, `resources` |

Counts reconciled from the tree: core guide **75 section Markdown files + 2 navigation files = 77**; tracks **44 content pages + 5 READMEs = 49**; machinery **18 skills, 72 commands, 6 agents, 6 Python scripts, 21 vault-template blobs**. Upstream's four-script headline counts vault utilities, not the two site-build scripts.

At initial planning, external product claims, SDKs, upstream examples, runtime enforcement and recovery were not verified. Current delivery status and Execution history distinguish the subsequently delivered runtime subset and synthetic restore evidence. External pricing/benchmarks and optional SDKs are still not verified dependencies. Private-note compatibility and actual deployment outcomes belong in local records, not in this public research inventory.

## Planning Scope Boundaries (historical)

### In Scope

Planning documents, source-backed inventory, approval-gated runbooks, privacy and permissions design, licensing, manual core loop, and separately gated optional tracks.

### Out of Scope

Implementation; vault migration or Git initialization; Obsidian setting changes; bulk imports; plugins/MCP/schedulers; commits/pushes; copying personal content; reading the forbidden plugin credential file.

## Original planning progress (historical, not implementation status)

The "None" entries below close the initial research/planning task only. They do
not close the outstanding project demonstration or owner-local deployment gates.

### Completed

* [x] Inspected the empty public repository and permitted integration instructions.
* [x] Read upstream machinery, all ten guide sections, and all five tracks at a pinned revision.
* [x] Consulted authoritative OpenCode docs/schema and recorded version/enforcement verification gaps.
* [x] Obtained explicit permission to write only the three planning documents despite the initial read-only restriction.
* [x] Consolidated plan, runbooks and decision register into the only tool-authorized file, `PLAN.md`.
* [x] Promoted chat export and vault statistics to required first-class ports with source/consumer tracing, concrete contracts, fixtures and runbooks.
* [x] Reconciled independent review of permissions, phase ordering, recovery, command expansion and privacy boundaries.
* [x] Reviewed phase exits, complete source inventory, and document content for private vault material; no notes, personal context or credentials are included.

### In Progress

* None.

### Remaining

* None.

### Blockers

* None for planning. Real-vault execution is separately approval-gated.

## Findings from initial planning (historical)

* Upstream provides no runnable test suite or CI for the machinery. Its scripts are useful references, not validated acceptance tooling.
* Upstream's declared schema omits fields used by its templates and control pages; the adaptation must establish one coherent contract.
* OpenCode `grep` permissions match the search expression, not a file exclusion list. A read-denied secret is not thereby protected from content search, shell commands, plugins, or MCP tools.
* The draft identifies Funsaized as the intended downstream copyright credit; D1 must confirm the exact notice/license before release. Copyright ownership is not conferred by choosing MIT, and this repository has no license file yet. The upstream notice says exactly `Copyright (c) 2026` without naming a holder. Preserve that notice verbatim and attribute the repository; do not invent an upstream holder or assume third-party linked content is MIT.
* Research-process exception: a delegated follow-up created a temporary upstream checkout outside this repository despite a read-only briefing. No upstream files were installed/copied into the public repository or vault and no upstream scripts were executed. The temporary checkout was not removed by this planning task.

## Planning questions (historical)

* Owner decisions before execution are collected in the Decision Register below; they do not prevent a ready-to-implement, approval-gated plan.

---

## Optional tracks (moved from the implementation runbooks)


Each is an independent approved learning/product project in a disposable synthetic/public-data lab, not a vault installation phase. Re-check external APIs, models and dependency licenses when selecting one. No new SDK, scheduler, MCP, plugin or CI credential is authorized by this plan alone.

### T1. Knowledge graphs — NOT NEEDED FOR VAULT SETUP

**Prerequisite/need:** functioning linked wiki and a question ordinary index/link traversal cannot answer efficiently. Try existing Obsidian graph view first; no database merely to visualize links.

**Inspect:** [overview](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-graph/README.md), [extract](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-graph/build-extract.md), [query](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-graph/build-query.md), [use](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-graph/build-use.md), [`graph_export.py`](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/scripts/graph_export.py). Conceptual/store/resource coverage is inventoried above.

**Checkpoint A:** show motivating question, graph fixture, canonical node IDs, relation vocabulary and provenance/contradiction representation. Approve before extraction.

**Implement later / substitutions:** deterministic wikilink export and small query first; NetworkX only when needed. Typed extraction uses approved OpenCode/provider as a schema-constrained proposal, retaining `found_in`/evidence locators and human review. Native namespaced command replaces `.claude/commands/connects.md` only after query behavior works. No graph database/MCP/embeddings/community summaries by default.

**Deliverables:** canonical edge export, optional provenance-bearing typed edges, neighbor/path report, data dictionary, repeatable fixture checks and read-only usage instructions.

**Verify:** known nodes/edges exact; duplicate titles distinct; alias/display handling consistent; missing/disconnected nodes useful; parallel/contradictory relations and provenance survive; unsupported links reported; only approved export destination written. Check twenty typed rows or all if fewer. Compare usefulness against baseline on the motivating question.

**Show/approve/exit:** export diff, evidence sample, fixture output and baseline comparison accepted. Graduate storage only for measured history/concurrency/size needs.

**Illustrative/unverified:** upstream `DiGraph` example overwrites multiple relations for one directed pair, drops provenance, searches paths without direction, and can crash on missing neighbors. Exporter and linter resolve names differently. Typed extraction is a prompt, not a tested pipeline. External GraphRAG/tool claims were not verified.

### T2. Jev engineering — NOT NEEDED FOR VAULT SETUP

**Prerequisite/need:** bounded classification/routing task, approved data, human labels, known error costs and budget. The track can finish with a stand-in; Jev access is not a vault dependency.

**Inspect:** [overview](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-jev/README.md), [endpoint](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-jev/build-decision-endpoint.md), [router](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-jev/build-router.md), [swap](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-jev/build-swap-in-jev.md), current [vendor docs](https://docs.typesafe.ai/) before integration.

**Checkpoint A:** show labels, human/fallback route, abstention policy, labeled fixtures, privacy/cost/latency/error limits. Approve before API calls.

**Implement later / substitutions:** HTTP/provider SDK is independent of OpenCode. Use deterministic rules if sufficient; otherwise replace Anthropic-specific structured-output/model calls with a verified provider interface. Keep one `decide` seam with validation, timeouts, bounded retries, unknown-label rejection and fallback. Five-sample agreement is `agreement`, not calibrated confidence.

**Deliverables:** decision endpoint, conservative router, redacted bounded log, labeled eval set, comparison report. Actual Jev swap additionally needs approved access/key, verified SDK/call shape, shadow adapter and rollback switch. No raw private tickets or keys in public source.

**Verify:** valid-label contract, malformed/timeout/rate-limit fallback, abstention, held-out per-label errors, measured latency/cost. Before swap, shadow comparison measures errors, p50/p95 latency, cost and calibration against human labels. Recalibrate thresholds: vote fraction and vendor probability are not interchangeable.

**Show/approve/exit:** baseline report first, separate approval for shadow calls and then live routing. Without access, report a completed stand-in exercise—not a working Jev adapter.

**Illustrative/unverified:** upstream marks `jev_decider.py` **UNTESTED**. Endpoint/SDK/model/access/pricing/speed/calibration are upstream/vendor claims not verified here. No out-of-schema outputs does not mean no wrong decisions; unanimous samples can be wrong. Decision/shadow logs need retention limits.

### T3. Agent harnesses — NOT NEEDED FOR VAULT SETUP

**Prerequisite/need:** explicit learning goal or demonstrated missing capability in OpenCode. Default: reuse OpenCode, not a second ingest/query harness.

**Inspect:** [overview](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-harness/README.md), [loop](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-harness/build-the-loop.md), [guardrails](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-harness/build-guardrails.md), [graduation](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-harness/build-graduate.md), [OpenCode SDK](https://opencode.ai/docs/sdk/), [server](https://opencode.ai/docs/server/), [plugins](https://opencode.ai/docs/plugins/).

**Checkpoint A:** show unmet requirement and native capabilities versus custom-loop options. Approve smallest experiment. Claude Agent SDK is not OpenCode SDK; imports/hooks cannot simply be renamed.

**Implement later / substitutions:** learning begins with fake responses and fixed harmless tools, no arbitrary shell. Live model adds verified provider/tool schema, turn/time/token limits, cancellation, result validation and filesystem isolation. Practical work should reuse native agents/skills/CLI/server; plugins/hooks/MCP require independent review and documented interfaces.

**Deliverables:** bounded synthetic loop or native capability demo, tool contract, trace, refusal/termination checks and reuse-versus-build report.

**Verify:** budgets stop execution; malformed calls/denials/provider errors/cancellation handled; untrusted input cannot execute shell; only approved fixtures exposed; repeated requests cannot spin forever.

**Show/approve/exit:** trace, negative tests and justified architecture decision accepted. Production use needs isolation/lifecycle/security checks beyond the teaching exercise.

**Unsafe to copy:** upstream first loop deliberately runs model-requested shell; its prefix allowlist admits chained commands. Interactive confirmation is not sandboxing. Claude hooks/paths are vendor-specific; OpenCode plugins execute startup code not controlled by AGENTS instructions.

### T4. Loop engineering — NOT NEEDED FOR VAULT SETUP

**Prerequisite/need:** independently checkable deterministic goal in a disposable development repo and a reason for automatic retry. Never target the personal vault with unattended repair.

**Inspect:** [overview](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-loop/README.md), [goal test](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-loop/build-goal-test.md), [critic](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-loop/build-critic.md), [overnight](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-loop/build-overnight.md), [OpenCode CLI](https://opencode.ai/docs/cli/).

**Checkpoint A:** show immutable goal tests, allowed paths, attempt/time/spend budgets, repeated-failure detection, cancellation and human handback. Approve attended single-loop experiment first.

**Implement later / substitutions:** replace Claude flags with tested `opencode run` and native permissions, not name substitution. Parse documented JSON events using fixtures; do not assume `total_cost_usd` exists or token count proves spend. If spend cannot be measured, use time/attempt limits plus conservative provider cap; no unattended use until adequate bounds exist. Use subprocess argument arrays, not task-interpolated shell strings.

**Deliverables:** bounded goal loop, optional independent narrow critic only after need, attempt-state report and failure handback. Disposable isolated workspace; no autonomous commits/pushes or dirty-tree resets. Critic approval cannot override failing deterministic tests.

**Verify:** green goal exits; budget exhaustion exits nonzero with evidence; repeated non-improvement stops; timeout/provider/malformed-output failure safe; test edits cannot game success; cancellation terminates children; untrusted task text never shell-executed; original workspace unchanged. Optional ratchet retains accepted improvements without discarding unrelated work.

**Show/approve/exit:** traces, goal/critic output, budget accounting and diff accepted; owner reviews before merge. Overnight operation is a separate proposal, not required track completion.

**Unsafe/unverified:** upstream overnight code uses `git reset --hard`, shell interpolation and a Claude permission flag not verified here. Its JSON cost fields/tools flags do not transfer to OpenCode. Never copy it into a live vault or treat model criticism as access control.

### T5. Eval engineering — NOT NEEDED FOR VAULT SETUP

**Prerequisite/need:** stable behavior and a concrete regression to detect. Core acceptance fixtures are required checks; a full eval platform/CI/provider project is optional.

**Inspect:** [overview](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-evals/README.md), [traces](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-evals/build-traces.md), [suite](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-evals/build-suite.md), [CI](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-evals/build-ci.md), [judge calibration](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/track-evals/llm-as-judge.md).

**Checkpoint A:** show representative public/synthetic cases and error taxonomy. Real traces remain private; construct new synthetic cases rather than copy/redact confidential records into public fixtures. Define protected behaviors and known failures before picking a platform.

**Implement later / substitutions:** target tested OpenCode CLI/server or approved provider, not upstream `from app import answer` placeholder. Deterministic checks first: citation existence/support expectations, abstention, claim/source coverage, forbidden tools, changed paths, index/log consistency. Judge only residual subjective criteria, calibrated against humans. No assumed equivalent of `claude plugin eval`.

**Deliverables:** versioned golden cases, target adapter, per-case outputs/trace metadata/results, optional human-labeled judge subset, baseline/spread report, optionally read-only CI artifacts. Record framework/prompt/model versions and alias drift.

**Verify:** known good/bad outputs classified correctly; empty/malformed cases handled; first-N smoke cases deliberate/representative; outputs available for calibration without private leakage; stochastic repeats show spread/cost; judge scores cannot overrule deterministic safety failures. Choose thresholds from measured baseline.

**CI checkpoint:** deterministic public fixtures on untrusted/fork PRs without secrets. Live provider tests only in approved trusted context, secrets scoped to invoking step, read-only repository permissions, spend limits and sanitized artifacts. Never run untrusted PR code with secrets. No scoreboard commit/push.

**Show/approve/exit:** case inventory, reproduced intentional failure, baseline, false-positive/negative examples, judge agreement if used and CI privacy/cost policy accepted. CI gets separate approval from local suite.

**Illustrative/unsafe:** upstream limits to first-N JSONL lines, divides by zero on empty cases, and omits target outputs needed for calibration. Its CI requests write access and pushes a scoreboard with broadly scoped provider key. Model/action versions, plugin eval and external tools were not verified here.
