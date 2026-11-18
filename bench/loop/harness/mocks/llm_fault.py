"""Fault stub for the OpenAI chat client boundary (langchain_openai's BaseChatOpenAI).

Installed only by relai/harness/adapter.py when RELAI_LLM_FAULT is set; project code never sees
it. Every chat call the agent makes (sync or async, streamed or not) is journaled and answered
with the error the real OpenAI SDK raises for an HTTP 429, so the agent's own retry and
exception handling run unchanged. No call reaches a real model: there is no other code path.

Modes (RELAI_LLM_FAULT):
  rate_limit   every call raises openai.RateLimitError (429). Fail closed: nothing is "matched"
               to a success reply.
"""

from __future__ import annotations

import json
from pathlib import Path

TARGET = "openai-chat (langchain_openai.BaseChatOpenAI)"


class Journal:
    def __init__(self, path: Path):
        self.path = path
        self.n = 0

    def write(self, operation: str, payload: dict, outcome: str, response: dict) -> None:
        self.n += 1
        entry = {"target": TARGET, "operation": operation, "input": payload, "outcome": outcome,
                 "response": response, "seq": self.n}
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _messages(messages) -> list[dict]:
    out = []
    for m in messages or []:
        out.append({"role": getattr(m, "type", "unknown"), "content": str(getattr(m, "content", m))})
    return out


def _rate_limit_error():
    import openai
    try:
        import httpx2 as httpx  # the installed openai SDK names its httpx fork this way
    except ImportError:  # pragma: no cover
        import httpx
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx.Response(429, request=request, json={"error": {"message": "Rate limit reached",
                                                                     "type": "requests", "code": "rate_limit_exceeded"}})
    return openai.RateLimitError("Error code: 429 - Rate limit reached (relai fault stub)",
                                 response=response, body={"message": "Rate limit reached"})


def install(mode: str, journal_path: Path) -> None:
    if mode != "rate_limit":
        raise SystemExit(f"llm_fault: unknown RELAI_LLM_FAULT mode {mode!r}")
    from langchain_openai.chat_models.base import BaseChatOpenAI

    journal = Journal(journal_path)

    def record(self, operation, messages):
        error = _rate_limit_error()
        journal.write(operation, {"model": getattr(self, "model_name", None),
                                  "temperature": getattr(self, "temperature", None),
                                  "messages": _messages(messages)},
                      "error", {"error_type": type(error).__name__, "status": 429, "message": str(error)})
        return error

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        raise record(self, "generate", messages)

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        raise record(self, "agenerate", messages)

    def _stream(self, messages, stop=None, run_manager=None, **kwargs):
        raise record(self, "stream", messages)
        yield  # pragma: no cover

    async def _astream(self, messages, stop=None, run_manager=None, **kwargs):
        raise record(self, "astream", messages)
        yield  # pragma: no cover

    BaseChatOpenAI._generate = _generate
    BaseChatOpenAI._agenerate = _agenerate
    BaseChatOpenAI._stream = _stream
    BaseChatOpenAI._astream = _astream
