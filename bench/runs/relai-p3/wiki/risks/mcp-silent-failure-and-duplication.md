# MCP failures are silent and fast mode pastes one result set into every sub-query

Mechanism: Tool errors are logged and skipped (mcp/research.py:133-135); the retriever returns [] on any error (retrievers/mcp/retriever.py:141-143,190-193); user-facing messages need VERBOSE (default False). In the default `fast` strategy the single cached MCP result is appended unfiltered to every sub-query context (researcher.py:327-341,552-562,747-768). The 300s timeout is not enforced because the executor `with` block waits for the thread (retriever.py:284-286).
Trigger: Misconfigured or down MCP server; any multi-sub-query report with MCP.
Observable failure: User believes a private data source was used when it returned nothing; the same MCP text is repeated across sections and can crowd out web sources; long hangs.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: 
Found at: fae2317 (agent: gpt_researcher (MCP))
Evidence: gpt_researcher/mcp/research.py:133-135; gpt_researcher/retrievers/mcp/retriever.py:141-143,190-193,284-286; gpt_researcher/skills/researcher.py:552-562,747-768
