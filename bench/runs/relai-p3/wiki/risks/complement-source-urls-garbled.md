# Complementing source URLs with web search garbles the web context

Mechanism: researcher.py:157-158 does `research_data += ' '.join(additional_research)` where `additional_research` is already a string, inserting a space between every character.
Trigger: `source_urls` plus `complement_source_urls=True`.
Observable failure: Web half of the context reads "T h e  m a r k e t ..."; the report relies only on the given URLs or misquotes.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher)
Evidence: gpt_researcher/skills/researcher.py:155-158,385-392
