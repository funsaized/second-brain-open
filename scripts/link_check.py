#!/usr/bin/env python3
"""Read-only check of the generated managed-wiki subset; no YAML/Obsidian parser.

collect(vault) returns canonical-path -> {metadata, body}, metadata diagnostics.
resolve_links(pages) returns unique directed node edges, link diagnostics.
The two functions can also be used by read-only statistics consumers.
Run locally as the owner on an approved, frozen corpus. Path checks do not lock
against concurrent replacement. Raw references are format-checked, never opened.
Unclosed fenced code suppresses the remaining body; anchors are not verified.
"""

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import stat
import sys


FOLDERS = {"sources": "source", "concepts": "concept", "entities": "entity", "synthesis": "synthesis"}
COMMON = {"title", "type", "created", "updated", "aliases", "tags"}
EXTRA = {"source": {"url", "author", "published", "captured", "raw"},
         "entity": {"kind"}, "concept": set(), "synthesis": set(),
         "index": set(), "log": set()}
TOKEN = re.compile(r"!?\[\[.*?\]\]|!?\[\[.*$|\]\]")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE = re.compile(r"(`+)(?!`)[^`\n]*?\1(?!`)")
ISO = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


def diagnostic(page, kind, target="", **details):
    return {"page": page, "kind": kind, "target": target, **details}


def safe_directory(path, required=False):
    try:
        info = path.lstat()
    except FileNotFoundError:
        if required:
            raise ValueError(f"missing directory: {path}") from None
        return False
    if not stat.S_ISDIR(info.st_mode):
        raise ValueError(f"not a real directory: {path}")
    return True


def safe_file(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError(f"not a unique regular file: {path}")


def metadata(text, page, expected):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text, [diagnostic(page, "metadata", detail="missing leading frontmatter")]
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        return {}, "", [diagnostic(page, "metadata", detail="unclosed frontmatter")]
    fields, issues = {}, []
    for line in lines[1:end]:
        match = re.fullmatch(r"([a-z]+): (.+)\s*", line.rstrip("\r\n"))
        if not match:
            issues.append("invalid key/value line")
            continue
        key, value = match.groups()
        if key in fields:
            issues.append(f"duplicate {key}")
            continue
        try:
            fields[key] = json.loads(value)
        except (ValueError, json.JSONDecodeError):
            issues.append(f"invalid JSON for {key}")
    for key in sorted((COMMON | EXTRA[expected]) - fields.keys()):
        if key != "url":
            issues.append(f"missing {key}")
    for key in sorted(fields.keys() - (COMMON | EXTRA[expected])):
        issues.append(f"unsupported {key}")
    if fields.get("type") != expected:
        issues.append("type does not match path")
    if not isinstance(fields.get("title"), str) or not fields["title"].strip():
        issues.append("invalid title")
    for key in ("aliases", "tags"):
        if not isinstance(fields.get(key), list) or not all(isinstance(v, str) for v in fields[key]):
            issues.append(f"invalid {key}")
    for key in ("created", "updated", "captured", "published"):
        if key in ("captured", "published") and expected != "source":
            continue
        value = fields.get(key)
        if key == "published" and value is None:
            continue
        if not isinstance(value, str) or not ISO.fullmatch(value):
            issues.append(f"invalid {key} date")
        else:
            try:
                date.fromisoformat(value)
            except ValueError:
                issues.append(f"invalid {key} date")
    if expected == "source":
        for key in ("author", "url"):
            value = fields.get(key)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                issues.append(f"invalid {key}")
        raw = fields.get("raw")
        if (not isinstance(raw, str) or not raw.startswith("raw/")
                or not canonical_parts(raw) or not Path(raw).suffix):
            issues.append("invalid raw path")
    if expected == "entity" and fields.get("kind") not in ("person", "org", "product", "tool", "unknown"):
        issues.append("invalid kind")
    if expected == "log" and fields.get("created") != fields.get("updated"):
        issues.append("log header dates must remain equal")
    return fields, "".join(lines[end + 1:]), [diagnostic(page, "metadata", detail=issue) for issue in issues]


def canonical_parts(path):
    """Require literal POSIX components; never normalize traversal/escaping paths."""
    return (bool(path) and all(part not in ("", ".", "..") for part in path.split("/"))
            and "\\" not in path and not any(ord(char) < 32 or ord(char) == 127 for char in path))


def collect(vault):
    """Read only adopted content folders and optional index/log, rejecting unsafe entries."""
    vault = Path(vault)
    if ".." in vault.parts:
        raise ValueError("traversal in vault path")
    absolute = vault.absolute()
    for ancestor in reversed((absolute, *absolute.parents)):
        safe_directory(ancestor, required=True)
    pages, issues = {}, []
    wiki = absolute / "wiki"
    if not safe_directory(wiki):
        return pages, issues  # valid but empty corpus

    def add(path, expected):
        safe_file(path)
        key = path.relative_to(absolute).as_posix()
        try:
            with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), encoding="utf-8") as stream:
                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ValueError(f"not a unique regular file: {key}")
                text = stream.read()
        except (UnicodeError, OSError) as exc:
            raise ValueError(f"cannot read adopted page: {key} ({type(exc).__name__})") from exc
        fields, body, diagnostics = metadata(text, key, expected)
        pages[key] = {"metadata": fields, "body": body}
        issues.extend(diagnostics)

    for control in ("index", "log"):
        path = wiki / f"{control}.md"
        if os.path.lexists(path):
            add(path, control)

    def visit(directory, expected):
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda e: e.name):
                path = Path(entry.path)
                if entry.name in (".obsidian", ".git"):
                    raise ValueError(f"protected entry inside adopted scope: {path}")
                mode = path.lstat().st_mode
                if stat.S_ISDIR(mode):
                    visit(path, expected)
                elif stat.S_ISREG(mode):
                    safe_file(path)
                    if path.suffix == ".md":
                        add(path, expected)
                else:
                    raise ValueError(f"unsafe adopted entry: {path}")

    for folder, expected in FOLDERS.items():
        path = wiki / folder
        if safe_directory(path):
            visit(path, expected)
    return dict(sorted(pages.items())), sorted(issues, key=lambda d: (d["page"], d["detail"]))


