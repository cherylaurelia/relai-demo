# Which entry point is the agent under evaluation?

Unclear: the repository holds four agent surfaces — core `GPTResearcher` (CLI/pip/web), `multi_agents` (LangGraph), `deep_agents`, and the backend chat agent — with different failure profiles. Recent benchmark work focuses on deep_agents.
Why it matters: decides which risks to probe first and what harness to build. Multi-agent risks are moot until its graph builds.
Recommendation: core `GPTResearcher` with `research_report` over web and hybrid sources first (widest use, most of the high-impact risks), deep_agents second.
