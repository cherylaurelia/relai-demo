# How should the agent treat instructions inside scraped pages and MCP tool output?

ISSUE_BACKLOG.md (2026-06-25) records a threat-model decision: the backend is operator-run with no built-in auth by design. That covers who can call the server. It does not cover third-party web content that any query can pull in. Page text, PDFs and MCP tool output reach the report prompt raw ([untrusted-page-prompt-injection](../risks/untrusted-page-prompt-injection.md)). MCP's pre-tool LLM text is also stored as evidence ([mcp-llm-analysis-as-evidence](../risks/mcp-llm-analysis-as-evidence.md)).

Why it matters: it decides whether injection probes belong in the eval suite, and whether MCP "LLM Analysis" text may be cited.

Choices: (a) retrieved content is data and the report must not follow instructions in it; (b) out of scope, because operators choose their sources.

Recommended: (a). Probe it with one or two adversarial pages in a mocked retriever.
Blocking: no
