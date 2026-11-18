# APA citations demand metadata the context does not carry

Mechanism: the report prompt requires APA author/date references and "prioritize newer articles", but context chunks carry only Source, Title and Content; no check that cited URLs appear in the context.
Trigger: any web report.
Observable failure: invented authors/dates, citations whose page does not support the claim.
Impact: high. Confidence: medium. Triggerability: high.
Status: proposed
Threatens: report-grounded-in-provided-sources, references-match-used-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/prompts.py:280-289, :307 (reported by code review, not re-read line by line); deep_agents/benchmark_results/drb/gptr-deepagent_fact_result.txt valid_rate 0.560 (~44% of cited claims unsupported, n=10 tasks); deep_agents/benchmark_results/reports_2026-07-04_14-33-21_n8.json citation_quality win rate gptr 2 vs baseline 6 (checked). Issues #1276, #1572.
