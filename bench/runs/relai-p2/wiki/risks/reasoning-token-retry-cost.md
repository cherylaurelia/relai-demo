# Empty responses from reasoning models are retried at full price up to 10 times

Mechanism: `create_chat_completion` retries empty responses and errors up to 10 times (1 when streaming to a websocket); costs are recorded only on success; the report call is capped at SMART_TOKEN_LIMIT, which reasoning tokens also consume.
Trigger: reasoning model exhausting its budget on thinking; invalid API key.
Observable failure: large hidden spend, long hangs before an error, truncated reports, under-reported `get_costs()`.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: report-meets-word-target
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/utils/llm.py:109 (checked); gpt_researcher/config/variables/default.py:14 (reviewer-reported).
