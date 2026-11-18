# REST multi_agents reports are written as a single character

Mechanism: for `multi_agents`, `run_agent` returns a string; `write_report` indexes `report_information[0]` and returns `"report": ""`.
Trigger: POST /report/ with `report_type=multi_agents` (currently also blocked by [the graph build crash](multi-agent-graph-build-crash.md)).
Observable failure: DOCX/PDF containing one character; empty report text in the response.
Impact: medium. Confidence: medium. Triggerability: low.
Status: proposed
Threatens: report-meets-word-target
Found at: 9ad2148 (agent: backend)
Evidence: backend/server/app.py:303-304, :321 (checked); backend/server/websocket_manager.py:180-183 (reviewer-reported).
