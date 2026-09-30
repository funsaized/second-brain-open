"""Opt-in semantic check through an owner-approved primary OpenCode agent.

Uses the owner's existing OpenCode authentication, not the isolated fake profile.
Only supplied test records are synthetic/public. Ordinary profile context,
including config-directory AGENTS.md, and OpenCode session retention still apply.
No raw response/config is printed or saved by this script. This is not a clean
profile, permission-confinement or native-ingestion acceptance test.
Run explicitly with --live --agent APPROVED_AGENT --model PROVIDER/MODEL.
"""

import argparse
import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
# Where live drivers stage trials; the owner may point it at an existing folder.
TRIAL_ROOT = Path(os.environ.get("SB_TRIAL_ROOT") or Path(tempfile.gettempdir()) / "sb-trials")
# The OpenCode release the recorded trials used; set SB_OPENCODE_VERSION to rerun on the installed one.
OPENCODE_VERSION = os.environ.get("SB_OPENCODE_VERSION", "1.18.32")
sys.path.insert(0, str(ROOT))
from scripts.sb_runtime import decoded, inspect_config, prepare_environment, validate_scope  # noqa: E402


def call_model(env, prompt):
    # Reject tokens rather than guess at escaping; arbitrary captures need a
    # separately verified literal-input API, not this fixed-fixture CLI probe.
    if "@" in prompt or re.search(r"!\s*`", prompt):
        raise RuntimeError("Refusing native preprocessing tokens in model input")
    with os.fdopen(os.memfd_create("opencode-synthetic-response", os.MFD_CLOEXEC), "w+b") as output:
        result = subprocess.run(
            ["opencode", "run", "--pure", "--agent", env["SB_SEMANTIC_AGENT"], "--format", "json", prompt],
            cwd=ROOT, env=env, stdout=output, stderr=subprocess.PIPE, text=True, timeout=180,
        )
        output.seek(0)
        events = [decoded(line, "model event") for line in output.read().decode("utf-8").splitlines() if line.startswith("{")]
    tool_events = sum(event.get("type") == "tool_use" or bool(event.get("part", {}).get("tool")) for event in events)
    if result.returncode or tool_events:
        raise RuntimeError("Model call failed or attempted a tool; response withheld")
    text = "".join(event.get("part", {}).get("text", "") for event in events if event.get("type") == "text").strip()
    if text.startswith("```json\n") and text.endswith("```"):
        text = text[8:-3].strip()
    answer = decoded(text, "structured model response")
    if not isinstance(answer, dict):
        raise RuntimeError("Model response is not an object")
    return answer, {"runtime_exit": result.returncode, "tool_events": tool_events,
                    "steps": sum(event.get("type") == "step_start" for event in events)}


def semantic_checks(answer):
    expected = {
        "preferred_vent": "not_established", "trial_a_open_minutes": 18, "trial_a_closed_minutes": 24,
        "trial_b_open_minutes": 25, "trial_b_closed_minutes": 19, "trial_b_publication_date": None,
        "why_results_differ": "not_covered",
    }
    checks = {key: key in answer and answer[key] == value for key, value in expected.items()}
    checks["recommendation_attribution"] = answer.get("recommendation_claim_ids") in (["A2", "B2"], ["B2", "A2"])
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="authorize one synthetic model turn")
    parser.add_argument("--agent", required=True, help="owner-approved existing primary agent")
    parser.add_argument("--model", required=True, help="approved provider/model; routing must match")
    args = parser.parse_args()
    if not args.live:
        parser.error("live provider use is opt-in; pass --live only after owner approval")
    env = prepare_environment(args.agent, args.model, OPENCODE_VERSION)
    fixture = ROOT / "tests/fixtures/contract"
    files = [Path(path) for path in ("raw/trial-a.md", "raw/trial-b.md", "wiki/sources/trial-a.md", "wiki/sources/trial-b.md")]
    validate_scope(fixture, files)
    prompt = (
        "This is an owner-approved synthetic semantic test, not an ingest. Do not use any tools. "
        "Use ONLY the complete fictional records below. Return just one JSON object with these keys: "
        "All minute values must be integers. preferred_vent (open, closed, or not_established); trial_a_open_minutes; trial_a_closed_minutes; "
        "trial_b_open_minutes; trial_b_closed_minutes; trial_b_publication_date (ISO string or null); "
        "why_results_differ (not_covered if the records do not explain it); "
        "recommendation_claim_ids (array of claim IDs supporting the two author recommendations). "
        "Do not guess dates, generalize one trial, or choose the newer source by default.\n\n"
    )
    for path in files:
        prompt += f"BEGIN COMPLETE RECORD {path.as_posix()}\n{(fixture / path).read_text()}\nEND RECORD\n\n"
    answer, observed = call_model(env, prompt)
    checks = semantic_checks(answer)
    passed = all(checks.values())
    print(json.dumps({"agent": args.agent, "model": args.model, "synthetic_records": len(files),
                      "checks": checks, "observed": observed, "passed": passed}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"setup_error": type(error).__name__, "detail": str(error) if isinstance(error, RuntimeError) else "Output withheld; no semantic pass claimed"}))
        sys.exit(2)
