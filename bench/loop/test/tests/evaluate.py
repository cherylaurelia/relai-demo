"""Score-file helper, adapted from the RELAI plugin's examples/evaluate.py (relai 0.1.0, 374f8ed):
only Results is kept, and paths come from the native trial directory instead of /logs.

Writes <trial>/verifier/reward.json {"<id>": number}, feedback.json {"<id>": "text"} and
errors.json {"<id>": "message"}. A check that raises is an error for that evaluator, never a
zero; an expected evaluator the script never scored is recorded as an error.
"""

from __future__ import annotations

import json
import math
import traceback
from contextlib import contextmanager
from pathlib import Path


class Results:
    def __init__(self, expected: list[str] | None = None) -> None:
        self.expected = list(expected or [])
        self.rewards: dict[str, float] = {}
        self.feedback: dict[str, str] = {}
        self.errors: dict[str, str] = {}

    def score(self, evaluator_id: str, value: float, feedback: str) -> None:
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{evaluator_id}: score must be a finite number")
        if not feedback.strip():
            raise ValueError(f"{evaluator_id}: feedback is required for every score")
        self.rewards[evaluator_id] = float(value)
        self.feedback[evaluator_id] = feedback
        self.errors.pop(evaluator_id, None)

    @contextmanager
    def check(self, evaluator_id: str):
        try:
            yield
        except Exception:
            self.rewards.pop(evaluator_id, None)
            self.feedback.pop(evaluator_id, None)
            self.errors[evaluator_id] = traceback.format_exc(limit=3)[-1500:]

    def write(self, directory: Path) -> None:
        for evaluator_id in self.expected:
            if evaluator_id not in self.rewards and evaluator_id not in self.errors:
                self.errors[evaluator_id] = "the check never ran: the script did not score this evaluator"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "reward.json").write_text(json.dumps(self.rewards))
        (directory / "feedback.json").write_text(json.dumps(self.feedback))
        (directory / "errors.json").write_text(json.dumps(self.errors))
