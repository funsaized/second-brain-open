"""Generated index, bounded catalogs and the checker's index rules, on invented pages."""

from pathlib import Path
import tempfile
import unittest

from scripts import link_check, wiki_index


def page(kind, title, summary=None, theme=None, gaps=None, part_of=None, body="", aliases=()):
    meta = {"title": title, "type": kind, "created": "2026-09-01", "updated": "2026-09-02",
            "aliases": list(aliases), "tags": []}
    for key, value in (("summary", summary), ("theme", theme), ("gaps", gaps), ("part_of", part_of)):
        if value is not None:
            meta[key] = value
    return {"metadata": meta, "body": body}


def write_vault(root, pages, index=True):
    import json
    for key, item in pages.items():
        path = root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        meta = dict(item["metadata"])
        if meta["type"] == "source":
            meta.update({"author": None, "published": None, "captured": "2026-09-01", "raw": "raw/x.md"})
        head = "\n".join(f"{k}: {json.dumps(v)}" for k, v in meta.items())
        path.write_text(f"---\n{head}\n---\n\n# {meta['title']}\n\n{item['body']}\n")
    (root / "raw").mkdir(exist_ok=True)
    (root / "raw/x.md").write_text("evidence\n")
    log = root / "wiki/log.md"
    log.write_text('---\ntitle: "Log"\ntype: "log"\ncreated: "2026-09-01"\nupdated: "2026-09-01"\n'
                   'aliases: []\ntags: []\n---\n\n# Log\n')
    if index:
        (root / "wiki/index.md").write_text(wiki_index.build_index(link_check.collect(root)[0]))


