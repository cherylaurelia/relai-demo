# Thin or partial context still yields a long, opinionated report

Mechanism: Retrieval failures are swallowed at every layer (tavily_search.py:145-147, scraper.py:168-170, researcher.py:393-396) and the 0.42 relevance threshold can drop most chunks (compression.py:134-136). The guard fires only on a completely empty context. The report prompt demands at least TOTAL_WORDS (1200) words, "as long as you can", and that the model "MUST determine your own concrete and valid opinion", with no instruction to flag insufficient evidence.
Trigger: One or two short snippets survive (partial rate limiting, bot-blocked pages, niche or non-English query).
Observable failure: A confident 1200-word report padded from model knowledge, with claims lacking or misattributing citations.
Impact: high. Confidence: medium. Triggerability: high.
Status: proposed
Threatens: state-insufficient-evidence, cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher)
Evidence: gpt_researcher/prompts.py:296-302; gpt_researcher/config/variables/default.py:6,23; gpt_researcher/retrievers/tavily/tavily_search.py:145-147; gpt_researcher/skills/researcher.py:393-396
