# MCP tool selection can choose mutating tools

Mechanism: The LLM picks "EXACTLY" max_tools tools from untrusted descriptions (prompts.py:61,82) and research.py:100-113 executes them with model-chosen arguments; the fallback matches substrings like `get`/`list`/`view` (tool_selector.py:175-199). No read-only allowlist exists.
Trigger: An MCP server exposing write/delete tools alongside search tools, or a poisoned tool description.
Observable failure: A mutating tool is called during research.
Impact: high. Confidence: medium. Triggerability: low.
Status: proposed
Threatens: 
Found at: fae2317 (agent: gpt_researcher (MCP))
Evidence: gpt_researcher/prompts.py:54-83; gpt_researcher/mcp/tool_selector.py:56-69,175-199; gpt_researcher/mcp/research.py:100-113
