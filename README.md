# second-brain-open

Reusable OpenCode machinery for a separate Obsidian vault, based on
[second-brain-os](https://github.com/undefined-ui/second-brain-os) at
`347feee87b305b291f7264890e5024db422e3467`.
See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

**Status: P0 distribution foundation only; not ready for vault installation.**
The ingest/query roles, templates, link checker, required statistics and chat
converter ports have not been implemented. See [PLAN.md](PLAN.md).
P0 is not complete until runtime enforcement tests and owner review pass.

## Current distribution allowlist

No file is currently approved for installation into a personal vault.
The sole configuration candidate is:

| Public source | Proposed isolated destination | Action | Collision status / gate |
|---|---|---|---|
| `framework/opencode.example.json` | `<test-workspace>/opencode.json` | Review and instantiate; never blind-copy over a config | Unknown until test workspace exists; R0/R1A approval required |

Root documentation, license notices, development instructions, tests, and
PLAN.md stay in this public repository. Do not copy its AGENTS.md into a vault.
The example has no roles, read grants, provider, credential, or private path.
It is a deny-default starting fragment, **not an isolation mechanism**. Empty
plugin/MCP/instruction collections do not erase inherited configuration.
No root default agent is changed. Do not activate this fragment in an ordinary
session: it intentionally grants no tools or providers.

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

Rehearse these steps on a synthetic pre-existing workspace with conflicting
instructions/config/templates before accepting R0. That rehearsal is pending;
the static checks below do not prove install/rollback or runtime enforcement.

## Next gate: R0 review / R1A isolated runtime proposal

Approve this distribution method and a synthetic-only runtime rehearsal:

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
- Keep synthetic runtime artifacts outside this checkout; propose deletion
  after sanitized evidence is accepted. No real content, backups, or sessions
  are covered by this retention proposal. Real-provider/data/retention approval
  remains separate before any live source.

Observed locally: OpenCode `1.18.32`, `bwrap`, and Python 3 are available.
The public schema was inspected for the example's fields. Namespace viability,
runtime schema acceptance, effective configuration, and actual enforcement
have **not** been tested. If isolation or safe inspection fails, stop rather
than fall back to an ordinary user session.

## Checks

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

These offline checks cover the inert fragment, notice consistency, and ignore
rules using synthetic path names only. They do not call a model, read a vault,
install anything, or establish a security boundary.
