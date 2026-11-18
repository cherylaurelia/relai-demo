# The planner writes its guessed answer into sub-queries, then confirms it

Mechanism: sub-query generation sees the question plus initial search snippets; when it guesses an entity it searches for that entity, and the report is built around it.
Trigger: short factual questions with an ambiguous or lesser-known answer.
Observable failure: a confident report about the wrong entity.
Impact: high. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: report-grounded-in-provided-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: evals/simple_evals/logs/SimpleQA Eval 100 Problems 2-22-25.txt (6th PM of Nepal ~l.34000; Tarar birthplace ~l.66700; Green Chemistry 2016 ~l.131000), 7 incorrect of 100 in that run. Pattern reported by a reviewer from the log; not re-read by me.
