"""Offline PDF capture checks with generated PDFs; skipped without Poppler (and OCR tools)."""

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts import pdf_capture
from scripts import sb_operator as op


POPPLER = shutil.which("pdftotext") and shutil.which("pdfinfo")


def make_pdf(pages, title="Invented Study of Vent Timing", author="Ada Example"):
    """Minimal text PDF: one Helvetica text line per list item, one page per inner list."""
    objects = ["<< /Type /Catalog /Pages 2 0 R >>", None, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    kids = []
    for lines in pages:
        stream = "BT /F1 11 Tf 50 780 Td 14 TL " + " ".join(
            "(" + line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") Tj T*" for line in lines) + " ET"
        objects.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] "
                       f"/Resources << /Font << /F1 3 0 R >> >> /Contents {len(objects)} 0 R >>")
        kids.append(len(objects))
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(f'{k} 0 R' for k in kids)}] /Count {len(kids)} >>"
    objects.append(f"<< /Title ({title}) /Author ({author}) /CreationDate (D:20260920120000Z) >>")
    out, offsets = b"%PDF-1.4\n", []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n{body}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets).encode()
    out += (f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R /Info {len(objects)} 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n").encode()
    return out


SENTENCE = "The invented trial measured crust colour after preheating the stone for a stated time"
PAGE = [f"{SENTENCE} in run {i}." for i in range(40)]


@unittest.skipUnless(POPPLER, "Poppler pdftotext/pdfinfo not installed")
class PdfCaptureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.vault = base / "vault"
        (self.vault / "raw").mkdir(parents=True)
        (self.vault / "wiki").mkdir()
        self.config = base / "operator.json"
        self.config.write_text(json.dumps({"agent": "a", "model": "p/m", "opencode_version": "0",
                                           "workdir": str(base / "ops")}))

    def tearDown(self):
        self.tmp.cleanup()

    def fields(self, relative):
        header = (self.vault / relative).read_text().split("---\n\n", 1)[0]
        return {line.split(": ", 1)[0]: json.loads(line.split(": ", 1)[1]) for line in header.splitlines()[1:]}

    def test_url_pdf_keeps_original_and_marks_pages(self):
        data = make_pdf([PAGE, PAGE[:20]])
        result = op.capture(self.vault, "https://example.com/files/study.pdf", self.config, "2026-09-29",
                            lambda url: (data, "application/pdf", url, None))
        self.assertEqual(result["pdf"], "raw/2026-09-29-invented-study-of-vent-timing.pdf")
        self.assertEqual((self.vault / result["pdf"]).read_bytes(), data)
        self.assertEqual(result["parts"], ["raw/2026-09-29-invented-study-of-vent-timing.md"])
        body = (self.vault / result["raw"]).read_text()
        self.assertIn("## Page 1\n", body)
        self.assertIn("## Page 2\n", body)
        self.assertIn(f"{SENTENCE} in run 39.", body)
        fields = self.fields(result["raw"])
        self.assertEqual((fields["url"], fields["source_pdf"], fields["pages"], fields["page_range"], fields["part"]),
                         ("https://example.com/files/study.pdf", result["pdf"], 2, "1-2", None))
        self.assertEqual((fields["title"], fields["author"], fields["published"], fields["pdf_created"], fields["ocr"]),
                         ("Invented Study of Vent Timing", "Ada Example", None, "2026-09-20", False))
        self.assertEqual(fields["pdf_sha256"], op.file_hash(self.vault / result["pdf"]))

    def test_long_pdf_splits_on_page_boundaries(self):
        pdf = self.vault / "raw/long.pdf"
        pdf.write_bytes(make_pdf([PAGE] * 60))
        result = op.capture_pdf(self.vault, "raw/long.pdf")
        self.assertGreater(len(result["parts"]), 1)
        ranges = [self.fields(part)["page_range"] for part in result["parts"]]
        self.assertEqual(ranges[0].split("-")[0], "1")
        self.assertEqual(ranges[-1].split("-")[1], "60")
        for part in result["parts"]:
            body = (self.vault / part).read_text().split("---\n\n", 1)[1]
            self.assertLessEqual(body.count("\n"), pdf_capture.MAX_PART_LINES)
            self.assertLessEqual(len(body.encode()), pdf_capture.MAX_PART_BYTES)
        self.assertEqual(self.fields(result["parts"][1])["part"], f"2/{len(result['parts'])}")

    def test_quality_check_and_refusals(self):
        metrics, problems = pdf_capture.quality(["a\nb\nc\n" * 200])
        self.assertTrue(any("interleaved" in p for p in problems))
        self.assertEqual(pdf_capture.quality(["\n".join(PAGE)])[1], [])
        (self.vault / "raw/broken.pdf").write_bytes(b"%PDF-1.4 not really")
        with self.assertRaisesRegex(ValueError, "pdfinfo"):
            op.capture_pdf(self.vault, "raw/broken.pdf")
        data = make_pdf([["x"] * 5])
        if not shutil.which("ocrmypdf"):
            with self.assertRaisesRegex(ValueError, "no text layer"):
                op.capture(self.vault, "https://example.com/tiny.pdf", self.config, "2026-09-29",
                           lambda url: (data, "application/pdf", url, None))
            self.assertEqual(sorted(p.name for p in (self.vault / "raw").iterdir()), ["broken.pdf"])

    def test_pending_and_stage_for_dropped_pdfs(self):
        (self.vault / "raw/dropped.pdf").write_bytes(make_pdf([PAGE]))
        self.assertEqual(op.pending(self.vault), ["raw/dropped.pdf"])
        with self.assertRaisesRegex(ValueError, "task"):
            op.stage(self.vault, "ingest", ["raw/dropped.pdf"], None, self.config)
        operation = op.stage(self.vault, "ingest", ["raw/dropped.pdf"], "Ingest the study", self.config, "2026-09-29")
        manifest = json.loads((operation / "manifest.json").read_text())
        self.assertEqual(manifest["inputs"], ["raw/dropped.md"])
        self.assertEqual(manifest["capture"]["pdf"], "raw/dropped.pdf")
        self.assertEqual(op.pending(self.vault), ["raw/dropped.md"])  # extracted text awaits ingest
        with self.assertRaisesRegex(ValueError, "one PDF"):
            op.stage(self.vault, "ingest", ["raw/dropped.pdf", "raw/dropped.md"], "t", self.config)

    def test_figure_pages_rendered_linked_and_staged(self):
        pages = [PAGE, PAGE[:30] + ["Figure 1: Invented chart of crust time against preheat minutes."],
                 PAGE[:30] + ["Fig. 2. Invented diagram of the oven.", "As Figure 1 shows, times fall."], PAGE[:30]]
        (self.vault / "raw/study.pdf").write_bytes(make_pdf(pages))
        result = op.capture_pdf(self.vault, "raw/study.pdf")
        self.assertEqual((result["figure_pages"], result["figure_pages_not_rendered"]), ([2, 3], []))
        for page in ("02", "03"):
            self.assertTrue((self.vault / f"raw/assets/study/page-{page}.png").read_bytes().startswith(b"\x89PNG"))
        body = (self.vault / result["raw"]).read_text()
        self.assertIn("![Figure 1 (page 2)](assets/study/page-02.png)", body)
        self.assertIn("![Figure 2 (page 3)](assets/study/page-03.png)", body)
        self.assertEqual(self.fields(result["raw"])["figures"],
                         [{"page": 2, "figures": ["1"], "image": "raw/assets/study/page-02.png"},
                          {"page": 3, "figures": ["2"], "image": "raw/assets/study/page-03.png"}])
        operation = op.stage(self.vault, "ingest", [result["raw"]], "Ingest the study", self.config, "2026-09-29")
        manifest = json.loads((operation / "manifest.json").read_text())
        self.assertEqual(manifest["figures"], ["raw/assets/study/page-02.png", "raw/assets/study/page-03.png"])
        self.assertIn("raw/assets/study/page-02.png", manifest["reads"])
        self.assertTrue((operation / "corpus/raw/assets/study/page-02.png").is_file())
        self.assertIn("raw/assets/study/page-03.png", op.worker_prompt(manifest, operation / "corpus"))
        with self.assertRaisesRegex(ValueError, "figure directory already exists"):
            op.capture_pdf(self.vault, "raw/study.pdf")

    def test_figure_page_cap_and_caption_rule(self):
        self.assertEqual(pdf_capture.figure_pages(["see Figure 3 below", "Figure 3: x", "  Fig. 4b: y\nFigure 5. z"]),
                         {2: ["3"], 3: ["4b", "5"]})
        pages = [PAGE[:20] + [f"Figure {i}: invented plot {i}."] for i in range(1, 16)]
        (self.vault / "raw/many.pdf").write_bytes(make_pdf(pages))
        result = op.capture_pdf(self.vault, "raw/many.pdf")
        self.assertEqual(len(result["figure_pages"]), pdf_capture.MAX_FIGURE_PAGES)
        self.assertEqual(result["figure_pages_not_rendered"], [13, 14, 15])

    @unittest.skipUnless(shutil.which("ocrmypdf") and shutil.which("tesseract"), "OCR tools not installed")
    def test_scanned_pdf_is_ocrd(self):
        from PIL import Image, ImageDraw, ImageFont
        image = Image.new("L", (1700, 2200), 255)
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 34)
        except OSError:
            font = ImageFont.load_default(size=34)
        for i in range(40):
            draw.text((80, 80 + i * 50), f"The invented scan reports trial {i} took twenty minutes.", fill=0, font=font)
        path = self.vault / "raw/scan.pdf"
        image.save(path, "PDF", resolution=200)
        result = op.capture_pdf(self.vault, "raw/scan.pdf")
        fields = self.fields(result["raw"])
        self.assertTrue(fields["ocr"])
        self.assertIn("ocrmypdf", fields["extracted_with"])
        self.assertIn("twenty minutes", (self.vault / result["raw"]).read_text())
        self.assertEqual(op.file_hash(path), fields["pdf_sha256"])  # original kept unchanged


if __name__ == "__main__":
    unittest.main()
