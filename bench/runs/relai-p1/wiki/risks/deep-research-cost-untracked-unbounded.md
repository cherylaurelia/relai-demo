# Deep research spend is under-reported and has no cap

Mechanism: Nested `GPTResearcher` costs are never added to the parent. Query generation, planning and result processing calls pass no `cost_callback`. Failed or retried calls are not counted. The breadth × depth recursion has no budget or time limit, its floor is 2 branches, and levels below the first run serially.
Trigger: Any deep research run, especially with breadth or depth above the defaults.
Observable failure: The displayed "Total Research Costs" is well below the real spend. Long runs cannot be stopped by budget.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/deep_research.py:249,280,320,366,425-445,543,601-608; gpt_researcher/utils/llm.py:138

## Probes

None yet.
