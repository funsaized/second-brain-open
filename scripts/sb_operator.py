#!/usr/bin/env python3
"""Operator for the second-brain workers: stage, run, apply and undo.

An operator (the owner, or a primary agent using the second-brain-operator
skill) runs one operation at a time:

  capture fetch one URL without any model. Web pages keep their main content as
         Markdown; PDFs keep the original and gain page-marked Markdown
         (OCR for scans, split into parts when long). Saved to raw/ with
         provenance frontmatter.
  pending list raw/ captures no source page references yet, oldest first.
  stage  copy the adopted wiki, the contract/templates and the operation's
         inputs into a new directory outside the vault, with a manifest of
         every vault file's hash.
  run    launch the worker role (sb-ingestor or sb-researcher) on that copy
         with exact read grants and every other tool denied, verify what it
         read, and save its proposal or answer.
  revise rerun the worker once, telling it why its proposal was refused.
  apply  validate the proposal (allowed paths, page cap, unchanged vault files,
         append-only log record, managed checker clean on the result), back up
         the files it replaces and write it into the vault.
  undo   restore an applied operation's files if nothing changed them since.

Workers never hold edit rights; only `apply` writes, and only under wiki/.
Settings come from VAULT/.opencode/second-brain/operator.json (see
framework/operator.example.json). Standard library only; Linux for `run`.
"""

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
import json
import os
import posixpath
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import textwrap
import urllib.parse

if __package__:
    from . import link_check
    from . import pdf_capture, web_capture
    from .sb_runtime import (answer_text, configure_worker, extract_citations, relative_read, run_role,
                             tool_calls, validate_scope)
else:
    import link_check
    import pdf_capture
    import web_capture
    from sb_runtime import (answer_text, configure_worker, extract_citations, relative_read, run_role,
                            tool_calls, validate_scope)


ROOT = Path(__file__).resolve().parents[1]
ROLES = {"ingest": ("sb-ingestor", "second-brain-ingest"), "compile": ("sb-ingestor", "second-brain-ingest"),
         "query": ("sb-researcher", "second-brain-query")}
CONTRACT = "instructions/wiki-contract.md"
INSTALLED = {
    "contract": (".opencode/instructions/second-brain/wiki-contract.md", "framework/instructions/wiki-contract.md"),
    "templates": ("templates/second-brain", "framework/templates"),
}
TEMPLATES = ("source", "concept", "entity", "synthesis")
CONFIG_KEYS = {"cli", "agent", "model", "opencode_version", "workdir", "max_pages", "steps", "timeout", "auto_apply",
               "search"}
WRITABLE = re.compile(r"wiki/(?:sources|concepts|entities|synthesis)/.+\.md")
INDEX_SECTIONS = ("Concepts", "Entities", "Synthesis", "Sources", "Gaps")
LINK = re.compile(r"\[\[([^\]|#]+)")
INDEX_LINE = re.compile(r"\s*(?:[-*]\s*)?(\w+)\s*\|\s*(?:(?!-\s)([^|\[\]\n]+?)\s*\|\s*)?(.+?)\s*")
RECORD = re.compile(r"## (\d{4}-\d{2}-\d{2}) — .+ — partial")
FILE_BLOCK = re.compile(r"^<<<FILE ([^\n]+)>>>\n(.*?)^<<<END FILE>>>[ \t]*$", re.M | re.S)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(path.read_bytes()) if path.is_file() else None


def load_config(vault, path=None):
    path = Path(path) if path else vault / ".opencode/second-brain/operator.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    missing = {"agent", "model", "opencode_version", "workdir"} - config.keys()
    if missing or set(config) - CONFIG_KEYS:
        raise ValueError(f"operator config needs {sorted(CONFIG_KEYS)}; missing {sorted(missing)}")
    config = {"max_pages": 10, "steps": 40, "timeout": 600, "auto_apply": True, "search": True, **config}
    workdir = Path(config["workdir"]).expanduser().resolve()
    if workdir == vault.resolve() or vault.resolve() in workdir.parents:
        raise ValueError("operator workdir must be outside the vault")
    config["workdir"] = str(workdir)
    return config


def wiki_state(vault):
    """Hash of every adopted wiki file; refuses links like the checker does."""
    pages, _ = link_check.collect(vault)
    return {key: file_hash(vault / key) for key in pages}


CAPTURE_SUFFIXES = (".md", ".txt", ".html", ".htm")
MIN_WORDS, MAX_LINES, WRAP_AT, MAX_LINE = 150, 1900, 1500, 1900


def text_blocks(body):
    """Split Markdown before headings, then (for oversized sections) at blank lines, never inside code."""
    sections, current, fence = [], [], None
    for line in body.splitlines():
        marker = re.match(r"^(`{3,}|~{3,})", line)
        if marker and (fence is None or marker.group(1)[0] == fence[0]):
            fence = None if fence else marker.group(1)
        if fence is None and re.match(r"#{1,3} ", line) and current:
            sections.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        sections.append("\n".join(current))
    blocks = []
    for section in sections:
        if pdf_capture.fits(section):
            blocks.append(section)
            continue
        paragraph, fence = [], None
        for line in section.splitlines():
            marker = re.match(r"^(`{3,}|~{3,})", line)
            if marker and (fence is None or marker.group(1)[0] == fence[0]):
                fence = None if fence else marker.group(1)
            if fence is None and not line.strip() and paragraph:
                blocks.append("\n".join(paragraph))
                paragraph = []
                continue
            paragraph.append(line)
        if paragraph:
            blocks.append("\n".join(paragraph))
    return blocks


def slugify(text, limit=60):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:limit].rstrip("-") or "capture"


def readable_lines(body):
    """Wrap only overlong prose lines so a worker can read every line in full; code is untouched."""
    out, fence = [], None
    for line in body.splitlines():
        marker = re.match(r"^(`{3,}|~{3,})", line)
        if marker and (fence is None or marker.group(1)[0] == fence[0]):
            fence = None if fence else marker.group(1)
        if fence is None and not marker and len(line) > WRAP_AT and not line.lstrip().startswith("|"):
            out.extend(textwrap.wrap(line, 500, break_long_words=False, break_on_hyphens=False))
        else:
            out.append(line)
    # The read tool truncates lines over 2,000 characters; split any that remain (code and tables too).
    out = [chunk for line in out for chunk in ([line[i:i + MAX_LINE] for i in range(0, len(line), MAX_LINE)]
                                                 if len(line) > MAX_LINE else [line])]
    return "\n".join(out).rstrip("\n") + "\n"


def capture_text(url, final_url, body, meta, captured, part=None):
    return frontmatter({"url": url, "final_url": final_url if final_url != url else None, "title": meta["title"],
                        "author": meta["author"], "published": meta["published"], "part": part,
                        "captured": captured,
                        "fetched_with": "sb_operator capture (main-content extraction, no model)",
                        "body_sha256": digest(body.encode())}) + body


def frontmatter(fields):
    lines = [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fields.items()]
    if any(len(line) > MAX_LINE for line in lines):
        raise ValueError("a capture frontmatter line would exceed the read tool's line limit")
    return "---\n" + "".join(line + "\n" for line in lines) + "---\n\n"


def exclusive(vault, stem, suffix, data):
    """Write bytes to the first free raw/ name; never overwrites."""
    (vault / "raw").mkdir(exist_ok=True)
    for n in range(1, 100):
        relative = stem + (f"-{n}" if n > 1 else "") + suffix
        try:
            with open(vault / relative, "xb") as stream:
                stream.write(data)
            return relative
        except FileExistsError:
            continue
    raise ValueError("too many captures with the same name")


def capture_pdf(vault, pdf, url=None, today=None):
    """Page-marked Markdown beside a PDF already in raw/; long documents become parts."""
    vault = Path(vault).resolve()
    validate_scope(vault, [Path(pdf)])
    texts, meta = pdf_capture.extract(vault / pdf)
    stem = pdf[:-len(Path(pdf).suffix)]
    assets = vault / "raw/assets" / Path(stem).name
    if assets.exists():
        raise ValueError(f"figure directory already exists: {assets.relative_to(vault)}")
    captions = pdf_capture.figure_pages(texts)
    chosen = []
    for first, last, _ in pdf_capture.split(texts):
        chosen += [page for page in captions if first <= page <= last][:pdf_capture.FIGURES_PER_PART]
    rendered = pdf_capture.render_figures(vault / pdf, chosen, captions, assets, len(texts))
    marked = list(texts)
    for page, (labels, image) in rendered.items():
        link = os.path.relpath(image, (vault / stem).parent)
        marked[page - 1] = (marked[page - 1].rstrip() + "\n\n" +
                            f"![Figure {', '.join(labels)} (page {page})]({link})")
    parts = pdf_capture.split(marked)
    captured = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    written = []
    for index, (first, last, body) in enumerate(parts, 1):
        body = readable_lines(body)
        figures = [{"page": page, "figures": labels, "image": image.relative_to(vault).as_posix()}
                   for page, (labels, image) in rendered.items() if first <= page <= last]
        not_rendered = sum(first <= page <= last and page not in rendered for page in captions)
        fields = {"url": url, "source_pdf": pdf, "pdf_sha256": file_hash(vault / pdf), "title": meta["title"],
                  "author": meta["author"], "published": meta["published"], "pdf_created": meta["pdf_created"],
                  "pages": len(texts),
                  "page_range": f"{first}-{last}", "part": f"{index}/{len(parts)}" if len(parts) > 1 else None,
                  "captured": captured, "extracted_with": f"pdftotext ({meta['mode']})", "ocr": meta["ocr"],
                  "quality": meta["quality"], "figures": figures,
                  "figures_not_rendered": not_rendered, "body_sha256": digest(body.encode())}
        name = stem + (f"-part-{index}" if len(parts) > 1 else "")
        written.append(exclusive(vault, name, ".md", (frontmatter(fields) + body).encode()))
    return {"raw": written[0], "parts": written, "pdf": pdf, "title": meta["title"], "pages": len(texts),
            "ocr": meta["ocr"], "mode": meta["mode"], "figure_pages": sorted(rendered),
            "figures_not_rendered": sum(page not in rendered for page in captions)}


