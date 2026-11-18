# Human-in-the-loop feedback cannot arrive over the web UI

Mechanism: HumanAgent awaits `receive_text()` on a socket whose main loop is already receiving; the server drops inbound messages while a task runs; the human_feedback handler is a TODO.
Trigger: `include_human_feedback=true` from the web app.
Observable failure: the run hangs or silently accepts the plan.
Impact: medium. Confidence: medium. Triggerability: low.
Status: proposed
Threatens: multi-agent-human-feedback-applied
Found at: 9ad2148 (agent: multi_agents via backend)
Evidence: multi_agents/agents/human.py:29; backend/server/server_utils.py:184, :357 (reviewer-reported, not executed).
