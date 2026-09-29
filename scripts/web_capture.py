"""Fetch one web page and keep its main content as Markdown; no model involved.

A small Readability-style extractor on the standard library: parse the HTML,
drop scripts, navigation, headers, footers and forms, take the richest
<article>, then <main>/[role=main], then <body>, and render headings,
paragraphs, lists, links, emphasis, quotes, tables and code blocks (verbatim)
as Markdown. Metadata comes from <title> and common meta tags. Pages that need
JavaScript or a login come back as fragments and are refused by the caller.
"""

from html.parser import HTMLParser
import re
import urllib.parse
import urllib.request


SKIP = {"script", "style", "noscript", "svg", "nav", "header", "footer", "aside", "form", "button",
        "iframe", "template", "select", "dialog", "canvas", "object"}
VOID = {"br", "hr", "img", "meta", "link", "input", "source", "area", "base", "col", "embed", "param", "track", "wbr"}
BLOCK = {"p", "div", "section", "article", "main", "ul", "ol", "li", "pre", "blockquote", "table", "tr",
         "h1", "h2", "h3", "h4", "h5", "h6", "figure", "figcaption", "dl", "dt", "dd", "hr", "details", "summary"}
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) second-brain-open capture"


class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs or {}), parent, []


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Node("document")
        self.meta = {}
        self.title = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            a = dict(attrs)
            key = (a.get("property") or a.get("name") or a.get("itemprop") or "").lower()
            if key and a.get("content"):
                self.meta.setdefault(key, a["content"].strip())
            return
        if tag == "title":
            self.in_title = True
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.current.tag == tag:
            self.current = self.current.parent

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        node = self.current
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.current = node.parent

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        self.current.children.append(data)


def text_length(node):
    if isinstance(node, str):
        return len(node.strip())
    if node.tag in SKIP:
        return 0
    return sum(text_length(child) for child in node.children)


def find_all(node, test):
    if isinstance(node, str):
        return
    if test(node):
        yield node
    for child in node.children:
        yield from find_all(child, test)


def content_root(document):
    for test in (lambda n: n.tag == "article", lambda n: n.tag == "main" or n.attrs.get("role") == "main",
                 lambda n: n.tag == "body"):
        candidates = [n for n in find_all(document, test) if text_length(n) > 200]
        if candidates:
            return max(candidates, key=text_length)
    return document


