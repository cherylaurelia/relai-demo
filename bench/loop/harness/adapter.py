"""Drive the GPT Researcher report agent through its public library API for one trial.

  python relai/harness/adapter.py <scenario.json> <trial agent dir>

Scenario keys: query, report_type, report_source, tone (optional), context (list of strings, the
research context `write_report(ext_context=...)` receives), fault (optional RELAI_LLM_FAULT mode).

Real-use path (README "Usage"): GPTResearcher(query, report_type=...) then
`await researcher.write_report()`. Research is supplied as ext_context instead of running
`conduct_research()`, which needs live retrievers and a model; the writer path after it is the
agent's own code, unchanged. Writes into the agent dir:
  outcome.json       what write_report did: returned (with the report) or raised (type, message)
  mock-journal.jsonl every model call the fault stub answered (relai/docs/files.md, Mocks)
  trajectory.json    ATIF: the user's request, each model request in causal order and its error,
                     then the agent's returned report as its reply (or the raised exception)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))  # live source: import the checkout's gpt_researcher
sys.path.insert(1, str(Path(__file__).resolve().parent))


def write_json(path: Path, doc) -> None:
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def read_journal(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def trajectory(scenario: dict, journal: list[dict], outcome: dict, model: str) -> dict:
    steps = [{"step_id": 1, "source": "user", "message": scenario["query"],
              "extra": {"report_type": scenario["report_type"], "ext_context_items": len(scenario["context"])}}]
    for call in journal:
        steps.append({
            "step_id": len(steps) + 1, "source": "system",
            "message": f"model request {call['seq']} ({call['input'].get('model')}) failed: "
                       f"{call['response'].get('error_type')} {call['response'].get('status')}",
            "extra": {"mock_journal_seq": call["seq"], "operation": call["operation"],
                      "temperature": call["input"].get("temperature"),
                      "request_messages": call["input"].get("messages")},
        })
    if outcome["outcome"] == "running":
        pass
    elif outcome["outcome"] == "returned":
        steps.append({"step_id": len(steps) + 1, "source": "agent", "message": outcome["report"] or "",
                      "extra": {"return": "write_report returned"}})
    else:
        steps.append({"step_id": len(steps) + 1, "source": "system",
                      "message": f"write_report raised {outcome['exception_type']}: {outcome['exception_message']}"})
    return {"schema_version": "ATIF-v1.7", "session_id": scenario.get("id", "trial"),
            # no model_name: no model answered (stubbed), so check_trajectory's stub warning stays visible
            "agent": {"name": "gpt-researcher", "version": os.environ.get("RELAI_AGENT_VERSION", "unknown"),
                      "extra": {"configured_model": model,
                                "model_stubbed": "relai/harness/mocks/llm_fault.py" if journal else None}},
            "steps": steps}


async def drive(scenario: dict):
    from gpt_researcher import GPTResearcher
    researcher = GPTResearcher(query=scenario["query"], report_type=scenario["report_type"],
                               report_source=scenario.get("report_source", "web"),
                               **({"tone": scenario["tone"]} if scenario.get("tone") else {}))
    return await researcher.write_report(ext_context=scenario["context"])


def main() -> int:
    scenario = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    agent_dir = Path(sys.argv[2])
    agent_dir.mkdir(parents=True, exist_ok=True)
    journal_path = agent_dir / "mock-journal.jsonl"
    fault = scenario.get("fault") or os.environ.get("RELAI_LLM_FAULT")
    if fault:
        from mocks import llm_fault
        llm_fault.install(fault, journal_path)

    model = "unknown"
    try:
        from gpt_researcher.config.config import Config
        cfg = Config()
        model = f"{cfg.smart_llm_provider}:{cfg.smart_llm_model}"
    except Exception:
        pass
    # partial trajectory first, so a killed trial still shows what it was asked
    write_json(agent_dir / "trajectory.json",
               trajectory(scenario, [], {"outcome": "running"}, model))
    started = time.time()
    try:
        report = asyncio.run(drive(scenario))
        outcome = {"outcome": "returned", "report": report if isinstance(report, (str, type(None))) else repr(report),
                   "report_type": type(report).__name__}
    except Exception as exc:  # record the agent's error as it happened (not re-raised: outcome.json carries it)
        chain, seen, cur = [], set(), exc
        while cur is not None and id(cur) not in seen:  # __cause__ / __context__ chain, outermost first
            seen.add(id(cur))
            chain.append(f"{type(cur).__module__}.{type(cur).__name__}")
            cur = cur.__cause__ or cur.__context__
        outcome = {"outcome": "raised", "exception_type": type(exc).__name__, "exception_chain": chain,
                   "exception_message": str(exc)[:2000], "traceback": traceback.format_exc()[-4000:]}
    outcome["seconds"] = round(time.time() - started, 1)
    write_json(agent_dir / "outcome.json", outcome)
    write_json(agent_dir / "trajectory.json", trajectory(scenario, read_journal(journal_path), outcome, model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
