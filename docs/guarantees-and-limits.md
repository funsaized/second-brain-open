# Guarantees and limits

What the machinery guarantees, and where its guarantees stop. The how-to guides
link here instead of repeating these points.

## Checks establish structure, not truth

- The checker proves metadata, links, index coverage and reciprocity are well
  formed. It does not prove a claim is supported, a summary is faithful or a
  note is useful. Statistics describe structure, not quality.
- An operation stays `partial` until the owner records acceptance. Only a
  `sampled` or `full` owner review completes it; no test, check or trial does.
- Exit 0 from a tool means it ran: a report was produced or a conversion
  succeeded. It is not acceptance of the content.

## Workers are confined by permissions, not by the operating system

- Workers run in a staged copy of the wiki with exact read grants, search
  within that copy, and every other tool denied. The operator checks the
  effective permissions with `opencode debug` before each run.
- OpenCode's search permission applies to the search pattern, not the files it
  returns, so the staged copy holds only files the worker may read; `run`
  refuses anything else.
- This is permission confinement, not OS isolation. Workers run under your
  normal OpenCode authentication. A Bubblewrap-isolated mode exists only in the
  runtime probes.
- File-safety checks (no symlinks, hardlinks or traversal) happen before
  launch. They are not a lock against another process changing files at the
  same time, so avoid editing the vault while an operation is applied.

## Evidence has classes

| Class | Establishes |
|---|---|
| Offline tests | Static, CLI and guard behaviour on invented fixtures |
| Runtime probes | OpenCode's permission behaviour for one version, with a fake provider |
| Live synthetic runs | Worker behaviour on invented vaults, for one date, version and model route |
| Owner acceptance | A deployment's content, recorded in its own log |

A result in one class never stands in for another. Native results carry their
OpenCode version; a later version needs its own run.

## Content keeps its provenance

- A generated statement, including a chat assistant's message, is an assertion,
  not independent evidence. A historical user statement is dated, not a current
  belief.
- The chat converter is not lossless: attachments, tool calls and other
  non-text payloads are counted as omitted, not kept. Keep the original export.
  Its short-conversation filter is not a privacy review.
- Generated work and project outputs are not evidence and are not approved for
  publication.

## What stays with each deployment

Backup policy and restore proof, private approvals, provider exposure and
content acceptance belong to the deployment and its local records. The public
backup rehearsal runs on invented files only. Nothing in this repository
certifies a private vault.