class Renderer:
    def __init__(self, base_url):
        self.base_url = base_url

    def inline(self, node):
        if isinstance(node, str):
            return re.sub(r"\s+", " ", node)
        tag = node.tag
        if tag in SKIP:
            return ""
        inner = "".join(self.inline(child) for child in node.children)
        if tag == "br":
            return "\n"
        if tag == "img":
            src = node.attrs.get("src")
            return f"![{node.attrs.get('alt', '').strip()}]({urllib.parse.urljoin(self.base_url, src)})" if src else ""
        if tag == "code":
            text = self.raw_text(node)
            fence = "``" if "`" in text else "`"
            return f"{fence}{text}{fence}" if text else ""
        if tag in ("strong", "b") and inner.strip():
            return f"**{inner.strip()}**"
        if tag in ("em", "i") and inner.strip():
            return f"*{inner.strip()}*"
        if tag == "a":
            href = node.attrs.get("href", "")
            if inner.strip() and href and not href.startswith(("javascript:", "#")):
                return f"[{inner.strip()}]({urllib.parse.urljoin(self.base_url, href)})"
        return inner

    def raw_text(self, node):
        if isinstance(node, str):
            return node
        if node.tag == "br":
            return "\n"
        return "".join(self.raw_text(child) for child in node.children)

    def blocks(self, node, depth=0):
        """Yield Markdown blocks (strings separated by blank lines)."""
        buffer = []

        def flush():
            text = re.sub(r"[ \t]+\n", "\n", "".join(buffer)).strip()
            buffer.clear()
            return text

        for child in node.children:
            if isinstance(child, str) or child.tag not in BLOCK:
                if isinstance(child, Node) and child.tag in SKIP:
                    continue
                buffer.append(self.inline(child))
                continue
            text = flush()
            if text:
                yield text
            yield from self.block(child, depth)
        text = flush()
        if text:
            yield text

    def block(self, node, depth):
        tag = node.tag
        if tag in SKIP:
            return
        if re.fullmatch(r"h[1-6]", tag):
            text = " ".join(self.inline(node).split())
            if text:
                yield "#" * int(tag[1]) + " " + text
        elif tag == "pre":
            code = self.raw_text(node).strip("\n")
            classes = " ".join(n.attrs.get("class", "") for n in find_all(node, lambda n: True))
            language = (re.search(r"(?:language|lang)-([\w+-]+)", classes) or [None, ""])[1]
            fence = "`" * max(3, max((len(m) for m in re.findall(r"`+", code)), default=0) + 1)
            yield f"{fence}{language}\n{code}\n{fence}"
        elif tag in ("ul", "ol"):
            items = [c for c in node.children if isinstance(c, Node) and c.tag == "li"]
            lines = []
            for number, item in enumerate(items, 1):
                marker = f"{number}." if tag == "ol" else "-"
                body = "\n\n".join(self.blocks(item, depth + 1)).strip()
                indented = body.replace("\n", "\n" + " " * (len(marker) + 1))
                lines.append(f"{marker} {indented}")
            if lines:
                yield "\n".join(lines)
        elif tag == "blockquote":
            body = "\n\n".join(self.blocks(node, depth))
            if body:
                yield "\n".join("> " + line if line else ">" for line in body.splitlines())
        elif tag == "table":
            rows = [[" ".join(self.inline(cell).split()).replace("|", "\\|")
                     for cell in row.children if isinstance(cell, Node) and cell.tag in ("td", "th")]
                    for row in find_all(node, lambda n: n.tag == "tr")]
            rows = [row for row in rows if any(row)]
            if rows:
                width = max(len(row) for row in rows)
                rows = [row + [""] * (width - len(row)) for row in rows]
                lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
                lines += ["| " + " | ".join(row) + " |" for row in rows[1:]]
                yield "\n".join(lines)
        elif tag == "hr":
            yield "---"
        else:
            yield from self.blocks(node, depth)


def extract(html, base_url):
    """Return (markdown, metadata) for the page's main content."""
    builder = TreeBuilder()
    builder.feed(html)
    builder.close()
    meta = builder.meta
    title = (meta.get("og:title") or meta.get("twitter:title") or " ".join("".join(builder.title).split()) or None)
    author = meta.get("author") or meta.get("article:author") or meta.get("parsely-author") or None
    published = None
    for key in ("article:published_time", "datepublished", "date", "dc.date", "publish-date", "pubdate"):
        match = re.match(r"\d{4}-\d{2}-\d{2}", meta.get(key, ""))
        if match:
            published = match.group()
            break
    if published is None:
        for node in find_all(builder.root, lambda n: n.tag == "time" and n.attrs.get("datetime")):
            match = re.match(r"\d{4}-\d{2}-\d{2}", node.attrs["datetime"])
            if match:
                published = match.group()
                break
    root = content_root(builder.root)
    markdown = "\n\n".join(Renderer(base_url).blocks(root)).strip() + "\n"
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    if author and (author.startswith("http") or not re.search(r"[^\W\d_]", author)):
        author = None  # profile URLs and numeric IDs are not names
    return markdown, {"title": title, "author": author,
                      "published": published}


def fetch(url, timeout=60, limit=50_000_000):
    """Return (bytes, content type, final URL, charset); callers decode text types."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.5"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        kind = response.headers.get_content_type()
        charset = response.headers.get_content_charset() or "utf-8"
        data = response.read(limit + 1)
        final = response.geturl()
    if len(data) > limit:
        raise ValueError(f"download is larger than {limit // 1_000_000} MB")
    return data, kind, final, charset
