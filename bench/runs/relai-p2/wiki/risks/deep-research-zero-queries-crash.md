# Deep research crashes when query generation returns nothing

Mechanism: the zero-queries early return reads `all_learnings` etc. before they are assigned.
Trigger: the model returns non-JSON or no `researchGoal` for search-query generation (common with non-OpenAI / reasoning models, cf. issues #1787, #1306).
Observable failure: UnboundLocalError ends the deep research run.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: abstain-when-no-evidence
Found at: 9ad2148 (agent: gpt_researcher deep research)
Evidence: gpt_researcher/skills/deep_research.py:406-420 (checked). tests/skills/test_deep_research_empty_results.py covers a different path.
