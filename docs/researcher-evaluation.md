# Evaluate the researcher on your wiki

Use this guide to measure how well `sb-researcher` answers questions from a
managed wiki: whether it follows the index, reads what it cites, finds the
pages you expect and declines questions the wiki cannot answer. Run it before
and after a change, such as adding concept pages, and compare the scores.

`tests/researcher_eval.py` makes live provider calls. It needs OpenCode, an
approved provider route and the framework roles. The model-free tools do not
depend on it.

## 1. Write questions with known answers

Create a JSON file outside this repository. Mix single-page, cross-page and
unanswerable questions:

```json
{
  "questions": [
    {"id": "trial-a-times",
     "question": "What cooking times did Trial A record for the open and closed vent settings?",
     "expect": "answer",
     "expected_pages": ["wiki/sources/trial-a.md"],
     "expected_terms": ["18", "24"]},
    {"id": "trial-b-published",
     "question": "On what date was the Trial B record published?",
     "expect": "abstain"}
  ]
}
```

| Field | Meaning |
|---|---|
| `id` | Lowercase hyphenated name, unique in the file |
| `question` | Plain text; `@` and `` !` `` are rejected because OpenCode preprocesses them |
| `expect` | `answer` or `abstain` |
| `expected_pages` | Content pages the answer must cite; required for `answer` |
| `expected_terms` | Optional words the answer must contain (case-insensitive) |

The file is validated against the wiki before any model call. The public example
for the invented fixture is `tests/fixtures/eval/contract-questions.json`. Keep
question files for a private wiki out of this repository.

## 2. Run the evaluation

```sh
python3 tests/researcher_eval.py --live \
  --vault /path/to/vault --questions /path/to/questions.json \
  --agent APPROVED_PRIMARY --model PROVIDER/MODEL --opencode-version X.Y.Z
```

The harness:

1. Copies the adopted `wiki/` pages and the installed contract, role and skill
   into a new temporary directory. It refuses symlinks and hardlinks. It never
   copies the vault's `AGENTS.md`, settings or other folders. Add
   `--include-raw` to also stage the raw captures that source pages name.
2. Grants the researcher exact reads on the staged files and denies everything
   else, then checks the effective configuration, role and skill with
   `opencode debug` before any model call. `--agent` and `--model` name the
   existing primary route whose authentication is reused; the OpenCode version
   must match `--opencode-version`.
3. Asks each question in its own `opencode run` and scores the answer.

Each question takes about a minute. `--steps` (default 8) limits the
researcher's turns and `--timeout` (default 300 seconds) stops a stuck run.
`--search` also grants grep and glob on the staged copy, as the operator does
by default; run with and without it to compare index-only and search-enabled
retrieval. The operator's own query runs also enforce `citations_read`.

## 3. Read the scores

Stdout shows one line of checks per question, then a summary. The full report,
including every answer, is written to `results.json` in the staging directory
with owner-only permissions.

| Check | Passes when |
|---|---|
| `run_completed` | The run exited 0 with an answer |
| `skill_loaded` | The query skill was loaded with the skill tool |
| `tools_ok` | Every tool call was a completed read or skill call |
| `index_first` | `wiki/index.md` was read before any content page |
| `citations_exist` / `citations_read` | Every cited page exists and was read in this run |
| `sections` | The answer has `Read:` and `Not covered:` lines |
| `zero_writes` | Staged files are byte-identical after the run |
| `cited_any` / `expected_cited` | An `answer` question cites pages, including every expected page |
| `expected_terms` | The answer contains every expected term |
| `abstained` | An `abstain` question's answer says the wiki does not cover it |

`abstained` is a phrase heuristic, and none of the checks establishes that a
claim is true. Read the answers in `results.json`. The staging directory holds
copies of your pages; delete it when you are done.

Metrics per question: distinct content pages read, read calls, steps, input and
output tokens, and seconds.

## Limits

The staged copy keeps personal instructions away from the provider, but it is
not filesystem isolation: the runs use your normal OpenCode authentication and
session retention. Provider exposure covers every staged page the researcher
chooses to read.
