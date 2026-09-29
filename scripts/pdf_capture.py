"""Turn a PDF into page-marked Markdown with a quality check; no model involved.

Uses Poppler's `pdftotext`/`pdfinfo`/`pdftoppm` and, for scans without a text layer,
`ocrmypdf` (Tesseract) when installed. Text is extracted in reading order
first, with `-layout` as a fallback when the quality check fails. Every page
becomes a `## Page N` section so claims can cite page numbers. Long documents
are split on page boundaries into parts a worker can read in one pass.
Pages whose text carries a figure caption are rendered to PNG, so figures
(embedded images and vector charts alike) survive as images a person can see
and a vision-capable worker can read.
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


MIN_WORDS = 150
MAX_PART_LINES = 1850
FIGURES_PER_PART = 6  # figure budget per part, so long books keep figures throughout
FIGURE_DPI = 110
CAPTION = re.compile(r"(?m)^\s*(?:Figure|Fig\.)\s*(\d+[A-Za-z]?)\s*[.:|]")


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


MAX_PART_BYTES = 42_000  # OpenCode's read output (with line-number prefixes) truncates above about 50 KB
LINE_PREFIX_BYTES = 8     # "00123| " per line in the read tool's output


def fits(text):
    lines = text.count("\n") + 1
    return lines <= MAX_PART_LINES and len(text.encode()) + LINE_PREFIX_BYTES * lines <= MAX_PART_BYTES


def pack(blocks):
    """Group consecutive blocks into parts that each fit one full read; returns [(first, last, text)] (0-based)."""
    parts, current, first = [], [], 0
    for index, block in enumerate(blocks):
        if not fits(block):
            raise ValueError(f"block {index + 1} alone is longer than one full read")
        if current and not fits("\n".join(current + [block])):
            parts.append((first, index - 1, "\n".join(current)))
            current, first = [], index
        current.append(block)
    if current:
        parts.append((first, len(blocks) - 1, "\n".join(current)))
    return parts


def split(texts):
    """Page-marked Markdown parts, each within one full read; returns [(first page, last page, body)]."""
    sections = [f"## Page {n}\n\n{text.strip() or '(no text on this page)'}\n" for n, text in enumerate(texts, 1)]
    try:
        return [(first + 1, last + 1, body) for first, last, body in pack(sections)]
    except ValueError as error:
        raise ValueError(str(error).replace("block", "page")) from None


def figure_pages(texts):
    """{page: [figure numbers]} for pages with a figure caption, in page order."""
    found = {}
    for number, text in enumerate(texts, 1):
        labels = list(dict.fromkeys(CAPTION.findall(text)))
        if labels:
            found[number] = labels
    return found


def render_figures(path, pages, labels, directory, total_pages):
    """Render the chosen caption pages to directory/page-NN.png; returns {page: (labels, file)}."""
    rendered = {}
    if pages:
        directory.mkdir(parents=True, exist_ok=True)
    width = max(2, len(str(total_pages)))
    for page in pages:
        target = directory / f"page-{page:0{width}d}"
        result = subprocess.run(["pdftoppm", "-r", str(FIGURE_DPI), "-png", "-singlefile", "-f", str(page),
                                 "-l", str(page), str(path), str(target)], capture_output=True, timeout=120)
        if result.returncode == 0 and target.with_suffix(".png").is_file():
            rendered[page] = (labels[page], target.with_suffix(".png"))
    return rendered
