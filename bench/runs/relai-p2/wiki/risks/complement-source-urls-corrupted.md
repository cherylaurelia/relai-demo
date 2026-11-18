# Complementing source_urls with web search corrupts the added context

Mechanism: `_get_context_by_web_search` returns a joined string; the caller does `research_data += ' '.join(additional_research)`, inserting a space between every character.
Trigger: `source_urls` with `complement_source_urls=True`.
Observable failure: supplemental web context becomes "S o u r c e : h t t p s …"; its citations are unusable.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: report-grounded-in-provided-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/skills/researcher.py:155-158 and the web-search return path (`return combined_context` string), both checked.
