# Is the multi-agent (LangGraph) mode a supported surface to evaluate?

At 0595cd3 the multi-agent graph references router methods that do not exist ([multi-agent-graph-missing-router](../risks/multi-agent-graph-missing-router.md)), so it cannot start. multi_agents/README.md still documents it as a feature.

Why it matters: if it is supported, it needs a smoke test and tests for its feedback and review loops (three high-impact risks). If it is deprecated, those risks should be rejected and the docs changed.

Choices: supported (fix it and add tests) / experimental (smoke test only) / deprecated (retire the risks).

Recommended: experimental, with a single smoke test until the maintainers decide.
Blocking: no
