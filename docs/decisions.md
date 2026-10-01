# Decisions

> Moved from PLAN.md on 2026-09-30: the design decisions and the decision
> register, including per-deployment owner choices and technical verification
> gates. Later owner decisions are recorded in dated [changelog](changelog.md)
> entries and the [backlog](../BACKLOG.md).

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
* Owner decision 2026-10-01 (P6): `wiki/index.md` stays one page but is generated by the operator from page frontmatter; gaps live on pages; capture parts are listed through their chapter. Workers read a bounded per-operation catalog plus search instead of the whole index. Existing deployments migrate once, after the owner assigns or drops each current gap; reprocessing content with models is not required.

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
