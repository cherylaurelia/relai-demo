# Deep-agents GPTR config is worse than raw search on recent facts

Mechanism: Measured on the recency benchmark; mechanism not diagnosed (thin date handling is a candidate: search results and scraped text carry no publish dates, prompts.py:307 asks to prefer new articles without dates to compare).
Trigger: Questions about fast-moving current events.
Observable failure: More wrong or stale answers and lower coverage than the baseline, at about 1.5-2x latency.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: 
Found at: fae2317 (agent: deep_agents)
Evidence: deep_agents/benchmark_results/recency_2026-07-04_18-54-47.json (wrong/stale 8 vs 2, coverage 0.583 vs 0.833); recency_2026-07-04_19-10-24.json (4 vs 2); recency_2026-07-04_22-11-41.json (6 vs 2); not mentioned in deep_agents/BENCHMARK.md or README.md

Historical benchmark evidence, 3 runs of 42 checkpoints; not a probe.
