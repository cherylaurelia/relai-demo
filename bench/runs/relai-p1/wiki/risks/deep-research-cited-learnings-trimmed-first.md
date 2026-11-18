# Deep research drops its cited learnings first when context is trimmed

Mechanism: The final context is `[learnings with [Source: url]] + raw context`. `trim_context_to_word_limit` keeps the most recent items, so the cited learnings at the front are dropped first. Citations are also keyed by learning text, and an LLM-returned `sourceUrl` is never checked against the URLs actually visited.
Trigger: Any deep research run whose raw context exceeds about 25k words. That is common at the default breadth and depth.
Observable failure: The writer sees only uncited raw text, or citations to URLs that were never visited. The report's citations become thin or wrong.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/deep_research.py:154-164,213-231,611-624; deep_agents/BENCHMARK.md:38 (56% citation precision in a 10-task run of the deep_agents variant)

## Probes

None yet.
