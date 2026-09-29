"""Turn a PDF into page-marked Markdown with a quality check; no model involved.

Uses Poppler's `pdftotext`/`pdfinfo` and, for scans without a text layer,
`ocrmypdf` (Tesseract) when installed. Text is extracted in reading order
first, with `-layout` as a fallback when the quality check fails. Every page
becomes a `## Page N` section so claims can cite page numbers. Long documents
are split on page boundaries into parts a worker can read in one pass.
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


MIN_WORDS = 150
MAX_PART_LINES = 1850


def info(path):
    """Title, author, date and page count from pdfinfo; unknown values are None."""
    result = subprocess.run(["pdfinfo", "-isodates", "-enc", "UTF-8", str(path)],
                            capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise ValueError("pdfinfo could not read the PDF (damaged or encrypted?)")
    fields = dict(line.split(":", 1) for line in result.stdout.splitlines() if ":" in line)
    fields = {key.strip(): value.strip() for key, value in fields.items()}
    date = re.search(r"(\d{4})-?(\d{2})-?(\d{2})", fields.get("CreationDate", "")) if fields.get("CreationDate") else None
    title = fields.get("Title") or None
    if title and re.fullmatch(r"(untitled|microsoft word - .*|.*\.(docx?|pdf|tex))", title, re.I):
        title = None
    # CreationDate is when the file was made, not when the work was published.
    return {"title": title, "author": fields.get("Author") or None, "published": None,
            "pdf_created": "-".join(date.groups()) if date else None, "pages": int(fields.get("Pages", "0") or 0),
            "encrypted": fields.get("Encrypted", "no").startswith("yes")}


def pages(path, layout=False):
    command = ["pdftotext", "-enc", "UTF-8", *(["-layout"] if layout else []), str(path), "-"]
    result = subprocess.run(command, capture_output=True, text=True, timeout=300)
    if result.returncode:
        raise ValueError("pdftotext could not extract the PDF")
    parts = result.stdout.split("\f")
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return [part.rstrip() for part in parts]


def quality(texts):
    """Heuristics for extraction garbage: interleaved columns, broken encoding, no text layer."""
    text = "\n".join(texts)
    words = len(text.split())
    lines = [line for line in text.splitlines() if line.strip()]
    visible = [ch for ch in text if not ch.isspace()]
    letters = sum(ch.isalpha() for ch in visible)
    metrics = {
        "words": words,
        "short_line_ratio": round(sum(len(line.strip()) <= 3 for line in lines) / len(lines), 3) if lines else 1.0,
        "letter_ratio": round(letters / len(visible), 3) if visible else 0.0,
        "replacement_chars": text.count("�"),
    }
    problems = []
    if words < MIN_WORDS:
        problems.append(f"only {words} words of text")
    if metrics["short_line_ratio"] > 0.35:
        problems.append("many one-to-three-character lines (columns or tables may be interleaved)")
    if metrics["letter_ratio"] < 0.6:
        problems.append("low share of letters (encoding or extraction failure)")
    if metrics["replacement_chars"] > max(5, len(visible) // 200):
        problems.append("many unreadable characters (missing font encoding)")
    return metrics, problems


def extract(path):
    """Best extraction of `path`: reading order, then layout, then OCR for scans.

    Returns (page texts, metadata including mode, ocr and quality metrics).
    """
    meta = info(path)
    if meta["encrypted"]:
        raise ValueError("the PDF is encrypted; save a decrypted copy into raw/ instead")
    attempts = []
    for mode in ("reading order", "layout"):
        texts = pages(path, layout=mode == "layout")
        metrics, problems = quality(texts)
        attempts.append((mode, texts, metrics, problems))
        if not problems:
            return texts, {**meta, "mode": mode, "ocr": False, "quality": metrics}
    if attempts[0][2]["words"] < MIN_WORDS:
        if not shutil.which("ocrmypdf"):
            raise ValueError("the PDF has no text layer (a scan) and ocrmypdf is not installed")
        with tempfile.TemporaryDirectory(prefix="sb-ocr-") as tmp:
            output = Path(tmp) / "ocr.pdf"
            result = subprocess.run(["ocrmypdf", "--skip-text", "--quiet", "-l", "eng", str(path), str(output)],
                                    capture_output=True, text=True, timeout=1800)
            if result.returncode or not output.is_file():
                raise ValueError("OCR failed on the scanned PDF")
            texts = pages(output)
        metrics, problems = quality(texts)
        if not problems:
            return texts, {**meta, "mode": "ocrmypdf + reading order", "ocr": True, "quality": metrics}
        raise ValueError("OCR text failed the quality check: " + "; ".join(problems))
    mode, texts, metrics, problems = attempts[0]
    raise ValueError("extraction failed the quality check: " + "; ".join(problems)
                     + ". Try exporting the document from its source, or a tool such as Zotero, into raw/")


def split(texts):
    """Page-marked Markdown parts, each within one full read; returns [(first, last, body)]."""
    parts, current, first, size = [], [], 1, 0
    for number, text in enumerate(texts, 1):
        section = f"## Page {number}\n\n{text.strip() or '(no text on this page)'}\n"
        lines = section.count("\n") + 1
        if lines > MAX_PART_LINES:
            raise ValueError(f"page {number} alone is longer than one full read")
        if current and size + lines > MAX_PART_LINES:
            parts.append((first, number - 1, "\n".join(current)))
            current, first, size = [], number, 0
        current.append(section)
        size += lines
    if current:
        parts.append((first, len(texts), "\n".join(current)))
    return parts
