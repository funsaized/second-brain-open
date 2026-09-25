# Calculate managed-wiki statistics

`scripts/vault_stats.py` is the required P2A core port. It uses Python's standard
library and the link checker's scanner/resolver. No installation, model call,
Obsidian plugin, graph database or agent shell grant is needed.

## Run the synthetic example

From the public checkout:

```sh
python3 scripts/vault_stats.py tests/fixtures/stats --as-of 2026-09-24
python3 scripts/vault_stats.py tests/fixtures/stats --as-of 2026-09-24 --json
# Equivalent module entry point:
python3 -m scripts.vault_stats tests/fixtures/stats --as-of 2026-09-24 --json
```

The positional argument is the corpus root containing `wiki/`, not `wiki/`
itself. `--as-of` requires a calendar-valid `YYYY-MM-DD` and defaults to the
operator's local date. Supply it explicitly for repeatable reports. It changes
date comparisons, not the graph's contents: this does not reconstruct history.

The wholly invented fixture has three concepts (`a`, `b`, `c`) and one source
(`s`), with edges `s → a`, `a → s`, `a → b`. Repeated mentions are deduplicated;
`c` is isolated. At the given as-of, `a` is 91 days old, `b` exactly 90 days,
and `c` has an invalid update date.

| Metric | Verified result |
|---|---:|
| Content pages / unique directed links | 4 / 3 |
| Average out-degree `E/N` | 0.75 |
| Average total directed degree `2E/N` | 1.5 |
| Inbound orphans | 1 / 4 = 25% |
| Weak components | 2 |
| Largest component | 3 / 4 = 75% |
| Stale concepts | 1 / 2 eligible = 50% |
| Concepts: total / eligible / unknown | 3 / 2 / 1 |
| Update dates: valid / missing / invalid / future | 3 / 0 / 1 / 0 |

The report also shows the invalid-date diagnostic. It is not silently treated
as fresh. Human and JSON outputs contain the same metrics; JSON additionally
includes definitions and scope. A representative subset is:

```json
{
  "schema_version": 1,
  "as_of": "2026-09-24",
  "pages": 4,
  "resolved_links": 3,
  "average_out_degree": 0.75,
  "average_total_degree": 1.5,
  "inbound_orphans": {"count": 1, "rate": 0.25},
  "weak_components": {"count": 2, "largest_size": 3, "largest_share": 0.75},
  "stale_concepts": {
    "total": 3, "eligible": 2, "unknown": 1,
    "count": 1, "rate": 0.5, "threshold_days": 90
  },
  "update_dates": {"valid": 3, "missing": 0, "invalid": 1, "future": 0}
}
```

## What is counted

- **Nodes:** Markdown files under `wiki/{sources,concepts,entities,synthesis}/`,
  identified by exact vault-relative paths. Malformed pages remain nodes so bad
  metadata cannot hide them. Root `wiki/index.md` and `wiki/log.md` are not opened.
  Other vault folders are not scanned. Exact instruction filenames `AGENTS.md`,
  `CLAUDE.md`, and `CONTEXT.md` are excluded even inside content folders; a real
  directory with one of those names is still traversed.
- **Types:** only recognized leading-frontmatter types count toward source,
  concept, entity or synthesis totals. Missing, invalid or ambiguous types count
  as `unknown`, not a type guessed from the folder or body. A recognized type
  filed in the wrong folder keeps its declared count and a mismatch diagnostic.
- **Edges:** unique directed non-self links between content nodes. Use the
  checker's canonical extensionless wikilinks, with optional display labels and
  spaces. Controls cannot provide inbound links or connect components. References
  to them are `excluded_control` diagnostics, not file-existence checks.
- **Orphans:** zero inbound edges, not necessarily completely isolated. A page
  with outgoing links but no incoming links is an inbound orphan.
- **Components:** weak connectivity—directions ignored while grouping nodes.
  The largest share is its node count divided by all content nodes.
- **Dates:** only leading-frontmatter `updated` is used, never body text,
  publication dates or filesystem modification times. Absent/null is missing;
  invalid type, ISO spelling, calendar date, JSON or duplicate field is invalid;
  dates after as-of are future. These categories plus valid non-future dates
  partition all nodes. Unsupported metadata is also reported by the checker.
- **Stale:** declared concepts older than **90 days**, not 90 or more. Only valid
  non-future dates enter the denominator. Missing, invalid and future concept
  dates count as unknown. Unknown page types are visible in `by_type`, not
  silently inferred to be concepts.
- **Most linked:** up to ten pages with positive unique inbound counts, sorted
  by descending count, then canonical path. Titles are not identifiers.

Empty corpora have zero counts and null means/rates. A real directory with no
`wiki/` is a valid empty corpus; a missing, non-directory or unsafe root is not.

## Diagnostics and limits

Exit **0** means a report was produced, **not** that the wiki is healthy. Broken,
malformed, ambiguous and unsupported links and metadata issues remain in
`diagnostics` without becoming edges. Fragment file links can be edges, but
heading/block validity remains `anchor_unchecked`. Run `scripts/link_check.py`
separately when a validation exit status is needed.

Exit **2** means invalid root/as-of, unsafe adopted paths, or a read failure;
no partial JSON report is emitted. The shared scanner refuses symlinked roots,
ancestors and adopted entries, hardlinks and non-regular files. Protected
`.obsidian`, `.opencode` and `.git` entries inside content trees cause refusal.
Excluded files are not inspected merely because a content page mentions them.

This is the [managed subset](manual-loop.md#checker-contract), not a general
YAML/Markdown/Obsidian parser. Leading generated metadata and ordinary fenced
code/simple inline spans are excluded from graph links. Shared parser diagnostics
mark unusable fields so a duplicate valid-looking date cannot count as fresh.
Freeze the approved corpus while running: path checks are not a lock against
concurrent replacement. High degree or low orphan rate proves neither accurate
claims nor useful knowledge. No repair, index/log update or metrics note is made.

## Run on a real corpus only after local approval

R7B remains an owner checkpoint: approve the managed scope, pause concurrent
edits, run locally, then review the report locally. Paths in reports can be
private; never paste a real report or private-derived fixture into this public
checkout or its transcripts. This slice tested synthetic data only.

If a dated private snapshot is useful, approve its destination separately,
outside the managed wiki; do not redirect output over a note, index or log.
Record the corpus identity/revision privately along with as-of and definitions.
The CLI writes stdout only and does not choose or create a snapshot destination.

## Comparing with upstream or older snapshots

This keeps the upstream positional vault argument, not its counting semantics.
Upstream scanned project/output/control files, resolved by lowercase basename,
counted repeated mentions and self-links, and called occurrence-count `E/N`
generic “average degree.” It supplied neither components nor staleness, despite
its skills requesting them. This port omits the unrequested word-count metric.

Do not treat the transition as a trend change in knowledge quality. Compare only
matching corpus scope, metric definitions/version and as-of policy. The new JSON
report records `schema_version`, `scope`, `definitions` and `as_of` for this reason.
