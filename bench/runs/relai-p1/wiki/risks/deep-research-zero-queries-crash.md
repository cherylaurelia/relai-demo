# Deep research crashes when query generation returns nothing

Mechanism: When `generate_search_queries` returns `[]`, `deep_research` returns `all_learnings` and other locals before assigning them, which raises `UnboundLocalError`. The recursive call is not wrapped in a try.
Trigger: The strategic model returns JSON the parser rejects (wrong keys, plain strings), or reasoning uses up the 4000-token budget.
Observable failure: The whole deep research run aborts after its spend, and all learnings gathered so far are lost.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/deep_research.py:400-420,543; ISSUE_BACKLOG.md #1787

## Probes

None yet.
