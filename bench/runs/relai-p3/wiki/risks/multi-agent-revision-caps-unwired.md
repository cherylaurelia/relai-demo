# Multi-agent revision caps are not enforced

Mechanism: The plan edge checks `revisions_count`, which nothing writes (HumanAgent writes `plan_revision_count`); `max_fact_check_revisions` / `max_draft_revisions` are never read; the routers that do read caps raise errors instead of force-accepting.
Trigger: Human keeps giving feedback, or a reviewer/fact-checker keeps flagging issues.
Observable failure: Unbounded loop, LangGraph recursion-limit error, or crash that discards a nearly finished report.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: multi-agent-follows-guidelines
Found at: fae2317 (agent: multi_agents)
Evidence: multi_agents/agents/orchestrator.py:88-99; multi_agents/agents/fact_review.py:16-21; multi_agents/agents/draft_review.py:24-29
