# Reference

Look up the operator CLI, the worker roles and the link checker. For the
content rules pages must follow, see the
[managed-wiki contract](../framework/instructions/wiki-contract.md).

## Operator CLI

`scripts/sb_operator.py` runs one operation at a time. Python 3 standard
library; `run` and `revise` need Linux and OpenCode.

```text
sb_operator.py stage VAULT ingest  --input raw/<capture> [--input ...] --task TEXT
sb_operator.py stage VAULT compile --input wiki/sources/<note>.md [--input ...] --task TEXT
sb_operator.py stage VAULT query   --question TEXT
sb_operator.py run    OPERATION
sb_operator.py revise OPERATION
sb_operator.py apply  OPERATION [--dry-run]
sb_operator.py undo   OPERATION
sb_operator.py status OPERATION
```

`stage` accepts `--config FILE`; the default is
`VAULT/.opencode/second-brain/operator.json`. Every command prints JSON.

| Command | What it does |
|---|---|
| `stage` | Creates `WORKDIR/<date>-<kind>-<id>/` holding `corpus/` (a copy of every adopted wiki page, the contract, the four content templates and the inputs), `profile/` (the worker role and skill) and `manifest.json` (every vault wiki file's SHA-256, the inputs and the config). Refuses symlinks, hardlinks and traversal. Never copies the vault's `AGENTS.md`, settings or other folders. |
| `run` | Grants the worker exact reads on the staged files, denies every other tool, verifies the effective configuration with `opencode debug`, then runs the worker once. Saves `response.md`, `run.json` and, for ingest and compile, `proposal.json`. |
| `revise` | Once per operation: reruns the worker with the dry-run problems as feedback and its previous reply readable as `previous-proposal.md`. The first attempt moves to `attempt-1/`. |
| `apply` | Validates the proposal (below), backs up every file it replaces to `backup/`, writes the pages and appends the log record, then runs the checker on the vault. If that check fails, it undoes the write. `--dry-run` validates without writing. |
| `undo` | Restores the files an applied operation changed, and removes files it created, when each still matches what `apply` wrote. Files changed since are listed in `skipped_changed_since` and left alone. |
| `status` | Shows the operation's kind, task, inputs and completed stages. |

Exit codes: `0` success; `1` the worker run failed verification, `apply`
found problems, or `undo` skipped changed files; `2` invalid input or setup.

### Operator config

| Key | Meaning | Default |
|---|---|---|
| `cli` | Path to `sb_operator.py`; read by the operator skill | — |
| `agent` | Existing primary agent whose provider authentication is reused | required |
| `model` | Worker route as `provider/model`; must match that agent's route | required |
| `opencode_version` | Installed OpenCode version you approved | required |
| `workdir` | Where operations are staged; must be outside the vault | required |
| `max_pages` | Most pages one proposal may change | `10` |
| `steps` | Worker turn limit | `10` |
| `timeout` | Seconds per worker run | `600` |
| `auto_apply` | Whether the operator skill may apply a passing proposal without asking | `true` |

Example: [`framework/operator.example.json`](../framework/operator.example.json).

### Worker run checks

`run` passes only when every check holds:

| Check | Passes when |
|---|---|
| `run_completed` | The worker exited 0 with a reply |
| `skill_loaded` | The worker loaded its designated skill with the skill tool |
| `only_reads` | Every tool call was a read or skill call |
| `reads_in_scope` | Every completed read was a staged file |
| `required_full_reads` | The index, the contract and every input were read completely (no offset, limit or truncation) |
| `zero_writes` | Staged files are byte-identical afterwards |

### Proposal format

```text
<<<FILE wiki/<folder>/<page>.md>>>
complete Markdown
<<<END FILE>>>
<<<LOG>>>
## YYYY-MM-DD — operation — partial
- bullets
<<<NOTES>>>
coverage review
```

A reply with only `<<<NOTES>>>` is a valid no-op. An optional closing marker
(`<<<LOG>>>` or `<<<END LOG>>>`, and the same for NOTES) is ignored; any other
marker line inside a page or the log record is an error.

### Apply checks

`apply` refuses the whole proposal, writing nothing, when any of these fail:

- **Pages:** at least one page and no more than `max_pages`.
- **Paths:** only `wiki/{sources,concepts,entities,synthesis}/**.md` and
  `wiki/index.md`; never `wiki/log.md` as a page, `raw/`, instruction
  filenames or traversal.
- **Log record:** a single record whose heading is
  `## YYYY-MM-DD — operation — partial`.
- **Drift:** every file it touches, and the log, still has its staged hash.
- **Checker:** the managed checker reports no errors or unsupported forms on a
  copy of the wiki with the proposal applied.

## Worker roles

| Role | Skill | Access when launched by the operator |
|---|---|---|
| `sb-ingestor` | `second-brain-ingest` | Exact reads on the staged files; no edits, shell, search, network or delegation. Returns a proposal. |
| `sb-researcher` | `second-brain-query` | Exact reads on the staged files; nothing else. Returns an answer ending with `Read:` and `Not covered:`. |
| Your primary agent | `second-brain-operator` | Its own permissions; it needs shell access to run the CLI. |

The role files deny every tool on their own. Selecting them in an ordinary
OpenCode session without the operator gives them no file access.

## Link checker

`python3 scripts/link_check.py VAULT [--json]`

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
- Reports contract errors: `placeholder` for leftover `{{...}}` text in metadata
  or in the body outside code (HTML comments included); `not_indexed` for a
  content page that `wiki/index.md` does not link, when the index exists; and
  `not_reciprocal` for a source ↔ concept/entity link without its back-link,
  reported on the page that lacks it.
- Strips fragments only to check the file; heading/block validity is **unchecked**.
  A zero exit with unchecked anchors is not proof that those anchors exist.
- Excludes leading frontmatter, ordinary fenced code and simple inline-code
  spans. An unclosed fence suppresses the rest of the page. This is not a full
  Markdown/Obsidian parser: HTML comments, indented code, blockquote fences and
  complex inline spans are not normalized.
- Exit 0: no error/unsupported form (review unchecked items separately).
  Exit 1: errors or unsupported forms. Exit 2: invalid/unsafe scope or read failure.

The checker does not establish factual support, whether a link's meaning is
right, or transaction completion. Review those separately.

The checker does not establish factual support, whether a link's meaning is
right, or transaction completion.
