# Truncated model output is accepted as a finished report

Mechanism: Nothing checks `finish_reason` or `stop_reason`. `SMART_TOKEN_LIMIT` (12000) and `STRATEGIC_TOKEN_LIMIT` (8000) also cover reasoning tokens on the default reasoning models, and deep research uses 4000 with high reasoning effort. Empty completions are retried up to 10 times, and each retry is billed.
Trigger: A large `TOTAL_WORDS`, a long section or conclusion, or high reasoning effort.
Observable failure: The report ends mid-sentence, or an empty response is retried and billed repeatedly before the run fails.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/utils/llm.py:110,128-138; gpt_researcher/config/variables/default.py:10-13; ISSUE_BACKLOG.md #1271

## Probes

None yet.
