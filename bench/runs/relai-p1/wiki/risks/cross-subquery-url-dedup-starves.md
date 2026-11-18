# Concurrent sub-queries race for URLs, leaving later ones without sources

Mechanism: Sub-queries run concurrently and share `visited_urls`. The first sub-query to claim a URL scrapes it and compresses it against its own query only. Other sub-queries that found the same URL get nothing. A URL whose scrape failed is never retried.
Trigger: Related sub-queries whose search results overlap. That is the normal case.
Observable failure: Some sub-queries log "No content found". Their aspects of the question are covered thinly or not at all, with no warning in the report.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/researcher.py:379-385,801-822,867

## Probes

None yet.