def capture_fields(path):
    """Leading JSON-valued frontmatter of a capture file, or {} when absent."""
    with open(path, encoding="utf-8", errors="replace") as stream:
        head = stream.read(65536)
    if not head.startswith("---\n") or "\n---\n" not in head[4:]:
        return {}
    fields = {}
    for line in head[4:].split("\n---\n", 1)[0].splitlines():
        key, _, value = line.partition(": ")
        try:
            fields[key] = json.loads(value)
        except ValueError:
            continue
    return fields


def capture(vault, url, config_path=None, today=None, fetch=None):
    """Save one URL to raw/; refuses fragments, unreadable PDFs and unsupported types."""
    vault = Path(vault).resolve()
    load_config(vault, config_path)
    if not re.fullmatch(r"https?://[^\s@]{3,2000}", url):
        raise ValueError("capture takes one http(s) URL without spaces or @")
    data, kind, final_url, charset = (fetch or web_capture.fetch)(url)
    today = today or date.today().isoformat()
    if kind == "application/pdf" or data[:5] == b"%PDF-":
        with tempfile.TemporaryDirectory(prefix="sb-pdf-") as tmp:
            probe = Path(tmp) / "download.pdf"
            probe.write_bytes(data)
            title = pdf_capture.info(probe)["title"]
        segment = Path(urllib.parse.urlparse(final_url).path).name
        name = title or re.sub(r"\.pdf$", "", segment, flags=re.I) or "document"
        pdf = exclusive(vault, f"raw/{today}-{slugify(name)}", ".pdf", data)
        try:
            return capture_pdf(vault, pdf, url, today)
        except ValueError:
            (vault / pdf).unlink()
            raise
    text = data.decode(charset or "utf-8", errors="replace")
    if kind in ("text/plain", "text/markdown"):
        heading = re.search(r"(?m)^# (.+)$", text)
        body, meta = text, {"title": heading.group(1).strip() if heading else None, "author": None, "published": None}
    elif kind in ("text/html", "application/xhtml+xml"):
        body, meta = web_capture.extract(text, final_url)
    else:
        raise ValueError(f"unsupported content type {kind}; save the file into raw/ yourself")
    body = readable_lines(body)
    words, lines = len(body.split()), body.count("\n")
    if words < MIN_WORDS:
        raise ValueError(f"only {words} words of main content: the page may need JavaScript, a login or a "
                         "subscription. Save it with the Obsidian Web Clipper into raw/ instead")
    parts = pdf_capture.pack(text_blocks(body))
    captured = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    stem = f"raw/{today}-{slugify(meta['title'] or re.sub(r'^https?://', '', url))}"
    written = []
    for index, (_, _, text) in enumerate(parts, 1):
        part = f"{index}/{len(parts)}" if len(parts) > 1 else None
        text = text.rstrip("\n") + "\n"
        written.append(exclusive(vault, stem + (f"-part-{index}" if part else ""), ".md",
                                 capture_text(url, final_url, text, meta, captured, part).encode()))
    return {"raw": written[0], "parts": written, "title": meta["title"], "words": words, "lines": lines}


def pending(vault):
    """Captures no source page references, oldest first; folders of multi-file captures count as referenced."""
    vault = Path(vault).resolve()
    pages, _ = link_check.collect(vault)
    referenced = {page["metadata"].get("raw") for key, page in pages.items() if key.startswith("wiki/sources/")}
    used_dirs = {str(Path(r).parent) for r in referenced if isinstance(r, str)} - {"raw"}
    found = []
    raw = vault / "raw"
    for path in (raw.rglob("*") if raw.is_dir() else ()):
        relative = path.relative_to(vault).as_posix()
        if (not path.is_file() or path.is_symlink() or path.suffix.lower() not in CAPTURE_SUFFIXES
                or any(part.startswith(".") for part in path.relative_to(raw).parts)
                or relative.startswith("raw/assets/") or relative in referenced
                or str(Path(relative).parent) in used_dirs):
            continue
        found.append((path.stat().st_mtime, relative))
    extracted = set()
    for path in (raw.rglob("*.md") if raw.is_dir() else ()):
        with open(path, encoding="utf-8", errors="replace") as stream:
            head = stream.read(4096)
        match = re.search(r'(?m)^source_pdf: "([^"\n]+)"$', head)
        if match:
            extracted.add(match.group(1))
    for path in (raw.rglob("*") if raw.is_dir() else ()):
        relative = path.relative_to(vault).as_posix()
        if (path.suffix.lower() == ".pdf" and path.is_file() and not path.is_symlink() and relative not in extracted
                and not relative.startswith("raw/assets/")
                and not any(part.startswith(".") for part in path.relative_to(raw).parts)):
            found.append((path.stat().st_mtime, relative))
    return [relative for _, relative in sorted(found)]


def stage(vault, kind, inputs=(), task=None, config_path=None, today=None, url=None, series=None):
    vault = Path(vault).resolve()
    captured = None
    if url is not None:
        if kind != "ingest" or inputs:
            raise ValueError("--url is for ingest and replaces --input")
        if not task or "@" in task or re.search(r"!\s*`", task):
            raise ValueError("ingest needs a plain-text --task without @ or !` tokens")
        captured = capture(vault, url, config_path, today)
        inputs = [captured["raw"]]
    config = load_config(vault, config_path)
    role, skill = ROLES[kind]
    if kind == "ingest" and len(inputs) == 1 and inputs[0].lower().endswith(".pdf"):
        if not inputs[0].startswith("raw/") or not link_check.canonical_parts(inputs[0]):
            raise ValueError(f"ingest input not allowed: {inputs[0]}")
        if not task or "@" in task or re.search(r"!\s*`", task):
            raise ValueError("ingest needs a plain-text --task without @ or !` tokens")
        captured = capture_pdf(vault, inputs[0], None, today)
        inputs = [captured["raw"]]
    elif any(item.lower().endswith(".pdf") for item in inputs):
        raise ValueError("ingest one PDF per operation")
    inputs = sorted(set(inputs))
    if kind == "query":
        if inputs or not task:
            raise ValueError("query takes --question and no inputs")
    elif not task or (kind == "ingest" and not inputs):
        raise ValueError(f"{kind} needs --task" + (" and --input or --url" if kind == "ingest" else ""))
    for item in inputs:
        valid = item.startswith("raw/") if kind == "ingest" else WRITABLE.fullmatch(item)
        if not valid or not link_check.canonical_parts(item):
            raise ValueError(f"{kind} input not allowed: {item}")
        validate_scope(vault, [Path(item)])
    if "@" in task or re.search(r"!\s*`", task):
        raise ValueError("task/question must be plain text without @ or !` preprocessing tokens")
    state = wiki_state(vault)
    today = today or date.today().isoformat()
    workdir = Path(config["workdir"])
    workdir.mkdir(parents=True, exist_ok=True, mode=0o700)
    op = workdir / f"{today}-{kind}-{secrets.token_hex(3)}"
    corpus, profile = op / "corpus", op / "profile"
    op.mkdir(mode=0o700)
    corpus.mkdir()
    profile.mkdir()
    copies = {key: vault / key for key in state}
    copies.update({item: vault / item for item in inputs})
    figures, input_parts = [], {}
    for item in inputs if kind == "ingest" else ():
        fields = capture_fields(vault / item)
        if fields.get("part"):
            input_parts[item] = {"part": fields["part"], "page_range": fields.get("page_range")}
        for figure in fields.get("figures") or []:
            image = figure.get("image") if isinstance(figure, dict) else None
            if (isinstance(image, str) and image.startswith("raw/assets/") and link_check.canonical_parts(image)
                    and (vault / image).is_file()):
                copies[image] = vault / image
                figures.append(image)
    installed, public = INSTALLED["contract"]
    copies[CONTRACT] = vault / installed if (vault / installed).is_file() else ROOT / public
    if kind != "query":
        installed, public = INSTALLED["templates"]
        for name in TEMPLATES:
            local = vault / installed / f"{name}.md"
            copies[f"templates/{name}.md"] = local if local.is_file() else ROOT / public / f"{name}.md"
    for target, source in sorted(copies.items()):
        base = vault if source.is_relative_to(vault) else ROOT
        validate_scope(base, [source.relative_to(base)])
        path = corpus / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source.read_bytes())
    # Workers with named inputs need titles and paths; compile by topic and query choose pages by description.
    compact = (kind == "ingest" or (kind == "compile" and bool(inputs))) and (corpus / "wiki/index.md").is_file()
    if compact:
        index = corpus / "wiki/index.md"
        index.write_text(compact_index(index.read_text(encoding="utf-8")))
    origin = {}
    for name in (f"agents/{role}.md", f"skills/{skill}/SKILL.md"):
        local = vault / ".opencode" / name
        source = local if local.is_file() else ROOT / "framework" / name
        base = vault if source.is_relative_to(vault) else ROOT
        validate_scope(base, [source.relative_to(base)])
        (profile / name).parent.mkdir(parents=True, exist_ok=True)
        (profile / name).write_bytes(source.read_bytes())
        origin[name] = {"from": "vault" if base == vault else "framework", "sha256": file_hash(source)}
    manifest = {"id": op.name, "kind": kind, "role": role, "skill": skill, "vault": str(vault), "date": today,
                "task": task, "inputs": inputs, "input_sha256": {i: file_hash(vault / i) for i in inputs},
                "wiki_preimages": state, "reads": sorted(copies) + ["operation.md"], "origin": origin,
                "figures": figures, "input_parts": input_parts, "series": series, "compact_index": compact,
                "config": {k: config[k] for k in sorted(config)},
                "capture": captured}
    (corpus / "operation.md").write_text(
        "# Operator-verified operation manifest\n\n```json\n" + json.dumps({
            "status": "operator preflight verifies these read grants before the worker starts",
            "operation": kind, "role": role, "task": task, "inputs": inputs, "date": today,
            "readable": f"{len(manifest['reads'])} staged files: every wiki page the index links, plus the paths below",
            "index": ("compact: titles and paths only; search the pages for more" if compact else "full catalog"),
            "search": "grep and glob over these staged files" if config["search"] else "not available",
            "paths": {"contract": CONTRACT, "index": "wiki/index.md", "log": "wiki/log.md",
                      "templates": [f"templates/{name}.md" for name in TEMPLATES] if kind != "query" else [],
                      "inputs": inputs, "figures": figures},
            "writes": "none; the worker returns a proposal and the operator validates and applies it"},
            indent=2) + "\n```\n")
    write_json(op / "manifest.json", manifest)
    subprocess.run(["git", "init", "--quiet", str(corpus)], check=True, capture_output=True)
    return op


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    path.chmod(0o600)


