# Writer LLM failures silently drop report parts

Mechanism: `generate_report`, `write_report_introduction` and `write_conclusion` catch exceptions and return `""`. Detailed reports skip an empty subtopic section without notice. A basic report becomes empty pdf, docx and md files. A streamed retry after a mid-stream failure re-streams into the same websocket.
Trigger: A provider error, timeout or rate limit while writing.
Observable failure: The report is missing its introduction, conclusion or sections, or is empty, and looks finished. Streamed output can be duplicated.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/actions/report_generation.py:58-60,110-112,155-157,290-307; backend/report_type/detailed_report/detailed_report.py:116

## Probes

None yet.
