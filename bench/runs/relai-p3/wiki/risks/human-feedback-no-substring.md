# Human plan feedback containing "no" anywhere is treated as approval

Mechanism: human.py:47 discards feedback when `"no" in user_feedback.lower()`; the strict helper `is_human_plan_approval` (agents/utils/none_sentinels.py:30-42) exists but is unused.
Trigger: Feedback such as "not enough on cost", "nothing on Asia", "know the market".
Observable failure: Plan is not revised; the user's correction is silently dropped.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: multi-agent-follows-guidelines
Found at: fae2317 (agent: multi_agents)
Evidence: multi_agents/agents/human.py:39-48; multi_agents/agents/utils/none_sentinels.py:30-42
