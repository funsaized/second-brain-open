# Convert a chat export and ingest one conversation

Use this guide to turn a Claude or ChatGPT export into reviewable Markdown,
choose a conversation, and add it to your wiki. The converter
(`scripts/chat_export_to_md.py`) runs locally with Python's standard library:
it makes no model or network calls and never changes your wiki or the export.
Run it yourself from this checkout, not through an agent.

What the converter keeps and omits, and why a conversation is not evidence by
itself, are in [guarantees and limits](guarantees-and-limits.md#content-keeps-its-provenance).
Its full specification is in the [reference](reference.md#chat-export-converter).

## Before you start

- Python 3.10 or later on Linux or macOS.
- The export file, and a staging folder **outside** this repository and your
  vault, with nothing syncing or publishing it.
- The IDs of the conversations you want. Find them by opening the export
  locally; the converter deliberately has no command that lists titles or
  messages.

## 1. Convert the conversations you chose

Dry-run first, then convert:

```sh
python3 scripts/chat_export_to_md.py /path/to/export.json /path/to/staging \
  --conversation-id CONVERSATION_ID --dry-run
python3 scripts/chat_export_to_md.py /path/to/export.json /path/to/staging \
  --conversation-id CONVERSATION_ID
```

Repeat `--conversation-id` to convert several. `--all` converts everything,
for your own local triage. Conversations under 150 words are skipped; change
that with `--min-words N` (`0` keeps everything).

The command prints counts only, such as
`selected=1 written=1 would_write=0 identical=0 too_short=0 unsupported=0 omitted_payloads=0 failed=0`.
Exit 0 means the conversion ran; exit 2 means an invalid option or input, an
unsupported format or an unsafe path, with the reason on stderr. Rerunning
with the same input is safe: identical files are skipped, and a changed
conversation gets a new versioned file beside the old one.

Each file is `chat-<id hash>-<content hash>.md`, with the title, dates, roles
and omission counts in its frontmatter and one numbered section per message.

## 2. Review the files locally

Open the converted files and sort each conversation: needs a privacy review,
ingest, archive only, or delete. Look for third-party, health, financial and
confidential content, and redact what you need to. Nothing is moved or deleted
for you.

## 3. Ingest one conversation

Copy the approved file into your vault's `raw/`, then
[ingest it with the operator](operator.md#ingest-a-file-you-saved).

Cite messages by `Message N`. Attribute each view to its speaker: what you
said is your dated statement, and what the assistant said is its assertion,
not an independent result. Check any factual claim against real sources before
treating it as established.

To try the whole flow on invented data first, run
`python3 tests/test_chat_handoff.py`. The trial evidence for the converter and
handoff is in the [synthetic acceptance packet](synthetic-acceptance.md) and the
[trial report](native-acceptance-trials.md).
