# Deep research crashes when the model returns no search queries

Mechanism: The early return for `not serp_queries` (deep_research.py:406-414) references `all_learnings` etc., which are first assigned at lines 416-420.
Trigger: Query-generation output that parses to an empty list (malformed JSON or missing fields), more likely at depth > 1.
Observable failure: UnboundLocalError aborts the entire deep research job.
Impact: medium. Confidence: high. Triggerability: low.
Status: proposed
Threatens: 
Found at: fae2317 (agent: gpt_researcher (deep research))
Evidence: gpt_researcher/skills/deep_research.py:400-420
