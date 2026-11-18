# MCP research stores the model's own pre-tool text as a cited source

Mechanism: after tool selection the LLM's `response.content` is appended to research results as `{"title": "LLM Analysis: …", "href": "mcp://llm_analysis"}`; it then enters the context alongside real evidence.
Trigger: any run with MCP retrievers configured.
Observable failure: unverified, possibly hallucinated claims appear in the report as though sourced; reference may show an `mcp://` pseudo-URL or none.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: report-grounded-in-provided-sources, references-match-used-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/mcp/research.py:137-144.
