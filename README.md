# second-brain-open

Reusable OpenCode machinery for a separate Obsidian vault, based on
[second-brain-os](https://github.com/undefined-ui/second-brain-os) at
`347feee87b305b291f7264890e5024db422e3467`.
See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

**Status: P0/P1 delivered; P2 checker and scoped roles/skills delivered.**
P2 is not complete: accepted native edits, injection/recovery and owner content
acceptance remain pending. A live staged ingest/repeat/query rehearsal has passed.
Unsafe slash-command wrappers are withheld as the plan permits;
use explicitly selected roles with plain, vetted requests. The required statistics
and chat converter ports follow in P2A/P2B; they are not optional. Not ready for
personal-vault installation. See [PLAN.md](PLAN.md) and the
[manual loop runbook](docs/manual-loop.md).

## Content contract and examples

- [Wiki contract](framework/instructions/wiki-contract.md): four knowledge types,
  source locators, competing claims, index/log maintenance and project promotion.
- [Seven plain-text templates](framework/templates/): no Obsidian plugins needed.
- [Synthetic index](tests/fixtures/contract/wiki/index.md): two invented trial
  records with conflicting recommendations, a concept, entity and synthesis.
- [Synthetic project brief](tests/fixtures/contract/projects/vent-repeat/brief.md):
  consumes wiki evidence; promotion remains a separate approved operation.

Generated metadata uses a flat JSON-value YAML subset. All six wiki types have
common metadata; source and entity fields are documented in the contract.
The append-only log keeps its creation-time header dates, with operation dates
in appended entries. Existing notes are not automatically normalized.
These examples are hand-authored fixtures, **not a demonstrated agent ingest**.

## Current distribution allowlist

No file is currently approved for installation into a personal vault.
Destinations below are candidates, relative to an approved isolated workspace
unless noted. Collision status must be checked locally; every copy/merge is
reviewed. P1 template/contract review does not waive the P3 entry gate.

| Public source | Proposed destination | Action |
|---|---|---|
| `framework/opencode.example.json` | `opencode.json` | Isolated test starting fragment only; review/instantiate, never overwrite |
| `framework/instructions/wiki-contract.md` | `.opencode/instructions/second-brain/wiki-contract.md` | Approved supplemental instruction reference, never root AGENTS replacement |
| `framework/templates/source.md` | `templates/second-brain/source.md` | Copy new or review local merge |
| `framework/templates/concept.md` | `templates/second-brain/concept.md` | Copy new or review local merge |
| `framework/templates/entity.md` | `templates/second-brain/entity.md` | Copy new or review local merge |
| `framework/templates/synthesis.md` | `templates/second-brain/synthesis.md` | Copy new or review local merge |
| `framework/templates/index.md` | `templates/second-brain/index.md` | Template only, not an overwrite of a live index |
| `framework/templates/log.md` | `templates/second-brain/log.md` | Template only, not an overwrite of a live log |
| `framework/templates/project.md` | `templates/second-brain/project.md` | Brief template; no project scaffolding |
| `framework/agents/sb-ingestor.md` | `.opencode/agents/sb-ingestor.md` | Primary ingest role; supply reviewed exact local grants |
| `framework/agents/sb-researcher.md` | `.opencode/agents/sb-researcher.md` | Primary read-only role; supply reviewed exact local grants |
| `framework/skills/second-brain-ingest/SKILL.md` | `.opencode/skills/second-brain-ingest/SKILL.md` | Designated ingest workflow |
| `framework/skills/second-brain-query/SKILL.md` | `.opencode/skills/second-brain-query/SKILL.md` | Designated query workflow |
| `LICENSE` | `.opencode/second-brain/LICENSE` | Retain downstream notice with copied material |
| `THIRD_PARTY_NOTICES.md` | `.opencode/second-brain/THIRD_PARTY_NOTICES.md` | Retain upstream notice and adaptation map |

Development instructions, tests and PLAN.md stay in this public repository.
Do not copy its AGENTS.md into a vault. License notices accompany copied material
in the namespaced locations above. Run `scripts/link_check.py` from this checkout
as an operator; no installation or agent shell grant is needed.
The inactive configuration example has no roles, read grants, provider,
credential, or private path.
It is a deny-default starting fragment, **not an isolation mechanism**. Empty
plugin/MCP/instruction collections do not erase inherited configuration.
No root default agent is changed. Do not activate this fragment in an ordinary
session: it intentionally grants no tools or providers.
The role files allow their designated skill and questions; exact reads and
ingestor ask-to-edit grants are supplied by the approved local manifest. The
research role remains read-only. This does not disable ordinary development tools in
the owner's existing OpenCode setup.

## Reviewed install, upgrade, and rollback

1. Pass the phase's gates before copying anything. Real integration additionally
   requires P2/P2A/P2B and R6 backup/isolated-restore proof.
2. In a private local manifest record the reviewed public commit SHA, each
   allowlisted source and its SHA-256, resolved destination, action (copy or
   merge), destination's preimage hash or absence, and private backup location.
   Reject traversal and symlinked sources/destinations/ancestors. Do not use
   directories or globs as manifest entries. No private paths belong here.
3. Pause edits to affected files; verify preimages immediately before each
   write. A collision or changed hash stops that file for owner review.
   Preserve existing root instructions and settings. No blanket overwrite.
4. Copy only individually approved new files. For existing files, review the
   old installed revision → new public revision → local contents, then approve
   a per-file merge. Record postimage hashes and retain local customizations.
5. Quit/restart the isolated OpenCode instance after config changes, inspect
   its sanitized effective policy, and repeat enforcement probes. Existing
   sessions keep old policy. No restart is needed for this inert checkout.
6. Roll back only manifest paths whose current hashes still match installed
   postimages. Restore their private preimages; remove newly created files
   only with owner approval and matching hashes. On drift, preserve human work
   and ask. Never broad-reset, recursively sync, or delete a vault tree.

The synthetic rehearsal in `tests/test_scope_and_distribution.py` preserves
conflicting instructions/config/templates, copies one approved new file,
refuses rollback on drift, and removes only a matching approved postimage.
It tests this manual procedure, not a production installer or a private restore.

## Approved R0 distribution / R1A runtime scope

The owner approved this distribution method and synthetic-only runtime rehearsal
on 2026-09-24, then approved the corpus/permissions distinction and continuing
in logical increments:

- Disposable Linux namespace/container with a clean home/XDG environment;
  mount only runtime dependencies and synthetic test data. No home/vault mount,
  credential import, personal AGENTS.md, or host configuration inheritance.
- Begin network-disabled with no provider and no authentication. Use a local
  deterministic fake provider if needed for tool-enforcement probes. This
  tests runtime behavior, not model quality or successful ingestion.
- No plugins/MCP/custom tools or remote instructions; disable compatibility
  skill/instruction discovery using settings verified for the installed
  release. Disable formatters/LSP, sharing, snapshots, and auto-update.
- Add a disposable deny-default probe role with exact synthetic read grants;
  test allowed reads, forbidden tools/writes, fake sensitive paths, traversal,
  symlinks, and approval rejection. No auto-approval. Later P2 must repeat the
  matrix for the actual named roles and command entry points.
- Inspect only allowlisted effective settings: permissions, selected roles,
  share/snapshot, plugin/MCP presence, instruction paths, formatter/LSP, and all
  provider/model routes. Never print a full effective config or environment.
- Keep runtime artifacts outside this checkout. The test namespace's fixtures
  and sessions disappear on exit; retain only sanitized results. Real data,
  backups and session-retention policy remain separately approved.

### Runtime baseline: actual results (2026-09-24)

Tested OpenCode `1.18.32`, Bubblewrap `0.12.0`, Python 3, in a cleared-environment
network namespace with a fresh home/XDG profile. Read-only `/usr` supplies
dependencies; the executable and probe are single-file read-only mounts.
No host home, vault, settings or credentials are mounted. A deterministic local
fake provider forces calls instead of relying on a model promising refusal.

| Check | Actual result |
|---|---|
| Approved exact read | Pass; source marker returned |
| Fake settings, `.env`, unrelated, traversal, outside reads | Five passes; permission refusal, no forbidden marker in events/provider requests |
| Edit/write/bash/grep/glob/webfetch/task/unapproved skill | Eight passes; runtime rejects calls to unavailable tools |
| Ask-scoped edit | Pass; noninteractive CLI rejects permission request; fixture unchanged |
| Symlink in approved input scope | Pass at **preflight**; no runtime/provider call |

All 16 cases pass. Each native case uses a fresh OpenCode process. Hash checks
cover the five named synthetic files' contents, not every runtime/session file.
The probe checks share/snapshot, formatter/LSP, plugin/MCP/instruction absence
and main/auxiliary fake-model routing without printing unrestricted config.
No live provider is involved; these tests do not prove ingestion quality.
The ask-edit case verifies rejection, not interactive approval persistence.
Never select a broad “always” grant; P2 must inspect the actual offered patterns
and prove that the named roles stay scoped after approved edits.

The original path mismatch is resolved: `read` asks on **worktree-relative**
paths. `debug scrap` reports `/` as this non-Git project's worktree, so the exact
grant is `workspace/wiki/index.md`, not `/workspace/wiki/index.md` or a wildcard.
Do not assume cwd equals worktree. HTTP inspection timed out (even on a health
request); we use the working CLI instead and do not claim the server was fixed.
OpenCode can exit 0 on tool denial, so assertions inspect actual tool outcomes.

### Boundary: permissions are not a filesystem sandbox

The initial native symlink characterization **did return denied synthetic data**
through an allowed filename. This runtime behavior has not been fixed upstream.
The adopted profile rejects symlinked files/ancestors, hardlinks, traversal and
non-files before launch; `validate_scope` in the probe and its unit tests make
that check explicit. It is not a lock against concurrent replacement.

For real use, the owner must prepare and freeze a regular-file-only approved
corpus with no outside writers, expose inputs read-only where practical, and
never mount personal settings/credentials or the vault/home wholesale. Tool
permissions then restrict actions within that isolated corpus. A preflight
followed by an ordinary mutable shared folder is **not** an acceptable substitute.
The named-role/command matrix and live-source/provider/backup gates still apply.

### P2 runtime results and withheld commands

`tests/runtime_roles_probe.py` copies the four public role/skill files into a
disposable clean native profile with both license notices, verifies their prompts
loaded, and supplies exact synthetic grants. **25 loading/tool checks pass**: both roles load their
actual designated skill and read approved data; forbidden reads, other skills,
wiki/raw/config edits, shell, search, glob, delegation and network calls are
refused. The ingestor's allowed edit path reaches permission rejection; the
researcher never obtains edit access. Fixture/installed-file hashes remain unchanged.
These are forced-tool runtime checks, not model reasoning or ingestion tests.

After role verification, two command candidates are installed only inside the
disposable profile. Six entry-point cases show: both literal invocations route
to the intended skill, but both `@file` arguments attach denied synthetic content
and both shell-like arguments are expanded before tool restrictions. Therefore
**neither `/sb-ingest` nor `/sb-ask` is distributed or approved for installation**.
The probe preserves their four failed safety results; exit 0 means the named
roles passed and unsafe wrappers remain withheld, not that commands are safe.
Use the [plain-request fallback](docs/manual-loop.md#2-invoke-the-role-directly-not-a-slash-wrapper).

### Link checker

```sh
python3 scripts/link_check.py tests/fixtures/contract
python3 scripts/link_check.py tests/fixtures/contract --json
```

The synthetic fixture reports 5 content pages, 2 controls and 18 unique directed
content links, with no diagnostics. Exact paths, labels and spaces are supported;
fragments are file-checked but anchors remain unchecked. Metadata/fenced examples
are excluded. Broken/malformed/ambiguous and unsupported links are reported, not
guessed. Exit 0 is clean except possible unchecked anchors, 1 is diagnostics,
2 is invalid/unsafe scope. See the [full limits](docs/manual-loop.md#checker-contract).

### Live staged rehearsal

With owner approval, the existing `dingus` primary (`openai/gpt-6-luna`) produced
two synthetic ingest proposals. The test driver applied only fixed temporary
wiki paths and checked schema, links, provenance, verbatim evidence excerpts,
reciprocal links for both sources, index entries, raw immutability and append-only partial logs. Unchanged
repeat input produced no changes. A sourced query preserved the disagreement,
unknown publication date and coverage gap. The four-turn run passed its 11 final
semantic/state checks, with one step and zero tool events observed per call.

This **does not prove native edit acceptance or complete P2**. The live helper
uses existing owner authentication/profile context and normal local session
retention, unlike the isolated permission probes. Only supplied test records
were synthetic/public; generated staging was removed and no transcript was
published. See [the live runbook](docs/manual-loop.md#optional-live-semantic-rehearsal).

## Checks

```sh
python3 -m unittest discover -s tests -v
git diff --check
# Manual Linux runtime probe; requires the reviewed OpenCode release and bwrap:
python3 tests/runtime_read_probe.py
python3 tests/runtime_roles_probe.py
```

The offline suite has 29 passing checks: distribution, scope preflight,
synthetic copy/rollback, schema/claim fixtures, framework invariants and checker
cases. Runtime probes exit 0 on their stated acceptance, 1 on a failed check,
2 on setup/runtime failure. The namespace probes have no unisolated fallback.
Separate live helpers require explicit `--live --agent ... --model ...`; they
are not run by unittest discovery or CI. P2 still requires named-role accepted
edits, injection/recovery and missing-role/skill handling. Only disposable
synthetic framework installation has occurred; no personal vault or persistent
owner configuration was changed. Normal authentication/session activity applies
to the separately approved primary-agent calls.
