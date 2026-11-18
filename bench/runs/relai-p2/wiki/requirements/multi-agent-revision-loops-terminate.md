# Multi-agent review loops stop at their caps with a clear outcome

Human plan review stops at `max_plan_revisions` with a clear error; revision loops do not run until a framework recursion limit.

Source: `multi_agents/README.md:69`; `multi_agents/agents/orchestrator.py:99` comment "bounded via task.max_fact_check_revisions".
What happens at the fact-check cap is unresolved: [revision cap outcome](../open-questions/revision-cap-outcome.md).
