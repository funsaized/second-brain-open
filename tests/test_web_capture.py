"""Offline capture checks: extraction, provenance, refusals and pending detection."""

import json
from pathlib import Path
import tempfile
import unittest

from scripts import sb_operator as op
from scripts import web_capture


ROOT = Path(__file__).resolve().parents[1]
WORDS = " ".join(f"word{i}" for i in range(200))
PAGE = f"""<!doctype html><html><head><title>Fallback title</title>
<meta property="og:title" content="Invented Article">
<meta name="author" content="Ada Example"><meta name="fb:app_id" content="1234">
<meta property="article:published_time" content="2026-09-20T10:00:00Z">
<script>var tracking = 1;</script></head><body>
<header><nav><a href="/">Home</a> <a href="/about">About</a></nav></header>
<aside>Subscribe to the newsletter</aside>
<article>
<h1>Invented Article</h1>
<p>An <strong>invented</strong> page with a <a href="/docs/x">relative link</a> and <code>inline()</code>. {WORDS}</p>
<h2>Steps</h2>
<ol><li>First step</li><li>Second <em>step</em></li></ol>
<pre><code class="language-python">def f(x):
    return x * 2  # keep `this`
</code></pre>
<blockquote><p>A quoted claim.</p></blockquote>
<table><tr><th>Choice</th><th>Cost</th></tr><tr><td>A</td><td>1 | 2</td></tr></table>
</article>
<footer>Copyright footer</footer></body></html>"""


