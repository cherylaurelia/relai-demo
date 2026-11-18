# Multi-agent pipeline cannot build its LangGraph

Mechanism: conditional edges reference `self._route_fact_check` (orchestrator) and `self._route_draft_review` (editor); neither method exists. The tested helpers `route_fact_check` / `route_draft_review` are never wired in.
Trigger: any multi-agent run (`multi_agents/main.py`, LangGraph dev server, web UI `report_type=multi_agents`).
Observable failure: AttributeError while building the graph; no report is produced.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-revision-loops-terminate
Found at: 9ad2148 (agent: multi_agents)
Evidence: multi_agents/agents/orchestrator.py:102; multi_agents/agents/editor.py:140; no `def _route_fact_check` / `def _route_draft_review` anywhere under multi_agents/ (grep, checked). Unit tests load the helpers in isolation, so CI does not catch it. Static reading only; not executed.
