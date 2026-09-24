"""Manual Linux/OpenCode 1.18.32 read probe; not part of offline discovery.

Run: python3 tests/runtime_read_probe.py
Exit 1 means a failed acceptance check; exit 2 means probe/setup failure.
No live provider, host home, or vault access.
"""

import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def validate_scope(root, relative_paths):
    """Reject links before launch; use only a frozen, owner-prepared corpus.

    This check is not a lock against concurrent filesystem replacement.
    The probe's namespace has no outside writers or mounted private corpus.
    """
    for relative in relative_paths:
        relative = Path(relative)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Scope must contain only confined relative files")
        path = root / relative
        if any(part.is_symlink() for part in (path, *path.parents)):
            raise ValueError("Symlinks are not allowed in the prepared corpus")
        if not path.is_file() or path.stat().st_nlink != 1:
            raise ValueError("Scope must contain regular, non-hardlinked files")


def runtime_paths():
    """Inspect only namespace-local paths, never dump resolved configuration."""
    # Initialize this disposable project before asking for its database record.
    initialized = subprocess.run(
        ["/opencode", "debug", "config", "--pure"],
        capture_output=True, text=True, timeout=20,
    )
    if initialized.returncode:
        raise RuntimeError("Isolated project initialization failed")
    config = json.loads(initialized.stdout)
    if (config.get("share") != "disabled" or config.get("snapshot") is not False
            or config.get("formatter") is not False or config.get("lsp") is not False
            or config.get("plugin") or config.get("mcp") or config.get("instructions")
            or config.get("enabled_providers") != ["anthropic"]
            or config.get("model") != "anthropic/probe" or config.get("small_model") != "anthropic/probe"):
        raise RuntimeError("Unexpected effective synthetic configuration")
    result = subprocess.run(
        ["/opencode", "debug", "scrap", "--pure"],
        capture_output=True, text=True, timeout=20,
    )
    if result.returncode:
        raise RuntimeError("Isolated project inspection failed")
    projects = json.loads(result.stdout)
    if not isinstance(projects, list) or len(projects) != 1:
        raise RuntimeError("Expected exactly one disposable project")
    worktree = projects[0].get("worktree")
    if not isinstance(worktree, str) or not Path(worktree).is_absolute():
        raise RuntimeError("Unexpected synthetic worktree")
    return {"directory": str(Path.cwd()), "worktree": worktree}


