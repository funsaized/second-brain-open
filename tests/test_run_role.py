"""Worker launch timeouts with a fake `opencode` script; no OpenCode or provider."""

from pathlib import Path
import os
import stat
import tempfile
import time
import unittest

from scripts import sb_runtime


FAKE = """#!/usr/bin/env python3
import os, sys, time
count = os.path.join({state!r}, "launches")
n = int(open(count).read()) + 1 if os.path.exists(count) else 1
open(count, "w").write(str(n))
mode = {mode!r}
if mode == "always-silent" or (mode == "silent-once" and n == 1):
    time.sleep(60)
print('{{"type": "text", "part": {{"text": "answer"}}}}', flush=True)
if mode == "slow":
    time.sleep(60)
"""


@unittest.skipUnless(hasattr(os, "memfd_create"), "Linux memfd required")
class RunRoleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def fake(self, mode):
        script = self.base / f"opencode-{mode}"
        script.write_text(FAKE.format(state=str(self.base), mode=mode))
        script.chmod(script.stat().st_mode | stat.S_IEXEC)
        return (str(script),)

    def launches(self):
        return int((self.base / "launches").read_text())

    def test_a_stalled_start_is_relaunched_once(self):
        started = time.monotonic()
        events, code, _ = sb_runtime.run_role({}, self.base, "sb-researcher", "q", timeout=30, startup=1,
                                              command=self.fake("silent-once"))
        self.assertEqual((code, sb_runtime.answer_text(events), self.launches()), (0, "answer", 2))
        self.assertLess(time.monotonic() - started, 15)

    def test_two_stalls_raise_instead_of_waiting_out_the_timeout(self):
        started = time.monotonic()
        with self.assertRaisesRegex(RuntimeError, "did not start"):
            sb_runtime.run_role({}, self.base, "sb-researcher", "q", timeout=30, startup=1,
                                command=self.fake("always-silent"))
        self.assertEqual(self.launches(), 2)
        self.assertLess(time.monotonic() - started, 15)

    def test_a_started_run_keeps_the_normal_timeout(self):
        events, code, _ = sb_runtime.run_role({}, self.base, "sb-researcher", "q", timeout=3, startup=1,
                                              command=self.fake("slow"))
        self.assertEqual((sb_runtime.answer_text(events), self.launches()), ("answer", 1))
        self.assertNotEqual(code, 0)  # killed at the timeout, not relaunched


if __name__ == "__main__":
    unittest.main()
