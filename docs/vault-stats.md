# Calculate managed-wiki statistics

Use `scripts/vault_stats.py` to measure your wiki's shape: how many pages of
each type, how they link, how much of it is a knowledge layer rather than a
mirror of sources, and which concepts are stale. It uses Python's standard
library and the link checker's scanner, reads only, and needs no model,
Obsidian plugin or graph database.

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
  "schema_version": 2,
  "as_of": "2026-09-24",
  "pages": 4,
  "knowledge_layer": {"pages": 3, "sources": 1, "ratio": 3.0},
  "links_by_type": {"concept->concept": 1, "concept->source": 1, "source->concept": 1},
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
- **Knowledge layer:** pages declared concept, entity or synthesis, against
  pages declared source; the ratio is their quotient (null with no sources). A
  wiki that only mirrors its sources has a ratio near zero however many links it
  has, so the human report shows this line and the next first.
- **Links by type:** the same unique edges, counted by the declared types of
  their two ends (`source->concept`, `source->source`, …; `unknown` included).
  Mostly `source->source` means navigation carried over from the sources rather
  than connected knowledge. The counts sum to the edge total.
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

## Diagnostics and exit status

- **Exit 0:** a report was produced. Broken, malformed, ambiguous or
  unsupported links and metadata stay in `diagnostics` and never become edges.
  Heading and block anchors are reported `anchor_unchecked`. For a pass/fail
  validation, run `scripts/link_check.py`.
- **Exit 2:** an invalid root or `--as-of`, an unsafe path (symlinks,
  hardlinks, non-regular files, or `.obsidian`, `.opencode` or `.git` inside
  the content folders) or a read failure. No partial report is printed.

The tool parses the [managed subset](reference.md#link-checker) of metadata and
links; fenced code and frontmatter never count as links. It writes nothing: no
repairs, index or log updates, or metrics note. What the numbers can and can't
tell you is in [guarantees and limits](guarantees-and-limits.md#checks-establish-structure-not-truth).

## Run it on your vault

Pause other edits, run it from this checkout, and read the report locally:

```sh
python3 scripts/vault_stats.py /path/to/vault --as-of 2026-09-30
```

Reports contain your page paths, so keep them out of this public repository.
The CLI prints to stdout only; to keep a dated snapshot, redirect it to a
private file outside the wiki, with the as-of date and definitions version.

## Comparing with upstream or older snapshots

This keeps the upstream positional vault argument, not its counting semantics.
Upstream scanned project/output/control files, resolved by lowercase basename,
counted repeated mentions and self-links, and called occurrence-count `E/N`
generic “average degree.” It supplied neither components nor staleness, despite
its skills requesting them. This port omits the unrequested word-count metric.

Compare reports only when their scope, definitions version and as-of policy
match; the JSON report records `schema_version`, `scope`, `definitions` and
`as_of` for exactly this. Definitions v2 added the knowledge layer and links by
type; every other v1 metric is unchanged.
