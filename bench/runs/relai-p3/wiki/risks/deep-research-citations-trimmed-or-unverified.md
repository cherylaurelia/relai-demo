# Deep research trims cited learnings first and accepts unverified source URLs

Mechanism: Learnings with citations are placed before raw context and `trim_context_to_word_limit` keeps from the end, so cited learnings are dropped first (deep_research.py:213-231,611-621); LLM-supplied `sourceUrl` is not checked against visited URLs (152-164); nested researchers drop query_domains and language (433-445) and lose the original query at depth > 1 (537-540).
Trigger: Large deep-research runs exceeding ~25k words of context; domain-restricted or non-English requests.
Observable failure: Report built on uncited raw text with possibly hallucinated citation URLs, drift from the original question, ignored domain restrictions.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: cite-only-provided-sources, write-in-requested-language
Found at: fae2317 (agent: gpt_researcher (deep research))
Evidence: gpt_researcher/skills/deep_research.py:152-164,213-231,433-445,537-540,611-621
