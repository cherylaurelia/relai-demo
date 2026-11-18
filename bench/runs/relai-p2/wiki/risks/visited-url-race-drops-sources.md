# Concurrent sub-queries lose overlapping sources

Mechanism: `_get_new_urls` adds a URL to the shared `visited_urls` before scraping; sub-queries run concurrently, so overlapping hits go only to the first claimant and failed scrapes are blacklisted for the run.
Trigger: sub-queries whose searches return overlapping URLs (typical).
Observable failure: some sub-queries get no content; the same URLs still appear in reference lists built from `visited_urls`.
Impact: medium. Confidence: medium. Triggerability: high.
Status: proposed
Threatens: references-match-used-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/skills/researcher.py:808-811 (checked); gpt_researcher/actions/markdown_processing.py:111 add_references(visited_urls) (reviewer-reported; used by detailed reports).
