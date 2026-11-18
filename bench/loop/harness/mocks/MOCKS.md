# Mocks

| Mock | Replaces | Real host / functions | Why | Authorization |
| --- | --- | --- | --- | --- |
| `llm_fault.py` (scenario `"fault"` or `RELAI_LLM_FAULT`: `rate_limit`) | LangChain's OpenAI chat model internals: `langchain_openai.chat_models.base.BaseChatOpenAI._astream`, `_agenerate`, `_stream`, `_generate` | `api.openai.com/v1/chat/completions` | Fault injection: every chat call raises the SDK's own `openai.RateLimitError` (429), so the agent's code (GenericLLMProvider, `create_chat_completion`'s retry loop, `generate_report`'s fallback and exception handling) runs unchanged. Not exercised: the OpenAI SDK's own HTTP retries and LangChain's Responses-API route (`use_responses_api`, off in the default config). | The user's request of 2026-11-17 ("make the writer LLM call fail with a stub"); `relai/decisions.md` |

Fail closed: the stub has no success reply; every call is journaled to
`<trial>/agent/mock-journal.jsonl` with `outcome: "error"`. Installed only by
`relai/harness/adapter.py` when the scenario names a fault; project code never imports it. Other
providers or routes are not stubbed. In a trial, the sandbox denies all outbound IP traffic
(`run_trial.py`), so an uncovered call fails instead of escaping, and the test's check errors on
a missing writer call.
