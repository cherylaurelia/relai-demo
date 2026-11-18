# Human plan-revision cap never triggers

Mechanism: the graph edge reads `revisions_count` but the human node writes `plan_revision_count`; the documented `max_plan_revisions` is only used by an unwired helper.
Trigger: `include_human_feedback=true` and repeated feedback.
Observable failure: planner/human loop until LangGraph's recursion limit, a generic error instead of the documented clear one.
Impact: medium. Confidence: high. Triggerability: low.
Status: proposed
Threatens: multi-agent-revision-loops-terminate
Found at: 9ad2148 (agent: multi_agents)
Evidence: multi_agents/agents/orchestrator.py:88-96, :106; multi_agents/agents/human.py:50 (checked).
