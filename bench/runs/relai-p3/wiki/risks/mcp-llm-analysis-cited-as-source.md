# MCP model's own pre-tool prose enters context labelled as a source

Mechanism: `gpt_researcher/mcp/research.py:137-144` appends `response.content` of the tool-selecting LLM call as a result titled "LLM Analysis: {query}" with href `mcp://llm_analysis`; researcher.py renders it as `*Source: ...*` inside report context. Only a single `ainvoke` occurs, so the text was written without seeing tool results.
Trigger: Any research run with MCP retrievers configured where the model emits text alongside tool calls.
Observable failure: Unverified model-generated claims appear in the report cited as if retrieved; `mcp://` pseudo-URLs can appear in source lists.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher (MCP))
Evidence: gpt_researcher/mcp/research.py:79,137-144; gpt_researcher/skills/researcher.py:757-762
