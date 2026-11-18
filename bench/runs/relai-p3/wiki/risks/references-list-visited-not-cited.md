# Source lists include every visited URL, not the cited ones

Mechanism: URLs join `visited_urls` when chosen for scraping, before fetch or relevance filtering (researcher.py:809-811). Detailed reports append `add_references(report, visited_urls)` (detailed_report.py:200); `get_source_urls()` returns all visited URLs to the API (agent.py:733-739, backend/server/app.py:310) and deep_agents appends them as Sources (deep_agents/tools.py:73-75).
Trigger: Any run where some scrapes fail or pages are filtered as irrelevant.
Observable failure: Authoritative-looking reference/source lists containing pages never read or cited.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: single-deduplicated-reference-list
Found at: fae2317 (agent: gpt_researcher, deep_agents, backend)
Evidence: gpt_researcher/skills/researcher.py:809-811; gpt_researcher/actions/markdown_processing.py:94-113; backend/report_type/detailed_report/detailed_report.py:200