class IndexTests(unittest.TestCase):
    def test_index_groups_by_section_and_theme_in_natural_order(self):
        pages = {
            "wiki/sources/b-10.md": page("source", "Book, part 10", "ten.", theme="Book"),
            "wiki/sources/b-2.md": page("source", "Book, part 2", "two.", theme="Book"),
            "wiki/sources/solo.md": page("source", "Solo", "alone.", gaps=["No date."]),
            "wiki/concepts/c.md": page("concept", "C | odd [title]", "a concept."),
        }
        text = wiki_index.build_index(pages, created="2026-08-01")
        self.assertTrue(wiki_index.is_generated(text))
        self.assertIn('created: "2026-08-01"\nupdated: "2026-09-02"', text)
        sources = text.split("## Sources\n", 1)[1].split("\n## ", 1)[0]
        self.assertLess(sources.index("solo|"), sources.index("### Book"))  # unthemed first
        self.assertLess(sources.index("part 2]]"), sources.index("part 10]]"))  # natural order
        self.assertIn("- [[wiki/concepts/c|C odd title]] — a concept.", text)  # label made link-safe
        self.assertIn("## Entities\n\nNo pages yet.", text)
        self.assertIn("## Gaps\n\n- [[wiki/sources/solo|Solo]]: No date.", text)
        self.assertEqual(text, wiki_index.build_index(dict(reversed(list(pages.items()))), created="2026-08-01"))

    def test_parts_are_listed_under_their_chapter_only_when_it_links_them(self):
        pages = {
            "wiki/sources/ch.md": page("source", "Chapter", "chapter.", body="[[wiki/sources/p1|1]]"),
            "wiki/sources/p1.md": page("source", "Part 1", "one.", part_of="wiki/sources/ch"),
            "wiki/sources/p2.md": page("source", "Part 2", "two.", part_of="wiki/sources/ch"),
        }
        text = wiki_index.build_index(pages)
        self.assertIn("[[wiki/sources/ch|Chapter]] — chapter. (1 part)", text)
        self.assertNotIn("[[wiki/sources/p1|", text)
        self.assertIn("[[wiki/sources/p2|", text)  # its chapter does not link it, so it stays listed

    def test_checker_reports_stale_index_missing_summary_and_bad_part_of(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_vault(root, {
                "wiki/sources/ch.md": page("source", "Chapter", "chapter.", body="[[wiki/sources/p1|1]]"),
                "wiki/sources/p1.md": page("source", "Part 1", "one.", part_of="wiki/sources/ch",
                                           body="[[wiki/sources/ch|chapter]]"),
            })
            self.assertEqual(link_check.check(root)["errors"], [])
            index = root / "wiki/index.md"
            index.write_text(index.read_text() + "\nHand edit.\n")
            self.assertIn("index_stale", {d["kind"] for d in link_check.check(root)["errors"]})
            write_vault(root, {
                "wiki/sources/ch.md": page("source", "Chapter", body="no links"),
                "wiki/sources/p1.md": page("source", "Part 1", "one.", part_of="wiki/sources/ch",
                                           body="[[wiki/sources/ch|chapter]]"),
            })
            kinds = {(d["kind"], d["page"]) for d in link_check.check(root)["errors"]}
            self.assertIn(("missing_summary", "wiki/sources/ch.md"), kinds)
            self.assertIn(("part_of", "wiki/sources/p1.md"), kinds)
            bad = root / "wiki/sources/ch.md"
            bad.write_text(bad.read_text().replace("tags: []", 'tags: []\nsummary: "two\\nlines"\ntheme: "A | B"'))
            details = {d.get("detail") for d in link_check.check(root)["errors"] if d["page"] == "wiki/sources/ch.md"}
            self.assertIn("invalid theme", details)
            self.assertTrue(any(d and d.startswith("invalid summary") for d in details))


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.pages = {f"wiki/sources/s{i}.md": page("source", f"Source {i} on topic {i % 7}",
                                                    f"Notes on subject {i}. " + "x" * 120, theme=f"Theme {i % 9}")
                      for i in range(600)}
        self.pages["wiki/sources/s1.md"]["body"] = "See [[wiki/concepts/zod|Zod]]."
        self.pages["wiki/concepts/zod.md"] = page("concept", "Schema validation with Zod", "Parse, don't validate.")
        for i in range(200):
            self.pages[f"wiki/concepts/k{i}.md"] = page("concept", f"Concept {i}", "c.")

    def test_catalog_stays_within_budget_and_puts_relevant_pages_first(self):
        text = wiki_index.catalog(self.pages, ["wiki/sources/s1.md"], "schema validation", budget=24_000)
        self.assertLessEqual(len(text), 24_200)
        related = text.split("## Related pages", 1)[1]
        self.assertTrue(related.lstrip().startswith("- [[wiki/concepts/zod|Schema validation with Zod]]"))
        self.assertIn("Theme 1", related)
        self.assertIn("further lines omitted", text)
        self.assertIn("## Inputs\n\n- wiki/sources/s1.md — Source 1 on topic 1", text)
        self.assertIn("search wiki/ with grep or glob", text)
        small = wiki_index.catalog(self.pages, [], "", budget=10_000)
        self.assertLessEqual(len(small), 10_200)

    def test_catalog_lists_remaining_themes_with_counts(self):
        pages = {"wiki/sources/a.md": page("source", "A", "a.", theme="Book"),
                 "wiki/sources/b.md": page("source", "B", "b.", theme="Book"),
                 "wiki/concepts/c.md": page("concept", "C", "c.")}
        text = wiki_index.catalog(pages, [], "unrelated words")
        self.assertIn("- Book: 2 source pages", text)
        self.assertIn("- [[wiki/concepts/c|C]] (concept)", text)


class HelperTests(unittest.TestCase):
    def test_set_and_get_fields(self):
        text = '---\ntitle: "T"\ntags: []\n---\n\nBody: here.\n'
        changed = wiki_index.set_fields(text, {"summary": "Ein Satz.", "tags": ["a"]})
        self.assertEqual(changed, '---\ntitle: "T"\ntags: ["a"]\nsummary: "Ein Satz."\n---\n\nBody: here.\n')
        self.assertEqual(wiki_index.get_field(changed, "tags"), ["a"])
        self.assertIsNone(wiki_index.get_field(changed, "theme"))
        self.assertTrue(wiki_index.has_field(changed, "summary"))
        with self.assertRaises(ValueError):
            wiki_index.set_fields("no frontmatter\n", {"a": 1})

    def test_first_sentence_skips_headings_lists_and_code(self):
        body = ("# Title\n\n<!-- note -->\n- a list\n```\ncode. here\n```\n"
                "This page, from [[wiki/sources/a|Source A]], explains *drying*. More follows.\n")
        self.assertEqual(wiki_index.first_sentence(body), "This page, from Source A, explains drying.")
        self.assertIsNone(wiki_index.first_sentence("# Only a heading\n"))

    def test_duplicates_compare_like_with_like(self):
        existing = {"wiki/concepts/type-erasure.md": page("concept", "Type erasure", "e.", aliases=["Erasure"]),
                    "wiki/sources/zod.md": page("source", "Zod", "z.")}
        new = {"wiki/concepts/erasure-of-types.md": page("concept", "Erasure", "x."),
               "wiki/entities/type-erasure-tool.md": page("entity", "Type Erasure!", "x."),
               "wiki/concepts/zod-library.md": page("concept", "Zod library", "x.")}
        found = {(a, b) for a, b, _ in wiki_index.duplicates(existing, new)}
        self.assertEqual(found, {("wiki/concepts/erasure-of-types", "wiki/concepts/type-erasure"),
                                 ("wiki/entities/type-erasure-tool", "wiki/concepts/type-erasure")})


if __name__ == "__main__":
    unittest.main()
