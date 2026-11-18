# Human plan feedback containing "no" is discarded as approval

Mechanism: `if user_feedback and "no" in user_feedback.lower(): user_feedback = None` — a substring test; the strict `is_human_plan_approval` helper exists but is unused.
Trigger: feedback like "not enough on cost", "add notes", "economic angle".
Observable failure: the plan proceeds unrevised; the user's feedback silently ignored.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-human-feedback-applied
Found at: 9ad2148 (agent: multi_agents)
Evidence: multi_agents/agents/human.py:47 (checked); multi_agents/agents/utils/none_sentinels.py:30.