def compact_index(text):
    """The index without frontmatter, comments or entry descriptions: headings, titles and paths only."""
    lines = text.split("\n")
    if lines and lines[0] == "---" and "---" in lines[1:]:
        lines = lines[lines.index("---", 1) + 1:]
    body = re.sub(r"<!--.*?-->", "", "\n".join(lines), flags=re.S)
    out, noted = [], False
    for line in body.split("\n"):
        entry = re.match(r"- \[\[[^\]]+\]\]", line)
        out.append(entry.group(0) if entry else line.rstrip())
        if line.startswith("# ") and not noted:
            out += ["", "> Compact copy for this operation: titles and paths only; the vault's index keeps the "
                        "descriptions. Search the staged pages when a title is not enough."]
            noted = True
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip("\n") + "\n"


def corpus_state(corpus):
    return {p.relative_to(corpus).as_posix(): digest(p.read_bytes())
            for p in sorted(corpus.rglob("*")) if p.is_file() and ".git" not in p.relative_to(corpus).parts}


def worker_prompt(manifest, corpus):
    kind, config = manifest["kind"], manifest["config"]
    search = config.get("search", False)
    head = ("You are running under an operator. Your read grants were verified before this call"
            + ("; you can also search the staged files with grep and glob" if search else "")
            + ". Edits and all other tools are denied. Load your designated skill with the skill tool. "
            f"Working directory: {corpus}. Read files by their paths relative to it, exactly as operation.md "
            f"lists them (for example wiki/index.md, {CONTRACT}, templates/concept.md); do not retype the absolute "
            "directory. If a read is denied, you used a path that is not staged: retry with the listed relative "
            "path, or continue without an optional page. Stop only when the index, the contract or an input cannot "
            "be read at its listed path. The index, the contract and every input must be read completely: when one "
            "is too long for one read (the output says it was capped, or does not end with 'End of file'), read "
            "it in consecutive ranges with offset and limit until you have seen every line; the operator checks "
            "this. Other files, such as wiki/log.md, may be read in part. A capped read is never a reason to stop: "
            "continue from the next offset. Read wiki/index.md first. ")
    if kind == "query":
        return head + (
            f"Question: {manifest['task']} Answer as your skill says, citing exact page paths such as "
            "wiki/sources/name.md, and end with a line starting 'Read:' and a line starting 'Not covered:'.")
    inputs = ", ".join(manifest["inputs"])
    source = ("This is an ingest: the input is an approved raw capture; use its path as the source page's raw "
              "field. When the capture has frontmatter, take the source page's url and any non-null author and "
              "published from it, and the date part of its captured timestamp as captured (otherwise "
              f"{manifest['date']}). When author or published is null there but the document itself states it, "
              "such as a paper's author list or dated byline, use that; otherwise leave it null. "
              + "".join(f"{name} is part {info['part']} of a longer document"
                        + (f" (pages {info['page_range']})" if info.get("page_range") else "")
                        + ": its end continues in the next part, which is not a truncated read. "
                        for name, info in manifest.get("input_parts", {}).items())
              + (f"Rendered figure pages you can open with the read tool: {', '.join(manifest['figures'])}. "
                 if manifest.get("figures") else "")
              if kind == "ingest" else
              ("This is a compile from the named inputs. " if manifest["inputs"] else
               "This is a compile by topic: you choose the pages to draw on. "))
    reading = (f"Read these inputs completely before proposing: {inputs}. " if manifest["inputs"] else "")
    if manifest.get("compact_index"):
        reading += "wiki/index.md is a compact catalog here: titles and paths, no descriptions. "
    series = manifest.get("series")
    if series:
        reading += (f"This is item {series['position']} of {series['count']} in an ordered series. "
                    + (f"The previous item's source page is {series['previous_source']}; link it as the previous part. "
                       if series.get("previous_source") else "")
                    + "Pages from later items do not exist yet: never link to them. "
                    + (f"The operator files this item's new Sources index entries under the theme '{series['theme']}'. "
                       if series.get("theme") else "")
                    + (f"The operator re-files the input notes' existing index entries under the theme "
                       f"'{series['file_inputs_under']}': give no INDEX lines for them. "
                       if series.get("file_inputs_under") else "")
                    + ("Write only this item's source page and its index entry; do not create or update concept, "
                       "entity or synthesis pages, which are compiled after the series. "
                       if series.get("sources_only") else ""))
    return head + source + (
        f"Task: {manifest['task']} {reading}Readable files, by exact relative path"
        + (" (find them with the index, grep or glob)" if search else " only (directory listings are not available)")
        + ": every page the index links, wiki/log.md, "
        f"{', '.join(f'templates/{name}.md' for name in TEMPLATES)}, the inputs and operation.md (the operation manifest, optional; there is no other manifest). "
        "Open candidate pages from the index as needed. "
        f"Today is {manifest['date']}. Propose at most {config['max_pages']} new or changed pages under "
        "wiki/sources, wiki/concepts, wiki/entities or wiki/synthesis. Never propose wiki/index.md, wiki/log.md, "
        "raw/ or any other path as a FILE: give index changes as INDEX entries, which the operator merges. "
        "Reply with no outer code fence, in this format:\n<<<FILE path>>>\ncomplete Markdown with final newline\n"
        "<<<END FILE>>>\n(one block per page)\n<<<INDEX>>>\none line per new or changed catalog entry, as "
        "'<Concepts|Entities|Synthesis|Sources|Gaps> | - [[wiki/<folder>/<page>|Title]] — short description' "
        "or, to file it under a '### <theme>' heading in that section (the document a part belongs to, or a "
        "topic), '<Section> | <theme> | - [[...]] — description'. Gaps entries are plain text. An entry replaces "
        "the existing entry for the same page; without a theme it keeps that entry's place\n"
        "<<<LINKS>>>\none line per link to add to an existing page without rewriting it, as "
        "'wiki/<folder>/<page>.md | - [[wiki/<folder>/<page>|Title]] — how they relate'; use this for "
        "reciprocal back-links on long source notes\n"
        f"<<<LOG>>>\none log record whose heading is '## {manifest['date']} — <operation> — partial', followed "
        "by bullets for source identity, changed paths, contradictions, gaps and pending verification\n"
        "<<<NOTES>>>\ncoverage review, claim/locator notes and open questions.\n"
        "If nothing should change (for example an unchanged repeat) or you cannot finish (truncated or "
        "unreadable input, conflicting evidence you cannot represent), reply with only <<<NOTES>>> and the reason.")


def section(text, name):
    """Section body without an optional closing marker (<<<NAME>>> or <<<END NAME>>>)."""
    lines = text.strip().splitlines()
    # Models close sections inconsistently; any final marker line is only a closer.
    if lines and re.fullmatch(r"<<<(?:END )?[A-Z ]+>>>", lines[-1].strip()):
        lines = lines[:-1]
    return "\n".join(lines).strip()


MARKER = re.compile(r"^\s*<<<\s*(END\s+)?(FILE|INDEX|LINKS|LOG|NOTES)(?:\s+([^>]*?))?\s*>>>\s*$")


