# Explore a source-grounded wiki

Follow one claim from a concept to its source, inspect a disagreement, and check
the example wiki's structure. By the end, you will know what the main note types
do and what the command-line checks can tell you.

This tutorial uses only the repository's **invented, hand-authored fixtures**.
Nothing here is real experimental evidence or the result of an agent ingest.
You will not configure OpenCode, call a model, write notes, or use private data.

## Before you start

You need Python 3 and a checkout of this repository. The tools use the standard
library; there are no Python packages to install. Obsidian is not required.

If you do not already have a checkout, use Git:

```sh
git clone https://github.com/funsaized/second-brain-open.git
cd second-brain-open
```

Otherwise, open a terminal in your existing checkout. Run every command below
from the repository root. Keep this checkout separate from your personal vault.

## 1. Check the example's structure

Run:

```sh
python3 scripts/link_check.py tests/fixtures/contract
```

You should see:

```text
pages: 5
controls: 2
links: 18
errors: 0
unsupported: 0
unchecked: 0
```

You have checked five knowledge pages and two control pages. No files changed.
If you see a missing-path error, check that your terminal is at the repository
root. If you see diagnostics, inspect them rather than editing files to force
these numbers. A modified checkout may differ from this example.

## 2. Follow a claim to its evidence

Open the [example index](../tests/fixtures/contract/wiki/index.md), then
[Vent choice](../tests/fixtures/contract/wiki/concepts/vent-choice.md).
Use these file links or a text editor; the fixture's wikilinks do not require
you to turn this checkout into an Obsidian vault.

Find the statement that Trial A reports **18 versus 24 minutes**. Follow its
reference to [Trial A's source note](../tests/fixtures/contract/wiki/sources/trial-a.md).
That note names claim A1 and the raw locator `Measurements`.

Open [the raw trial record](../tests/fixtures/contract/raw/trial-a.md) and find
`## Measurements`. You should find the two values, the nominal temperature,
and the single-trial scope. Then read `## Recommendation` for its limitations.

**Checkpoint:** the source note reports one document; the concept uses it to
explain an idea. The locator tells you where to check the statement. The link
checker did not perform this evidence comparison or open the raw file for you.

## 3. Inspect the disagreement

Return to the concept's **What argues against it** section. Open
[Trial B](../tests/fixtures/contract/wiki/sources/trial-b.md) and
[its raw record](../tests/fixtures/contract/raw/trial-b.md).

Trial B reports open at 25 minutes and closed at 19 minutes. Its recommendation
conflicts with Trial A. Its publication date is unknown; an observation date is
not a substitute for that missing fact.

Now read the [vent-setting synthesis](../tests/fixtures/contract/wiki/synthesis/vent-setting.md).
It does not select a winner merely because one observation is later. Its inference
is that the observations do not establish a preferred setting. Repeating matched
trials is a proposed next step, not another source claim. The cause of the ranking
difference remains not covered.

**Checkpoint:** neither a valid link nor a newer date settles a disagreement.
The wiki preserves evidence and uncertainty instead of turning them into a
confident unsupported answer. These are all fictional records.

## 4. Inspect the same wiki as a graph

Run the statistics tool with a fixed date so the result is repeatable:

```sh
python3 scripts/vault_stats.py tests/fixtures/contract --as-of 2026-09-24
```

The report should show:

- Five pages: two sources, one concept, one entity and one synthesis.
- Eighteen unique directed links and one connected component.
- Zero inbound orphans and zero stale concepts out of one eligible concept.
- Zero diagnostics. Index and log are not knowledge nodes.

These counts describe structure. They do not prove that the fictional
recommendations are correct, or that every page is useful.

## What you learned

You traced a claim to a raw section, saw how a synthesis preserves uncertainty,
and ran two read-only checks. You did not test model behavior or create a vault.

Next, choose the task you need:

- [Install the framework into a separate vault](installation.md).
- [Operate an approved ingest and read-only query](manual-loop.md).
- [Understand sources, concepts and the approval boundary](how-it-works.md).
- [Look up checker limits](manual-loop.md#checker-contract) or
  [statistics definitions](vault-stats.md#what-is-counted).
