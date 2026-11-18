# Which entry points should evaluation cover?

Unclear: the repository ships several agents — the core `GPTResearcher` report types
(research, detailed, deep, resource, outline, custom), `multi_agents` (LangGraph), `multi_agents/ag2`,
`deep_agents`, the backend chat, and an MCP server. `multi_agents` cannot build its graph
([multi-agent-graph-undefined-routers](../risks/multi-agent-graph-undefined-routers.md)), which
suggests it is not currently exercised.

Why it matters: sets which risks get tests first and whether multi-agent risks are worth probing
or should be retired.

Recommended: core `research_report` and `deep` first, then detailed reports and `deep_agents`;
treat `multi_agents` as out of scope until its graph is fixed.
