# Plan: OpenCode-native second-brain machinery

> The plan proper: objective, standing requirements, delivery approach, phases
> with exit criteria, validation and the implementation runbooks. Current state
> is in [STATUS.md](STATUS.md); dated results in [docs/changelog.md](docs/changelog.md);
> decisions in [docs/decisions.md](docs/decisions.md); proposals in
> [BACKLOG.md](BACKLOG.md); the planning record in
> [docs/archive/planning-history.md](docs/archive/planning-history.md).
>
> Execution update (2026-09-24): the owner authorized implementation up to the first blocker/approval gate, including operational autonomy. After the D1 question, “continue” approved MIT with `Copyright (c) 2026 Funsaized`. The original planning record remains historical; its planning-only restrictions do not revoke that later authorization. Named integration checkpoints remain in force.

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

The suite's result at each change is recorded in that change's dated entry in
[docs/changelog.md](docs/changelog.md); counts are kept nowhere else. The
structured source-template test is static compatibility evidence, not proof of
model editorial quality.

Opt-in runtime and live-provider trials are separate; see the evidence map and
`docs/native-acceptance-trials.md`. Do not rerun them merely to edit this plan or
turn waived cases into passing ones. Runtime version, route, inputs, approvals
and isolation must be checked for an actual deployment. `--format json` is an
event-output mode, not a guarantee that a model answer satisfies a schema.

Never use private content as a public fixture or print a real-vault secret scan.
Owner content acceptance, private recovery and deployment records remain local;
neither an offline pass nor a historical native trial proves those outcomes.

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

### Runbook completion evidence

For each future checkpoint retain locally: approved scope, tested versions, source revision, before/after manifest, checks, unresolved failures, rollback route and owner approval. Only wholly synthetic/public evidence may enter this repository. A skipped/failed check remains such; an upstream example or prose instruction is not a verified result.
