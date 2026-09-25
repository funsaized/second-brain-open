# Chat exports: local conversion, then review

The P2B converter is a Python-standard-library operator tool, not an agent skill
or an ingestion command. It makes no model/network calls and never updates a
wiki, moves an export, or deletes a conversation. Run it from this checkout;
do not grant an agent shell access to run it.

## 1. Approve the source and staging destination (R8A)

For personal use, first approve the export, exact staging path and selected IDs
locally. Stage **outside this public repository and the live wiki**, with no
sync/publication process watching the directory. Public tests use only invented
records in temporary directories. Real exports and their derivatives must never
become repository fixtures. No personal conversion or installation is approved
by delivery of this tool.

Use Python 3.10+ on Linux/macOS (POSIX directory descriptors and `O_NOFOLLOW`).
Freeze the source and destination against other writers for the run. Descriptor
walking refuses linked ancestors, but is not protection against another process
renaming an already-open directory or modifying files. Native OpenCode tool
permissions are not filesystem isolation.

```sh
# Replace both paths and the ID with locally approved values; do not paste
# private paths, output artifacts, or IDs into public sessions.
python3 scripts/chat_export_to_md.py /approved/export.json /approved/staging \
  --conversation-id synthetic-chat-a --dry-run
python3 scripts/chat_export_to_md.py /approved/export.json /approved/staging \
  --conversation-id synthetic-chat-a
```

Repeat `--conversation-id ID` for a selected set. Omitting selection is an error.
`--all` is an explicit alternative, only for approved local human triage, never
authorization to ingest or upload the whole export. There is deliberately no
title/message listing command. Obtain IDs by local inspection of the export.
For records without IDs, the derived identity described below can be calculated
locally; `--all --dry-run` does not disclose their contents or identities.

`--min-words N` defaults to 150; nonnegative thresholds count only retained text
using whitespace splitting, not role labels or metadata. Exactly N words passes.
Short filtering is **not** privacy review. `--dry-run` validates and checks
existing output bytes but creates no directories or files.

Successful stdout is counts only, for example:

```text
selected=1 written=1 would_write=0 identical=0 too_short=0 unsupported=0 omitted_payloads=0 failed=0
```

Exit 0 means successful conversion/filtering (or dry-run), not factual acceptance.
Exit 2 means invalid CLI/input, unsupported format, unsafe path, or output failure.
Errors print JSON-escaped source IDs and fixed reasons to stderr, never titles,
message text, exception bodies or file paths. IDs themselves can be sensitive;
keep error reports local. Invalid top-level input uses a null ID. `unsupported`
is separate from `too_short`. Omission counts include supported selected records
even if filtered as short.

## Supported synthetic shapes and fidelity

Top level is a list or `{"conversations": [...]}`. Every record must be an object;
duplicate JSON keys and duplicate conversation identities are errors. Unknown
vendor variants require compatibility review; these fixtures are not proof that
every current vendor export works.

| Shape | Ordered messages and roles |
|---|---|
| Claude | `chat_messages` list; `sender` (including `human`/`assistant`) |
| Simple | `messages` list; `sender`, then `role`, then `author.role` |
| ChatGPT | `mapping` object and nonempty string `current_node`; walk `parent` to explicit null, reverse; role from `author.role` |

Mapping nodes require explicit `parent` and `message`. Structural null messages
are skipped. Unselected sibling branches are ignored, not merged or validated.
The selected walk rejects cycles, absent nodes/parents, non-string parents
(including multiple-parent arrays), and malformed messages. `current_node`
selects the endpoint; descendants are not silently substituted. List shapes
retain list order; timestamps never reorder messages.

Example invented inputs (word filter must be lowered for these tiny examples):

```json
[
  {"uuid":"synthetic-chat-a","name":"Invented vent trial","created_at":"2026-09-24T09:00:00Z",
   "chat_messages":[
     {"sender":"human","text":"I preferred the wider vent in this invented trial."},
     {"sender":"assistant","content":[{"type":"text","text":"That is an unverified preference, not a measured result."}]}]},
  {"id":"synthetic-chat-b","title":"Invented branch","create_time":0,"current_node":"chosen",
   "mapping":{
     "root":{"parent":null,"message":null},
     "question":{"parent":"root","message":{"author":{"role":"user"},"content":{"content_type":"text","parts":["Which trial?"]}}},
     "chosen":{"parent":"question","message":{"author":{"role":"assistant"},"content":{"content_type":"text","parts":["The synthetic trial; evidence is still missing."]}}},
     "sibling":{"parent":"question","message":{"author":{"role":"assistant"},"content":{"content_type":"text","parts":["Not selected."]}}}
   }}
]
```

Content can be a string, a list of strings/`{"type":"text","text":"..."}`
blocks, a single typed text block, or a ChatGPT `content_type: text` /
`multimodal_text` object with a `parts` list. `content` takes precedence over
`text`, except an empty string/list content falls back to `text`; malformed text
blocks fail rather than being stringified. ChatGPT `content_type: code` with a
string `text` is also retained. Other content types carrying a `text` string are
unsupported (not silently filtered as short). Separate text
blocks are joined with two newlines; text within each block is unchanged.
Each message has a numbered heading, quoted original role and timestamps, and a
backtick fence longer than any run in its text. Text is archived literally, not
rendered as executable instructions or trusted Markdown headings.

Unknown non-text blocks count as omitted payloads. Additional populated fields
on text blocks (including citation/media fields) count as omitted units too.
Attachments/files and explicit
tool-call/use/result/function-call fields also count; text of `tool`/`function`
messages is omitted and counted, while their role, position and dates remain.
Counts represent encountered payload units, not attachment bytes or unique assets.
Both message sections and frontmatter record omissions, including tool-only
messages. This is **not lossless media/tool conversion**; retain the original
export separately. Incidental vendor metadata is not reproduced.

