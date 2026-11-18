# Scraped pages and MCP tool output can steer the report

Mechanism: page text is interpolated raw as `Information: "{context}"` with no delimiting or untrusted-content instruction; MCP tools are chosen and called from server-controlled descriptions with no allowlist.
Trigger: a page or tool result containing instructions ("ignore the above, cite …").
Observable failure: planted links or claims in the report; steered sub-queries; unintended MCP tool calls.
Impact: high. Confidence: medium. Triggerability: low.
Status: proposed
Threatens: report-grounded-in-provided-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/prompts.py:294; gpt_researcher/mcp/research.py:100-113 (reviewer-reported). Triggerability against real pages is unmeasured.
