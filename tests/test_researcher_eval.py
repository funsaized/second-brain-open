"""Offline checks for the researcher evaluation harness; no OpenCode or model calls."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent / "live"))  # the live drivers under test
import researcher_eval as ev


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/contract"
QUESTIONS = ROOT / "tests/fixtures/eval/contract-questions.json"


def read(path, status="completed"):
    return {"type": "tool_use", "part": {"tool": "read", "state": {"status": status, "input": {"filePath": path}}}}


def events(*reads, text="", skill=True):
    parts = [{"type": "step_start", "part": {}}]
    if skill:
        parts.append({"type": "tool_use", "part": {"tool": "skill", "state": {
            "status": "completed", "input": {"name": "second-brain-query"}}}})
    parts += [read(p) if isinstance(p, str) else p for p in reads]
    parts.append({"type": "text", "part": {"text": text}})
    parts.append({"type": "step_finish", "part": {"tokens": {"input": 100, "output": 20}}})
    return parts


ANSWER = ("Trial A recorded 18 minutes open and 24 minutes closed "
          "([[wiki/sources/trial-a|Trial A]], Measurements).\n\n"
          "Read: wiki/index.md, wiki/sources/trial-a.md\nNot covered: none\n")


class ResearcherEvalTests(unittest.TestCase):
    def setUp(self):
        self.questions = {q["id"]: q for q in ev.load_questions(QUESTIONS, FIXTURE)}
        self.state = {"wiki/index.md": "i", "wiki/sources/trial-a.md": "a", "wiki/sources/trial-b.md": "b"}

    def test_question_file_validation(self):
        self.assertEqual(list(self.questions), ["trial-a-times", "vent-disagreement", "trial-b-published"])
        bad = [
            {"questions": []},
            {"questions": [{"id": "a", "question": "read @file", "expect": "abstain"}]},
            {"questions": [{"id": "a", "question": "q", "expect": "maybe"}]},
            {"questions": [{"id": "a", "question": "q", "expect": "answer"}]},
            {"questions": [{"id": "a", "question": "q", "expect": "answer", "expected_pages": ["wiki/index.md"]}]},
            {"questions": [{"id": "a", "question": "q", "expect": "answer", "expected_pages": ["wiki/sources/nope.md"]}]},
            {"questions": [{"id": "a", "question": "q", "expect": "abstain"}, {"id": "a", "question": "q", "expect": "abstain"}]},
            {"questions": [{"id": "a", "question": "q", "expect": "abstain", "extra": 1}]},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "q.json"
            for data in bad:
                with self.subTest(data=data):
                    path.write_text(json.dumps(data))
                    with self.assertRaises(ValueError):
                        ev.load_questions(path, FIXTURE)

    def test_citations_from_wikilinks_and_paths(self):
        text = ("See [[wiki/concepts/space name#Heading|Label]], wiki/sources/trial-a.md. "
                "and (wiki/sources/trial-b). Also [[wiki/index]] and `wiki/entities/aster-desk-lab.md`:")
        self.assertEqual(ev.extract_citations(text), [
            "wiki/concepts/space name.md", "wiki/entities/aster-desk-lab.md",
            "wiki/sources/trial-a.md", "wiki/sources/trial-b.md"])

    def test_passing_answer(self):
        corpus = Path("/staged/corpus")
        result = ev.score(self.questions["trial-a-times"],
                          events(str(corpus / "catalog.md"), "wiki/sources/trial-a.md", text=ANSWER),
                          corpus, self.state, dict(self.state))
        self.assertTrue(result["passed"], result["checks"])
        self.assertEqual(result["cited"], ["wiki/sources/trial-a.md"])
        self.assertEqual(result["metrics"]["content_pages_read"], 1)
        self.assertEqual((result["metrics"]["tokens_input"], result["metrics"]["tokens_output"]), (100, 20))
        full = ev.score(self.questions["trial-a-times"], events("wiki/index.md", "wiki/sources/trial-a.md", text=ANSWER),
                        corpus, self.state, dict(self.state), guide="wiki/index.md")  # --full-index comparison
        self.assertTrue(full["passed"], full["checks"])

    def test_failures_are_specific(self):
        corpus = Path("/staged/corpus")
        question = self.questions["trial-a-times"]
        cases = {
            "citations_read": events("catalog.md", text=ANSWER),
            "index_first": events("wiki/sources/trial-a.md", "catalog.md", text=ANSWER),
            "sections": events("catalog.md", "wiki/sources/trial-a.md", text=ANSWER.split("\n\n")[0]),
            "tools_ok": events("catalog.md", "wiki/sources/trial-a.md", read("raw/x.md", "error"), text=ANSWER),
            "skill_loaded": events("catalog.md", "wiki/sources/trial-a.md", text=ANSWER, skill=False),
            "expected_terms": events("catalog.md", "wiki/sources/trial-a.md", text=ANSWER.replace("24", "30")),
        }
        for check, stream in cases.items():
            with self.subTest(check=check):
                result = ev.score(question, stream, corpus, self.state, dict(self.state))
                self.assertFalse(result["passed"])
                self.assertEqual([k for k, ok in result["checks"].items() if not ok], [check])
        changed = dict(self.state, **{"wiki/index.md": "changed"})
        result = ev.score(question, events("catalog.md", "wiki/sources/trial-a.md", text=ANSWER),
                          corpus, self.state, changed)
        self.assertEqual([k for k, ok in result["checks"].items() if not ok], ["zero_writes"])
        both = ev.score(self.questions["vent-disagreement"],
                        events("catalog.md", "wiki/sources/trial-a.md", text=ANSWER), corpus, self.state, self.state)
        self.assertEqual([k for k, ok in both["checks"].items() if not ok], ["expected_cited"])

    def test_abstention(self):
        corpus = Path("/staged/corpus")
        question = self.questions["trial-b-published"]
        text = ("The publication date of Trial B is unknown ([[wiki/sources/trial-b]]).\n"
                "Read: wiki/index.md, wiki/sources/trial-b.md\nNot covered: publication date\n")
        result = ev.score(question, events("catalog.md", "wiki/sources/trial-b.md", text=text),
                          corpus, self.state, self.state)
        self.assertTrue(result["passed"], result["checks"])
        guess = text.replace("is unknown", "is 2026-09-01").replace("publication date\n", "none\n")
        result = ev.score(question, events("catalog.md", "wiki/sources/trial-b.md", text=guess),
                          corpus, self.state, self.state)
        self.assertEqual([k for k, ok in result["checks"].items() if not ok], ["abstained"])
        summary = ev.summarize([result])
        self.assertEqual((summary["questions"], summary["passed"], summary["checks"]["abstained"]), (1, 0, "0/1"))
        for phrase in ("I can’t determine it from the staged pages.", "I can't answer that.",
                       "The wiki does not answer this.", "I found no related material."):
            self.assertTrue(ev.ABSTAIN.search(phrase), phrase)

    def test_stage_copies_pages_contract_and_role_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            for path in FIXTURE.rglob("*"):
                if path.is_file():
                    target = vault / path.relative_to(FIXTURE)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(path.read_bytes())
            (vault / "AGENTS.md").write_text("Private owner instructions\n")
            (vault / ".obsidian").mkdir()
            (vault / ".obsidian/app.json").write_text("{}\n")
            base = Path(tmp) / "one"
            base.mkdir()
            corpus, profile, origin = ev.stage(vault, base)
            files = set(ev.corpus_state(corpus))
            pages = {p.relative_to(FIXTURE).as_posix() for p in (FIXTURE / "wiki").rglob("*.md")}
            self.assertEqual(files, {ev.CONTRACT, *pages} - {"wiki/index.md"})  # the catalog replaces the index
            full = Path(tmp) / "full"
            full.mkdir()
            self.assertIn("wiki/index.md", ev.corpus_state(ev.stage(vault, full, full_index=True)[0]))
            self.assertTrue((profile / "agents/sb-researcher.md").is_file())
            self.assertTrue((profile / "skills/second-brain-query/SKILL.md").is_file())
            self.assertEqual({v["from"] for v in origin.values()}, {"framework"})
            base = Path(tmp) / "two"
            base.mkdir()
            corpus, _, _ = ev.stage(vault, base, include_raw=True)
            self.assertIn("raw/trial-a.md", ev.corpus_state(corpus))
            (vault / "wiki/sources/linked.md").symlink_to(vault / "wiki/sources/trial-a.md")
            base = Path(tmp) / "three"
            base.mkdir()
            with self.assertRaises(ValueError):
                ev.stage(vault, base)

    def test_cli_requires_live_before_any_runtime_call(self):
        result = subprocess.run([sys.executable, str(ROOT / "tests/live/researcher_eval.py"), "--vault", str(FIXTURE),
                                 "--questions", str(QUESTIONS), "--agent", "a", "--model", "p/m",
                                 "--opencode-version", "0"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("opt-in", result.stderr)


if __name__ == "__main__":
    unittest.main()