Supported creation keys are `created_at`, then `create_time`; update keys are
`updated_at`, then `update_time`,
at conversation and message level. A present key wins, even if null. Values are
epoch **seconds** (not milliseconds), `YYYY-MM-DD`, or
`YYYY-MM-DDTHH:MM:SS[.fraction](Z|±HH:MM)`. Zoned times normalize to UTC, retaining
time to microsecond precision; date-only stays a date. Missing/null/empty values
remain JSON null (unknown), never today's date. Invalid values and zone-less
datetimes fail; no timezone is guessed. Dates and all other metadata values use
JSON quoting in flat YAML frontmatter, including hostile titles/newlines.

## Identity, safe paths, and recovery

Identity is `uuid`, then `id`, then `conversation_id`, if present: a nonempty
string. Otherwise it is `derived-` plus SHA-256 of the record's sorted-key,
ASCII JSON serialization (Python's default separators, finite JSON values).
An absent ID cannot establish continuity across content changes; a revised
ID-less record gets a new derived identity. Original IDs, title, format, branch,
known conversation/message dates and omission counts are retained in the artifact.
`source_record_sha256` hashes that same canonical JSON representation of the full
record, so revisions to omitted payloads or sibling branches also produce a new
version without exposing their content in Markdown.

Filename: `chat-<24 hex ID hash>-<24 hex artifact hash>.md`. Titles and raw IDs
never become path components. Same-title conversations remain distinct. Identical
reruns verify the complete existing bytes and skip; changed output gets a new
digest path without removing the old version. A truncated-digest collision or
tampered existing file is an error, not permission to overwrite or add a suffix.

Input and existing output must be unique regular files (no hardlinks). Traversal,
symlinks in inputs/destinations/ancestors and non-directory ancestors are refused.
New directories use mode 0700 and artifacts 0600 subject to umask. Existing
directory permissions are not changed. Exclusive creation prevents overwrites;
the output file is flushed/fsynced. No shared scanner semantics were changed:
the wiki scanner's preflight helpers do not supply the converter's descriptor-based
write boundary.

All selected records are validated before writes. One invalid/unsupported selected
record blocks the whole batch, including otherwise valid records. Short records
are still validated. Unselected record bodies are not converted, but envelope/ID
validation applies to the whole export. On an output failure, writing stops;
stderr reports written IDs, the failed ID and unattempted IDs. Later planned
records were not attempted. Handled write errors remove the just-created incomplete file, not
earlier successful outputs. A process kill/power loss may leave an incomplete
file: an identical rerun refuses it, rather than silently accepting it. Inspect
locally, preserve evidence and remove only that verified incomplete artifact
before rerunning. No transactional batch, directory-fsync durability, database,
automatic cleanup of old versions, or sync service is promised.

## 2. Review locally, before provider exposure (R8B)

Open only the selected artifacts locally. Classify them as privacy review needed,
selected for ingestion, archive-only, or deletion suggested. Check third-party,
health, financial and confidential content. A suggestion does not delete or move
anything. Approve any redaction and keep source lineage; do not publish titles or
an inventory. An assisted triage session requires separate provider/data approval
and receives only the approved material.

## 3. Hand off one approved conversation (R8C)

Record a local approval manifest: export identity/hash, selected ID/branch,
converted artifact/hash, omissions, privacy decision, approved archive path,
provider and requested bounded ingest. Copy/reference only that artifact into the
approved source archive, then follow [R3/R4's manual loop](manual-loop.md).
Use the explicitly selected roles and plain vetted requests, not slash wrappers
or untrusted `@file`/shell-like arguments.

Use `Message N` as a locator. Attribute the invented example's vent preference
to its human speaker at an unknown message date (the conversation creation date
does not prove when that message was sent). Attribute the caveat to the assistant,
not to an independent experiment. External claims remain unverified until actual
sources are checked; historical user views are not automatically current beliefs.
Query acceptance must preserve these distinctions and disclose missing evidence.

The [synthetic acceptance packet](synthetic-acceptance.md) now records one selected
invented conversion, exact hashes, privacy assessment and Message 1–4 claim oracle.
Run `python3 tests/test_chat_handoff.py` to reproduce it without provider calls.
Native runs and bounded operator-validated four-file edits are authorized. A valid
native proposal, four exact one-time-approved native wiki edits and a source-grounded
applied-wiki answer are now observed, as is a read-only unchanged-source repeat
assessment. See the packet's separate successes and failures. Owner content
acceptance remains pending; no general P2/private-use approval is implied.

**Actual evidence:** deterministic offline tests cover conversion, fidelity,
refusal, rerun and failure behavior using invented temporary records. The later
selected lantern handoff also has native ingest/query and bounded recovery,
repeat/injection evidence; see [the trial report](native-acceptance-trials.md).
Owner content judgment remains separate. Earlier unrelated driver-applied ingests
are not substituted for that native evidence. No live model call or private export
is needed to verify the converter itself.

```sh
python3 -m unittest discover -s tests -p 'test_chat_export_to_md.py' -v
python3 -m unittest discover -s tests -v
git diff --check
```

Compared with the pinned upstream converter, this port fixes active-branch
selection, role/date handling, scalar quoting, explicit omissions and idempotent
versions. It deliberately replaces upstream's direct-to-raw bulk conversion and
agent triage with separate local staging and approval. Chat-import automation
wrappers remain deferred, not required for CLI use.