def parse_proposal(text):
    """Read a worker reply as marked sections, tolerating formatting noise.

    Prose outside sections, repeated section markers and missing closing
    markers are ignored; malformed INDEX/LINKS lines are skipped with a warning.
    Only a reply without any proposal marker, or a FILE without a path, fails.
    """
    lines = text.strip().splitlines()
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].strip().startswith("```"):
        lines = lines[1:-1]
    files, sections, warnings = {}, {"INDEX": [], "LINKS": [], "LOG": [], "NOTES": []}, []
    current, path, buffer, seen, ignored = None, None, [], False, 0

    def close_file():
        nonlocal path, buffer
        if path is not None:
            if path in files:
                warnings.append(f"duplicate FILE {path}: the last one is used")
            files[path] = "\n".join(buffer).strip("\n") + "\n"
        path, buffer = None, []

    for line in lines:
        match = MARKER.match(line)
        if not match:
            if current == "FILE":
                buffer.append(line)
            elif current:
                sections[current].append(line)
            elif line.strip():
                ignored += 1
            continue
        seen = True
        closing, kind, argument = bool(match.group(1)), match.group(2), (match.group(3) or "").strip()
        if current == "FILE":
            close_file()
        if closing:
            current = None
        elif kind == "FILE":
            if not argument:
                raise ValueError("FILE marker without a path")
            current, path, buffer = "FILE", argument, []
        else:
            current = kind
    if current == "FILE":
        close_file()
    if not seen:
        raise ValueError("the reply contains no proposal markers")
    if ignored:
        warnings.append(f"ignored {ignored} line(s) of text outside sections")
    index = []
    for line in sections["INDEX"]:
        if not line.strip():
            continue
        match = INDEX_LINE.fullmatch(line)
        name = match.group(1).capitalize() if match else None
        if name not in INDEX_SECTIONS:
            warnings.append(f"skipped INDEX line: {line.strip()[:60]}")
            continue
        entry = match.group(3) if match.group(3).startswith("- ") else "- " + match.group(3)
        index.append([name, entry, match.group(2)] if match.group(2) else [name, entry])
    links = []
    for line in sections["LINKS"]:
        if not line.strip():
            continue
        match = re.fullmatch(r"\s*(?:[-*]\s*)?`?(wiki/\S+?\.md)`?\s*\|\s*(.+?)\s*", line)
        if not match or not first_link(match.group(2)):
            warnings.append(f"skipped LINKS line: {line.strip()[:60]}")
            continue
        entry = match.group(2) if match.group(2).startswith("- ") else "- " + match.group(2)
        links.append([match.group(1), entry])
    log = "\n".join(sections["LOG"]).strip() or None
    return {"files": files, "index": index, "links": links, "log": log,
            "notes": "\n".join(sections["NOTES"]).strip(), "warnings": warnings}


def lines_seen(output):
    """Line numbers shown in one read tool output ("12: text" lines)."""
    body = output.split("<content>", 1)[-1]
    return {int(number) for number in re.findall(r"(?m)^(\d+): ", body)}


def verify_events(manifest, corpus, events, returncode, before, after, required=None):
    """Worker evidence: designated skill, in-scope reads covering every required line, no writes.

    A large file may be read in several ranges (offset/limit); it counts as read when
    the reads together show every one of its lines and none was cut short.
    """
    calls = tool_calls(events)
    search = manifest["config"].get("search", False)
    allowed_tools = ("read", "skill", "grep", "glob") if search else ("read", "skill")
    searches = [c.get("state", {}).get("input", {}).get("path") for c in calls if c["tool"] in ("grep", "glob")]
    seen, cut = {}, set()
    for call in calls:
        state = call.get("state", {})
        if call["tool"] == "read" and state.get("status") == "completed":
            path = relative_read(corpus, state.get("input", {}).get("filePath", ""))
            output = state.get("output", "")
            seen.setdefault(path, set()).update(lines_seen(output))
            if "(line truncated to" in output:
                cut.add(path)
    reads = {}
    for path, numbers in seen.items():
        target = corpus / path if path else None
        if target is not None and target.is_file() and target.suffix.lower() in (".md", ".txt", ".json"):
            total = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
            reads[path] = path not in cut and set(range(1, total + 1)) <= numbers
        else:
            reads[path] = False
    required = required or {"wiki/index.md", CONTRACT, *manifest["inputs"]}
    # An answer may cite only pages the researcher opened; a search hit is not a read.
    unread_citations = ([p for p in extract_citations(answer_text(events)) if p not in seen]
                        if manifest["kind"] == "query" else [])
    checks = {
        "run_completed": returncode == 0 and bool(answer_text(events)),
        "skill_loaded": any(c["tool"] == "skill" and c.get("state", {}).get("status") == "completed"
                            and c["state"].get("input", {}).get("name") == manifest["skill"] for c in calls),
        "only_reads": all(c["tool"] in allowed_tools for c in calls),
        "searches_in_scope": all(not path or (relative_read(corpus, path) is not None
                                              and ".." not in Path(relative_read(corpus, path)).parts)
                                 for path in searches),
        "reads_in_scope": all(p in manifest["reads"] for p in seen),
        "required_full_reads": all(reads.get(p) for p in required),
        "zero_writes": before == after,
    }
    if manifest["kind"] == "query":
        checks["citations_read"] = not unread_citations
    failed = [{"tool": c["tool"] if c["tool"] in ("read", "skill", "grep", "glob", "edit", "bash") else "other",
               "path": relative_read(corpus, c.get("state", {}).get("input", {}).get("filePath", "")) or None}
              for c in calls if c.get("state", {}).get("status") != "completed"]
    evidence = {"checks": checks, "reads": sorted(p or "(outside)" for p in seen), "searches": len(searches),
                "failed_tool_calls": failed,
                "unread_required": sorted(p for p in required if not reads.get(p)),
                **({"unread_citations": unread_citations} if unread_citations else {})}
    return all(checks.values()), evidence


def run(op, feedback=None, format_only=False):
    op = Path(op).resolve()
    manifest = json.loads((op / "manifest.json").read_text())
    if (op / "run.json").exists() and feedback is None:
        raise ValueError("operation already ran; use revise or stage a new one")
    corpus, profile, config = op / "corpus", op / "profile", manifest["config"]
    prompt = worker_prompt(manifest, corpus)
    if feedback is not None and format_only:
        prompt += ("\n\nYour previous reply, saved as previous-proposal.md, could not be read: " + "; ".join(feedback)
                   + ". You already read the inputs completely for it. Read previous-proposal.md and return the same "
                   "content in exactly the reply format above: FILE blocks, then INDEX, LINKS, LOG and NOTES sections.")
    elif feedback is not None and manifest["kind"] == "query":
        prompt += ("\n\nThe operator's checks rejected your previous answer, saved as previous-proposal.md: "
                   + "; ".join(feedback) + ". Read previous-proposal.md, open and read every page you cite, or drop "
                   "the claims that rest on pages you have not read, and return a complete corrected answer.")
    elif feedback is not None:
        prompt += ("\n\nThe operator's checks rejected your previous proposal, saved as previous-proposal.md. "
                   "Problems: " + "; ".join(feedback) + ". Read previous-proposal.md, fix every problem and return "
                   "a complete corrected proposal in the same format, including every page that should change.")
    search = config.get("search", False)
    extra = sorted(set(corpus_state(corpus)) - set(manifest["reads"]))
    if search and extra:
        # Search permission matches the pattern, not the files, so everything staged must be readable.
        raise ValueError(f"staged corpus holds files without read grants: {', '.join(extra[:5])}")
    env = configure_worker(corpus, profile, manifest["role"], manifest["skill"], manifest["reads"],
                           config["agent"], config["model"], config["opencode_version"], config["steps"], search)
    before = corpus_state(corpus)
    events, returncode, seconds = run_role(env, corpus, manifest["role"], prompt, config["timeout"])
    text = answer_text(events)
    (op / "response.md").write_text(text + "\n")
    (op / "response.md").chmod(0o600)
    passed, evidence = verify_events(manifest, corpus, events, returncode, before, corpus_state(corpus),
                                     required={"previous-proposal.md"} if format_only else None)
    result = {"passed": passed, "seconds": seconds, **evidence}
    if passed and manifest["kind"] != "query":
        try:
            proposal = parse_proposal(text)
            write_json(op / "proposal.json", proposal)
            result["proposed_files"] = sorted(proposal["files"])
            result["proposed_links"] = len(proposal["links"])
            if proposal["warnings"]:
                result["parse_warnings"] = proposal["warnings"]
        except ValueError as error:
            result.update(passed=False, proposal_error=str(error))
    write_json(op / "run.json", result)
    return result


MAX_REVISIONS = 2


def revise(op):
    """Rerun the worker with feedback: parse errors (format only) or dry-run problems; at most twice."""
    op = Path(op).resolve()
    manifest = json.loads((op / "manifest.json").read_text())
    if (op / "receipt.json").exists():
        raise ValueError("revise needs an unapplied ingest or compile operation")
    attempts = len(list(op.glob("attempt-*")))
    if attempts >= MAX_REVISIONS:
        raise ValueError(f"already revised {attempts} times; stage a new operation")
    previous = json.loads((op / "run.json").read_text()) if (op / "run.json").exists() else {}
    if manifest["kind"] == "query":
        failed = [name for name, ok in previous.get("checks", {}).items() if not ok]
        if failed != ["citations_read"]:
            raise ValueError("revise a query only when citations_read is its one failed check")
        problems, format_only = [f"you cited pages you did not read: {', '.join(previous['unread_citations'])}"], False
    elif (op / "proposal.json").exists():
        problems, format_only = apply(op, dry_run=True)["problems"], False
        if not problems:
            raise ValueError("the proposal already passes; apply it")
        if all(p.startswith("vault file changed since staging") for p in problems):
            raise ValueError("only pages changed in the vault since staging; a revision cannot fix that, "
                             "stage the operation again")
    elif previous.get("proposal_error"):
        problems, format_only = [previous["proposal_error"]], True
    else:
        raise ValueError("revise needs a proposal, or a reply that could not be parsed")
    archive = op / f"attempt-{attempts + 1}"
    archive.mkdir(mode=0o700)
    for name in ("run.json", "proposal.json", "response.md"):
        if (op / name).exists():
            os.replace(op / name, archive / name)
    corpus = op / "corpus"
    shutil.copy2(archive / "response.md", corpus / "previous-proposal.md")
    manifest["reads"] = sorted({*manifest["reads"], "previous-proposal.md"})
    write_json(op / "manifest.json", manifest)
    result = run(op, feedback=problems, format_only=format_only)
    result["feedback"] = problems
    return result


