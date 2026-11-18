# Multi-agent fact-check has no sources and treats LLM failure as approval

Mechanism: fact_checker.py:18-27 sends only the draft, not the research context, so checks rely on model memory. `call_model` returns None on any exception (agents/utils/llms.py:34-36); the fact-checker then returns `fact_check_notes: None`, which routes as accept. The writer may revise only intro/conclusion (writer.py:40), so section-body issues cannot be fixed.
Trigger: Any API error, rate limit or context overflow during fact-checking; errors located in section bodies.
Observable failure: Report ships as fact-checked when it was not, or revision loops without progress.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: multi-agent-follows-guidelines
Found at: fae2317 (agent: multi_agents)
Evidence: multi_agents/agents/fact_checker.py:18-27; multi_agents/agents/utils/llms.py:29-36; multi_agents/agents/writer.py:40

Currently masked by multi-agent-graph-undefined-routers; becomes live once the routers are wired.
