I found 18 likely failure points in gpt-researcher (snapshot `9ad2148`). Several are definite bugs I confirmed in the code. The committed benchmark results also show the research agent losing to a plain-search baseline more often than the project's docs say. This was a read of the code, prompts, docs, saved results and issue summaries only; I didn't run the agent.

## Top findings

1. **The multi-agent pipeline can't start.** Its graph refers to `self._route_fact_check` and `self._route_draft_review`, and neither method exists (`multi_agents/agents/orchestrator.py:102`, `editor.py:140`). Every multi-agent run should fail with an AttributeError before doing any research. The unit tests check those routing helpers in isolation, so they don't catch this.
2. **"Local documents" research still searches the web.** Before planning, the agent always runs one web search, whatever source the user chose (`gpt_researcher/skills/researcher.py:64-70`). The deep_agents scoping tool is always web too (`deep_agents/tools.py:35`). Private topic names go to a third-party search API, and the outline is shaped by web results. Users have reported this (#1004, #1334).
3. **Hybrid mode can write a confident report with no sources.** When both the local and web passes find nothing, the empty results are wrapped into a non-empty string. The writer's "I could not gather any sources" check therefore never fires (`researcher.py:184`, `prompts.py:563`, `writer.py:83`).
4. **With MCP tools configured, the model's own text becomes a source.** The model's reply, written before it saw any tool output, is stored as evidence titled "LLM Analysis" (`gpt_researcher/mcp/research.py:137-144`).
5. **Failures are swallowed.**
   - `generate_report` prints the error and returns an empty report (`actions/report_generation.py:306-309`).
   - Failed sub-queries return nothing, so a report built from part of its research looks complete.
6. **Citations are weak, and the saved benchmark results show it.**
   - The prompt demands APA author and date, but the context it gets has neither.
   - In the 10-task DeepResearch Bench run, about 44% of cited claims weren't supported by the cited page.
   - The baseline won on citation quality in 6 of 8 report head-to-heads.
7. **It falls behind the baseline on recent facts, and the docs don't report this.**
   - Recency coverage was 58–70% against the baseline's 79–83%.
   - Stale or wrong answers were 4–8 per run against 2.
   - FRAMES was also lower. The documented "83% vs 83%" SimpleQA parity uses one favourable run.
8. **Smaller confirmed bugs:**
   - With `source_urls` plus `complement_source_urls`, the added web context gets a space between every character.
   - Deep research crashes when the model returns no search queries.
   - Any human plan feedback containing the letters "no" (for example "not enough on cost") is treated as approval.
   - The plan-revision limit reads the wrong field, so it never stops the loop.
   - Multi-agent reports requested over the REST API come out as a single character.

The other risks, all rated with evidence in the wiki, are:
- The planner putting its guessed answer into its own searches (seen in SimpleQA misses).
- Prompt injection from scraped pages.
- Concurrent sub-queries losing sources they share.
- Some report types ignoring the language setting.
- Hidden cost from empty reasoning-model replies being retried up to 10 times.
- Human feedback from the web UI never arriving.

One earlier lead turned out to be wrong: an empty or missing local-docs folder doesn't quietly fall back to the web. It raises an error (`gpt_researcher/document/document.py:57`).

## Questions I would have asked you
These are recorded in the wiki and on the board with my recommendations; none of them blocks anything.
1. **Which part should we evaluate first?** The core researcher, multi-agent, deep_agents or the backend chat. I'd start with the core researcher on web and hybrid sources.
2. **May local-document research contact the web at all, even for planning?** I'd say no. This decides whether finding 2 is a privacy defect.
3. **Is "say so when nothing was found" intended behavior?** It currently rests only on a code comment. I'd confirm it as a requirement.
4. **When a multi-agent revision limit is reached, should the run fail or publish with a warning?** I'd publish with a warning.

All 18 risks are marked "proposed" and need your call on which to pursue.

## Coverage and limits
- Four parallel reviewers covered the core pipeline and prompts, retrievers/scrapers/MCP, multi-agent/deep_agents/backend, and the existing evals and issues.
- I re-read the code behind every finding above and the benchmark numbers in findings 6–7. Points I didn't re-read myself are marked "reviewer-reported" on their wiki pages.
- I didn't cover the frontend or terraform, and didn't read the full issue bodies or the benchmark grading code.
- Nothing was executed, so the crashes are inferred from reading the code. The cause of the stale-facts gap is a guess.

## What I created
I set up a new `relai/` folder; nothing is committed:
- `relai/wiki/` holds 8 requirements, 18 risks, 4 open questions and an index; the wiki checker passes.
- `relai/STATUS.md` is the board.
- `relai/decisions.md` records the assumptions I made for you.
- `relai/UPSTREAM.md` records where the copied files came from.

The useful next step is to answer the four questions, then probe the top four risks (findings 1–4) with RELAI's `eval` skill. I can also walk you through the evidence for any risk.