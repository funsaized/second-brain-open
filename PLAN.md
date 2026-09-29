# Plan: OpenCode-native second-brain machinery

> Status: public core delivered; native evidence is bounded; project round-trip demonstration outstanding; deployment acceptance is owner-local
> Updated: 2026-09-29
> Execution update (2026-09-24): the owner authorized implementation up to the first blocker/approval gate, including operational autonomy. After the D1 question, “continue” approved MIT with `Copyright (c) 2026 Funsaized`. The original planning record below remains historical; its planning-only restrictions do not revoke that later authorization. Named integration checkpoints remain in force.

## Current delivery status

This summary is the current implementation checklist, reconciled against public
code and evidence through the 2026-09-28 review-backlog slice. The execution history below preserves earlier
results and failures; its old test counts and "next step" statements are not the
current backlog. The phase specifications and runbooks describe requirements and
repeatable procedures, not a list of features that are all still unimplemented.

**Verification baseline:** 134 offline tests pass with
`python3 -m unittest discover -s tests`. Live native probes are opt-in and are not
part of that count. Static fixtures, driver-applied model proposals, native tool
edits, and owner content acceptance are different evidence classes.

### Delivered public machinery

| Phase / runbook | Delivery status | Evidence and limits |
|---|---|---|
| **P0 / R0** — provenance and distribution | Delivered | `LICENSE`, `THIRD_PARTY_NOTICES.md`, inert config example, [installation manifest](docs/installation.md#1-copy-the-files), scope/distribution tests. Per-file installation remains an approved operator action, not a sync service. |
| **P1 / R2** — page and project contracts | Delivered | Contract, seven templates, populated synthetic fixtures and `tests/test_contract.py`. `415d72b` adds flexible learning/reference content and proposal coverage review; the review-backlog slice adds owner acceptance levels (`technical`/`sampled`/`full`). No new metadata types or permissions. |
| **P2 / R1A–B, R3–R4** — ingest/query core | Delivered, with evidence limits | Two roles, two skills, `scripts/link_check.py` (including placeholder, index-coverage and reciprocity checks), manual invocation runbook, opt-in native drivers and the opt-in researcher evaluation. Native ingest/query/repeat/recovery/injection cases are documented; see the evidence table below rather than assuming every planned variant passed natively. |
| **Operator** — autonomous ingest/compile/query | Delivered | `scripts/sb_operator.py` (stage/run/revise/apply/undo), `scripts/sb_runtime.py`, the `second-brain-operator` skill and `docs/operator.md`. Live synthetic runs on OpenCode 1.18.33, including a fully autonomous ingest by the primary agent, are in `docs/native-acceptance-trials.md`. |
| **P2A / R7** — vault statistics | Delivered | `scripts/vault_stats.py`, deterministic synthetic tests and `docs/vault-stats.md`; read-only human/JSON output, fixed `--as-of`, defined denominators. Running a real-corpus report is an owner-local operation. |
| **P2B / R8** — selected chat-export conversion | Delivered | `scripts/chat_export_to_md.py`, supported export/branch tests and `docs/chat-exports.md`. Selected synthetic handoff has native evidence; real-export privacy review and content acceptance remain local decisions. |
| **R6B–C** — reporting and restore rehearsal | Public tools/rehearsal delivered | Checker/statistics plus `tests/test_r6_backup_restore.py` and `docs/backup-restore.md`. The six restore tests prove the invented rehearsal, not an operational private backup or a production backup CLI. |

### Not the same as missing shared code

| Item | Status / next action |
|---|---|
| **P3 / R1C, R3–R4** — deployment and real-source acceptance | Owner-local. Public documentation contains a scoped bootstrap record, not a complete deployment ledger. Consult the relevant local approvals and receipts; absence of private evidence here does not mean an operation has not happened. Do not copy private results into this plan to mark a box complete. |
| **R6A / private R6C** — backup policy and real restore proof | Per-deployment responsibility. Check the actual mechanism, scope, retention and restore evidence locally. The recorded greenfield bootstrap waiver is limited to that completed add-only bootstrap; do not reopen it or treat it as a successful restore test. |
| **R7B / R8B–C** — real reports, export selection and acceptance | Tools are shipped. Whether to run them, which data may be read/sent, and whether their output is accepted are owner-local choices, not unfinished CLI implementation. |

### Outstanding, withheld and deferred work

1. **Outstanding public demonstration: P4 / R5 project round trip.** The project
   brief template and fixture exist. An end-to-end synthetic test of wiki context
   selection → project output/feedback → approved durable promotion is not yet
   documented. Implement that bounded demonstration when this phase is selected;
   do not rebuild the already delivered checker, statistics or restore rehearsal.
2. **Native evidence gaps:** contradiction handling has driver-applied live
   evidence; ambiguous/broken-link handling has offline checker evidence. Native
   variants are not claimed. These are coverage distinctions, not authorization
   to start new model trials or an assertion that the shipped core is absent.
3. **Withheld for safety: `/sb-ingest` and `/sb-ask`.** They are intentionally not
   distributed because command preprocessing exposed denied synthetic content
   and evaluated shell-like arguments. Use direct named-role invocation. Revisit
   wrappers only after a separately approved safe-entry-point change is verified.
4. **Waived, not passed: missing-skill/nonexistent-agent negative scenarios.**
   Historical failures and cheap resource preflight remain. They are not release
   blockers under the recorded amendment; do not restart that campaign merely
   to make the status table uniformly green.
5. **Deferred by need: P5 / T1–T5 and extra agents, skills or wrappers.** No track
   implementation is claimed. These are optional projects, not a setup backlog
   that must all be completed. Scheduling, publication and private Git adoption
   also require separate decisions; none is a default automation requirement.
6. **Review backlog.** [BACKLOG.md](BACKLOG.md) holds the 2026-09-28 review's
   prioritized proposals and records which were closed, implemented or deferred.

### Evidence map

| Evidence class | What is established | Where to inspect |
|---|---|---|
| Offline distribution suite | 134 passing static/CLI/guard tests; includes operator stage/apply/undo/revise, worker search evidence, compact and themed index handling, checker contract checks and researcher-evaluation scoring | `tests/`, current verification baseline above |
| Live researcher evaluation | Scored native `sb-researcher` answers on a staged wiki copy (OpenCode 1.18.33); the synthetic fixture passed 3/3 | `docs/researcher-evaluation.md`; private-wiki results stay local |
| Isolated native runtime probes | Documented version-specific loading/read/refusal behavior; fake-provider cases are not semantic ingest proof | `tests/runtime_read_probe.py`, `tests/runtime_roles_probe.py`, historical execution record below |
| Live, driver-applied semantic rehearsal | Two-source proposals, contradiction retention, repeat and sourced answering; driver applied the pages | `docs/native-acceptance-trials.md` (earlier rehearsals), `docs/synthetic-acceptance.md` |
| Live native named-role trials | Actual approved edits, applied-wiki and raw-source queries, no-op repeat, bounded injection assessment, interruption/operator-mediated recovery and log append | `docs/native-acceptance-trials.md`, `docs/synthetic-acceptance.md` |
| Owner acceptance / private deployment | Not inferred from any test count; maintained outside this repository | Local owner records, never private fixtures or transcripts here |

The native results above are documented observations, not claims that the live
suite was rerun for this status update. Runtime receipts are not committed;
preserve the qualifications and historical failures in the linked evidence docs.

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

## Objective

Supply a small, reusable OpenCode framework from this public repository to a separate local Obsidian vault. Demonstrate one approved source ingestion and one sourced query before adding automation. Preserve the upstream's two content layers: an enduring, source-grounded wiki and time-bounded project work that consumes and feeds the wiki.

`raw/` is an input archive, not a third knowledge layer. A project hub is not a replacement for the wiki. Obsidian remains an editor/viewer; direct Markdown file access is sufficient.

## Standing requirements

These are continuing constraints, not unchecked implementation tasks. Delivery
and remaining evidence are tracked in Current delivery status above.

* Keep public machinery and private vault data physically separate; no reverse sync, vault symlink, public fixtures made from private notes, or automatic publication.
* Preserve provenance, competing claims, bidirectional links, and same-run `wiki/index.md` and append-only `wiki/log.md` maintenance.
* Query from actual pages and their sources; name coverage gaps and do not silently substitute model knowledge.
* Preserve project inputs/process/outputs/feedback and an explicit project-to-wiki promotion step.
* Verify native OpenCode formats and actual permission behavior rather than transplant Claude tool declarations, hooks, or scheduling flags.
* Require owner approval at each integration checkpoint; preserve existing vault instructions, notes, and Obsidian settings.
* Retain upstream MIT notices for adapted material and keep third-party content licenses distinct.
* Give every phase a testable exit criterion, including required safety tests and recovery; keep waivers and failed checks explicit.
* Keep `chat_export_to_md.py` and `vault_stats.py` as **delivered first-class core ports**, with documented CLIs, synthetic regression tests, and operator runbooks—not deferred optional utilities.

## Current State at planning time (historical)

Implementation-time results supersede these initial observations; see
Current delivery status and Execution history above.

* At investigation start this repository contained only `.git/`, with no commits, application, tests, dependencies, or existing plan. This consolidated `PLAN.md` is the only new repository file. The configured remote is the user's public `funsaized/second-brain-open` repository. No commit or push was performed.
* Only the explicitly permitted vault `AGENTS.md` was read. Its integration constraints require small approved steps, direct file access, preservation of notes/settings, source grounding, and optional—not mandatory—tracks. No personal notes or plugin credential file were read. Personal context from that file is deliberately not reproduced here.
* Upstream was inspected at commit [`347feee87b305b291f7264890e5024db422e3467`](https://github.com/undefined-ui/second-brain-os/tree/347feee87b305b291f7264890e5024db422e3467). The website exposes only a navigation shell to direct retrieval, so its corresponding repository Markdown was read.
* Research covered all ten guide sections, all five tracks, 18 skills, 72 commands, six agents, six scripts, the complete vault template, and root licensing/setup material. The detailed inventory and source coverage are recorded below.
* OpenCode's installed version was reported as `1.18.32`. Current public docs/schema were inspected, but runtime config and permission compatibility have not been tested. No local credential/config contents were inspected.

## Delivery approach

The shipped core uses two narrowly permissioned worker roles and their skills for ingestion and read-only querying, launched by an operator skill and CLI that stage, verify and apply each operation. The two proposed slash wrappers are withheld after failed safety characterization. Page contracts, a project brief/handoff contract, a read-only link checker, **first-class chat-export conversion and vault-statistics CLIs**, and synthetic fixtures support the loop. Both CLI ports are delivered even though their optional skill/command wrappers are deferred. Do not ship the whole upstream catalog.

Keep distribution files inert under a public `framework/` directory until explicitly installed. Integrate by reviewing an allowlisted, one-way file manifest; add only approved framework files into the local vault. Never recursively copy a vault, overwrite its root instructions, or use a two-way synchronization tool. First test in a synthetic disposable vault, then use one owner-approved real source.

The public/private boundary is a data-management boundary, not merely `.gitignore`. Agent permissions constrain tool use but are not an OS sandbox. Restrict filesystem exposure and provider context before authorizing private data processing.

### Delivered file layout (key paths)

```text
AGENTS.md                          public machinery development guidance only
README.md                          user overview and documentation navigation
LICENSE                            chosen license for original downstream work
THIRD_PARTY_NOTICES.md              verbatim upstream MIT notice + adaptation map
framework/
  opencode.example.json             inactive, credential-free config fragment
  instructions/wiki-contract.md     merge/reference, never replace local AGENTS.md
  agents/sb-ingestor.md
  agents/sb-researcher.md
  skills/second-brain-ingest/SKILL.md
  skills/second-brain-query/SKILL.md
  templates/{source,concept,entity,synthesis}.md
  templates/{index,log,project}.md
scripts/link_check.py                read-only, managed-wiki scope
scripts/chat_export_to_md.py         first-class local converter, never automatic ingest
scripts/vault_stats.py               first-class read-only wiki health report
docs/                               operating runbooks and evidence summaries
tests/                              wholly synthetic fixtures and runnable checks
```

There is no distributed `framework/commands/` directory. The framework is inert in the public checkout: it does not auto-load under `.opencode/`. Approved integration maps reviewed files to vault-local `.opencode/{agents,skills}/`, a namespaced template folder, and an explicit contract instruction. Keep installed revision and hashes in a local manifest. Local configuration contains resolved paths and provider choices; public examples contain placeholders only.

Use two explicitly selected **primary** roles rather than a delegation tree. This avoids treating `task` permissions as a control on agents invoked directly by the user. Do not replace the owner's existing default agent. Since 2026-09-28 an operator (the owner's primary agent with the `second-brain-operator` skill, or the owner) launches the worker roles through `scripts/sb_operator.py`; see `docs/operator.md`. Any future wrapper must name `agent:`, omit `subtask`, verify the designated skill call and pass argument-expansion safety tests. The earlier namespaced candidates failed those tests; do not copy them into an installation or treat their absence as an accidental missing feature.

### Data and page contract

* Knowledge: `wiki/{sources,concepts,entities,synthesis}/`; control pages: `wiki/index.md`, `wiki/log.md`.
* Project work: `projects/<slug>/{Inputs,Process,Outputs,Feedback}/` plus a local project instruction/brief. Create only when a real project needs it. A single brief may precede the folders; no empty project scaffolding is required for setup.
* Source archive: approved captures in `raw/`; immutable to the ingest agent. Record canonical URL or original artifact, author/publisher when known, publication date when known, capture date, and stable source location. Unknown provenance stays explicitly unknown, not guessed.
* Output: local `output/` or project `Outputs/`; generated work is neither automatically authoritative nor automatically publishable.
* Common page metadata: `title`, `type`, `created`, `updated`, `aliases`, `tags`. Content types are `source`, `entity`, `concept`, `synthesis`; **control types `index` and `log` are explicit exceptions**, not extra knowledge layers.
* Source extensions: `url`, `author`, `published`, `captured`, `raw`; `url` can be absent for a non-web source. `entity.kind` is explicitly documented. Arrays use JSON-compatible flow lists in generated templates; dates use ISO `YYYY-MM-DD`. Do not impose this serialization on pre-existing notes.
* Each material source claim includes a source page and a useful locator (section, page, timestamp, or preserved excerpt). Synthesis distinguishes quotation/source claims, the author's view, and agent inference. Page-level links alone do not establish which source supports which claim.
* Prefer vault-relative, extensionless target paths with display labels, e.g. `[[wiki/concepts/example|Example]]`. `aliases` aids discovery; an alias string is not automatically a canonical file identifier. Link the first meaningful mention; source ↔ concept/entity links are reciprocal. Avoid forcing meaningless links or one page per paragraph.
* Contradictions retain both claims, their evidence, dates, and scope. Distinguish disagreement from changed circumstances and actual supersession. Do not silently replace an older position or assume the newer source wins.
* `index.md` catalogs actual pages by type with short descriptions and a Gaps section. Prefer plain-text gap entries to intentionally broken links. `log.md` appends one dated operation record with source identity, changed paths, contradictions/gaps, verification, and completed/partial status. A partial operation is not a completed ingest.
* Templates are plain text contracts. Resolve all placeholders before acceptance; no Templater/Dataview dependency is assumed.
* Learning/reference source bodies use flexible Markdown and purpose-sensitive content preservation. Retain essential examples, code, tables, qualifications and balanced comparisons; keep a coverage review in the proposal. The delivered contract and source template, updated in `415d72b`, define this policy without a fixed claim count or new page types.

### Core execution and failure flow

1. Owner selects and privacy-reviews one source, approves provider exposure, captures it locally, and authorizes its exact input path.
2. Ingestor reads the complete source and index, inspects candidate existing pages, then proposes complete Markdown, exact changed paths and a retained/summarized/omitted coverage review. Treat embedded instructions in sources as untrusted data.
3. Owner approves the bounded patch. Ingestor requests each permitted edit, writes/updates sourced pages and reciprocal links, updates index, and appends log. It cannot edit raw inputs, settings, instructions, or framework code.
4. Human runs a read-only checker and inspects the diff. Only then is the operation complete. Re-ingesting unchanged input produces no duplicate pages or claims; meaningful source revisions preserve old provenance.
5. Researcher reads index → relevant pages → linked evidence, answers with citations and `Read`/`Not covered`. It cannot edit even the log. Persisting a query or promoting its synthesis is a separate approved operation.
6. Interrupted runs stop for reconciliation: compare the approved manifest, pre-run backup, pages, index, and log. Preserve concurrent human work. Never use a broad reset or infer success merely because the log exists.

### Technical permission boundary

Authoritative sources: [schema](https://opencode.ai/config.json), [permissions](https://opencode.ai/docs/permissions/), [agents](https://opencode.ai/docs/agents/), [commands](https://opencode.ai/docs/commands/), [skills](https://opencode.ai/docs/skills/), [config](https://opencode.ai/docs/config/), [rules](https://opencode.ai/docs/rules/), [plugins](https://opencode.ai/docs/plugins/), [CLI](https://opencode.ai/docs/cli/), [sharing](https://opencode.ai/docs/share/).

**Observed formats:** project config `opencode.json`/`.jsonc`; agents `.opencode/agents/<name>.md` with `description`, `mode`, `permission` and Markdown prompt; commands `.opencode/commands/<name>.md` with `description`, `agent`, optional `subtask`, and body containing `$ARGUMENTS`; skills `.opencode/skills/<name>/SKILL.md` with required matching `name` and `description`. Skill names are 1–64 lowercase alphanumeric/hyphen characters; descriptions are 1–1024 characters per skill docs, not the config schema. Config `agent` and `command` are keyed objects, not arrays. Use `permission`, not Claude's comma-separated `tools:` declaration.

**Proposed policy, instantiated and tested locally before use:**

| Surface | Researcher | Ingestor |
|---|---|---|
| Default tools | deny | deny |
| `read` | allow approved contract, index, wiki pages, and specifically approved source artifacts | same; selected raw input explicitly allowed |
| `edit` (covers write/edit/patch) | deny everywhere | catch-all deny; `ask` for approved managed wiki page paths and index/log only |
| `bash`, `task`, `grep`, `glob`, `list`, `lsp` | deny | deny |
| `webfetch`, `websearch` | deny | deny; capture is an owner action |
| `external_directory` | deny except any precisely reviewed framework resource path needed | same |
| `skill` | allow only query skill | allow only ingest skill |
| `question` | allow | allow |
| `.obsidian/`, secrets, credentials, `.git/`, unrelated files | deny reads/writes | deny reads/writes |
| Runtime config (not permissions) | top-level `share: "disabled"`, `snapshot: false` | same; recovery uses explicit backups |

Rules are last-match-wins: broad denial first, narrow grants next, final sensitive-path denials. `external_directory` belongs **inside** `permission`; external access does not itself restrict edit access. Resolve local resource paths, then verify each tool's actual permission-match representation; do not assume environment expansion in map keys works. **P0 runtime correction:** OpenCode 1.18.32 read requests use worktree-relative patterns, not absolute paths; the initial absolute allow failed the positive probe. Later native trials document bounded accepted edit cases; neither result establishes every tool's mapping in every profile/version. Agent rules override global rules, and global/project configurations merge: a small config fragment alone is not proof of the effective restriction. Inspect inherited agents/tools/plugins and test the actual invoked role, not just the file.

`grep` matches the search regex and `glob` the requested glob, **not every returned file path**. Denying `read` on secrets does not deny search leakage. The minimal loop therefore uses index-first scoped reads, not unrestricted search. Owner-assisted candidate lists cover discovery/recovery until an approved corpus can be searched in filesystem isolation. Do not promise full-vault retrieval recall from index-only reads; disclose incomplete coverage.

No MCP, plugins, custom tools, shell expansion in commands, `@file` interpolation, automatic sharing, auto-approve, or background delegation in the core. `--pure` is documented and listed in local help, but disabling plugins is not full isolation and may affect provider authentication. Verify a clean, owner-approved runtime profile; do not modify the owner's global configuration as a shortcut. A provider-auth plugin, if necessary, is an explicit exception requiring review.

For the isolated path, use a disposable OS identity/container with a clean home/XDG configuration and only approved fixture/data mounts. Explicit `OPENCODE_CONFIG` and `OPENCODE_CONFIG_DIR` may select framework configuration, but they **do not by themselves erase other configuration sources**. Verify inherited global/managed/environment/remote configuration, auto-loaded instructions and compatibility skills are absent or safely restricted. Disable Claude instruction/skill compatibility using options verified against the installed release. In this profile, disable automatic formatters/LSP and remote instructions; restrict every provider route, including `small_model`/title/summary use, to the approved data policy. Stop if managed policy or authentication bootstrap injects unreviewed capabilities.

Before private use, inspect an allowlisted effective-config summary locally: permissions, top-level share/snapshot, agent/command selection, MCP/plugin presence, instruction paths/URLs (not contents), formatter/LSP, provider allowlist, and auxiliary model routing. Never print an unrestricted resolved config: nested MCP/plugin/provider fields can contain credentials. Where the runtime lacks a safe summary interface, the engineer must inspect/redact locally without exposing secrets to this public session; inability to verify effective configuration blocks integration.

Tool permissions are **not** OS access control. For an enforceable secret boundary, isolate the process identity/container as well as exposing only an approved corpus without `.obsidian/` or credentials; a staging folder under the ordinary unisolated runtime is not enough. The isolated agent never uses the personal vault as cwd and never receives its personal `AGENTS.md`; it reads only an approved generic contract. The owner applies a reviewed per-file patch/copy to the local vault after checking preimage hashes—never wholesale sync. No new installer/applier service is required. Direct-vault use is a distinct option only after acceptance that vault/global instructions may be automatically sent to the provider regardless of read-tool denials, plus all permission gates. Symlinks and path traversal must be rejected or proved confined with fake fixtures.

Provider calls and local transcripts can retain private content even with sharing disabled. Establish provider/data approval, local session retention, and backup handling before the first real source. Never use the real credential file as a negative-test fixture.

## Decisions

See the Decision Register below for resolved choices, per-deployment decisions and their consequences. Proposed defaults are not permission to execute them. The original planning-only write restriction is historical; delivered operating runbooks now also live under `docs/`.

### Minimal core, not a catalog port

**Choice:** Two skills, two explicitly invoked roles, explicit contracts, a read-only link check, and delivered chat-export/statistics CLI ports. The two command wrappers remain withheld. Maintenance, chat triage, and project handoffs start as reviewed procedures; automation around them is not required to make the underlying tools first-class.

**Rationale:** Upstream identifies ingest/query as load-bearing. Most of its 72 commands are thin prompts routing to 18 skills, not independent implementations. Broad command coverage adds risk before proving the loop.

**Alternative:** Copying every skill/command/agent is rejected: it imports unsupported integrations and a much larger permission surface.

### One-way reviewed distribution

**Choice:** Versioned allowlist and file-by-file copy/merge after approval; no installer or sync daemon in the core.

**Rationale:** The public repo ships machinery, not vault contents. Explicit review protects local edits and keeps upgrades reversible. Existing vault instructions are merged, never replaced.

### Source fidelity before convenience

**Choice:** Canonical paths, claim locators, preserved contradictions, raw immutability, and report-before-repair.

**Rationale:** A source summary without links or a confident uncited answer fails the user's goal even if a command reports success.

## Phase specifications and exit criteria

Dependency order: provenance/distribution and safety → page contract → synthetic ingest/query and link checker → required statistics/chat-export ports (P2A/P2B, independent of each other) → approved local integration and real-source proof → project handoff and operations. Optional tracks branch only after a relevant need exists.

The phase descriptions retain the intended scope and exit criteria. Status lines
distinguish delivered artifacts from evidence gaps and owner-local gates; do not
interpret a procedural "implement" or "verify" step as proof that it is still
outstanding. The current delivery summary is authoritative for public status.

### P0. Establish provenance and safe distribution

**Status:** public baseline delivered; per-deployment runtime checks remain necessary.

**Files:** `README.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md`, public `AGENTS.md`, `.gitignore`, `framework/opencode.example.json`; synthetic security fixtures under `tests/`.

**Changes:** choose the downstream license; preserve the exact upstream MIT notice; record source SHA/file mapping for adaptations. Define the allowlisted install/upgrade/rollback manifest and inert framework layout. Deny public data directories, runtime captures, credentials, and Obsidian settings without hiding intended synthetic fixtures. Resolve an isolated test profile and validate effective OpenCode permissions before any private input.

**Dependencies/risks:** owner license/provider decisions; runtime `1.18.32` versus moving docs/schema; inherited tools, global instructions, plugins, symlinks, and config merging can bypass expectations. `.gitignore` is not a secrecy boundary.

**Exit:** a disposable deny-default test role/profile (not the P2 ingest/query implementation) passes baseline confinement/read/refusal tests and effective-config inspection; manifest has no vault data; license notices reviewed; no auto-share/auto-approve. Show sanitized results and manifest. The complete named-role and command matrix is repeated after those roles exist in P2; P0 does not depend on P2. See R0–R1.

### P1. Establish page and project contracts

**Status:** delivered, including the content-preservation policy follow-up.

**Files:** `framework/instructions/wiki-contract.md`, seven templates listed above, synthetic fixture pages.

**Changes:** reconcile schema with all four content templates and index/log exceptions; document claim locators, links, gaps, contradictions/supersession, immutable source archive, and project-to-wiki promotion. Define canonical filename/metadata handling and distinguish unknown facts from inferred facts.

**Dependencies/risks:** P0; collision with existing names/templates; over-extraction; importing illustrative frontmatter inconsistently.

**Exit:** one populated example of each content type and both control pages has no placeholder residue; every fixture claim traces to its evidence; a conflicting fixture preserves both positions; project brief references wiki knowledge without replacing it. Show examples and schema before local template installation. See R2.

### P2. Implement and prove the smallest loop in a synthetic vault

**Status:** core delivered with documented native evidence; wrappers withheld,
missing-resource scenarios waived, and native contradiction/ambiguity variants
not claimed. See the evidence map above for the level of each result.

**Files:** two agents, two skills, `scripts/link_check.py`, synthetic tests and native trial drivers. Proposed command wrappers are not distributed.

**Changes:** adapt upstream ingest/query semantics using explicit OpenCode roles, not Claude tool declarations or unsafe command interpolation. Strengthen the link check only to support the documented managed-page contract: vault-relative paths, display labels, fragment handling, ambiguous basename reporting, frontmatter exclusion from link counts, managed-wiki scope, non-mutating reports, failure exit status. Do not build a general Obsidian/YAML parser. Unsupported link forms must be reported, not silently counted as valid. Validate the narrow generated metadata format; defer arbitrary legacy YAML normalization.

**Dependencies/risks:** P1 + permission smoke tests; prompt injection in source text; incomplete read; broken reciprocal links; partial writes; false linter reassurance. Existing upstream scripts conflate wiki/project/output and resolve aliases inconsistently.

**Order within P2:** checker fixtures preceded adaptation, then roles/skills and their boundary matrix. Candidate wrappers were tested and withheld; direct named-role invocation became the approved path for subsequent native ingestion trials. Baseline checker grammar is `[[vault/relative/path]]` or `[[vault/relative/path|label]]`, resolving to an in-scope `.md` file with exact path identity. Fixtures include valid display label/space path, missing target, two identical basenames in different directories, and malformed syntax. Strip a fragment only for file-existence checking, and report heading/block-anchor validity as **unchecked**, not verified. Report embeds and bare/alias-only targets as unsupported until explicitly adopted. Do not count frontmatter/fenced-code examples as graph links. These limited checks do not prove full Obsidian compatibility or factual support.

**Exit:** one synthetic ingest, repeat-ingest, contradiction, interruption/recovery, source-injection, missing-evidence query, ambiguous/broken-link fixture, and sourced query pass. Raw files are unchanged, index/log agree with actual changes, researcher writes zero files, and the checker itself changes zero files. Show diffs, claim/source matrix, refusal evidence, and test output. See R3–R4.

**Owner amendment (2026-09-25):** missing-role/skill negative scenarios are not
release blockers; the operator ensures the intended resources exist. This does
not waive path/permission scope, provenance, raw immutability or recovery checks.

### P2A. Deliver the first-class vault statistics port

**Status:** delivered; real-corpus reporting is an owner-local choice, not a missing port.

**Files:** `scripts/vault_stats.py`, reusable pure collection/link-resolution functions in `scripts/link_check.py`, synthetic CLI tests and usage documentation. Reuse those functions between the two real consumers; do not add a generic graph framework.

**Upstream purpose/consumers:** `scripts/vault_stats.py`; `skills/second-brain-metrics/SKILL.md`, `skills/second-brain-graph/SKILL.md`, and `docs/05-graphs/metrics.md`. The existing script does not supply component count or stale-concept rate even though its consumers request them.

**Contract/adaptation:** retain the positional vault argument; add documented `--json` and reproducible `--as-of YYYY-MM-DD`. Read only adopted `wiki/{sources,entities,concepts,synthesis}/` content pages; controls, project/output/raw/template/settings/instruction files are excluded from node and link denominators. Parse type/updated only from the leading supported frontmatter. Canonical relative paths identify nodes; collect unique directed non-self links between nodes. Report page/type counts, resolved links, average out-degree `E/N` (explicitly named), average total directed degree `2E/N`, inbound orphan count/rate, weak component count/largest component share, stale-concept count/rate (>90 days relative to as-of), invalid/missing/future update-date counts, and sorted most-linked pages. Stale rate denominator is concepts with valid non-future dates; show total/eligible/unknown counts so missing dates are not silently fresh. Empty corpus yields zero counts and null/not-applicable rates, not division by zero. Unknown/broken/unsupported links remain visible and are not edges; link validation stays the checker's job.

**Safety:** read-only CLI run by the owner on an approved scope, never an excuse to grant agents Bash. Reject escaping symlinks/paths, never modify index/log or append a metrics note automatically. Human-readable output can contain private titles/paths; keep real output local. JSON includes scope/metric definitions and as-of, and sorts collections for deterministic tests.

**Dependencies/risks:** P1 contract and P2 shared link semantics. Upstream counts repeated mentions, collapses basenames, includes project/output and control files, mislabels `E/N` as generic degree, and lacks required metrics. Document intentional semantic changes; do not compare old/new trend values without noting the new definition.

**Exit:** deterministic fixture with 4 nodes `a,b,s,c`, edges `s→a`, `a→s`, `a→b` (duplicate mentions deduplicated), and isolated `c`: `N=4`, `E=3`, out-degree `0.75`, total degree `1.5`, orphan `1/4`, components `2`, largest share `3/4`. With three concepts (one >90 days old, one exactly 90 days, one invalid), stale is `1/2` eligible with one unknown. Control/project/raw/output links do not alter values. Empty/malformed/date-boundary/duplicate-basename/fragment fixtures pass; same as-of repeats identically; all input hashes unchanged. Show table/JSON and tests. See R7.

### P2B. Deliver the first-class chat-export converter

**Status:** converter and selected synthetic native handoff delivered; owner content
acceptance is separate from technical evidence. Real-export approval is per deployment.

**Files:** `scripts/chat_export_to_md.py`, synthetic Claude/ChatGPT fixtures, CLI regression checks and usage documentation.

**Upstream purpose/consumers:** `scripts/chat_export_to_md.py`; `docs/03-ingestion/chat-exports.md`, `skills/second-brain-chat-import/SKILL.md`, and `commands/ingest-chats.md`. Convert conversations to faithful local Markdown before privacy review/triage, not directly into wiki knowledge.

**Contract/adaptation:** preserve positional `export outdir` and `--min-words` (default 150); document a no-write `--dry-run`, explicit conversation-ID selection, and count-only default summary. Support the upstream list/`conversations` wrapper with Claude `chat_messages` and documented simple `messages`, plus ChatGPT `mapping`/`current_node` with `message.author.role`. For mapping exports, walk parent ancestry from current node, reverse to chronological order, skip structural null-message nodes, and preserve the selected branch only. Unselected sibling branches are valid and ignored. Missing current node/leaf/parent, cycles, or an invalid multiple-parent walk are errors, not a guessed flat merge. Identify unsupported formats separately from short conversations. Preserve user/assistant roles, message order, known timestamps, and source conversation identity; do not treat assistant statements as independent evidence.

**Boundary/data handling:** conversion is local deterministic stdlib work, no model/API calls. Owner chooses a private staging destination outside both public repo and live wiki; an export is never bulk-ingested. Normalize epoch/ISO dates to documented UTC dates, keep unknown dates unknown, quote title/provenance scalars safely, preserve textual content, and explicitly report omitted non-text attachments/tool payloads. Do not claim lossless conversion of unsupported media. Reject malformed input before writes where possible; partial failure reports written/failed IDs without message text and never promotes results.

**Output identity/re-runs:** source ID plus short content digest identifies the emitted version; source ID may be derived deterministically from content if absent. Titles are display metadata, not unique IDs. Restrict filenames to safe components, reject destination escape/symlink hazards, never overwrite existing files. Identical rerun skips verified identical content; changed content gets a distinct version without deleting the earlier one. Do not silently add a new suffix on every identical run. Dry-run performs no mkdir/write. This needs no persistent database or sync service.

**Dependencies/risks:** P0 privacy/distribution, P1 provenance contract and R3 single-conversation ingestion. Upstream silently skips ChatGPT mapping exports as short, loses author roles, truncates epoch numbers as dates, mishandles non-string parts, emits unquoted YAML titles, and duplicates files on rerun. Synthetic fixtures establish supported shapes; do not claim every current vendor export is verified without an owner-approved sample review.

**Exit:** Claude and branching ChatGPT fixtures retain correct order/roles/text/dates and selected branch; malformed/missing/cyclic mappings are explicit failures; min-word boundary/quoted title/multimodal omission/duplicate title/repeat-run/change-version/path escape/partial failure tests pass. Dry-run writes nothing; original export unchanged; writes confined to approved staging. One selected synthetic conversation passes privacy review then R3/R4, with assistant content correctly attributed. Show count report, synthetic diff, conversion fidelity checks and source-grounded result. See R8. No private chat export is required for acceptance.

### P3. Approve local integration and perform one real ingest/query

**Status:** owner-local deployment checklist, not unfinished shared implementation.
Consult local approvals and evidence before calling an item outstanding. The public
bootstrap record below is not a complete account of later private operations.

**Files:** only the owner-approved local install targets and managed pages; no local content enters public files.

**Changes:** inspect non-sensitive topology and path conflicts locally; preserve settings and existing instructions; create/verify an external private backup before writes; review the one-way manifest; approve provider exposure and exact source. Apply the same tested loop to one real source, not a bulk import.

**Dependencies/risks:** P0–P2 including delivered P2A/P2B tool ports; owner's explicit path/provider/source/backup approvals; concurrent note editing; real source complexity/confidentiality. **Default deployment gates:** R6A backup policy and R6C isolated restore proof, subject only to explicit narrowly scoped owner exceptions such as the recorded add-only bootstrap waiver below. Check local completion records and applicable exceptions before treating a step as outstanding. This plan grants no new waiver and does not reopen completed bootstrap checks. R6 is a reusable procedure, not work automatically deferred until P4. If direct runtime confinement is unavailable, use separately isolated staging and an owner-applied patch, not an unisolated staging folder or sync.

**Scoped owner exception:** the later greenfield approval waives initial backup
for the approved new-file-only machinery bootstrap. It is not a passing private
restore test or permission to overwrite existing content, modify settings, process
private sources, or expand provider/tool access. Those decisions remain separate.

**Exit:** owner verifies complete source read, correct attribution, reciprocal links, index/log and raw immutability, a sourced answer and honest coverage gap, no unrelated file changes, and a successful private restore drill. Public repo diff contains machinery/tests only. Show private evidence locally, not in public reports. See R1, R3, R4, R6.

### P4. Establish project handoffs and routine recovery/maintenance

**Status:** partial. Project contract/template and maintenance/reporting tools exist;
the end-to-end synthetic project-to-wiki round-trip demonstration is outstanding.
Private backup/restore and operating cadence are owner-local checks.

**Files:** delivered project template, operating instructions and checker/restore fixtures; add the missing round-trip evidence when approved. Local project files only with specific approval.

**Changes:** demonstrate wiki → project context selection → output/feedback → reviewed durable promotion with source lineage. Define report-only lint, index/log reconciliation, safe rename/merge proposals, private versioning options, backups, restore drills, and retention. No scheduler or autonomous git operation.

**Dependencies/risks:** P3; project outputs mistaken for evidence, private output publication, overly broad reset, backups containing secrets.

**Exit:** one synthetic project handoff is verified end-to-end, one partial run is recovered without overwriting concurrent work, a deliberate broken-link/index discrepancy is detected, and a private backup restoration is checked by path/hash comparison. Owner approves cadence and whether to adopt private Git later. See R5–R6.

### P5. Optional tracks, each separately approved

**Status:** deferred by need; no optional-track implementation is claimed in this repository.

**Files:** a separate owner-approved lab/project, never prerequisites inside the vault framework. See runbooks T1–T5 below.

**Dependencies:** working core plus a concrete graph, routing, harness, bounded-loop, or evaluation need. These tracks do not depend on each other.

**Exit:** only the selected track's concrete deliverables and negative tests pass, costs/data exposure are approved, and the owner accepts its report. No track completion is required to declare vault setup complete.

## Validation

Run the offline distribution suite from the repository root:

```sh
python3 -m unittest discover -s tests
git diff --check
```

Current result: **134 tests pass**. The structured source-template test is static
compatibility evidence, not proof of model editorial quality. Historical counts
in the execution record and dated evidence reports describe their own checkpoints.

Opt-in runtime and live-provider trials are separate; see the evidence map and
`docs/native-acceptance-trials.md`. Do not rerun them merely to edit this plan or
turn waived cases into passing ones. Runtime version, route, inputs, approvals
and isolation must be checked for an actual deployment. `--format json` is an
event-output mode, not a guarantee that a model answer satisfies a schema.

Never use private content as a public fixture or print a real-vault secret scan.
Owner content acceptance, private recovery and deployment records remain local;
neither an offline pass nor a historical native trial proves those outcomes.

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

## Implementation Runbooks

> Repeatable procedures and original exit criteria, not a claim that every step is unexecuted. R0–R4 and R6–R8 have delivered public components/evidence as summarized above; R5's round-trip demonstration remains outstanding. Resolve only the relevant owner-local choices at each use. A delivered public rehearsal is not a private deployment receipt.

Every checkpoint follows **inspect → propose/implement within the previously approved scope → verify → show evidence → obtain approval for the next step**. A passing test is not authorization to install into the personal vault, publish, commit, or push. Use synthetic/public material in this repository; keep real-source diffs, logs, transcripts, and backups local and private.

Upstream references are pinned to `347feee87b305b291f7264890e5024db422e3467`. No shell snippet should be executed merely because it appears in an upstream guide.

### R0. Establish provenance, scope, and reviewable distribution

**Supports P0.**

**Inspect**

* [Upstream license](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/LICENSE), [README quickstart](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/README.md), [vault template](https://github.com/undefined-ui/second-brain-os/tree/347feee87b305b291f7264890e5024db422e3467/vault-template), and this plan's component inventory.
* Public working-tree status, downstream license, and changes since this plan. Do not assume the repo remains empty.
* Installed OpenCode version and current [config schema](https://opencode.ai/config.json). Moving documentation alone is not a runtime compatibility guarantee.

**Delivered distribution procedure; reapply its checks for each approved install/upgrade**

1. Obtain approval for downstream license and core scope. Add the exact upstream MIT notice and source/change attribution for each selected adaptation. Preserve `Copyright (c) 2026` verbatim; do not invent a holder. Reference third-party writing rather than copy it under MIT.
2. Use the inert `framework/` layout. Publish generic examples and synthetic fixtures only; no owner biography, real project inventory, usernames, absolute private paths, notes, or credentials.
3. Define an install manifest: source revision, public source path, intended local destination, existing-file/collision status, and copy-versus-merge action. Expand destinations only in the local manifest.
4. Add public-repo exclusions for `.obsidian/`, `.env*` and credential artifacts, runtime/session exports, and accidental root `raw/`, `wiki/`, `projects/`, `output/` directories. Preserve explicitly intended synthetic fixtures. Exclusions are a secondary guard, not permission to put vault data in the repo.
5. Upgrade by reviewing old installed revision → new framework revision → local file. Preserve local customizations; stop on conflicts. No `rsync --delete`, recursive vault copy, private-data symlink, or reverse sync.

**Verify / show / approve**

* Show file-level attribution and install manifest. Every destination has a reason and approval requirement.
* Rehearse install and rollback on a synthetic pre-existing vault with conflicting instruction/template filenames. Existing files remain unchanged unless a merge was approved.
* Inspect public diff and fixtures for private data/credentials; do not scan real private sources into a public transcript.
* **Exit:** license choice, attribution, inert layout, and one-way install/upgrade/rollback method approved. This public checkpoint alone does not authorize local integration or determine a private deployment's status.

**Do not copy blindly:** upstream `cp -r vault-template ~/brain` assumes a new vault; its ignore file does not protect all plugin/vault data. `/install` targets `.claude/`, not OpenCode.

### R1. Prepare a safe runtime and integrate only approved files

**Supports P0 and P3. Public synthetic checks are delivered; local use requires the applicable P3 approvals and recovery evidence, with explicitly scoped exceptions honored. Consult local records rather than assuming private gates remain unmet.**

**Inspect**

* Owner-approved vault instructions and non-sensitive topology only. Ask the owner to confirm managed paths/collisions rather than listing personal notes in public reports. Never read the Local REST API plugin credential file.
* [OpenCode config](https://opencode.ai/docs/config/), [agents](https://opencode.ai/docs/agents/), [permissions](https://opencode.ai/docs/permissions/), [skills](https://opencode.ai/docs/skills/), [commands](https://opencode.ai/docs/commands/), [rules](https://opencode.ai/docs/rules/), [plugins](https://opencode.ai/docs/plugins/), [sharing](https://opencode.ai/docs/share/), [CLI](https://opencode.ai/docs/cli/).
* [Upstream safety](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/06-agents/safety-and-guardrails.md), [direct files versus MCP](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/02-setup/mcp-obsidian.md), [project scoping](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/02-setup/project-scoping.md).

**Checkpoint A — runtime/provider proposal**

1. Record version, owner-selected provider/model, authentication mechanism, approved data classes, retention, and whether context leaves the machine. Do not print credentials or run a full resolved-config dump.
2. Use the isolated-profile mechanism in Technical Permission Boundary: clean OS identity/container and home/XDG configuration, approved mounts, explicit config selections, no unreviewed inherited/managed/remote/environment overrides. Verify `OPENCODE_CONFIG`/`OPENCODE_CONFIG_DIR` do not leave inherited capabilities active. Disable compatibility instruction/skill discovery and automatic formatters/LSP using version-verified settings. Review required auth exceptions without copying secrets; do not change the owner's global configuration.
3. Apply the permission table above: default-deny, scoped reads, ingestor ask-to-edit approved wiki files, researcher deny edits, no shell/task/search/network. Final denies cover settings, credentials, instructions, framework and out-of-scope files. No home-directory grant or private-vault reference in public config.
4. Explain that native-tool permissions do not sandbox provider/plugin code, global instructions, or the OS process. Prefer an isolated approved-data workspace for a hard boundary. Obtain explicit acceptance of residual exposure before direct-vault mode.
5. Set **top-level** `share: "disabled"` and propose **top-level** `snapshot: false`, not entries in agent `permission`. Replace snapshot recovery with explicit backup. Inspect a sanitized effective subset including all auxiliary provider/model routes. Session logs still exist; these options do not suppress all storage/telemetry.

**Show/approve:** credential-free profile design, permission table, provider/data flow, local retention/backup plan, and exact read/write scope. Preserve the existing default agent and Obsidian settings.

**Checkpoint B — synthetic enforcement test**

Create a disposable synthetic vault outside public source with approved wiki/raw content and **fake** sensitive files. Never point a probe at real credentials or unrelated private directories.

| Probe | Required result |
|---|---|
| Read approved index/page/source | succeeds only for authorized inputs |
| Read fake `.obsidian/` secret, fake `.env`, unrelated root file | refused; fake value absent from transcript |
| Researcher write/edit/patch wiki or log | refused; hashes unchanged |
| Ingestor edit approved wiki page | asks; rejection changes nothing; inspect requested path and suggested approval pattern; no broader grant is assumed from `once` |
| Ingestor edit raw/instructions/config/skill/settings/unrelated notes | refused |
| Shell, grep/glob/list, network, task, unapproved skill | refused |
| Path traversal, outside absolute path, symlink to fake outside secret | refused or runtime rejected as unsafe; no private integration until confined |
| Malicious path/instruction in command arguments | treated as input, no permission expansion |
| Source instructs agent to read secrets/change policy/use shell | treated as untrusted source text; forbidden actions refused |
| Restart and role/command selection | same effective restrictions; no permissive-agent fallback |
| Auto-share/auto-approve | disabled; no shared-session URL |
| Actual command invocation with fake `@file` / shell-interpolation-like argument | no unintended expansion/access; test through command UI or version-confirmed command CLI, not just a direct-agent prompt |
| Missing/broken named agent or skill | waived as a release/acceptance blocker; refusal is not claimed as passing. Verify actual resources at launch and retain historical failure evidence; do not restart the waived campaign. |
| Synthetic inherited instruction marker/remote instruction endpoint/formatter | absent/not fetched/not run in isolated profile; no extra provider route |
| Share action and snapshot/undo behavior | sharing remains disabled and no snapshot created; use synthetic data only |

Test actual tool enforcement, not merely an agent promising refusal. If the model will not attempt a forbidden action, use a deterministic runtime/tool test where available, or record the coverage gap and withhold the corresponding safety claim. Injection fixtures supplement permission tests; they do not replace them.

Discovery diagnostics may print prompts/paths; review locally and publish sanitized outcomes only. Local help confirmed `opencode run --pure --agent <name> --format json "<prompt>"`, but behavior must be tested. `--pure` alone is not isolation and may affect authentication. Never use `--auto` or `--share`.

**Exit B:** required positive/negative probes pass, with waived missing-resource scenarios explicitly distinguished. Unresolved path confinement or inherited-policy behavior blocks private integration. Show results and effective restrictions for approval.

**Checkpoint C — owner-local integration after confirming applicable P3 approvals and recovery requirements, including recorded scoped exceptions**

1. Pause edits to affected paths. Confirm the applicable R6 backup/restore requirements and local evidence; make/verify the required backup unless an explicit scoped exception covers this operation. Do not reopen the completed add-only bootstrap waiver or initialize vault Git without separate approval.
2. Present the manifest. Add only approved namespaced agents/skills/templates and notices; merge or reference the contract from existing instructions. Withheld wrappers are not install targets. No replacing root `AGENTS.md`, bulk copy, or Obsidian changes.
3. Record installed revision, hashes, and pre-existing-file backups locally, never in public source.
4. Quit/restart OpenCode after config/agent/skill changes; repeat discovery/confinement checks. Running sessions may retain previous policy.
5. With staging, expose approved content and generic contract only in the isolated profile; never load personal vault instructions there. The **owner**, outside the agent runtime, applies the reviewed path-by-path patch/copy after checking preimage hashes. On drift, preserve human work and ask which version to keep. Never wholesale-sync staging back.

**Exit C:** delivered public prerequisites are available, applicable owner-local approvals/recovery requirements are satisfied or explicitly excepted, and the owner verifies the local diff, preservation and confinement. Record any exception rather than claiming a restore was demonstrated. Authorize source work separately; this public checklist does not determine which local operations have already occurred.

### R2. Establish wiki contract and templates

**Supports P1.**

**Inspect**

* [Two layers](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/01-concepts/two-layers.md), [vault structure](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/02-setup/vault-structure.md).
* [Page types](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/04-structuring/page-types.md), [frontmatter](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/04-structuring/frontmatter-schema.md), [linking](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/04-structuring/linking-rules.md), [contradictions](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/04-structuring/contradictions-and-supersession.md), [index/log](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/04-structuring/index-and-log.md).
* [Actual templates](https://github.com/undefined-ui/second-brain-os/tree/347feee87b305b291f7264890e5024db422e3467/vault-template/templates), [root contract](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/vault-template/CLAUDE.md), [control pages](https://github.com/undefined-ui/second-brain-os/tree/347feee87b305b291f7264890e5024db422e3467/vault-template/wiki).

**Delivered contract/template procedure; review changes before redistributing**

1. Write one authoritative contract, then derive templates. Include source provenance, `entity.kind`, index/log exceptions, projects, and unknown-value handling.
2. Preserve source identity/claims/relevance/links; concept definition/support/opposition/questions; entity identity/mentions; synthesis question/evidence/disagreement/current position/what would change it. Do not require synthesis on every ingest.
3. Establish canonical file identity/path rules and supported fragments/embeds; resolve duplicate titles before writing. Metadata aliases are not automatically target files. Report unsupported forms honestly.
4. Require claim-level evidence locators. Project observations can be evidence, but retain artifact/date/scope/limitations and label them as observations.
5. Index actual pages; list missing ideas as Gaps without pretending they exist. Append dated operations with status, paths, contradictions and checks. Corrections append new records.
6. Exclude old notes from automatic backfill. Record human-authored protected pages in local policy; do not rely solely on optional upstream frontmatter.

**Verify / show / approve**

* Populate four content templates, index/log and one project brief with fictional/public evidence. Check fields/dates/arrays, placeholder removal, links, and source traceability.
* Show conflicting claims without automatically choosing a winner. True supersession explains why, not merely which source is newer.
* Project goals/deadlines/tasks stay project-local; reusable conclusions can enter the wiki with provenance.
* **Exit:** owner approves contract/sample pages before local installation.

**Do not copy blindly:** upstream schema omits fields its templates use and index/log types. `{{title}}` does not mean a plugin exists. Confidence/publish/human-maintained/typed-link fields scattered across prose are not one mandatory schema.

### R3. Capture and manually ingest one source

**Supports P2 and P3.**

**Inspect**

* [Ingest skill](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/skills/second-brain-ingest/SKILL.md), [command](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/commands/ingest.md), [agent](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/agents/ingestor.md).
* [Capture](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/03-ingestion/web-clipper.md), [PDFs](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/03-ingestion/pdfs-and-books.md), [backfill](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/03-ingestion/bulk-backfill.md).

**Checkpoint A — source and proposed patch**

1. Owner selects a short public source for the first real proof. Preserve a local capture with canonical URL/capture date. Public availability alone does not authorize copying it into public fixtures; review its license.
2. Verify completeness, author/date when known, encoding/assets, and conversion fidelity. Preserve page/timestamp locators. If reading exceeds context limits, stop for a bounded extraction/reading plan; a truncated tool response is not a complete read.
3. Review confidentiality/provider exposure. Capture is an owner action; the core agent has no web/REST/MCP access or raw-write permission.
4. Ingestor reads the whole source and index, opens candidate pages/evidence, and proposes changed paths. Obtain owner-supplied candidates if the index is incomplete; do not quietly broaden search permissions.
5. Show source identity, claim locators, new/updated pages, reciprocal links, contradictions, gaps, raw hash and protected paths. Extract only reusable concepts/entities, not one page per paragraph. In an empty wiki, linking the new source and concepts/entities to each other is valid; do not invent pre-existing connections.

**Approve before writes:** exact source/provider scope and paths. Do not use session-wide “always approve” as a shortcut.

**Checkpoint B — bounded writes and verification**

1. Capture preconditions/hashes and private backups of affected paths. Stop on drift/concurrent changes.
2. Apply source/concept/entity changes with attribution and first-mention/reciprocal links. Keep earlier conflicting evidence intact; record competing scope/dates.
3. Update `wiki/index.md` and append truthful `wiki/log.md` status. After partial failure, report completed/remaining paths and reconcile before retry; do not record a completed ingest prematurely.
4. Human runs read-only checks and reviews the whole changed set. Corrections are separately bounded. Raw hash and unrelated files remain unchanged.
5. Report `Ingested`, `New pages`, `Updated pages`, `Links added`, `Contradictions found`, `Gaps created`, plus verification and partial/completed status. Prose success is not sufficient evidence.

**Acceptance cases**

* Synthetic and approved real ingests have attributable claims, reciprocal links, current index, matching log.
* Repeat unchanged source produces no duplicate pages/claims. Revised capture retains earlier provenance instead of silent replacement.
* Conflicting claims retain both evidence/date/locators; missing facts remain unknown.
* Interrupted ingest resumes or restores only its paths, without duplicate completion records or lost unrelated work.
* Embedded malicious instructions cannot change policy or read outside scope.

**Exit:** show diff, claim/source matrix, checker output, unchanged raw hash, index/log agreement and gaps; owner accepts. Stop before backfill.

**Do not copy blindly:** upstream ten-item batches follow a successful single-source loop, not precede it. Its “dead links” Python snippet only prints input. Chat/newsletter/media/live-data inputs need separate confidentiality/consent/provider checks.

### R4. Query the vault with sources, not model memory

**Supports P2 and P3.**

**Inspect**

* [Query skill](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/skills/second-brain-query/SKILL.md), [researcher](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/agents/researcher.md), [ask command](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/commands/ask.md).
* [Questions](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/07-retrieval/asking-questions.md), [search](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/07-retrieval/search-tools.md), [context](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/07-retrieval/context-budget.md), [wiki versus RAG](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/01-concepts/wiki-vs-rag.md).

**Delivered query procedure; apply only to approved local inputs**

1. Explicitly invoke `sb-researcher` and its query skill with a vetted request. `/sb-ask` remains withheld; no unrestricted-agent fallback or arbitrary file interpolation.
2. Read index → relevant pages → outward links/evidence. Stop when evidence suffices or budget/coverage is exhausted, and disclose the limit.
3. Answer with canonical page references and source locators; distinguish source claims from conclusions, and disclose disagreements/dates. Core default: omit outside knowledge.
4. End with `Read` and `Not covered`; offer an ingest/synthesis next step without doing it.
5. Damaged/incomplete index means request approved candidate paths or a separate repair. Index-only retrieval is a deliberate safety/recall tradeoff, not proof of exhaustive coverage.

**Verify / show / approve**

* Test supported fact, conflicting-source comparison, and unsupported question. Every cited destination exists and supports its associated claim; unsupported question abstains.
* A fact found only in project output is identified as project-derived or outside current coverage, not established wiki knowledge.
* Compare before/after corpus hashes: zero writes, including index/log; zero network/shell calls.
* **Exit:** show answer, claim/source matrix, consulted pages, gaps and zero-write evidence. Persisting the answer/synthesis needs a new approval.

**Do not copy blindly:** embeddings/GraphRAG are optional, not provenance substitutes. A `read` deny is not secret-safe broad grep.

### R5. Project ↔ wiki handoff

**Supports P1 and P4. No real project scaffolding without current need.**

**Inspect**

* [Two layers](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/01-concepts/two-layers.md), [project template](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/vault-template/projects/example-project/CLAUDE.md), [project skill](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/skills/second-brain-project/SKILL.md).
* [Writing](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/08-outputs/writing-from-the-vault.md), [reports](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/08-outputs/research-reports.md), [publishing](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/08-outputs/publishing-and-export.md).

**Checkpoint A — wiki → project**

1. Agree one measurable outcome/deadline/boundary. Start a brief with status, evidence needs, decisions, wiki links. Project instructions are behavior guidance; actual project-write permissions must separately restrict approved paths.
2. Use `Inputs/Process/Outputs/Feedback` when artifacts need them, not mandatory empty scaffolding. Hypotheses, tasks, drafts and feedback stay project-local.
3. Researcher supplies a sourced context brief read-only; the **owner** records project artifacts in the core workflow. A dedicated project writer is deferred, not an unnamed core agent. If selected later, it needs deny-default rules, read access to approved context, ask-to-edit only the named project's paths, and deny wiki/raw/settings/config/shell/task/network writes. Wiki-ingestor remains unable to write `projects/` before and after handoff.

**Show/approve:** outcome, paths, wiki evidence, gaps, proposed artifacts. A project hub never replaces `wiki/index.md`.

**Checkpoint B — project → wiki**

1. At a milestone, select reusable findings/decisions/lessons with evidence. Task status remains local to the project.
2. Distinguish external evidence, observations, untested hypotheses and generated prose. Retain date/method/locator/limitations. Generated text is not independent corroboration.
3. Freeze/reference the approved artifact, then use R3's proposal to promote knowledge and contradictions. Link back to local evidence; do not copy entire project directories.
4. Update project handoff/status separately with promoted wiki links and uncertainty. Archive only if evidence paths remain valid.

**Verify / show / approve**

* Synthetic round-trip: wiki informs a project decision, observed feedback updates durable knowledge, unsupported speculation does not become fact.
* Proposed archive/rename retains evidence links; otherwise postpone or approve repairs.
* No publication. Future exports require explicit page/asset allowlist and privacy/license review; never follow all private links automatically.
* **Exit:** show both handoff manifests and source-linked diffs; owner approves promotion and project status separately.

### R6. Versioning, secrets exclusion, backup/restore, lint, maintenance

**Supports P0, P3, P4. No vault Git initialization/remote is authorized by this runbook alone.**

**Inspect**

* [Git/sync](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/02-setup/git-and-sync.md), [versioning](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/09-maintenance/versioning-with-git.md), [backup](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/09-maintenance/backups-and-portability.md), [privacy](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/09-maintenance/privacy-and-secrets.md).
* [Lint](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/09-maintenance/lint-and-health.md), [cadence](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/09-maintenance/review-cadence.md), [broken links](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/10-troubleshooting/broken-links.md), [bad writes](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/10-troubleshooting/agent-writes-garbage.md).
* [`link_check.py`](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/scripts/link_check.py), [`vault_stats.py`](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/scripts/vault_stats.py), [lint skill](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/skills/second-brain-lint/SKILL.md).

**Checkpoint A — backup/versioning policy**

1. Inspect existing backup policy with owner; do not assume sync is backup or Git exists. Minimum proposal: private pre-change snapshot plus independent regular encrypted backup with tested restore.
2. Back up approved notes, raw/assets, templates and local framework/config **without credentials**. Exclude `.obsidian/` wholesale from agent-driven backup. Any settings/credential backup is an owner-managed secret-storage task; never read the forbidden credential file to build exclusions.
3. Agree destination/access, retention, encryption/key recovery, frequency and recovery-point expectations. No public cloud/Git defaults. Transcripts/output may also be private.
4. Private Git remains optional. If separately approved, review exclusions/tracked paths before first add; commits are human-authorized/path-specific. Never share a remote with public machinery or use blanket `git add .` as agent workflow.
5. Git does not cover all untracked files/assets or lost credentials. Ignoring a file does not remove history. If a secret was published, stop, revoke/rotate and plan remediation; deleting current content is insufficient.

**Exit A:** record approved backup scope, retention, restore target and versioning choice locally. Before a write, confirm the applicable recovery requirement or an explicit scoped exception. The completed greenfield bootstrap waiver is not reopened here and is not evidence of a working private backup.

**Checkpoint B — lint/maintenance**

1. Scope to managed wiki by default, separate from raw/projects/output/templates/settings/non-adopted legacy notes.
2. Test canonical paths, labels/fragments, spaces, duplicate basenames, invalid targets and supported arrays. Do not treat basenames as unique IDs or regex as a general YAML parser.
3. Check inventory versus index, source/claim locators, reciprocal source links, orphan candidates, gaps/placeholders, and completion records versus actual files. Semantics/contradictions still require human review.
4. Report first. Link repairs need bounded approval; rename/merge/delete/schema changes require review/recovery. Do not rewrite human notes automatically.
5. Begin with after-ingest checks and owner-triggered review. Assess useful knowledge/gaps/stale evidence, not page counts. Upstream orphan/degree/staleness thresholds are heuristics, not tiny-wiki SLAs.
6. No scheduling until manual runs prove useful. Future scheduling needs a separate bounded identity, concurrency/locking, stop budget, failure reporting and approval; Claude examples are not installed features.

**Exit B:** intentional broken-link/index mismatch detected; clean fixtures pass; unsupported/uncertain forms distinguished from success; checker changes zero files. Show report and repairs separately.

**Checkpoint C — restore and partial-run drill**

The [public synthetic rehearsal](docs/backup-restore.md) implements and exercises
the procedure below on fixed invented files only. It is not private R6C evidence
or authority to use its internal helpers on a live vault.

1. Restore into an isolated **private** alternate location, not over the live vault. Compare manifest paths/hashes, assets, index/log consistency and source links.
2. Rehearse half-completed ingest. Reconstruct intent from approved manifest and pre-run backup; log alone is not a transaction journal. Complete/revert only that operation's paths with preconditions.
3. On a drifted path, stop; **human changes win by default**. Owner chooses preserve/merge/restore before any further write. Append an approved recovery/correction record. No `git checkout .`, `git reset --hard`, broad restore or recursive deletion on the live vault.
4. Show restore checks/plan; live restoration needs separate approval.

**Exit C:** restored content/links match expectations and partial operation recovers without losing unrelated work. Repeat after backup-policy changes and at an owner-approved interval.

**Do not copy blindly:** upstream broad rollback examples can destroy unrelated changes; stat/graph scripts conflate scopes and collapse basenames; alias/frontmatter parsing is incomplete; stub thresholds conflict. No upstream automated suite validates them.

### R7. First-class vault statistics: calculate, verify, interpret

**Supports required P2A and routine P4 maintenance; not the optional graph track.**

**Inspect:** [`vault_stats.py`](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/scripts/vault_stats.py), [metric definitions](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/05-graphs/metrics.md), [metrics skill](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/skills/second-brain-metrics/SKILL.md), [graph skill](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/skills/second-brain-graph/SKILL.md), and the ported checker's link/scope contract.

**Checkpoint A — definition/fixture approval:** show node scope, unique directed-edge rules, degree/orphan/component/stale denominators, 90-day boundary, unknown-date handling, and P2A's exact expected fixture. Approve before implementation; upstream numbers are not trustworthy ground truth.

**Delivered implementation (P2A):** operator CLI compatibility, JSON/as-of, shared scanner/link-resolution behavior, weak components with stdlib traversal and stale concepts with stdlib dates. Reports expose metric definitions/scope, unusable dates and unsupported targets. No automatic writes, model calls, DB or NetworkX dependency. Source reading and graph traversal remain subject to path confinement. See `docs/vault-stats.md` and `tests/test_vault_stats.py`.

**Verify:** exact P2A fixture; duplicate links/self-links; two same-named pages in different paths; control/project/output exclusions; frontmatter-only dates/types; invalid/missing/future dates; empty corpus; deterministic output for fixed as-of; hashes unchanged. Test CLI error exit for invalid root/as-of, distinct from a valid empty corpus.

**Checkpoint B — local report approval:** owner runs on approved managed corpus, reviews report locally, and chooses whether to preserve a dated private snapshot. Core agents remain shell-denied. Show only synthetic examples in public docs; no automatic metrics-note/log append. State that high degree/low orphan count does not prove factual accuracy or useful knowledge.

**Exit:** documented runnable CLI and synthetic tests pass; owner sees repeatable human/JSON reports and understands definitions. Before comparing old snapshots, confirm matching scope/definitions; annotate the transition from upstream `E/N` occurrence counts.

### R8. First-class chat export: convert locally, review, then select

**Supports required P2B. Delivery is mandatory; processing personal history is not.**

**Inspect:** [`chat_export_to_md.py`](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/scripts/chat_export_to_md.py), [chat exports guide](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/docs/03-ingestion/chat-exports.md), [chat-import skill](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/skills/second-brain-chat-import/SKILL.md), [wrapper](https://github.com/undefined-ui/second-brain-os/blob/347feee87b305b291f7264890e5024db422e3467/commands/ingest-chats.md). Inspect synthetic export shape first, not personal message bodies.

**Checkpoint A — format/destination approval:** show supported fixture shapes, branch-selection policy, chronology/role/date rules, non-text omission reporting, stable identity/rerun policy and exact private staging destination. No network/model call is needed for conversion. Owner approves whether to convert a selected set or a whole export privately for human triage; neither authorizes wholesale ingest or provider upload. Default to explicit conversation IDs.

**Delivered implementation (P2B):** stdlib-only converter with preserved positional CLI/min-word filter, no-write dry-run, explicit selection, branch traversal, safe scalar encoding, text fidelity and ID/digest filenames. Original exports are immutable. Count summaries distinguish converted, identical/skipped, too-short, unsupported, omitted non-text and failed records. Titles/messages are not printed by default; errors use opaque IDs and reasons. Invalid destinations/escaping symlinks are refused and existing artifacts are never silently overwritten. See `docs/chat-exports.md` and `tests/test_chat_export_to_md.py`.

**Verify:** branching ChatGPT fixture chooses only current-node ancestry; Claude messages preserve text/roles/order; ISO/epoch normalization; null structural nodes; malformed/cyclic/missing parent failure; non-text annotations; safely quoted title; same-title different IDs; identical rerun and revised conversation; threshold boundary; dry-run zero writes; invalid input/destination and partial failure reported. No real personal export is needed to prove support for documented shapes; actual new vendor variants require explicit compatibility review rather than silent guessing.

**Checkpoint B — privacy/triage approval:** owner reviews converted artifacts **locally before a model reads them**, classifying privacy review needed, selected for ingestion, archive-only, and deletion suggestion. Do not print sensitive titles, automatically delete, move, or send the whole archive to an agent. A later assisted triage session sees only explicitly approved material and uses the approved provider. A count summary is not a confidentiality review.

**Checkpoint C — selected conversation handoff:** copy/reference only approved conversation artifact into the local source archive with source ID/date/branch/omission metadata, then use R3/R4. Describe user reasoning as dated user statements, assistant text as generated assertions, and external claims as unverified until their actual sources are checked. A past discussion is not automatically the owner's current belief.

**Exit:** converter CLI and synthetic tests pass, staged output faithfully represents supported content, and one selected synthetic conversation completes sourced ingest/query. Show conversion counts/fidelity diff/approval manifest, not private chat contents. Whole history ingestion remains prohibited.

**Do not copy blindly:** upstream ignores ChatGPT `mapping/current_node`, counts unsupported conversations as short, misses `author.role`, mishandles epoch dates/non-text parts, emits unsafe unquoted titles and creates duplicates on reruns. Privacy is not solved by filtering short conversations.

### Optional Tracks — NOT NEEDED FOR VAULT SETUP

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

### Runbook completion evidence

For each future checkpoint retain locally: approved scope, tested versions, source revision, before/after manifest, checks, unresolved failures, rollback route and owner approval. Only wholly synthetic/public evidence may enter this repository. A skipped/failed check remains such; an upstream example or prose instruction is not a verified result.

## Decision Register

> Recommendations are proposals, not authorization. Questions below block only their named execution checkpoints, not planning.

### Facts versus recommendations

| Learned from inspected sources | Engineering recommendation |
|---|---|
| Wiki and time-bounded projects are the two content layers; raw is an archive. | Preserve both layers; no project dashboard/raw inbox substitute for wiki. |
| Ingest/query are upstream's load-bearing skills; most commands are dispatch prompts. | Use the delivered two skills and two scoped roles directly; unsafe wrapper candidates remain withheld. |
| Local integration instructions require approved small steps and preserve notes/settings; direct files need no REST API. | One-way reviewed manifest, no MCP/settings changes/new default agent. Do not publish personal context from those instructions. |
| MIT notice reads `Copyright (c) 2026` without named holder. | Preserve full notice verbatim, attribute repo/revision/files, choose downstream license separately. Missing name is not proof there is no license. |
| OpenCode has native formats and merged last-match rules; grep rules match search input, not returned file paths. | Test actual policy; initially deny shell/search/delegation/network. OS isolation for a hard boundary. |
| OpenCode `1.18.32` has documented bounded native loading, permission and ingest/query trial evidence. | Reverify the actual profile/version for an approved deployment. Schema-valid does not mean safely enforced; do not generalize bounded results to untested cases. |
| Five tracks are separate curricula with illustrative/vendor-specific/unsafe examples. | Keep each optional and separately approved. |

### Per-deployment owner choices

Ask at the relevant checkpoint, not all at once. Some choices may already have
been resolved in an owner's local records; this table is not a claim that they
remain unanswered for every installation. D1 is resolved and listed below.

| ID / checkpoint | Choice to confirm locally | Recommended default | Consequence / alternative |
|---|---|---|---|
| D2 / R1A, before real source | Provider/model and allowed data classes | Short public source on owner-approved provider, no confidential data | Sharing disabled does not stop provider retention/processing. Private content needs approved policy/local provider; credentials/patient information remain excluded. |
| D3 / R1A | Direct vault or isolated approved-data workspace? | Isolated synthetic rehearsal; hard-isolated approved corpus for sensitive use until runtime trusted | May need reviewed per-file patch handoff. Direct access is simpler but inherits process/global-context risks. Neither AGENTS nor tool policy is an OS sandbox. |
| D4 / R1C/R2 | Managed paths/template namespace | Proposed paths only where non-conflicting, namespaced templates, merged contract | Existing layout may need mapping; no automatic migration/rename/backfill. Keep actual private topology local. |
| D5 / R1A/R6A | Backup destination, encryption, retention, sessions/snapshots | Verified private pre-change backup plus independent encrypted backup; share disabled, propose snapshot false | Disabling snapshots removes one undo route, not transcripts. Owner chooses retention/recovery/key policy; no real writes before restore proof. |
| D6 / R6A | Private vault Git/remote? | Defer Git initialization/remote; use approved backups first | Git improves diffs later, not complete backup. Separate confidentiality approval for any remote; never public machinery remote. |
| D7 / R3A | First source/question | Owner-selected short public source, supported and unsupported questions | Small privacy/cost/reading scope. Large PDF/chat/media requires extractor/consent/provider checks. |
| D8 / R5A | Which real project needs handoff? | Synthetic handoff first, then one active project | No automatic personal project inventory import or unused scaffolding. |
| D9 / R6B | Cadence/automation? | After-ingest checks and owner-triggered review, no schedule | Transparent but attended. Scheduling needs bounded identity, isolation, concurrency/failure policy and approval. |
| D10 / P5 | Which optional track? | None for setup; select by motivating need | Each adds dependency/testing/data/cost burden; not a required sequence. |

### Resolved planning choices

* D1 resolved: downstream MIT with `Copyright (c) 2026 Funsaized`; the upstream blank-holder notice is preserved verbatim and adaptations are mapped in `THIRD_PARTY_NOTICES.md`.
* The initial planning task was restricted to `PLAN.md`. Later implementation authorizations superseded that restriction; public code, framework files, tests and operating docs have been delivered. Each local data operation still needs its own applicable approvals.
* Public/private separation: inert reusable files, one-way reviewed install, no vault symlink/reference/submodule/reverse sync/private fixture import. Preserve local customizations.
* Minimal core now explicitly includes the owner's required first-class chat-export and vault-statistics ports, alongside ingest/query, contract/templates, read-only checker and synthetic cases. Their R7/R8 workflows are required; dedicated metrics/chat-triage slash wrappers remain optional automation, not a dependency for CLI delivery.
* Preserve the existing default agent; explicitly selected roles, designated skills and native permissions replace Claude tool lists. Withheld wrappers are not part of the installed core.
* Raw immutable to agents; unknown facts stay unknown; claim locators and contradictions retained; generated prose not independent evidence.
* No automatic publication/git actions. Promotion/export reviewed separately; commit/push/rollback/setup/scheduling are human-runbook operations.
* Initial index-first approved reads trade recall for safety. Disclose incomplete coverage; add search only over safely exposed corpus after separate tests.

### Technical verification gates, not owner product choices

* Verify the actual installed resources, runtime schema, merged permissions, canonical paths/symlinks and required safety checks. Preserve the missing-resource waiver and do not label historical failures as passing. Withheld commands remain outside the installed core; unresolved confinement or inherited-policy failures block affected use.
* Docs/schema drift exists: permissions guide describes URL matching, but current schema makes `webfetch` action-only. Core uses `deny`; do not invent unsupported URL policy objects.
* `--pure` exists in local help, but authentication and absence of inherited custom tools/MCP need tests. Required auth plugin is a reviewed exception, not silent global reconfiguration.
* Upstream utilities require fixture-backed adaptation and managed-wiki scope; document unsupported forms.
* Restore and compare content/links; successful backup command alone is insufficient.
* Optional Jev SDK, graph dependencies, structured outputs, eval CI actions and cost/event fields are checked when selected, not presumed working today.

### Open planning blockers

The original research/planning task is complete; its temporary file-write
restriction is no longer active. Outstanding public work is listed at the top
of this document. Owner-local choices and runtime gates are checked against local
records when relevant, not presumed unresolved because private evidence is absent
from this repository.

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
