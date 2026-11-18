# Reviewer or fact-checker errors count as approval

Mechanism: `call_model` logs and returns `None` on any exception. The reviewer and fact-checker treat a `None` response as "no revisions needed", and the router accepts the draft.
Trigger: An API error, rate limit or wrong model or provider pairing during review (`task['model']` is paired with `cfg.smart_llm_provider`).
Observable failure: A draft is published as reviewed and fact-checked although no check ran.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: multi_agents/agents/utils/llms.py:20-36; multi_agents/agents/reviewer.py:44,61-63; multi_agents/agents/fact_checker.py:31,49-55

## Probes

None yet.