class ExtractTests(unittest.TestCase):
    def test_main_content_markdown_and_metadata(self):
        markdown, meta = web_capture.extract(PAGE, "https://example.com/posts/1")
        self.assertEqual(meta, {"title": "Invented Article", "author": "Ada Example", "published": "2026-09-20"})
        for expected in ("# Invented Article", "## Steps", "1. First step", "2. Second *step*",
                         "**invented**", "[relative link](https://example.com/docs/x)", "`inline()`",
                         "```python\ndef f(x):\n    return x * 2  # keep `this`\n```", "> A quoted claim.",
                         "| Choice | Cost |", "| A | 1 \\| 2 |"):
            self.assertIn(expected, markdown)
        for dropped in ("Home", "Subscribe", "Copyright footer", "tracking"):
            self.assertNotIn(dropped, markdown)

    def test_numeric_author_ids_are_not_names(self):
        page = PAGE.replace('content="Ada Example"', 'content="262588213843476"')
        self.assertIsNone(web_capture.extract(page, "https://example.com/")[1]["author"])


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.vault = base / "vault"
        (self.vault / "wiki").mkdir(parents=True)
        self.config = base / "operator.json"
        self.config.write_text(json.dumps({"agent": "a", "model": "p/m", "opencode_version": "0",
                                           "workdir": str(base / "ops")}))

    def tearDown(self):
        self.tmp.cleanup()

    def fake(self, html=PAGE, kind="text/html", final="https://example.com/posts/1"):
        return lambda url: (html.encode(), kind, final, "utf-8")

    def test_capture_writes_provenance_and_never_overwrites(self):
        first = op.capture(self.vault, "https://example.com/posts/1", self.config, "2026-09-29", self.fake())
        second = op.capture(self.vault, "https://example.com/posts/1", self.config, "2026-09-29", self.fake())
        self.assertEqual((first["raw"], second["raw"]),
                         ("raw/2026-09-29-invented-article.md", "raw/2026-09-29-invented-article-2.md"))
        text = (self.vault / first["raw"]).read_text()
        header, body = text.split("---\n\n", 1)
        fields = {line.split(": ", 1)[0]: json.loads(line.split(": ", 1)[1]) for line in header.splitlines()[1:]}
        self.assertEqual((fields["url"], fields["final_url"], fields["author"], fields["published"]),
                         ("https://example.com/posts/1", None, "Ada Example", "2026-09-20"))
        self.assertEqual(fields["body_sha256"], op.digest(body.encode()))
        self.assertTrue(fields["captured"].endswith("Z"))

    def test_capture_refusals(self):
        cases = [("ftp://example.com/x", self.fake(), "http"), ("https://a@example.com/", self.fake(), "http"),
                 ("https://example.com/", self.fake("<html><body><p>Please log in.</p></body></html>"), "words"),
                 ("https://example.com/", self.fake(kind="application/zip"), "unsupported")]
        for url, fetch, expected in cases:
            with self.subTest(expected=expected), self.assertRaisesRegex(ValueError, expected):
                op.capture(self.vault, url, self.config, "2026-09-29", fetch)
        self.assertFalse((self.vault / "raw").exists() and any((self.vault / "raw").iterdir()))

    def test_long_page_splits_between_headings_within_one_read(self):
        sections = "".join(f"<h2>Section {i}</h2>" + "".join(f"<p>{WORDS} paragraph {j}.</p>" for j in range(12))
                           for i in range(12))
        html = f"<html><head><title>Long invented guide</title></head><body><article>{sections}</article></body></html>"
        result = op.capture(self.vault, "https://example.com/long", self.config, "2026-09-29",
                            self.fake(html, final="https://example.com/long"))
        self.assertGreater(len(result["parts"]), 1)
        from scripts import pdf_capture
        for number, part in enumerate(result["parts"], 1):
            text = (self.vault / part).read_text()
            body = text.split("---\n\n", 1)[1]
            self.assertLessEqual(len(body.encode()), pdf_capture.MAX_PART_BYTES)
            self.assertIn(f'part: "{number}/{len(result["parts"])}"', text)
            self.assertTrue(body.startswith("## Section"), body[:40])
        self.assertTrue(result["parts"][0].endswith("-part-1.md"))

    def test_plain_text_and_long_lines(self):
        text = "# Plain notes\n\n" + " ".join([WORDS] * 10) + "\n\n```\n" + "x" * 3000 + "\n```\n"
        result = op.capture(self.vault, "https://example.com/n.txt", self.config, "2026-09-29",
                            self.fake(text, "text/plain", "https://example.com/n.txt"))
        body = (self.vault / result["raw"]).read_text().split("---\n\n", 1)[1]
        self.assertEqual(result["title"], "Plain notes")
        code = body.split("```\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(code.replace("\n", ""), "x" * 3000)  # split to fit a read, nothing lost
        self.assertTrue(all(len(line) <= op.MAX_LINE for line in (self.vault / result["raw"]).read_text().splitlines()))
        self.assertTrue(max(len(line) for line in body.splitlines() if not line.startswith("x")) <= 500)

    def test_pending_lists_unreferenced_captures_oldest_first(self):
        fixture = ROOT / "tests/fixtures/contract"
        for path in fixture.rglob("*"):
            if path.is_file():
                target = self.vault / path.relative_to(fixture)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(path.read_bytes())
        self.assertEqual(op.pending(self.vault), [])
        import os
        for name, mtime in (("raw/new-b.md", 200), ("raw/new-a.html", 100), ("raw/assets/pic.md", 50),
                            ("raw/.hidden.md", 50), ("raw/data.json", 50), ("raw/trial-a-notes/x.md", 50)):
            (self.vault / name).parent.mkdir(parents=True, exist_ok=True)
            (self.vault / name).write_text("x")
            os.utime(self.vault / name, (mtime, mtime))
        self.assertEqual(op.pending(self.vault), ["raw/trial-a-notes/x.md", "raw/new-a.html", "raw/new-b.md"])

    def test_stage_url_captures_then_stages(self):
        (self.vault / "wiki/index.md").write_text('---\ntitle: "Index"\ntype: "index"\ncreated: "2026-09-29"\n'
                                                 'updated: "2026-09-29"\naliases: []\ntags: []\n---\n# Index\n\n'
                                                 + op.wiki_index.MARKER + '\n')
        original = op.web_capture.fetch
        op.web_capture.fetch = self.fake()
        try:
            with self.assertRaisesRegex(ValueError, "task"):
                op.stage(self.vault, "ingest", [], None, self.config, url="https://example.com/posts/1")
            self.assertFalse((self.vault / "raw").exists())
            operation = op.stage(self.vault, "ingest", [], "Ingest it", self.config, "2026-09-29",
                                 url="https://example.com/posts/1")
        finally:
            op.web_capture.fetch = original
        manifest = json.loads((operation / "manifest.json").read_text())
        self.assertEqual(manifest["inputs"], ["raw/2026-09-29-invented-article.md"])
        self.assertIn("raw/2026-09-29-invented-article.md", manifest["reads"])


if __name__ == "__main__":
    unittest.main()
