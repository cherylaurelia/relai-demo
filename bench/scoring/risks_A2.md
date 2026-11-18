# Final answer to the user

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

---

# Risk page citation-metadata-fabricated.md

# APA citations demand metadata the context does not carry

Mechanism: the report prompt requires APA author/date references and "prioritize newer articles", but context chunks carry only Source, Title and Content; no check that cited URLs appear in the context.
Trigger: any web report.
Observable failure: invented authors/dates, citations whose page does not support the claim.
Impact: high. Confidence: medium. Triggerability: high.
Status: proposed
Threatens: report-grounded-in-provided-sources, references-match-used-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/prompts.py:280-289, :307 (reported by code review, not re-read line by line); deep_agents/benchmark_results/drb/gptr-deepagent_fact_result.txt valid_rate 0.560 (~44% of cited claims unsupported, n=10 tasks); deep_agents/benchmark_results/reports_2026-07-04_14-33-21_n8.json citation_quality win rate gptr 2 vs baseline 6 (checked). Issues #1276, #1572.


---

# Risk page complement-source-urls-corrupted.md

# Complementing source_urls with web search corrupts the added context

Mechanism: `_get_context_by_web_search` returns a joined string; the caller does `research_data += ' '.join(additional_research)`, inserting a space between every character.
Trigger: `source_urls` with `complement_source_urls=True`.
Observable failure: supplemental web context becomes "S o u r c e : h t t p s …"; its citations are unusable.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: report-grounded-in-provided-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/skills/researcher.py:155-158 and the web-search return path (`return combined_context` string), both checked.


---

# Risk page deep-research-zero-queries-crash.md

# Deep research crashes when query generation returns nothing

