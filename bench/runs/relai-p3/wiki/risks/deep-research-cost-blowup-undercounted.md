# Deep research cost grows multiplicatively and is under-reported

Mechanism: Recursion runs per result per level (deep_research.py:514-551) with breadth floored at 2, each spawning full nested GPTResearcher runs whose costs are never added to the parent; several LLM calls pass no cost_callback, so `research_costs` (line 601) understates spend. Non-streaming LLM calls retry up to 10 times on any error (utils/llm.py:110) and failed attempts are not costed.
Trigger: deep_research_depth >= 3 or higher breadth; provider errors causing retries.
Observable failure: Unexpectedly large bills and long runtimes while the displayed cost is lower than actual.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: 
Found at: fae2317 (agent: gpt_researcher (deep research))
Evidence: gpt_researcher/skills/deep_research.py:433-445,514-551,601; gpt_researcher/utils/llm.py:110,137

Dollar magnitude not measured.
