# Retrieved web, document and MCP text is spliced unfenced into prompts

Mechanism: Context goes into `Information: "{context}"` (prompts.py:294) with no delimiter or instruction to treat it as data; search snippets go into the query-planning prompt (prompts.py:241); MCP tool descriptions go into tool selection (prompts.py:59). clean_soup does not strip hidden text.
Trigger: A page ranking for the query (or a user-supplied URL / uploaded doc / MCP result) containing instructions.
Observable failure: Steered report content (promotion, misinformation, injected links), attacker-chosen sub-queries, or a different MCP tool selected.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher, deep_agents, chat)
Evidence: gpt_researcher/prompts.py:241,294,346; gpt_researcher/scraper/utils.py:108-120; backend/chat/chat.py:216

Mechanism confirmed; exploitability against a given model not probed.
