# Appended References list every URL seen, not the ones used

Mechanism: URLs are added to `visited_urls` before they are scraped. `add_references` then appends the whole sorted set as "## References". Failed scrapes, short or blocked pages and pages whose chunks were all filtered out stay in the set. Detailed reports also seed it with the user's `source_urls`. For local documents the set is empty, so a bare heading is appended.
Trigger: Any detailed report, or any caller using `add_references`.
Observable failure: The reference list names pages that were never read or used. A reader cannot tell which reference supports which claim. Local-document reports get an empty References section.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: references-list-used-sources, cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/researcher.py:809-810; gpt_researcher/actions/markdown_processing.py:111; backend/report_type/detailed_report/detailed_report.py:89,200-201; ISSUE_BACKLOG.md #1276, #1119, #565

## Probes

None yet.
