# Failed research steps are swallowed and the report looks complete

Mechanism: `_process_sub_query` returns "" on any exception, retriever errors return `[]`, `generate_report` prints the error and returns "", intro/conclusion/subtopic steps return empty on error.
Trigger: rate limits, bad key, context too large, transient scraper failures.
Observable failure: a thinner report built from a fraction of sub-queries with no warning, or an empty report string with no error to the caller.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: abstain-when-no-evidence, report-meets-word-target
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/actions/report_generation.py:306-309 (checked); gpt_researcher/skills/researcher.py:642-651 (reviewer-reported). Issues #1275, #1579, #1764.
