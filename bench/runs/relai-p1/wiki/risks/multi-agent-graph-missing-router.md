# Multi-agent workflow references router methods that do not exist

Mechanism: The orchestrator and editor pass `self._route_fact_check` and `self._route_draft_review` to `add_conditional_edges`. Neither method is defined. The real routers (`route_fact_check`, `route_draft_review`) are module functions that are never wired in.
Trigger: Building the research team graph (`multi_agents/main.py`).
Observable failure: `AttributeError` before any research runs, so multi-agent mode cannot start. Existing tests exercise only the helper functions.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-human-feedback
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: multi_agents/agents/orchestrator.py:102; multi_agents/agents/editor.py:140; multi_agents/agents/fact_review.py:8; multi_agents/agents/draft_review.py:8

## Probes

None yet.
