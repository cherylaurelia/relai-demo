# Multi-agent pipeline wires graph edges to methods that do not exist

Mechanism: `ChiefEditorAgent._add_workflow_edges` passes `self._route_fact_check` (multi_agents/agents/orchestrator.py:100-104) and `EditorAgent._create_workflow` passes `self._route_draft_review` (multi_agents/agents/editor.py:138-142); neither method is defined. The real routers `route_fact_check` / `route_draft_review` in fact_review.py / draft_review.py are never imported.
Trigger: Any run of `python -m multi_agents.main` or `report_type=multi_agents` from the backend.
Observable failure: AttributeError while building the graph; no report is produced.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-follows-guidelines
Found at: fae2317 (agent: multi_agents)
Evidence: multi_agents/agents/orchestrator.py:100-106; multi_agents/agents/editor.py:138-142; grep shows the names only at call sites

Static verification only: an import attempt failed earlier on a missing dependency (`json_repair`), so the AttributeError was not observed at runtime.
