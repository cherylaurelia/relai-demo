"""Smoke verifier: python check.py <trial_dir>. Not frozen; see relai/docs/files.md (smoke test).

Checks the harness, not the agent's quality: the agent ran, its writer call reached the fault stub,
and the trajectory records the request, each model call in order and the outcome.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from evaluate import Results  # noqa: E402

EV = "agent-ran-and-recorded"
MARKER = "lower specific energy than lithium nickel manganese cobalt oxide"  # from scenario.json context


def main() -> int:
    trial = Path(sys.argv[1]).resolve()
    agent = trial / "agent"
    results = Results([EV])
    with results.check(EV):
        outcome = json.loads((agent / "outcome.json").read_text())
        traj = json.loads((agent / "trajectory.json").read_text())
        journal_path = agent / "mock-journal.jsonl"
        journal = ([json.loads(l) for l in journal_path.read_text().splitlines() if l.strip()]
                   if journal_path.is_file() else [])
        steps = traj.get("steps") or []
        problems = []
        if not any(MARKER in m.get("content", "") for c in journal for m in c["input"]["messages"]):
            problems.append(f"no journaled model call carries the scenario context ({len(journal)} calls)")
        if not steps or steps[0].get("source") != "user":
            problems.append("trajectory does not start with the user request")
        calls = [s for s in steps if (s.get("extra") or {}).get("mock_journal_seq") is not None]
        if [s["extra"]["mock_journal_seq"] for s in calls] != [c["seq"] for c in journal]:
            problems.append("trajectory model-call steps do not match the journal, in order")
        elif any(s["extra"].get("request_messages") != c["input"]["messages"] for s, c in zip(calls, journal)):
            problems.append("a model-call step lacks the request messages the journal recorded")
        last = steps[-1] if steps else {}
        if outcome.get("outcome") == "returned":
            if last.get("source") != "agent" or last.get("message") != (outcome.get("report") or ""):
                problems.append("last step is not the returned report as the agent's reply")
        elif outcome.get("outcome") == "raised":
            if last.get("source") != "system" or not str(last.get("message", "")).startswith("write_report raised"):
                problems.append("last step does not record the raised exception")
        else:
            problems.append(f"outcome.json has no final outcome: {outcome.get('outcome')!r}")
        if problems:
            results.score(EV, 0.0, "Harness smoke failed: " + "; ".join(problems))
        else:
            results.score(EV, 1.0, f"Agent ran; {len(journal)} model calls reached the fault stub and appear in "
                                   f"order in the trajectory; outcome '{outcome['outcome']}' is recorded last.")
    results.write(trial / "verifier")
    return 0


if __name__ == "__main__":
    sys.exit(main())