def check_proposal(manifest, proposal):
    vault, config = Path(manifest["vault"]), manifest["config"]
    files, record = proposal["files"], proposal["log"]
    problems = []
    links = proposal.get("links", [])
    touched = set(files) | {path for path, _ in links}
    if not touched and not proposal.get("index"):
        problems.append("proposal has no pages or index entries")
    # The limit bounds pages to review; LINKS lines are one-line appends and do not count.
    if len(files) > config["max_pages"]:
        problems.append(f"proposal writes {len(files)} pages; the limit is {config['max_pages']}")
    for path, _ in links:
        if path in files:
            problems.append(f"{path} is both rewritten and link-patched: put the link in its FILE")
        elif not WRITABLE.fullmatch(path) or not link_check.canonical_parts(path) or not (vault / path).is_file():
            problems.append(f"LINKS target is not an existing wiki page: {path}")
    for path in files:
        if path == "wiki/index.md":
            problems.append("wiki/index.md must not be rewritten: give INDEX entries and the operator merges them")
        elif (not WRITABLE.fullmatch(path) or not link_check.canonical_parts(path)
                or Path(path).name in link_check.INSTRUCTIONS):
            problems.append(f"path not writable by the operator: {path}")
        elif (vault / path).is_file() and link_check.canonical_parts(path):
            old = (vault / path).read_text(encoding="utf-8", errors="replace")
            dropped = sorted(set(LINK.findall(old)) - set(LINK.findall(files[path])))
            if dropped:
                problems.append(f"update of {path} drops {len(dropped)} existing link(s) ({', '.join(dropped[:5])}): "
                                "return the whole page with its existing links plus additions")
            old_lines, new_lines = old.count("\n"), files[path].count("\n")
            if old_lines >= 20 and new_lines < old_lines // 2:
                problems.append(f"update of {path} shrinks it from {old_lines} to {new_lines} lines: "
                                "return the whole page, not a summary")
    if not record or not RECORD.fullmatch(record.splitlines()[0].strip()):
        problems.append("log record must start with '## YYYY-MM-DD — operation — partial'")
    elif re.search(r"(?m)^(#{1,2} |<<<)", "\n".join(record.splitlines()[1:])):
        problems.append("log record must be a single record without markers")
    # Only whole-page rewrites need their preimage: the log is appended to, the index merged and LINKS
    # patched against the vault's current content at apply time, so concurrent operations don't collide.
    for path in sorted(files):
        if file_hash(vault / path) != manifest["wiki_preimages"].get(path):
            problems.append(f"vault file changed since staging: {path}")
    return problems


def appended_log(vault, record):
    current = (vault / "wiki/log.md").read_text() if (vault / "wiki/log.md").is_file() else ""
    return current.rstrip("\n") + "\n\n" + record.strip() + "\n"


def first_link(line):
    match = LINK.search(line)
    return match.group(1).strip() if match else None


def merge_index(text, entries, today):
    """Add or replace catalog entries section by section; never removes other entries.

    An entry is [section, line] or [section, line, theme]. A theme files the line
    under a '### theme' heading inside its section. A replacement without a theme
    keeps the existing entry's place; theme headings left empty are dropped.
    """
    lines = text.rstrip("\n").split("\n")
    if lines and lines[0] == "---" and "---" in lines[1:]:
        for i in range(1, lines.index("---", 1)):
            if lines[i].startswith("updated: "):
                lines[i] = f'updated: "{today}"'

    def section_of(position):
        return next((lines[i][3:].strip() for i in range(position, -1, -1) if lines[i].startswith("## ")), None)

    for section_name, entry, *rest in entries:
        theme = rest[0] if rest and rest[0] else None
        target = first_link(entry)
        if not target and entry in lines:
            continue
        existing = [i for i, line in enumerate(lines) if target and line.startswith("- ") and first_link(line) == target]
        if existing and theme is None and section_of(existing[0]) == section_name:
            lines[existing[0]] = entry
            for i in reversed(existing[1:]):
                del lines[i]
            continue
        for i in reversed(existing):
            del lines[i]
        heading = f"## {section_name}"
        if heading not in lines:
            position = lines.index("## Gaps") if "## Gaps" in lines and section_name != "Gaps" else len(lines)
            lines[position:position] = [heading, "", ""]
        start = lines.index(heading)
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        for i in reversed(range(start + 1, end)):
            if re.match(r"\s*No (pages|known gaps) yet", lines[i]):
                del lines[i]
                end -= 1
        if theme:
            sub = f"### {theme}"
            if sub not in lines[start + 1:end]:
                lines[end:end] = ["", sub, "", entry, ""]
                continue
            start = lines.index(sub, start + 1)
        end = next((i for i in range(start + 1, end) if lines[i].startswith("### ")), end)
        items = [i for i in range(start + 1, end) if lines[i].startswith("- ")]
        if items:
            lines.insert(items[-1] + 1, entry)
        else:
            while start + 1 < len(lines) and start + 1 < end and not lines[start + 1].strip():
                del lines[start + 1]
                end -= 1
            lines[start + 1:start + 1] = ["", entry, ""]
    for i in reversed(range(len(lines))):
        if lines[i].startswith("### "):
            following = next((j for j in range(i + 1, len(lines)) if lines[j].startswith("#")), len(lines))
            if not any(line.strip() for line in lines[i + 1:following]):
                del lines[i:following]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).rstrip("\n") + "\n"


