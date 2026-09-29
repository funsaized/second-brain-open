"""Manual Linux/OpenCode search-boundary probe; not part of offline discovery.

Run: python3 tests/runtime_search_probe.py
Grants a synthetic role grep and glob beside exact reads, as the operator does
for workers in a staged corpus, and forces one tool call per case through a
local fake provider inside Bubblewrap. It shows what search can reach: files
inside the worktree, not paths outside it or link targets. Exit 1 means a
failed check; exit 2 means probe/setup failure. No live provider, host home or
vault access.
"""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, "/src/tests" if sys.argv[1:] == ["--inside"] else str(Path(__file__).resolve().parent))
from runtime_read_probe import launch, probe_config, runtime_paths, start_provider  # noqa: E402

VERSION = "1.18.33"
CASE = "search-boundary"


def isolated_probe():
    if os.environ.get("SB_P0_ISOLATED") != "1" or Path.cwd() != Path("/workspace"):
        raise SystemExit("Refusing fixture creation outside the probe namespace")
    subprocess.run(["git", "init", "--quiet", "."], check=True, capture_output=True)
    approved, index = Path("wiki/sources/a.md"), Path("wiki/index.md")
    approved.parent.mkdir(parents=True)
    index.write_text("# Index\n\n- [[wiki/sources/a|A]]\n")
    approved.write_text("SYNTHETIC_APPROVED_SOURCE\n")
    # A worktree file without a read grant: search sees it. The operator therefore
    # stages only files every worker may read.
    Path("unlisted.md").write_text("SYNTHETIC_UNLISTED_WORKTREE\n")
    # Hidden folders such as .obsidian can hold plugin tokens in a real vault.
    Path(".obsidian").mkdir()
    Path(".obsidian/data.json").write_text("SYNTHETIC_HIDDEN_WORKTREE\n")
    outside = [Path("/tmp/outside/secret.md"), Path("/home/test/secret.md")]
    for path in outside:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("SYNTHETIC_FORBIDDEN_VALUE\n")
    Path("wiki/sources/link.md").symlink_to("/tmp/outside/secret.md")
    requests, action = [], {}
    server = start_provider(requests, action)
    config = probe_config(server.server_port)
    os.environ["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)
    try:
        version = subprocess.run(["/opencode", "--version"], capture_output=True, text=True, timeout=10)
        if version.returncode or version.stdout.strip() != VERSION:
            raise RuntimeError(f"Probe requires the reviewed OpenCode {VERSION}")
        paths = runtime_paths()
        config["agent"]["sb-probe"]["permission"] = {
            "*": "deny", "read": {"*": "deny", "wiki/index.md": "allow", "wiki/sources/a.md": "allow"},
            "grep": "allow", "glob": "allow", "external_directory": {"*": "deny"}}
        os.environ["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)
        cases = [
            ("grep-worktree", "grep", {"pattern": "SYNTHETIC_"}),
            ("glob-worktree", "glob", {"pattern": "**/*.md"}),
            ("grep-outside-path", "grep", {"pattern": "SYNTHETIC_", "path": "/tmp/outside"}),
            ("grep-traversal", "grep", {"pattern": "SYNTHETIC_", "path": "/workspace/../tmp/outside"}),
            ("grep-home", "grep", {"pattern": "SYNTHETIC_", "path": "/home/test"}),
            ("glob-outside-path", "glob", {"pattern": "**/*", "path": "/tmp/outside"}),
            ("read-ungranted", "read", {"filePath": "/workspace/unlisted.md"}),
            ("deny-bash", "bash", {"command": "cat /tmp/outside/secret.md", "description": "Synthetic shell"}),
        ]
        results = []
        for label, tool, arguments in cases:
            action.update(tool=tool, input=arguments)
            requests.clear()
            files = [approved, index, Path("unlisted.md"), *outside]
            before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            result = subprocess.run(["/opencode", "run", "--pure", "--agent", "sb-probe", "--format", "json",
                                     "Perform the synthetic search probe."],
                                    capture_output=True, text=True, timeout=60)
            calls = []
            for line in result.stdout.splitlines():
                part = json.loads(line).get("part", {})
                if part.get("tool"):
                    state = part.get("state", {})
                    error = state.get("error") or ""
                    calls.append({"tool": part["tool"], "status": state.get("status"),
                                  "permission_denied": "rule which prevents" in error,
                                  "tool_unavailable": "Model tried to call unavailable tool" in error})
            after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            transcript = result.stdout + result.stderr + json.dumps(requests)
            seen = {"approved": "SYNTHETIC_APPROVED_SOURCE" in transcript,
                    "unlisted": "SYNTHETIC_UNLISTED_WORKTREE" in transcript,
                    "hidden": "SYNTHETIC_HIDDEN_WORKTREE" in transcript or ".obsidian" in transcript,
                    "forbidden": "SYNTHETIC_FORBIDDEN_VALUE" in transcript}
            one = len(calls) == 1 and calls[0]["tool"] == tool
            if label == "grep-worktree":
                # Search reaches every worktree file, granted or not, but not link targets outside it.
                expected = one and calls[0]["status"] == "completed" and seen["approved"] and seen["unlisted"]
            elif label == "glob-worktree":
                expected = one and calls[0]["status"] == "completed" and "wiki/sources/a.md" in transcript
            elif label == "deny-bash":
                expected = one and calls[0]["tool_unavailable"]
            else:
                expected = one and calls[0]["status"] == "error" and calls[0]["permission_denied"]
                expected = expected and not seen["unlisted"]
            passed = result.returncode == 0 and expected and not seen["forbidden"] and before == after
            results.append({"case": label, "runtime_exit": result.returncode, "tool_calls": calls,
                            "markers_seen": seen, "fixture_hashes_unchanged": before == after,
                            "passed": passed})
        passed = all(result["passed"] for result in results)
        print(json.dumps({"runtime": VERSION, "case": CASE, "paths": paths, "results": results,
                          "passed": passed}, indent=2))
        return 0 if passed else 1
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    try:
        sys.exit(isolated_probe() if sys.argv[1:] == ["--inside"] else
                 launch(__file__, mounts=[(Path(__file__).resolve().parents[1] / name, f"/src/{name}")
                                          for name in ("tests", "scripts")], case=CASE))
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"case": CASE, "setup_error": type(error).__name__,
                          "reason": str(error) if isinstance(error, RuntimeError) else "Runtime output withheld"}))
        sys.exit(2)
