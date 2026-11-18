# Time-sensitive answers are stale or invented

Mechanism (hypothesis): context has no publication dates, scrape order is shuffled and compression keeps early chunks, so older pages can win; the writer fills gaps (e.g. prices) from memory.
Trigger: questions about recent releases, prices or events.
Observable failure: outdated or fabricated current facts stated confidently.
Impact: high. Confidence: medium. Triggerability: high.
Status: proposed
Threatens: report-grounded-in-provided-sources
Found at: 9ad2148 (agent: deep_agents with GPT Researcher tools)
Evidence: deep_agents/benchmark_results/recency_2026-07-04_{18-54-47,19-10-24,22-11-41}.json — gptr coverage 0.583/0.702/0.643 vs baseline 0.833/0.786/0.821, wrong_stale 8/4/6 vs 2/2/2 over 42 checkpoints (checked). Mechanism is not confirmed; it is the reviewers' inference from gpt_researcher/scraper and context/compression.py.
