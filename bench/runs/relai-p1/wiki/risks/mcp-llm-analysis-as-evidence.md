# MCP's pre-tool LLM text is injected as a source

Mechanism: MCP research makes one tool-bound LLM call, runs the tools, and never returns their output to the model. It then adds the model's own pre-tool `response.content` as a result titled "LLM Analysis". The researcher stores that result next to the real tool results as MCP context.
Trigger: Any research with an MCP retriever where the model writes text along with its tool calls.
Observable failure: Planning text or claims from model memory enter the context as evidence and can be cited as "LLM Analysis".
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/mcp/research.py:79-144; gpt_researcher/skills/researcher.py:444-457,757

## Probes

None yet.
