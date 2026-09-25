#!/usr/bin/env python3
"""Local, selected chat conversion. See docs/chat-exports.md for the contract."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys


class Unsupported(ValueError):
    pass


class SelectionError(ValueError):
    def __init__(self, reason, source_id):
        super().__init__(reason)
        self.source_id = source_id


def digest(value):
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, allow_nan=False)


def identity(record):
    for key in ("uuid", "id", "conversation_id"):
        if key in record:
            if not isinstance(record[key], str) or not record[key]:
                raise ValueError("invalid conversation ID")
            return record[key]
    return "derived-" + digest(encoded(record).encode())


def timestamp(value):
    if value is None or value == "":
        return None
    try:
        if isinstance(value, bool):
            raise ValueError
        if isinstance(value, (int, float)) and math.isfinite(value):
            result = datetime.fromtimestamp(value, timezone.utc)
        elif isinstance(value, str) and re.fullmatch(
            r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?", value
        ):
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
            # Date-only is a known calendar date; naive times have no known zone.
            if len(value) == 10:
                return result.date().isoformat()
            if result.tzinfo is None:
                raise ValueError
            result = result.astimezone(timezone.utc)
        else:
            raise ValueError
        return result.isoformat().replace("+00:00", "Z")
    except (ValueError, OverflowError, OSError):
        raise ValueError("invalid timestamp (use epoch seconds or zoned ISO)") from None


def messages(record):
    if "mapping" in record:
        mapping, node = record["mapping"], record.get("current_node")
        if not isinstance(mapping, dict) or not isinstance(node, str) or not node:
            raise ValueError("missing/invalid mapping or current_node")
        branch, seen = [], set()
        while node is not None:
            if not isinstance(node, str) or node not in mapping:
                raise ValueError("missing/invalid ancestry node")
            if node in seen:
                raise ValueError("cyclic ancestry")
            seen.add(node)
            item = mapping[node]
            if not isinstance(item, dict) or "parent" not in item or "message" not in item:
                raise ValueError("malformed ancestry node")
            if item["message"] is not None:
                branch.append(item["message"])
            node = item["parent"]
        return list(reversed(branch)), "chatgpt", record["current_node"]
    for key in ("chat_messages", "messages"):
        if key in record:
            if not isinstance(record[key], list):
                raise ValueError("messages must be a list")
            return record[key], "claude" if key == "chat_messages" else "simple", None
    raise Unsupported("unsupported conversation shape")


def text_content(value):
    if isinstance(value, str):
        return value, 0
    if isinstance(value, list):
        parts, omitted = [], 0
        for part in value:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                text, extra = text_content(part)
                if text:
                    parts.append(text)
                omitted += extra
            else:
                omitted += 1
        return "\n\n".join(parts), omitted
    if isinstance(value, dict):
        kind = value.get("content_type", value.get("type"))
        extra = sum(bool(item) for key, item in value.items()
                    if key not in ("type", "content_type", "text", "parts"))
        if kind in ("text", "code") and "text" in value:
            if not isinstance(value["text"], str):
                raise ValueError("malformed text block")
            return value["text"], extra + bool(value.get("parts"))
        if kind in ("text", "multimodal_text"):
            if not isinstance(value.get("parts"), list):
                raise ValueError("malformed text parts")
            text, omitted = text_content(value["parts"])
            return text, omitted + extra
        if isinstance(value.get("text"), str):
            raise Unsupported("unsupported textual content type")
        return "", 1
    raise ValueError("malformed content")


def render(record, source_id):
    items, provider, branch = messages(record)
    title = record.get("name", record.get("title", "untitled"))
    if not isinstance(title, str):
        raise ValueError("invalid title")
    created = timestamp(record.get("created_at", record.get("create_time")))
    updated = timestamp(record.get("updated_at", record.get("update_time")))
    sections, words, total_omitted = [], 0, 0
    for number, message in enumerate(items, 1):
        if not isinstance(message, dict):
            raise ValueError("malformed message")
        author = message.get("author", {})
        if not isinstance(author, dict):
            raise ValueError("malformed author")
        role = message.get("sender", message.get("role", author.get("role")))
        if not isinstance(role, str) or not role:
            raise ValueError("missing/invalid role")
        when = timestamp(message.get("created_at", message.get("create_time")))
        modified = timestamp(message.get("updated_at", message.get("update_time")))
        content = message.get("content", message.get("text", ""))
        if content == [] or content == "":
            content = message.get("text", content)
        text, omitted = text_content(content)
        for key in ("attachments", "files", "tool_calls", "tool_use", "tool_result", "function_call"):
            payload = message.get(key)
            if payload:
                omitted += len(payload) if isinstance(payload, list) else 1
        if role in ("tool", "function"):
            omitted += bool(text)
            text = ""
        words += len(text.split())
        total_omitted += omitted
        # A longer fence preserves text verbatim without letting it forge headings.
        fence = "`" * max(3, max((len(p) for p in re.findall(r"`+", text)), default=0) + 1)
        sections.append(
            f"## Message {number}\n\nRole: {encoded(role)}\n\n"
            f"Created: {encoded(when)}\n\nUpdated: {encoded(modified)}\n\n"
            f"Omitted non-text/tool payloads: {omitted}\n\n{fence}text\n{text}\n{fence}\n"
        )
    metadata = {"title": title, "source": "chat export", "conversation_id": source_id,
                "source_record_sha256": digest(encoded(record).encode()),
                "format": provider, "branch": branch, "created": created, "updated": updated,
                "omitted_payloads": total_omitted}
    output = "---\n" + "".join(f"{key}: {encoded(value)}\n" for key, value in metadata.items())
    output += "---\n\nAssistant statements are generated assertions, not independent evidence.\n\n"
    output += "\n".join(sections)
    return output.encode("utf-8"), words, total_omitted


def directory(path, create=False):
    """Walk using directory descriptors: never follow a linked ancestor."""
    path = Path(path)
    if ".." in path.parts:
        raise ValueError("parent traversal forbidden")
    path = path.absolute()
    fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            try:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except FileNotFoundError:
                if not create:
                    os.close(fd)
                    return None
                os.mkdir(part, mode=0o700, dir_fd=fd)
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def read_regular(fd, name):
    file_fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    with os.fdopen(file_fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("not a unique regular file")
        return stream.read()


def save(fd, name, content, dry_run):
    if fd is not None:
        try:
            old = read_regular(fd, name)
        except FileNotFoundError:
            pass
        else:
            if old != content:
                raise ValueError("version path exists with different bytes")
            return "identical"
    if dry_run:
        return "would_write"
    file_fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    try:
        with os.fdopen(file_fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        os.unlink(name, dir_fd=fd)
        raise
    return "written"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    parser.add_argument("outdir", type=Path)
    parser.add_argument("--min-words", type=int, default=150)
    parser.add_argument("--dry-run", action="store_true")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--conversation-id", action="append", dest="ids")
    selection.add_argument("--all", action="store_true", help="explicit whole-export conversion, not ingestion")
    args = parser.parse_args(argv)
    if args.min_words < 0:
        parser.error("--min-words must be nonnegative")
    counts = dict.fromkeys(("selected", "written", "would_write", "identical", "too_short",
                            "unsupported", "omitted_payloads", "failed"), 0)
    fd = None
    written, failures, planned = [], [], []
    attempted = 0
    try:
        parent = directory(args.export.parent)
        if parent is None or ".." in args.export.parts:
            raise ValueError("invalid export path")
        try:
            raw = read_regular(parent, args.export.name)
        finally:
            os.close(parent)
        data = json.loads(raw, object_pairs_hook=unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
        records = data.get("conversations") if isinstance(data, dict) else data
        if not isinstance(records, list):
            raise Unsupported("expected list or conversations wrapper")
        indexed = {}
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("conversation must be an object")
            source_id = identity(record)
            if source_id in indexed:
                raise SelectionError("duplicate conversation ID", source_id)
            indexed[source_id] = record
        ids = sorted(set(args.ids)) if args.ids else list(indexed)
        for source_id in ids:
            if source_id not in indexed:
                raise SelectionError("selected conversation ID not found", source_id)
        for source_id in ids:
            counts["selected"] += 1
            try:
                content, words, omitted = render(indexed[source_id], source_id)
                counts["omitted_payloads"] += omitted
                if words < args.min_words:
                    counts["too_short"] += 1
                    continue
                name = f"chat-{digest(source_id.encode())[:24]}-{digest(content)[:24]}.md"
                planned.append((source_id, name, content))
            except ValueError as error:
                counts["unsupported" if isinstance(error, Unsupported) else "failed"] += 1
                reason = str(error) if type(error) in (ValueError, Unsupported) else "invalid text encoding"
                failures.append((source_id, reason))
        # Validate all selected records before even creating the destination.
        if not failures:
            fd = directory(args.outdir, create=bool(planned) and not args.dry_run)
            for source_id, name, content in planned:
                attempted += 1
                try:
                    result = save(fd, name, content, args.dry_run)
                    counts[result] += 1
                    if result == "written":
                        written.append(source_id)
                except (OSError, ValueError):
                    counts["failed"] += 1
                    failures.append((source_id, "destination write/verification failed"))
                    break
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        # OS/JSON errors may embed paths or message contents; never echo them.
        counts["unsupported" if isinstance(error, Unsupported) else "failed"] += 1
        reason = str(error) if type(error) in (ValueError, Unsupported, SelectionError) else "invalid input or unsafe/unavailable path"
        failures.append((getattr(error, "source_id", None), reason))
    finally:
        if fd is not None:
            os.close(fd)
    print(" ".join(f"{key}={value}" for key, value in counts.items()))
    if failures:
        print(encoded({"written_ids": written, "failures": failures,
                       "unattempted_ids": [item[0] for item in planned[attempted:]]}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
