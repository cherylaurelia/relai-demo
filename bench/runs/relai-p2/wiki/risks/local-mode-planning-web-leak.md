# Local-document research still sends the query to web search and plans from web results

Mechanism: `plan_research` always runs a live search with `retrievers[0]` before sub-queries are generated, regardless of `report_source`; deep_agents' `quick_search` tool builds a GPTResearcher without `report_source`, so scoping is always web.
Trigger: `report_source=local` (or deep_agents `source=local`) on private material.
Observable failure: internal topic names go to a third-party search API; the outline and sub-queries are shaped by web snippets, not the private corpus.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: local-source-stays-local
Found at: 9ad2148 (agents: gpt_researcher, deep_agents)
Evidence: gpt_researcher/skills/researcher.py:64-70; deep_agents/tools.py:35. User reports: #1004, #1334 ("My Documents" still web-searches). Note: an earlier hypothesis that empty DOC_PATH falls back to web scraping was checked and rejected — `DocumentLoader.load` raises (gpt_researcher/document/document.py:57).
