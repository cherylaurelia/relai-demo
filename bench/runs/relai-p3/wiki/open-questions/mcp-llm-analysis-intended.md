# Is the MCP "LLM Analysis" result meant to be a citable source?

Unclear: `gpt_researcher/mcp/research.py:137-144` deliberately appends the model's own response as
a research result; no doc says whether reports may cite it.

Why it matters: if unintended, [mcp-llm-analysis-cited-as-source](../risks/mcp-llm-analysis-cited-as-source.md)
is a high-impact attribution defect; if intended, it still needs labelling as non-evidence.

Recommended: exclude it from report context, or label it as model analysis that must not be cited.