def body_lines(body):
    """Exclude fenced blocks and inline-code spans; not a full Markdown parser."""
    fence = None
    for number, line in enumerate(body.splitlines(), 1):
        marker = FENCE.match(line)
        if marker:
            run = marker.group(1)
            if fence is None and (run[0] != "`" or "`" not in line[marker.end():]):
                fence = run
                continue
            elif fence is not None and run[0] == fence[0] and len(run) >= len(fence) and not line[marker.end():].strip():
                fence = None
                continue
        if fence is None:
            yield number, INLINE.sub(lambda m: " " * len(m.group()), line)


def resolve_links(pages):
    """Return unique directed node edges and diagnostics, without guessing aliases."""
    edges, issues = set(), []
    stems = {}
    for key in pages:
        if key.startswith("wiki/") and key not in ("wiki/index.md", "wiki/log.md"):
            stems.setdefault(Path(key).stem, []).append(key)
    for page, content in sorted(pages.items()):
        for line, text in body_lines(content["body"]):
            for match in TOKEN.finditer(text):
                token = match.group()
                detail = {"line": line}
                if not token.endswith("]]") or token.count("[[") != 1 or token.count("]]") != 1 or token == "]]":
                    issues.append(diagnostic(page, "malformed", token, **detail))
                    continue
                if token.startswith("!"):
                    issues.append(diagnostic(page, "embed", token, **detail))
                    continue
                inner = token[2:-2]
                parts = inner.split("|")
                if len(parts) > 2 or not parts[0] or (len(parts) == 2 and not parts[1].strip()):
                    issues.append(diagnostic(page, "malformed", token, **detail))
                    continue
                target, *fragment = parts[0].split("#")
                if len(fragment) > 1 or (fragment and not fragment[0]):
                    issues.append(diagnostic(page, "malformed", token, **detail))
                    continue
                if not target.startswith("wiki/"):
                    candidates = stems.get(target, [])
                    if len(candidates) > 1:
                        issues.append(diagnostic(page, "ambiguous", token, candidates=candidates, **detail))
                    else:
                        issues.append(diagnostic(page, "bare_or_alias", token, **detail))
                    continue
                suffix = target.removeprefix("wiki/")
                folder = suffix.split("/", 1)[0]
                if not canonical_parts(target) or target.endswith(".md") or (folder not in FOLDERS and target not in ("wiki/index", "wiki/log")) or (folder in FOLDERS and "/" not in suffix):
                    issues.append(diagnostic(page, "unsupported_target", token, **detail))
                    continue
                dest = target + ".md"
                if fragment:
                    issues.append(diagnostic(page, "anchor_unchecked", token, **detail))
                if dest not in pages:
                    issues.append(diagnostic(page, "missing", token, **detail))
                elif page != dest and page not in ("wiki/index.md", "wiki/log.md") and dest not in ("wiki/index.md", "wiki/log.md"):
                    edges.add((page, dest))
    return edges, issues


def check(vault):
    pages, metadata_issues = collect(vault)
    edges, issues = resolve_links(pages)
    errors = metadata_issues + [d for d in issues if d["kind"] in ("missing", "malformed", "ambiguous")]
    unsupported = [d for d in issues if d["kind"] in ("embed", "bare_or_alias", "unsupported_target")]
    return {"pages": len(pages) - sum(p in pages for p in ("wiki/index.md", "wiki/log.md")),
            "controls": [p for p in ("wiki/index.md", "wiki/log.md") if p in pages],
            "links": sorted(edges), "errors": errors, "unsupported": unsupported,
            "unchecked": [d for d in issues if d["kind"] == "anchor_unchecked"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault", help="real directory containing optional wiki/")
    parser.add_argument("--json", action="store_true", help="deterministic machine-readable report")
    args = parser.parse_args()
    try:
        result = check(args.vault)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"invalid scope: {exc}\n")
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for key in ("pages", "controls", "links", "errors", "unsupported", "unchecked"):
            print(f"{key}: {result[key] if key == 'pages' else len(result[key])}")
        for key in ("errors", "unsupported", "unchecked"):
            for item in result[key]:
                print(f"  {key}: {item}")
    return int(bool(result["errors"] or result["unsupported"]))


if __name__ == "__main__":
    sys.exit(main())