def add_links(text, entries, today):
    """Append link lines to a page's '## Links' section (created if absent); skips links already present."""
    lines = text.rstrip("\n").split("\n")
    if lines and lines[0] == "---" and "---" in lines[1:]:
        for i in range(1, lines.index("---", 1)):
            if lines[i].startswith("updated: "):
                lines[i] = f'updated: "{today}"'
    present = set(LINK.findall(text))
    for entry in entries:
        if first_link(entry) in present:
            continue
        present.add(first_link(entry))
        heading = next((i for i, line in enumerate(lines) if re.fullmatch(r"## (Links|Related)", line.strip())), None)
        if heading is None:
            lines += ["", "## Links", "", entry]
            continue
        end = next((i for i in range(heading + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        items = [i for i in range(heading + 1, end) if lines[i].startswith("- ")]
        position = items[-1] + 1 if items else heading + 1
        lines[position:position] = [entry] if items else ["", entry]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).rstrip("\n") + "\n"


IMAGE = re.compile(r"!\[([^\]\n]*)\]\(<?([^)\s>]+)>?\)")
PAGELINK = re.compile(r"(?<![!\[])\[([^\]\n]*)\]\(<?(?![A-Za-z][A-Za-z0-9+.-]*:|#)([^)\s>]+)>?\)")
WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#]+)(#[^\]|]*)?(?:\|([^\]]+))?\]\]")


def normalize(manifest, proposal):
    """Deterministic repairs before checking; every repair is reported, nothing else changes.

    Links for a page that is also rewritten are merged into the rewrite; links to
    pages that do not exist become plain text (outside code); INDEX and LINKS
    entries pointing at missing pages are dropped; a missing or mis-headed log
    record gets an operator heading with status partial.
    """
    proposal = json.loads(json.dumps(proposal))
    files, fixes = proposal["files"], []
    kept = []
    for path, entry in proposal.get("links", []):
        if path in files:
            files[path] = add_links(files[path], [entry], manifest["date"])
            fixes.append(f"merged link to {first_link(entry)} into rewritten {path}")
        else:
            kept.append([path, entry])
    existing = {key[:-3] for key in manifest["wiki_preimages"]} | {key[:-3] for key in files if key.endswith(".md")}

    def missing(target):
        return target.startswith("wiki/") and target not in existing and target not in ("wiki/index", "wiki/log")

    for path, body in files.items():
        out, fence = [], None
        for line in body.split("\n"):
            marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
            if marker and (fence is None or marker.group(1)[0] == fence[0]):
                fence = None if fence else marker.group(1)
            elif fence is None:
                def wikify(match):
                    text, link = match.group(1), urllib.parse.unquote(match.group(2).split("#", 1)[0])
                    link = link[:-3] if link.endswith(".md") else link
                    for target in (posixpath.normpath(link),
                                   posixpath.normpath(posixpath.join(posixpath.dirname(path), link))):
                        if target.startswith("wiki/"):
                            fixes.append(f"converted Markdown link to {target} into a wikilink in {path}")
                            return f"[[{target}|{text}]]" if text else f"[[{target}]]"
                    return match.group(0)
                line = PAGELINK.sub(wikify, line)

                def unlink(match):
                    target = match.group(1).strip()
                    if not missing(target):
                        return match.group(0)
                    fixes.append(f"unlinked missing {target} in {path}")
                    return match.group(3) or target.rsplit("/", 1)[-1]
                line = WIKILINK.sub(unlink, line)

                def unembed(match):
                    alt, link = match.group(1), match.group(2)
                    if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:|#", link):
                        return match.group(0)
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(path), urllib.parse.unquote(link)))
                    if not target.startswith("raw/") or link_check.evidence_target(manifest["vault"], target):
                        return match.group(0)
                    if "raw/raw/" in target and link_check.evidence_target(manifest["vault"], target.replace("raw/raw/", "raw/", 1)):
                        fixes.append(f"corrected doubled raw/ in an image link in {path}")
                        return match.group(0).replace("raw/raw/", "raw/", 1)
                    fixes.append(f"replaced missing image {target} with its caption in {path}")
                    return f"{alt or 'Figure'} (image not rendered)"
                line = IMAGE.sub(unembed, line)
            out.append(line)
        files[path] = "\n".join(out)
    links = []
    for path, entry in kept:
        target = first_link(entry)
        if path[:-3] not in existing or missing(target):
            fixes.append(f"dropped link {path} -> {target} (missing page)")
        else:
            links.append([path, entry])
    # The contract requires source <-> concept/entity links to be reciprocal. For every such link the
    # proposal adds (in a page it writes or a LINKS line), add a missing back-link: into the page when the
    # proposal writes it, otherwise as a LINKS line on the existing page.
    def text_of(key):
        if key + ".md" in files:
            return files[key + ".md"]
        page = Path(manifest["vault"], key + ".md")
        return (page.read_text(encoding="utf-8", errors="replace")
                if link_check.canonical_parts(key + ".md") and page.is_file() else None)

    def kind_of(key):
        return ("source" if key.startswith("wiki/sources/")
                else "concept" if re.match(r"wiki/(concepts|entities)/", key) else None)

    edges = {(path[:-3], target.strip()) for path, body in files.items() for target in LINK.findall(body)}
    edges |= {(path[:-3], first_link(entry)) for path, entry in links}
    for origin, target in sorted(edges):
        body = text_of(target)
        if ({kind_of(origin), kind_of(target)} != {"source", "concept"} or body is None
                or origin in {t.strip() for t in LINK.findall(body)}
                or any(p == target + ".md" and first_link(e) == origin for p, e in links)):
            continue
        title = re.search(r'(?m)^title: "(.*)"$', text_of(origin) or "")
        label = re.sub(r"[|\[\]]", " ", title.group(1) if title else origin.rsplit("/", 1)[-1]).strip()
        entry = (f"- [[{origin}|{label}]] — "
                 + ("source that cites this page" if kind_of(origin) == "source" else "page that cites this source"))
        if target + ".md" in files:
            files[target + ".md"] = add_links(files[target + ".md"], [entry], manifest["date"])
        else:
            links.append([target + ".md", entry])
        fixes.append(f"added the back-link {target} -> {origin}")
    proposal["links"] = links
    index = []
    series = manifest.get("series") or {}
    theme, refile = series.get("theme"), series.get("file_inputs_under")
    inputs = {path[:-3] for path in manifest["inputs"]}
    for section_name, entry, *rest in proposal.get("index", []):
        target = first_link(entry)
        if target and missing(target):
            fixes.append(f"dropped index entry for missing {target}")
            continue
        if refile and target in inputs:
            fixes.append(f"dropped the worker's index entry for input {target}; the operator re-files it")
            continue
        if (theme and section_name == "Sources" and (target or "").startswith("wiki/sources/")
                and target not in inputs and rest[:1] != [theme]):
            rest = [theme]
            fixes.append(f"filed the index entry for {target} under the series theme")
        index.append([section_name, entry, *rest[:1]] if rest and rest[0] else [section_name, entry])
    if refile:
        current = Path(manifest["vault"], "wiki/index.md")
        lines = current.read_text(encoding="utf-8").split("\n") if current.is_file() else []
        heading, sub = None, None
        for line in lines:
            if line.startswith("## "):
                heading, sub = line[3:].strip(), None
            elif line.startswith("### "):
                sub = line[4:].strip()
            elif line.startswith("- ") and first_link(line) in inputs and sub != refile:
                index.append([heading, line, refile])
                fixes.append(f"re-filed the index entry for {first_link(line)} under '{refile}'")
    proposal["index"] = index
    record = (proposal.get("log") or "").strip()
    if files or links:
        heading = f"## {manifest['date']} — {manifest['kind']} {', '.join(manifest['inputs']) or manifest['task'][:60]} — partial"
        first = record.splitlines()[0].strip() if record else ""
        match = re.fullmatch(r"## (\d{4}-\d{2}-\d{2}) — (.+) — (\w+)", first)
        if not record:
            record = heading + "\n- Changed paths: " + ", ".join(sorted({*files, *(p for p, _ in links)})) + "."
            fixes.append("added the missing log record")
        elif not match:
            record = heading + "\n" + "\n".join(line for line in record.splitlines()
                                                 if not line.lstrip().startswith("#"))
            fixes.append("gave the log record an operator heading")
        elif match.group(3) != "partial":
            record = f"## {match.group(1)} — {match.group(2)} — partial" + record[len(first):]
            fixes.append("set the log record status to partial")
        proposal["log"] = record
    return proposal, fixes


def changes_for(manifest, proposal):
    """Every file the proposal writes: pages, the merged index and the appended log."""
    vault = Path(manifest["vault"])
    changes = dict(proposal["files"])
    grouped = {}
    for path, entry in proposal.get("links", []):
        grouped.setdefault(path, []).append(entry)
    for path, entries in grouped.items():
        changes[path] = add_links((vault / path).read_text(), entries, manifest["date"])
    if proposal.get("index"):
        current = (vault / "wiki/index.md").read_text() if (vault / "wiki/index.md").is_file() else "# Index\n"
        changes["wiki/index.md"] = merge_index(current, proposal["index"], manifest["date"])
    changes["wiki/log.md"] = appended_log(vault, proposal["log"])
    return changes


def problem_keys(report):
    """Checker problems as a multiset, without line numbers, which shift when a page is edited."""
    return Counter((d["kind"], d["page"], d.get("target") or d.get("detail", "")) for d in report["errors"] + report["unsupported"])


def new_problems(before, after):
    """Problems in `after` beyond those already in `before`, so existing issues (a hand edit, an older
    page) are reported but never block an operation that doesn't add to them."""
    extra = problem_keys(after) - problem_keys(before)
    found = []
    for d in after["errors"] + after["unsupported"]:
        key = (d["kind"], d["page"], d.get("target") or d.get("detail", ""))
        if extra[key]:
            extra[key] -= 1
            found.append(d)
    return found


def candidate_check(manifest, proposal):
    """Run the managed checker on a copy of the vault's wiki with the proposal applied.

    Only problems the proposal adds count; problems the vault already has are reported as `existing`.
    """
    vault = Path(manifest["vault"])
    before = link_check.check(vault)
    with tempfile.TemporaryDirectory(prefix="sb-candidate-") as tmp:
        root = Path(tmp)
        for key in manifest["wiki_preimages"]:
            (root / key).parent.mkdir(parents=True, exist_ok=True)
            (root / key).write_bytes((vault / key).read_bytes())
        for path, body in changes_for(manifest, proposal).items():
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(body)
        report = link_check.check(root, evidence_root=vault)
    return {"errors": new_problems(before, report), "existing": sum(problem_keys(before).values()),
            "unchecked": len(report["unchecked"]), "pages": report["pages"], "links": len(report["links"])}


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.sb-{secrets.token_hex(4)}")
    with open(temporary, "x", encoding="utf-8") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def apply(op, dry_run=False):
    op = Path(op).resolve()
    manifest = json.loads((op / "manifest.json").read_text())
    if manifest["kind"] == "query":
        raise ValueError("query operations write nothing")
    if not json.loads((op / "run.json").read_text()).get("passed"):
        raise ValueError("the worker run did not pass verification")
    if (op / "receipt.json").exists():
        raise ValueError("operation already applied")
    proposal, fixes = normalize(manifest, json.loads((op / "proposal.json").read_text()))
    vault = Path(manifest["vault"])
    problems = check_proposal(manifest, proposal)
    checker = None if problems else candidate_check(manifest, proposal)
    if checker and checker["errors"]:
        problems += [f"checker: {d['kind']} {d['page']} {d.get('target') or d.get('detail', '')}".strip()
                     for d in checker["errors"]]
    summary = {"operation": manifest["id"], "dry_run": dry_run, "problems": problems, "fixes": fixes,
               "files": [{"path": p, "action": "update" if manifest["wiki_preimages"].get(p) else "create"}
                         for p in sorted(proposal["files"])],
               "index_entries": [f"{item[0]}{' / ' + item[2] if len(item) > 2 else ''}: {first_link(item[1]) or item[1]}"
                                 for item in proposal.get("index", [])],
               "links_added": [f"{path} -> {first_link(entry)}" for path, entry in proposal.get("links", [])],
               "log_record": (proposal["log"] or "").splitlines()[0] if proposal["log"] else None,
               "checker": checker and {k: checker[k] for k in ("pages", "links", "unchecked", "existing")}}
    if problems or dry_run:
        return summary
    before_check = link_check.check(vault)
    backup = op / "backup"
    backup.mkdir(mode=0o700)
    changes = changes_for(manifest, proposal)
    receipt = []
    for path, text in sorted(changes.items()):
        target = vault / path
        before = file_hash(target)
        if before:
            (backup / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup / path)
        atomic_write(target, text)
        receipt.append({"path": path, "before": before, "after": file_hash(target)})
        write_json(op / "receipt.json", {"files": receipt, "complete": False})
    ok = not new_problems(before_check, link_check.check(vault))
    write_json(op / "receipt.json", {"files": receipt, "complete": True, "post_check_clean": ok})
    if not ok:
        undo(op)
        summary["problems"] = ["post-apply checker errors; the operation was undone"]
        return summary
    summary["applied"] = True
    return summary


def undo(op):
    op = Path(op).resolve()
    manifest = json.loads((op / "manifest.json").read_text())
    receipt = json.loads((op / "receipt.json").read_text())
    vault, restored, skipped = Path(manifest["vault"]), [], []
    for entry in reversed(receipt["files"]):
        target = vault / entry["path"]
        if file_hash(target) != entry["after"]:
            skipped.append(entry["path"])
            continue
        if entry["before"] is None:
            target.unlink()
        else:
            atomic_write(target, (op / "backup" / entry["path"]).read_text())
        restored.append(entry["path"])
    write_json(op / "undo.json", {"restored": sorted(restored), "skipped_changed_since": sorted(skipped)})
    return {"restored": sorted(restored), "skipped_changed_since": sorted(skipped)}


