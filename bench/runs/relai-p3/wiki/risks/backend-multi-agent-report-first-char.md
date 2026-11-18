# REST API saves only the first character of multi-agent reports

Mechanism: For multi_agents, run_agent returns a string (websocket_manager.py:180-183), but app.py:303-304 writes `report_information[0]` to DOCX and PDF.
Trigger: POST report generation with report_type=multi_agents.
Observable failure: DOCX/PDF containing one character.
Impact: low. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: 
Found at: fae2317 (agent: backend)
Evidence: backend/server/app.py:303-305; backend/server/websocket_manager.py:180-183

Low impact while multi-agent-graph-undefined-routers prevents any multi-agent report.
