# Deep-agents reports: about 44% of citations fail verification

Mechanism: The deep_agents GPTR configuration produces many more citations, but the share that FACT verification accepts barely moves; the headline reports the count gain.
Trigger: Long-form research reports through deep_agents (DeepResearch Bench).
Observable failure: Of 62.9 citations per report, 35.2 were judged valid (valid_rate 0.56); baseline 0.54.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cite-only-provided-sources
Found at: fae2317 (agent: deep_agents)
Evidence: deep_agents/benchmark_results/drb/gptr-deepagent_fact_result.txt:1-3; baseline-tavily-deepagent_fact_result.txt:1-3; BENCHMARK.md:33-38,155-158 (FACT re-fetches URLs, so blocked sites count as invalid for both arms)

Historical benchmark evidence, not a probe; part of the invalid share may be fetch failures rather than unsupported claims.