ACCEPT_LEVELS = ("technical", "sampled", "full")


def unaccepted(log_text):
    """Partial operation records ('date name') that no owner acceptance record names yet, in log order."""
    records = re.split(r"(?m)^(?=## )", log_text)
    accepted = " ".join(r.lower() for r in records if re.match(r"## .+ — Owner acceptance \(", r))
    found = []
    for record in records:
        match = re.match(r"## (\d{4}-\d{2}-\d{2}) — (.+) — partial\s*$", record.split("\n", 1)[0])
        if match and "owner acceptance" not in match.group(2).lower():
            key = f"{match.group(1)} {match.group(2)}"
            if key.lower() not in accepted:
                found.append(key)
    return found


def accept(vault, level, sample, defects, match=None, config_path=None, dry_run=False, today=None):
    """Append one owner acceptance record naming every unaccepted partial operation (optionally filtered).

    The operator records what the owner states; it never judges content. `technical` keeps the
    operations partial; `sampled` and `full` complete them.
    """
    vault = Path(vault).resolve()
    config = load_config(vault, config_path)
    if level not in ACCEPT_LEVELS:
        raise ValueError(f"level must be one of {', '.join(ACCEPT_LEVELS)}")
    if not sample.strip() or not defects.strip():
        raise ValueError("acceptance needs --sample (pages reviewed, or 'not itemized') and --defects ('none' or a list)")
    log = vault / "wiki/log.md"
    text = log.read_text(encoding="utf-8")
    operations = [key for key in unaccepted(text) if not match or re.search(match, key, re.I)]
    if not operations:
        raise ValueError("no unaccepted partial operations match")
    status = "partial" if level == "technical" else "completed"
    today = today or date.today().isoformat()
    record = "\n".join([f"## {today} — Owner acceptance ({level}) — {status}", "- Accepted operations:",
                         *[f"  - {key}" for key in operations],
                         f"- Sample: {sample.strip()}.".replace("..", "."),
                         f"- Defects: {defects.strip()}.".replace("..", "."),
                         f"- Result: {len(operations)} operation(s) " + (
                             "remain partial; technical acceptance does not complete them." if level == "technical"
                             else f"are completed at the `{level}` acceptance level.")])
    summary = {"level": level, "status": status, "operations": len(operations), "first": operations[0],
               "last": operations[-1], "record_heading": record.split("\n", 1)[0], "dry_run": dry_run}
    if dry_run:
        return summary
    backup = Path(config["workdir"]) / f"accept-{datetime.now():%Y%m%d-%H%M%S}-log.md"
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(log, backup)
    before_check = link_check.check(vault)
    atomic_write(log, text.rstrip("\n") + "\n\n" + record + "\n")
    if new_problems(before_check, link_check.check(vault)):
        atomic_write(log, text)
        raise ValueError("the checker failed after appending; the log was restored")
    return {**summary, "backup": str(backup)}


def natural_key(text):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text)]


def raw_sources(vault):
    """{raw path: source page} for every adopted source page."""
    pages, _ = link_check.collect(vault)
    return {page["metadata"].get("raw"): key for key, page in pages.items()
            if key.startswith("wiki/sources/") and isinstance(page["metadata"].get("raw"), str)}


def series_step(vault, item, task, config_path, info, emit, kind="ingest", inputs=None):
    """Stage, run, repair and apply one item with the fixed retry policy; returns its result line."""
    line = {"input": item, "position": info["position"], "count": info["count"], "retries": []}
    op = None
    for attempt in (1, 2):
        op = stage(vault, kind, inputs or [item], task, config_path, series=info)
        result = run(op)
        if not result["passed"] and result.get("proposal_error"):
            line["retries"].append(f"format: {result['proposal_error']}")
            result = revise(op)
            # A format-only revision restates the previous reply; if that reply held no proposal (for
            # example the worker ran out of steps), NOTES alone are a failed run, not a no-op.
            if result["passed"] and not result.get("proposed_files") and not result.get("proposed_links"):
                result = {**result, "passed": False, "proposal_error": "the format revision found no proposal to restate"}
        if result["passed"]:
            break
        line["retries"].append("run failed: " + ", ".join(k for k, ok in result.get("checks", {}).items() if not ok)
                               + (f" (not read in full: {', '.join(result['unread_required'])})"
                                  if result.get("unread_required") else "")
                               + (f" ({result['proposal_error']})" if result.get("proposal_error") else ""))
        op = None
    line["operation"] = str(op) if op else None
    if op is None:
        return {**line, "status": "stopped", "reason": "the worker failed twice: " + " | ".join(line["retries"])[:500]}
    proposal = json.loads((op / "proposal.json").read_text())
    if not proposal["files"] and not proposal["links"]:
        return {**line, "status": "no change", "notes": proposal["notes"][:300]}
    summary = apply(op, dry_run=True)
    if summary["problems"]:
        line["retries"].append("checks: " + "; ".join(summary["problems"])[:300])
        try:
            if not revise(op)["passed"]:
                return {**line, "status": "stopped", "reason": "the revision failed its run checks"}
        except ValueError as error:
            return {**line, "status": "stopped", "reason": str(error)}
        proposal = json.loads((op / "proposal.json").read_text())
        if not proposal["files"] and not proposal["links"]:
            return {**line, "status": "no change", "notes": proposal["notes"][:300]}
        summary = apply(op, dry_run=True)
        if summary["problems"]:
            return {**line, "status": "stopped", "reason": "; ".join(summary["problems"])[:500]}
    applied = apply(op)
    if not applied.get("applied"):
        return {**line, "status": "stopped", "reason": "; ".join(applied["problems"])[:500]}
    return {**line, "status": "applied", "files": [f["path"] for f in applied["files"]],
            "fixes": applied["fixes"], "checker": applied["checker"]}


def series_theme(vault, inputs, theme=None):
    """The index theme for a series: the given one, else the first capture's title; None when neither is usable."""
    if theme is None and inputs and (vault / inputs[0]).is_file():
        theme = capture_fields(vault / inputs[0]).get("title")
    if not isinstance(theme, str):
        return None
    theme = re.sub(r"\s+", " ", re.sub(r"[|\[\]#]", " ", theme)).strip()[:100]
    return theme or None


def load_plan(vault, path):
    """A series plan: {"theme"?, "items": [{"kind", "inputs", "task", "done_if"?, "file_inputs_under"?}]}."""
    plan = json.loads(Path(path).read_text(encoding="utf-8"))
    items = plan.get("items") if isinstance(plan, dict) else None
    if not items or set(plan) - {"theme", "items"}:
        raise ValueError("a plan is {\"theme\": optional, \"items\": [...]}")
    for item in items:
        if (not isinstance(item, dict) or item.get("kind") not in ("ingest", "compile")
                or set(item) - {"kind", "inputs", "task", "done_if", "file_inputs_under"}
                or not isinstance(item.get("task"), str) or not isinstance(item.get("inputs", []), list)):
            raise ValueError("each plan item needs kind (ingest|compile), task, and optional inputs, done_if, "
                             "file_inputs_under")
        done_if = item.get("done_if")
        if done_if is not None and not (WRITABLE.fullmatch(done_if) and link_check.canonical_parts(done_if)):
            raise ValueError(f"done_if must be a wiki page path: {done_if}")
        if item.get("file_inputs_under") is not None and item["kind"] != "compile":
            raise ValueError("file_inputs_under applies to compile items")
    return plan


def series(vault, inputs, task, config_path=None, sources_only=True, limit=None, emit=None, theme=None, plan=None):
    """Run items in order, one operation each, and resume on rerun.

    Without a plan, each input is an ingest, skipped once a source page cites it.
    A plan's items may also be compiles, skipped once their done_if page exists.
    """
    vault = Path(vault).resolve()
    config = load_config(vault, config_path)
    if plan is not None:
        theme = series_theme(vault, [], plan.get("theme"))
        items = [dict(item, label=item.get("done_if") or item["task"][:80]) for item in plan["items"]]
    else:
        theme = series_theme(vault, inputs, theme)
        items = [{"kind": "ingest", "inputs": [item], "label": item, "task": task or "Ingest {input}"}
                 for item in inputs]
    emit = emit or (lambda line: print(json.dumps(line, ensure_ascii=False), flush=True))
    lock = Path(config["workdir"]) / "series.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    if lock.exists():
        try:
            os.kill(int(lock.read_text()), 0)
            raise ValueError("another series is running on this workdir")
        except (ProcessLookupError, ValueError) as error:
            if "another series" in str(error):
                raise
    lock.write_text(str(os.getpid()))
    try:
        done, counts = raw_sources(vault), {"applied": 0, "no change": 0, "skipped": 0}
        for position, entry in enumerate(items, 1):
            item = entry["label"]
            if (entry.get("done_if") and (vault / entry["done_if"]).is_file()) or (
                    plan is None and item in done):
                counts["skipped"] += 1
                continue
            if limit is not None and counts["applied"] + counts["no change"] >= limit:
                return {"status": "paused", "next": item, **counts}
            previous = items[position - 2]["inputs"][0] if position > 1 and entry["kind"] == "ingest" and \
                items[position - 2]["kind"] == "ingest" else None
            info = {"position": position, "count": len(items), "theme": theme,
                    "sources_only": sources_only and entry["kind"] == "ingest" and plan is None,
                    "file_inputs_under": entry.get("file_inputs_under"),
                    "previous_source": raw_sources(vault).get(previous) if previous else None}
            declined = []
            for attempt in (1, 2):
                try:
                    line = series_step(vault, item, entry["task"].format(
                        input=item, position=position, count=len(items)), config_path, info, emit,
                        kind=entry["kind"], inputs=entry.get("inputs") or None)
                except (ValueError, RuntimeError, subprocess.SubprocessError, KeyError, IndexError) as error:
                    line = {"input": item, "position": position, "status": "stopped", "reason": str(error)}
                # A plan item that declines without creating its page gets one fresh operation.
                if not (line["status"] == "no change" and entry.get("done_if")
                        and not (vault / entry["done_if"]).is_file()):
                    break
                declined.append((line.get("notes") or "")[:300])
                line = {**line, "status": "stopped",
                        "reason": f"{entry['done_if']} was not created: " + " | ".join(declined)}
            if declined and line["status"] != "stopped":
                line["retries"] = line.get("retries", []) + [f"declined: {note}" for note in declined]
            emit(line)
            if line["status"] == "stopped":
                return {"status": "stopped", "stopped_at": item, "reason": line["reason"], **counts}
            counts[line["status"]] += 1
        return {"status": "completed", **counts}
    finally:
        lock.unlink(missing_ok=True)


