# Install or upgrade the framework in a vault

Use this guide to add the roles, skills, contract, templates and operator
config to an existing Obsidian vault, or to upgrade them, while keeping your
notes, settings and primary agent. For a first look without configuration or
model calls, start with the [read-only tutorial](tutorial.md).

This is a per-file copy, not a directory sync. Nothing here changes your root
`AGENTS.md`, Obsidian settings or default agent.

## Before you start

- **Tools:** OpenCode, Python 3.10+ and a checkout of this repository kept
  outside the vault. The operator runs on Linux. Public evidence covers
  OpenCode 1.18.32 and 1.18.33.
- **Primary agent:** an existing primary agent with shell access. It becomes
  the operator.
- **Provider route:** a model route you approve for sending wiki content to
  the provider. Sharing stays off, but the provider still processes what the
  workers read.
- **Backup:** a backup of any vault file you are about to replace.

## 1. Copy the files

Copy each file from this checkout to the vault path below. Create new files; if
a destination already exists, compare it with the new version and merge any
local changes deliberately. Never copy directories wholesale.

| Public source | Vault destination | Role |
|---|---|---|
| `framework/instructions/wiki-contract.md` | `.opencode/instructions/second-brain/wiki-contract.md` | Content rules the workers follow |
| `framework/templates/{source,concept,entity,synthesis,index,log,project}.md` | `templates/second-brain/<same name>` | Page and project templates |
| `framework/agents/sb-ingestor.md` | `.opencode/agents/sb-ingestor.md` | Ingest worker |
| `framework/agents/sb-researcher.md` | `.opencode/agents/sb-researcher.md` | Read-only research worker |
| `framework/skills/second-brain-ingest/SKILL.md` | `.opencode/skills/second-brain-ingest/SKILL.md` | Ingest and compile procedure |
| `framework/skills/second-brain-query/SKILL.md` | `.opencode/skills/second-brain-query/SKILL.md` | Sourced-answer procedure |
| `framework/skills/second-brain-operator/SKILL.md` | `.opencode/skills/second-brain-operator/SKILL.md` | Operator procedure for your primary agent |
| `framework/operator.example.json` | `.opencode/second-brain/operator.json` | Operator settings; edit after copying |
| — | `opencode.json` (vault root) | Operator path permission; see step 2 |
| `LICENSE`, `THIRD_PARTY_NOTICES.md` | `.opencode/second-brain/` | Notices |

The scripts stay in this checkout; the operator config points to them. Don't
copy this repository's `AGENTS.md`, tests or fixtures into the vault. The
separate [`framework/opencode.example.json`](../framework/opencode.example.json)
is a deny-everything fragment for isolated testing, not part of an install.

Record the public commit (`git rev-parse HEAD`) and each copied file's SHA-256
somewhere private, so a later upgrade can tell whether you changed a file.

## 2. Configure the operator

Edit `.opencode/second-brain/operator.json`:

- `cli`: absolute path to `scripts/sb_operator.py` in this checkout.
- `agent` and `model`: your primary agent and the approved `provider/model`
  route it uses.
- `opencode_version`: the output of `opencode --version`.
- `workdir`: a private directory **outside** the vault for staged operations.

Other keys are in the [config reference](reference.md#operator-config).

Then let your primary agent reach those two paths. Both are outside the vault,
so OpenCode asks before each use. In the TUI you can answer "always" once. For
runs without anyone watching, add this to the vault's `opencode.json`, creating
it if needed:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "YOUR_PRIMARY_AGENT": {
      "permission": {
        "external_directory": {
          "/path/to/second-brain-open/scripts/*": "allow",
          "/path/outside/the/vault/sb-operations/*": "allow"
        }
      }
    }
  }
}
```

This changes only that agent's access to these two directories, and only in
this vault. The worker roles never read the vault's `opencode.json`: the
operator launches them with project config disabled.

## 3. Set up the vault's index and log

If the vault has no `wiki/index.md` and `wiki/log.md`, create them from the
templates. Fill in the dates and delete the comment blocks. If they already
exist, give them the contract's frontmatter.

Then check the vault:

```sh
python3 /path/to/second-brain-open/scripts/link_check.py /path/to/vault
```

It should exit 0.

## 4. Verify

Restart OpenCode so it discovers the new roles and skills. Then ask your primary
agent a question:

> Use the second-brain-operator skill to answer: what does the index list?

A working install stages a query, runs `sb-researcher` and returns an answer
ending with `Read:` and `Not covered:`. Continue with
[the operator guide](operator.md).

## Upgrade or remove

To upgrade, repeat step 1 for each file whose public version changed.

- **You never edited the vault copy:** its hash matches the one you recorded,
  so replace it.
- **You edited it:** merge by hand.

Keep `operator.json`, which holds your settings. Restart OpenCode afterwards.

To remove the framework, delete the copied files whose hashes still match. The
wiki pages the workers wrote are yours and stay.

## Related

- [Why operators and workers are separate](how-it-works.md#operators-and-workers).
- [Reference: CLI, config and roles](reference.md).
- [Managed-wiki contract](../framework/instructions/wiki-contract.md).
