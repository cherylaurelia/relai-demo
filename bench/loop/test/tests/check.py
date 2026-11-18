"""Verifier for report-llm-failure-not-silent: python check.py <trial_dir>

Reads <trial>/agent/outcome.json (what write_report did) and <trial>/agent/mock-journal.jsonl (every
model call the fault stub answered). Expected values live in params.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from evaluate import Results  # noqa: E402

EVALUATOR = "failure-not-silent"


def main() -> int:
    trial = Path(sys.argv[1]).resolve()
    agent = trial / "agent"
    params = json.loads((HERE / "params.json").read_text(encoding="utf-8"))
    results = Results([EVALUATOR])
    with results.check(EVALUATOR):
        outcome = json.loads((agent / "outcome.json").read_text(encoding="utf-8"))  # missing: error
        journal_path = agent / "mock-journal.jsonl"
        journal = ([json.loads(l) for l in journal_path.read_text(encoding="utf-8").splitlines() if l.strip()]
                   if journal_path.is_file() else [])
        marker = params["writer_call_marker"]
        writer_calls = [c for c in journal
                        if any(marker in m.get("content", "") for m in c["input"].get("messages", []))]
        if len(writer_calls) < params["min_writer_calls"]:
            raise RuntimeError(
                f"probe invalid: {len(writer_calls)} report-writer model call(s) reached the fault stub "
                f"(need {params['min_writer_calls']}; {len(journal)} journaled call(s) in total), so the "
                "writer failure was never triggered")
        not_failed = [c["seq"] for c in journal if c.get("outcome") != "error"]
        if not_failed:
            raise RuntimeError(f"probe invalid: journal calls {not_failed} were not answered with the injected error")

        evidence = (f"All {len(writer_calls)} report-writer model requests failed with "
                    f"{writer_calls[0]['response'].get('error_type')} ({writer_calls[0]['response'].get('status')})")
        need = "Full marks need write_report to raise an exception to its caller when the report cannot be written."
        if outcome["outcome"] == "raised":
            chain = outcome.get("exception_chain")
            if not isinstance(chain, list) or not chain:
                raise RuntimeError("outcome.json records no exception_chain; the adapter is too old for this check")
            if chain[0] in params["programming_errors"]:
                raise RuntimeError(
                    f"probe invalid: write_report raised {chain[0]} (chain {chain}), a programming error, not a "
                    "deliberate failure signal; it says nothing about how the writer failure is handled")
            how = (f"caused by {params['injected_error']}" if params["injected_error"] in chain
                   else "(a fresh error, not chained to the provider error)")
            results.score(EVALUATOR, 1.0,
                          f"Writer failure reached the caller. {evidence}, and write_report raised "
                          f"{chain[0]} {how} instead of returning a report.")
        else:
            report = outcome.get("report")
            if isinstance(report, str) and not report.strip():
                what = f"returned {report!r} (empty, length {len(report)})"
            elif isinstance(report, str):
                first = report.strip().splitlines()[0][:200]
                what = (f"returned {len(report)} characters of text beginning {first!r}, which callers "
                        "(the CLI, the backend's md/pdf/docx writers) save as the report")
            else:
                what = f"returned a {outcome.get('report_type')} ({report!r})"
            results.score(EVALUATOR, 0.0,
                          f"Writer failure not surfaced. {evidence}; write_report then {what} without raising, "
                          f"so the caller cannot tell a failed report from a finished one. {need}")
    results.write(trial / "verifier")
    return 0


if __name__ == "__main__":
    sys.exit(main())
