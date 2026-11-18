# Hybrid mode writes a "sourced" report when both passes found nothing

Mechanism: in hybrid mode both context passes return `[]` on failure, and `join_local_web_documents` wraps them in a non-empty string ("Context from local documents: []..."); the writer's abstain guard only checks for an empty context.
Trigger: `report_source=hybrid` with search blocked/rate-limited and no relevant document chunks.
Observable failure: a confident report with no real sources, written from model memory, instead of the abstain message.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: abstain-when-no-evidence, report-grounded-in-provided-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/skills/researcher.py:180-184; gpt_researcher/prompts.py:563-565; gpt_researcher/skills/writer.py:82-83. Web-only mode does reach the guard when every retriever fails (researcher.py web-search path returns `[]`).
