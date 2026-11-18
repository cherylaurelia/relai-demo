# Plan feedback containing "no" anywhere is discarded as approval

Mechanism: `human.py` treats any feedback where `"no" in feedback.lower()` as approval. A strict `is_human_plan_approval` helper exists and is tested, but it is not used. The revision cap reads `revisions_count`, while the human node writes `plan_revision_count`, so `max_plan_revisions` never applies. `receive_text()` has no timeout.
Trigger: Feedback such as "add a section on technology", "not enough data" or "economy".
Observable failure: The feedback is ignored and the original plan proceeds. The documented revision cap never fires. A silent client hangs the run.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-human-feedback
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: multi_agents/agents/human.py:29,47; multi_agents/agents/orchestrator.py:89-97; tests/test_none_accept_sentinels.py:52-62

## Probes

None yet.
