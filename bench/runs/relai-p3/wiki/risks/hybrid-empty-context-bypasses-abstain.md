# Hybrid mode with no results bypasses the empty-context guard

Mechanism: The writer abstains only when the joined context is blank (skills/writer.py:77-90). In hybrid mode `join_local_web_documents` wraps both parts in labels (prompts.py:566), so two empty results become the non-blank string "Context from local documents: []\n\nContext from web sources: []".
Trigger: `report_source=hybrid` with no local docs matching and web search failing (bad key, rate limit, blocked).
Observable failure: A full-length report with citations is written from no source material.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: state-insufficient-evidence, cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher)
Evidence: gpt_researcher/skills/researcher.py:171-184; gpt_researcher/prompts.py:564-566; gpt_researcher/skills/writer.py:77-90