def isolated_probe():
    if os.environ.get("SB_P0_ISOLATED") != "1" or Path.cwd() != Path("/workspace"):
        raise SystemExit("Refusing fixture creation outside the probe namespace")
    page = Path("wiki/index.md")
    page.parent.mkdir()
    marker = "SYNTHETIC_APPROVED_INDEX"
    page.write_text(marker + "\n")
    forbidden_marker = "SYNTHETIC_FORBIDDEN_VALUE"
    forbidden = [Path(".obsidian/fake.md"), Path(".env"), Path("unrelated.md"), Path("/tmp/outside.md")]
    for path in forbidden:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(forbidden_marker + "\n")
    requests = []
    requested_tool = "read"
    requested_input = {"filePath": str(page.absolute())}

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            requests.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            # Force one real tool attempt, then terminate; no model discretion.
            tool = len(requests) == 1
            block = (
                {"type": "tool_use", "id": "toolu_probe", "name": requested_tool, "input": {}}
                if tool else {"type": "text", "text": ""}
            )
            delta = (
                {"type": "input_json_delta", "partial_json": json.dumps(requested_input)}
                if tool else {"type": "text_delta", "text": "Synthetic probe finished."}
            )
            events = [
                ("message_start", {"message": {
                    "id": "msg_probe", "type": "message", "role": "assistant",
                    "model": "probe", "content": [], "stop_reason": None,
                    "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1},
                }}),
                ("content_block_start", {"index": 0, "content_block": block}),
                ("content_block_delta", {"index": 0, "delta": delta}),
                ("content_block_stop", {"index": 0}),
                ("message_delta", {"delta": {
                    "stop_reason": "tool_use" if tool else "end_turn", "stop_sequence": None,
                }, "usage": {"output_tokens": 1}}),
                ("message_stop", {}),
            ]
            data = "".join(
                f"event: {name}\ndata: {json.dumps({'type': name, **value})}\n\n"
                for name, value in events
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Provider)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    config = {
        "$schema": "https://opencode.ai/config.json",
        "share": "disabled", "snapshot": False, "autoupdate": False,
        "formatter": False, "lsp": False, "plugin": [], "mcp": {}, "instructions": [],
        "enabled_providers": ["anthropic"], "model": "anthropic/probe", "small_model": "anthropic/probe",
        "provider": {"anthropic": {
            "options": {"apiKey": "synthetic-not-a-credential", "baseURL": f"http://127.0.0.1:{server.server_port}"},
            "models": {"probe": {"name": "Synthetic probe", "tool_call": True,
                "limit": {"context": 64000, "output": 4096}}},
        }},
        "permission": {"*": "deny"},
        "agent": {
            "sb-probe": {"mode": "primary", "description": "Synthetic permission probe",
                "permission": {"*": "deny", "read": {"*": "deny"}}},
            "title": {"disable": True}, "summary": {"disable": True}, "compaction": {"disable": True},
        },
    }
    os.environ["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)
    try:
        version = subprocess.run(["/opencode", "--version"], capture_output=True, text=True, timeout=10)
        if version.returncode or version.stdout.strip() != "1.18.32":
            raise RuntimeError("Probe requires the reviewed OpenCode 1.18.32")
        paths = runtime_paths()
        read_pattern = os.path.relpath(page.absolute(), paths["worktree"])
        config["agent"]["sb-probe"]["permission"]["read"] = {
            "*": "deny", read_pattern: "allow", "**/.obsidian/**": "deny",
        }
        os.environ["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)
        results = []
        cases = [(label, "read", {"filePath": path}) for label, path in [
            ("approved", str(page.absolute())), ("sensitive", "/workspace/.obsidian/fake.md"),
            ("environment", "/workspace/.env"), ("unrelated", "/workspace/unrelated.md"),
            ("traversal", "/workspace/wiki/../.obsidian/fake.md"), ("outside", "/tmp/outside.md"),
        ]]
        edit_input = {"filePath": str(page.absolute()), "oldString": marker, "newString": "CHANGED"}
        cases.extend([
            ("deny-edit", "edit", edit_input),
            ("deny-write", "write", {"filePath": str(page.absolute()), "content": "CHANGED"}),
            ("deny-bash", "bash", {"command": "true", "description": "Synthetic forbidden shell"}),
            ("deny-grep", "grep", {"pattern": "SYNTHETIC", "path": "/workspace"}),
            ("deny-glob", "glob", {"pattern": "**/*", "path": "/workspace"}),
            ("deny-webfetch", "webfetch", {"url": f"http://127.0.0.1:{server.server_port}", "format": "text"}),
            ("deny-task", "task", {"description": "Synthetic probe", "prompt": "Stop", "subagent_type": "general"}),
            ("deny-skill", "skill", {"name": "customize-opencode"}),
            ("reject-edit-approval", "edit", edit_input),
            ("symlink-at-approved-path", "read", {"filePath": str(page.absolute())}),
        ])
        for label, requested_tool, requested_input in cases:
            requests.clear()
            if label == "symlink-at-approved-path":
                page.unlink()
                page.symlink_to("../.obsidian/fake.md")
            try:
                validate_scope(Path.cwd(), [page])
            except ValueError:
                results.append({"case": label, "preflight_rejected": True,
                                "local_fake_provider_requests": len(requests),
                                "passed": label == "symlink-at-approved-path" and page.is_symlink() and not requests})
                if not results[-1]["passed"]:
                    break
                continue
            if label == "reject-edit-approval":
                config["agent"]["sb-probe"]["permission"]["edit"] = {"*": "deny", read_pattern: "ask"}
                os.environ["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)
            before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in [page, *forbidden]}
            result = subprocess.run(
                ["/opencode", "run", "--pure", "--agent", "sb-probe", "--format", "json",
                 "Perform the synthetic read probe."],
                capture_output=True, text=True, timeout=30,
            )
            calls = []
            for line in result.stdout.splitlines():
                event = json.loads(line)
                part = event.get("part", {})
                if part.get("tool"):
                    state = part.get("state", {})
                    error = state.get("error") or ""
                    calls.append({"tool": part["tool"], "status": state.get("status"), "permission_denied":
                        "rule which prevents" in error, "approval_rejected": "rejected permission" in error.lower(),
                        "tool_unavailable": "Model tried to call unavailable tool" in error})
            after = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in [page, *forbidden]}
            transcript = result.stdout + result.stderr + json.dumps(requests)
            seen = marker in transcript
            exposed = forbidden_marker in transcript
            if label == "approved":
                expected = seen and len(calls) == 1 and calls[0]["tool"] == "read" and calls[0]["status"] == "completed"
            elif label == "reject-edit-approval":
                expected = len(calls) == 1 and calls[0]["approval_rejected"]
            elif label.startswith("deny-"):
                expected = len(calls) == 1 and calls[0]["tool_unavailable"]
            else:
                expected = len(calls) == 1 and calls[0]["permission_denied"]
            if label != "approved":
                expected = expected and calls[0]["tool"] == requested_tool and calls[0]["status"] == "error"
            passed = result.returncode == 0 and expected and not exposed and before == after
            results.append({
                "case": label, "runtime_exit": result.returncode, "local_fake_provider_requests": len(requests),
                "tool_calls": calls, "approved_marker_seen": seen, "forbidden_marker_seen": exposed,
                "fixture_hashes_unchanged": before == after, "passed": passed,
            })
            if not passed:
                break
        passed = len(results) == len(cases) and all(result["passed"] for result in results)
        print(json.dumps({
            "runtime": "1.18.32", "case": "baseline-read-boundary",
            "paths": paths, "read_pattern": read_pattern,
            "results": results, "passed": passed,
        }, indent=2))
        if passed:
            return 0
        return 1
    finally:
        server.shutdown()
        server.server_close()


def launch():
    binary = shutil.which("opencode")
    if not binary or not shutil.which("bwrap"):
        raise RuntimeError("Requires opencode and bwrap; no unisolated fallback")
    command = [
        "bwrap", "--unshare-all", "--die-with-parent", "--new-session", "--clearenv",
        "--ro-bind", "/usr", "/usr", "--symlink", "usr/bin", "/bin",
        "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib", "/lib64",
        "--ro-bind", str(Path(binary).resolve()), "/opencode",
        "--ro-bind", str(Path(__file__).resolve()), "/probe.py",
        "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
        "--dir", "/home/test", "--dir", "/workspace", "--chdir", "/workspace",
    ]
    env = {
        "SB_P0_ISOLATED": "1", "HOME": "/home/test", "PATH": "/usr/bin", "PWD": "/workspace",
        "XDG_CONFIG_HOME": "/home/test/.config", "XDG_DATA_HOME": "/home/test/.local/share",
        "XDG_CACHE_HOME": "/home/test/.cache", "XDG_STATE_HOME": "/home/test/.local/state",
    }
    for flag in (
        "OPENCODE_PURE", "OPENCODE_DISABLE_DEFAULT_PLUGINS", "OPENCODE_DISABLE_CLAUDE_CODE",
        "OPENCODE_DISABLE_EXTERNAL_SKILLS", "OPENCODE_DISABLE_MODELS_FETCH",
        "OPENCODE_DISABLE_LSP_DOWNLOAD", "OPENCODE_DISABLE_AUTOUPDATE",
        "OPENCODE_DISABLE_PROJECT_CONFIG", "OPENCODE_DISABLE_SHARE",
    ):
        env[flag] = "1"
    for key, value in env.items():
        command.extend(["--setenv", key, value])
    result = subprocess.run(
        command + ["/usr/bin/python3", "/probe.py", "--inside"],
        capture_output=True, text=True, timeout=560,
    )
    # Setup failures must not look like the expected permission-denial result.
    if not result.stdout.strip():
        raise RuntimeError("Isolated probe produced no summary")
    summary = json.loads(result.stdout)
    if not isinstance(summary, dict) or summary.get("case") != "baseline-read-boundary":
        raise RuntimeError("Missing probe summary")
    print(json.dumps(summary, indent=2))
    return result.returncode if result.returncode in (0, 1, 2) else 2


if __name__ == "__main__":
    try:
        sys.exit(isolated_probe() if sys.argv[1:] == ["--inside"] else launch())
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        # Do not dump captured runtime output/config on errors.
        print(json.dumps({
            "case": "baseline-read-boundary", "setup_error": type(error).__name__,
            "reason": str(error) if isinstance(error, RuntimeError) else "Runtime output withheld",
        }))
        sys.exit(2)
