# Hybrid research with no sources writes a report from model memory

Mechanism: When nothing is gathered, `_get_context_by_web_search` returns `[]`. `join_local_web_documents` interpolates it, so the context becomes the literal text "Context from local documents: []\n\nContext from web sources: []". The writer's no-source guard only abstains on blank context, so it does not fire.
Trigger: `report_source=hybrid` while retrieval fails or the similarity filter drops everything (a bad search key, rate limiting, an unreachable document URL).
Observable failure: A confident-looking report with no real sources, instead of the "could not gather any source material" message the other modes return.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/researcher.py:180-184, 393-396; gpt_researcher/prompts.py:566; gpt_researcher/skills/writer.py:82-88

## Probes

None yet.