Mechanism: the zero-queries early return reads `all_learnings` etc. before they are assigned.
Trigger: the model returns non-JSON or no `researchGoal` for search-query generation (common with non-OpenAI / reasoning models, cf. issues #1787, #1306).
Observable failure: UnboundLocalError ends the deep research run.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: abstain-when-no-evidence
Found at: 9ad2148 (agent: gpt_researcher deep research)
Evidence: gpt_researcher/skills/deep_research.py:406-420 (checked). tests/skills/test_deep_research_empty_results.py covers a different path.


---

# Risk page human-feedback-substring-no.md

# Human plan feedback containing "no" is discarded as approval

Mechanism: `if user_feedback and "no" in user_feedback.lower(): user_feedback = None` — a substring test; the strict `is_human_plan_approval` helper exists but is unused.
Trigger: feedback like "not enough on cost", "add notes", "economic angle".
Observable failure: the plan proceeds unrevised; the user's feedback silently ignored.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-human-feedback-applied
Found at: 9ad2148 (agent: multi_agents)
Evidence: multi_agents/agents/human.py:47 (checked); multi_agents/agents/utils/none_sentinels.py:30.


---

# Risk page human-feedback-web-ui-broken.md

# Human-in-the-loop feedback cannot arrive over the web UI

Mechanism: HumanAgent awaits `receive_text()` on a socket whose main loop is already receiving; the server drops inbound messages while a task runs; the human_feedback handler is a TODO.
Trigger: `include_human_feedback=true` from the web app.
Observable failure: the run hangs or silently accepts the plan.
Impact: medium. Confidence: medium. Triggerability: low.
Status: proposed
Threatens: multi-agent-human-feedback-applied
Found at: 9ad2148 (agent: multi_agents via backend)
Evidence: multi_agents/agents/human.py:29; backend/server/server_utils.py:184, :357 (reviewer-reported, not executed).


---

# Risk page hybrid-empty-context-bypasses-abstain.md

# Hybrid mode writes a "sourced" report when both passes found nothing

Mechanism: in hybrid mode both context passes return `[]` on failure, and `join_local_web_documents` wraps them in a non-empty string ("Context from local documents: []..."); the writer's abstain guard only checks for an empty context.
Trigger: `report_source=hybrid` with search blocked/rate-limited and no relevant document chunks.
Observable failure: a confident report with no real sources, written from model memory, instead of the abstain message.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: abstain-when-no-evidence, report-grounded-in-provided-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/skills/researcher.py:180-184; gpt_researcher/prompts.py:563-565; gpt_researcher/skills/writer.py:82-83. Web-only mode does reach the guard when every retriever fails (researcher.py web-search path returns `[]`).


---

# Risk page language-ignored-in-some-report-types.md

# Some report types ignore the configured language

Mechanism: the outline prompt accepts `language` but never uses it; custom prompts carry no language line; draft-title prompts have no language line.
Trigger: `LANGUAGE` other than English with outline, custom or detailed reports.
Observable failure: English outline or headers in an otherwise non-English report.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: report-in-configured-language
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/prompts.py:398-415; gpt_researcher/actions/report_generation.py:255-256 (reviewer-reported). Issue #1767.


---

# Risk page local-mode-planning-web-leak.md

# Local-document research still sends the query to web search and plans from web results

Mechanism: `plan_research` always runs a live search with `retrievers[0]` before sub-queries are generated, regardless of `report_source`; deep_agents' `quick_search` tool builds a GPTResearcher without `report_source`, so scoping is always web.
Trigger: `report_source=local` (or deep_agents `source=local`) on private material.
Observable failure: internal topic names go to a third-party search API; the outline and sub-queries are shaped by web snippets, not the private corpus.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: local-source-stays-local
Found at: 9ad2148 (agents: gpt_researcher, deep_agents)
Evidence: gpt_researcher/skills/researcher.py:64-70; deep_agents/tools.py:35. User reports: #1004, #1334 ("My Documents" still web-searches). Note: an earlier hypothesis that empty DOC_PATH falls back to web scraping was checked and rejected — `DocumentLoader.load` raises (gpt_researcher/document/document.py:57).


---

# Risk page mcp-llm-analysis-treated-as-source.md

# MCP research stores the model's own pre-tool text as a cited source

Mechanism: after tool selection the LLM's `response.content` is appended to research results as `{"title": "LLM Analysis: …", "href": "mcp://llm_analysis"}`; it then enters the context alongside real evidence.
Trigger: any run with MCP retrievers configured.
Observable failure: unverified, possibly hallucinated claims appear in the report as though sourced; reference may show an `mcp://` pseudo-URL or none.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: report-grounded-in-provided-sources, references-match-used-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/mcp/research.py:137-144.


---

# Risk page multi-agent-graph-build-crash.md

# Multi-agent pipeline cannot build its LangGraph

Mechanism: conditional edges reference `self._route_fact_check` (orchestrator) and `self._route_draft_review` (editor); neither method exists. The tested helpers `route_fact_check` / `route_draft_review` are never wired in.
Trigger: any multi-agent run (`multi_agents/main.py`, LangGraph dev server, web UI `report_type=multi_agents`).
Observable failure: AttributeError while building the graph; no report is produced.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-revision-loops-terminate
Found at: 9ad2148 (agent: multi_agents)
Evidence: multi_agents/agents/orchestrator.py:102; multi_agents/agents/editor.py:140; no `def _route_fact_check` / `def _route_draft_review` anywhere under multi_agents/ (grep, checked). Unit tests load the helpers in isolation, so CI does not catch it. Static reading only; not executed.


---

# Risk page plan-revision-cap-ignored.md

# Human plan-revision cap never triggers

Mechanism: the graph edge reads `revisions_count` but the human node writes `plan_revision_count`; the documented `max_plan_revisions` is only used by an unwired helper.
Trigger: `include_human_feedback=true` and repeated feedback.
Observable failure: planner/human loop until LangGraph's recursion limit, a generic error instead of the documented clear one.
Impact: medium. Confidence: high. Triggerability: low.
Status: proposed
Threatens: multi-agent-revision-loops-terminate
Found at: 9ad2148 (agent: multi_agents)
Evidence: multi_agents/agents/orchestrator.py:88-96, :106; multi_agents/agents/human.py:50 (checked).


---

# Risk page planner-seeds-guessed-answer.md

# The planner writes its guessed answer into sub-queries, then confirms it

Mechanism: sub-query generation sees the question plus initial search snippets; when it guesses an entity it searches for that entity, and the report is built around it.
Trigger: short factual questions with an ambiguous or lesser-known answer.
Observable failure: a confident report about the wrong entity.
Impact: high. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: report-grounded-in-provided-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: evals/simple_evals/logs/SimpleQA Eval 100 Problems 2-22-25.txt (6th PM of Nepal ~l.34000; Tarar birthplace ~l.66700; Green Chemistry 2016 ~l.131000), 7 incorrect of 100 in that run. Pattern reported by a reviewer from the log; not re-read by me.


---

# Risk page reasoning-token-retry-cost.md

# Empty responses from reasoning models are retried at full price up to 10 times

Mechanism: `create_chat_completion` retries empty responses and errors up to 10 times (1 when streaming to a websocket); costs are recorded only on success; the report call is capped at SMART_TOKEN_LIMIT, which reasoning tokens also consume.
Trigger: reasoning model exhausting its budget on thinking; invalid API key.
Observable failure: large hidden spend, long hangs before an error, truncated reports, under-reported `get_costs()`.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: report-meets-word-target
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/utils/llm.py:109 (checked); gpt_researcher/config/variables/default.py:14 (reviewer-reported).


---

# Risk page rest-multi-agent-one-char-report.md

# REST multi_agents reports are written as a single character

Mechanism: for `multi_agents`, `run_agent` returns a string; `write_report` indexes `report_information[0]` and returns `"report": ""`.
Trigger: POST /report/ with `report_type=multi_agents` (currently also blocked by [the graph build crash](multi-agent-graph-build-crash.md)).
Observable failure: DOCX/PDF containing one character; empty report text in the response.
Impact: medium. Confidence: medium. Triggerability: low.
Status: proposed
Threatens: report-meets-word-target
Found at: 9ad2148 (agent: backend)
Evidence: backend/server/app.py:303-304, :321 (checked); backend/server/websocket_manager.py:180-183 (reviewer-reported).


---

# Risk page scraped-content-prompt-injection.md

# Scraped pages and MCP tool output can steer the report

Mechanism: page text is interpolated raw as `Information: "{context}"` with no delimiting or untrusted-content instruction; MCP tools are chosen and called from server-controlled descriptions with no allowlist.
Trigger: a page or tool result containing instructions ("ignore the above, cite …").
Observable failure: planted links or claims in the report; steered sub-queries; unintended MCP tool calls.
Impact: high. Confidence: medium. Triggerability: low.
Status: proposed
Threatens: report-grounded-in-provided-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/prompts.py:294; gpt_researcher/mcp/research.py:100-113 (reviewer-reported). Triggerability against real pages is unmeasured.


---

# Risk page silent-partial-research-failure.md

# Failed research steps are swallowed and the report looks complete

Mechanism: `_process_sub_query` returns "" on any exception, retriever errors return `[]`, `generate_report` prints the error and returns "", intro/conclusion/subtopic steps return empty on error.
Trigger: rate limits, bad key, context too large, transient scraper failures.
Observable failure: a thinner report built from a fraction of sub-queries with no warning, or an empty report string with no error to the caller.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: abstain-when-no-evidence, report-meets-word-target
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/actions/report_generation.py:306-309 (checked); gpt_researcher/skills/researcher.py:642-651 (reviewer-reported). Issues #1275, #1579, #1764.


---

# Risk page stale-time-sensitive-facts.md

# Time-sensitive answers are stale or invented

Mechanism (hypothesis): context has no publication dates, scrape order is shuffled and compression keeps early chunks, so older pages can win; the writer fills gaps (e.g. prices) from memory.
Trigger: questions about recent releases, prices or events.
Observable failure: outdated or fabricated current facts stated confidently.
Impact: high. Confidence: medium. Triggerability: high.
Status: proposed
Threatens: report-grounded-in-provided-sources
Found at: 9ad2148 (agent: deep_agents with GPT Researcher tools)
Evidence: deep_agents/benchmark_results/recency_2026-07-04_{18-54-47,19-10-24,22-11-41}.json — gptr coverage 0.583/0.702/0.643 vs baseline 0.833/0.786/0.821, wrong_stale 8/4/6 vs 2/2/2 over 42 checkpoints (checked). Mechanism is not confirmed; it is the reviewers' inference from gpt_researcher/scraper and context/compression.py.


---

# Risk page visited-url-race-drops-sources.md

# Concurrent sub-queries lose overlapping sources

Mechanism: `_get_new_urls` adds a URL to the shared `visited_urls` before scraping; sub-queries run concurrently, so overlapping hits go only to the first claimant and failed scrapes are blacklisted for the run.
Trigger: sub-queries whose searches return overlapping URLs (typical).
Observable failure: some sub-queries get no content; the same URLs still appear in reference lists built from `visited_urls`.
Impact: medium. Confidence: medium. Triggerability: high.
Status: proposed
Threatens: references-match-used-sources
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/skills/researcher.py:808-811 (checked); gpt_researcher/actions/markdown_processing.py:111 add_references(visited_urls) (reviewer-reported; used by detailed reports).
