# Say so when search results cannot answer the query

When the gathered results are insufficient to answer the query, the answer says so clearly
instead of answering from nothing.

Source: quick-summary prompt `gpt_researcher/prompts.py:550`; the report writer abstains when
context is entirely empty (`gpt_researcher/skills/writer.py:77-90`, code evidence of intent).
Scope beyond quick search and fully-empty context is unresolved: see
[thin-evidence-abstain-or-opine](../open-questions/thin-evidence-abstain-or-opine.md).