def series_status(vault, config_path=None):
    """Progress of the most recent background series."""
    config = load_config(Path(vault).resolve(), config_path)
    logs = sorted(Path(config["workdir"]).glob("series-*.jsonl"))
    if not logs:
        return {"status": "none"}
    lines = []
    for line in logs[-1].read_text().splitlines():
        try:
            parsed = json.loads(line)
        except ValueError:
            continue  # progress lines only; tolerate stray output
        if isinstance(parsed, dict):
            lines.append(parsed)
    pid_file = logs[-1].with_suffix(".pid")
    running = False
    if pid_file.exists():
        try:
            os.kill(int(pid_file.read_text()), 0)
            running = True
        except ProcessLookupError:
            pass
    final = next((line for line in reversed(lines) if line.get("status") in ("completed", "stopped", "paused")
                  and "input" not in line), None)
    items = [line for line in lines if "input" in line]
    return {"log": str(logs[-1]), "running": running, "done": len(items),
            "applied": sum(line["status"] == "applied" for line in items),
            "no_change": sum(line["status"] == "no change" for line in items),
            "last": items[-1] if items else None, "result": final}


def status(op):
    op = Path(op).resolve()
    manifest = json.loads((op / "manifest.json").read_text())
    stages = [name for name in ("run.json", "proposal.json", "receipt.json", "undo.json") if (op / name).exists()]
    result = {"operation": manifest["id"], "kind": manifest["kind"], "task": manifest["task"],
              "inputs": manifest["inputs"], "stages": stages}
    if (op / "run.json").exists():
        result["run"] = json.loads((op / "run.json").read_text())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    staging = commands.add_parser("stage", help="copy an operation's inputs outside the vault")
    staging.add_argument("vault", type=Path)
    staging.add_argument("kind", choices=sorted(ROLES))
    staging.add_argument("--input", action="append", default=[], help="raw/ capture (ingest) or source note (compile)")
    staging.add_argument("--task", help="what to ingest or compile")
    staging.add_argument("--question", help="query question")
    staging.add_argument("--url", help="ingest: capture this URL into raw/ first")
    staging.add_argument("--config", type=Path, help="operator config (default: VAULT/.opencode/second-brain/operator.json)")
    capturing = commands.add_parser("capture", help="capture a URL, or extract a raw/ PDF, into raw/ without a model")
    capturing.add_argument("vault", type=Path)
    capturing.add_argument("url")
    capturing.add_argument("--config", type=Path)
    commands.add_parser("pending", help="list raw/ captures without a source page").add_argument("vault", type=Path)
    running = commands.add_parser("series", help="ingest many inputs in order, one operation each, resumable")
    running.add_argument("vault", type=Path)
    running.add_argument("--input", action="append", default=[], help="input in order (repeatable)")
    running.add_argument("--glob", help="raw/ glob added in natural order, e.g. 'raw/book-part-*.md'")
    running.add_argument("--task", help="task template; {input}, {position} and {count} are filled in")
    running.add_argument("--with-concepts", action="store_true", help="let each item create or update concepts")
    running.add_argument("--theme", help="index theme for the items' source entries (default: the capture title)")
    running.add_argument("--plan", type=Path, help="JSON plan of ingest/compile items, run in order (replaces --input)")
    running.add_argument("--limit", type=int, help="stop after this many items (rerun to continue)")
    running.add_argument("--background", action="store_true", help="run detached; check with series-status")
    running.add_argument("--config", type=Path)
    running.add_argument("--log", type=Path, help=argparse.SUPPRESS)
    commands.add_parser("series-status", help="progress of the latest background series").add_argument("vault", type=Path)
    accepting = commands.add_parser("accept", help="append the owner's acceptance record for partial operations")
    accepting.add_argument("vault", type=Path)
    accepting.add_argument("--level", required=True, choices=ACCEPT_LEVELS)
    accepting.add_argument("--sample", required=True, help="pages the owner reviewed, or 'not itemized'")
    accepting.add_argument("--defects", required=True, help="'none' or the defects found")
    accepting.add_argument("--match", help="only operations whose 'date name' matches this regex")
    accepting.add_argument("--dry-run", action="store_true")
    accepting.add_argument("--config", type=Path)
    for name, text in (("run", "run the worker on a staged operation"), ("status", "show an operation's stage"),
                       ("revise", "rerun the worker once with the dry-run problems as feedback"),
                       ("undo", "restore files an applied operation changed")):
        commands.add_parser(name, help=text).add_argument("operation", type=Path)
    applying = commands.add_parser("apply", help="validate and write a proposal into the vault")
    applying.add_argument("operation", type=Path)
    applying.add_argument("--dry-run", action="store_true", help="validate and check without writing")
    args = parser.parse_args()
    try:
        if args.command == "stage":
            if args.kind == "query" and args.task:
                parser.error("query uses --question, not --task")
            operation = stage(args.vault, args.kind, args.input,
                              args.question if args.kind == "query" else args.task, args.config, url=args.url)
            result = {"operation": str(operation)}
            captured = json.loads((operation / "manifest.json").read_text()).get("capture")
            if captured:
                result["capture"] = captured
        elif args.command == "capture":
            if args.url.startswith("raw/") and args.url.lower().endswith(".pdf"):
                load_config(args.vault.resolve(), args.config)
                result = capture_pdf(args.vault, args.url)
            else:
                result = capture(args.vault, args.url, args.config)
        elif args.command == "pending":
            result = {"pending": pending(args.vault)}
        elif args.command == "accept":
            result = accept(args.vault, args.level, args.sample, args.defects, args.match, args.config, args.dry_run)
        elif args.command == "series-status":
            result = series_status(args.vault)
        elif args.command == "series":
            vault = args.vault.resolve()
            inputs = list(args.input)
            if args.glob:
                if not args.glob.startswith("raw/") or ".." in args.glob:
                    raise ValueError("--glob must stay under raw/")
                inputs += sorted((p.relative_to(vault).as_posix() for p in vault.glob(args.glob)
                                  if p.is_file() and p.suffix == ".md"), key=natural_key)
            inputs = list(dict.fromkeys(inputs))
            plan = load_plan(vault, args.plan) if args.plan else None
            if bool(plan) == bool(inputs):
                raise ValueError("series needs --input/--glob or --plan, not both")
            if args.background:
                config = load_config(vault, args.config)
                log = Path(config["workdir"]) / f"series-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
                log.parent.mkdir(parents=True, exist_ok=True)
                command = [sys.executable, str(Path(__file__).resolve()), "series", str(vault), "--log", str(log)]
                command += [f"--input={item}" for item in inputs]
                command += [f"--plan={args.plan.resolve()}"] if args.plan else []
                command += [f"--task={args.task}"] if args.task else []
                command += ["--with-concepts"] if args.with_concepts else []
                command += [f"--theme={args.theme}"] if args.theme else []
                command += [f"--limit={args.limit}"] if args.limit else []
                command += [f"--config={args.config}"] if args.config else []
                with open(log, "a") as stream:
                    process = subprocess.Popen(command, cwd=vault, stdout=stream, stderr=subprocess.STDOUT,
                                               stdin=subprocess.DEVNULL, start_new_session=True)
                log.with_suffix(".pid").write_text(str(process.pid))
                result = {"series": "started in background", "items": len(plan["items"]) if plan else len(inputs),
                          "log": str(log),
                          "check": f"python3 {Path(__file__).resolve()} series-status ."}
            else:
                result = series(vault, inputs, args.task, args.config, not args.with_concepts, args.limit,
                                theme=args.theme, plan=plan)
        elif args.command == "run":
            result = run(args.operation)
            if json.loads((args.operation / "manifest.json").read_text())["kind"] == "query":
                result["answer"] = str(args.operation / "response.md")
        elif args.command == "apply":
            result = apply(args.operation, args.dry_run)
        else:
            result = {"status": status, "undo": undo, "revise": revise}[args.command](args.operation)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error) if isinstance(error, (ValueError, RuntimeError)) else type(error).__name__}))
        return 2
    # A background series logs one JSON object per line, so series-status can read its final result.
    background = args.command == "series" and getattr(args, "log", None)
    print(json.dumps(result, ensure_ascii=False) if background else json.dumps(result, indent=2, ensure_ascii=False))
    failed = (result.get("passed") is False or result.get("problems") or result.get("skipped_changed_since")
              or result.get("status") == "stopped")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
