# Final answer to the user

# Where GPT Researcher is likely to fail

I read the agent's prompts, code and docs, and the benchmark and eval results already committed to the repo. I ran nothing: no traces exist, and Python dependencies aren't installed. The result is 22 likely failure points (risks), 6 requirements and 6 open questions, written to `relai/wiki/` (index at `relai/wiki/index.md`). Three findings are backed by your own benchmark numbers; every other code claim I spot-checked against the source held up.

## Most important

1. **The multi-agent pipeline can't start.** The LangGraph setup calls `self._route_fact_check` (`multi_agents/agents/orchestrator.py:102`) and `self._route_draft_review` (`multi_agents/agents/editor.py:140`), and neither method exists. Every `multi_agents` run should fail with `AttributeError` before producing a report. I found this by reading the code; I couldn't run it. Once fixed, more problems sit behind it:
   - The fact-checker never sees the sources it is supposed to check against.
   - If the fact-check LLM call fails, the draft is treated as approved.
   - The revision limits are never applied.
   - Plan feedback containing "no" anywhere (e.g. "not enough on cost") is treated as approval (`human.py:47`).
   - The shipped `task.json` turns guideline review off.
2. **MCP results include the model's own text as a citable source.** `gpt_researcher/mcp/research.py:137-144` adds the tool-calling model's reply as a result labelled "LLM Analysis". The model wrote that reply before seeing any tool results, yet the report writer can cite it like retrieved evidence.
3. **Measured: about 44% of citations fail verification.** The deep_agents setup averaged 62.9 citations per report, of which 35.2 were valid (56%), versus 54% for the baseline. The docs headline "+89% verified citations", which is the count rising, not the accuracy.
4. **Measured: worse than plain search on recent facts.** On the recency benchmark, the deep_agents agent gave 8, 4 and 6 wrong-or-stale answers across three runs versus 2 for the baseline, with lower coverage and about twice the latency. The docs don't mention this, or that FRAMES accuracy was 13/20 versus the baseline's 15/20.
5. **Reports get written from little or no evidence.**
   - **Partial empty-context check.** There is a check that refuses to write when nothing was found (`skills/writer.py:77-90`). In hybrid mode, two empty results are joined into a non-empty string, so the check is skipped.
   - **Errors become empty results.** Search and scraping errors are silently turned into empty results throughout.
   - **The prompt pushes for length and opinion.** It demands at least 1,200 words and that the model "MUST determine your own concrete and valid opinion", with no instruction to say when evidence is thin.
6. **Scraped page text goes straight into prompts** (`prompts.py:294`, and query planning at `:241`). It isn't marked as untrusted data, so a page containing instructions can steer the report. The team's "operator-run, no auth" decision covers who can call the server, not what pages the agent reads.
7. **Deep research costs grow quickly and are under-reported.** Each level spawns full nested researchers whose costs never reach the total shown. There's also a crash: if the model returns no search queries, the early-exit path refers to variables that don't exist yet (`deep_research.py:406-420`).

## Other risks (details in the wiki)

- **Settings silently ignored:**
  - A plain-string tone like `tone="formal and objective"` (as `pip-package.md:228` shows) silently becomes "Objective".
  - The `detailed_report.md` example uses `Tone.FORMAL`, which doesn't exist, and `report_source="web_search"`, which gathers nothing.
  - A configured prompt family isn't applied to the main report body.
  - Custom and outline prompts drop the language and citation rules.
- **Reference lists include unread pages.** They contain every URL the agent tried to read, including failed and filtered ones.
- **Using `complement_source_urls` garbles the web context** with a space between every character (`researcher.py:158`).
- **Chat shows the wrong sources.** It lists sources from a second search, not the one the answer was based on.
- **MCP failures are silent.** In the default "fast" mode, one MCP result set is pasted into every sub-query.
- **Detailed reports silently lose subtopics** when subtopic generation fails.
- **The REST API saves one character of multi-agent reports.** It writes only the first character to the PDF/DOCX.

## Gaps in the existing evals

SimpleQA (92% correct on 100 questions) only checks short factual answers. The hallucination eval has 2 records, and one is labelled a hallucination while its own reasoning says there is none. Nothing currently measures whether citations support claims, behaviour on empty or partial retrieval, injected instructions, or cost.

## Questions I would have asked you

Recorded in `relai/wiki/open-questions/`, each with my recommendation:

1. **Which entry points matter?** I'd start with the core research report and deep research, and leave `multi_agents` out until its graph is fixed.
2. **On thin evidence, should the report flag it and run short, or still give a concrete opinion at full length?** The prompts conflict; I'd flag it and run short.
3. **Is the MCP "LLM Analysis" text meant to be citable?** I'd exclude it.
4. **Should reference lists contain only cited sources?** I'd say yes.
5. **Is resisting instructions planted in web content a requirement?** I'd say yes.
6. **Should a "no sources found" result be a visible error with its cause?** Today it's an English-only sentence saved and exported as a normal report. I'd make it an error.

All 22 risks are left as "proposed" until you rule on them.

## What I created

A new `relai/` folder, uncommitted:
- the wiki pages, which pass `check_wiki.py`;
- `STATUS.md`, with the open questions at the top;
- `decisions.md`, which records the assumptions I made in your absence;
- `UPSTREAM.md` and the copied checker.

The next step is to answer the questions, then turn the top risks into tests.

**Not covered:** the frontend, `multi_agents/ag2`, `mcp-server`, most individual retrievers and scrapers, and the `deepagents` library itself. The gpt-researcher MCP server failed to connect, so I couldn't use it.

---

# Risk page backend-multi-agent-report-first-char.md

# REST API saves only the first character of multi-agent reports

Mechanism: For multi_agents, run_agent returns a string (websocket_manager.py:180-183), but app.py:303-304 writes `report_information[0]` to DOCX and PDF.
Trigger: POST report generation with report_type=multi_agents.
Observable failure: DOCX/PDF containing one character.
Impact: low. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: 
Found at: fae2317 (agent: backend)
Evidence: backend/server/app.py:303-305; backend/server/websocket_manager.py:180-183

Low impact while multi-agent-graph-undefined-routers prevents any multi-agent report.


---

# Risk page chat-sources-from-second-search.md

# Chat shows sources from a second search, not the one the model read

Mechanism: After the model's tool-using answer, chat.py:170-176 calls quick_search again to get metadata; results may differ, and on tool errors utils/tools.py:206-227 retries without tools and may answer current-events questions from memory without telling the user.
Trigger: Any chat turn that uses search.
Observable failure: Displayed sources do not match what the answer was based on; doubled search cost.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cite-only-provided-sources
Found at: fae2317 (agent: backend chat)
Evidence: backend/chat/chat.py:170-176; gpt_researcher/utils/tools.py:188-227


---

# Risk page complement-source-urls-garbled.md

# Complementing source URLs with web search garbles the web context

Mechanism: researcher.py:157-158 does `research_data += ' '.join(additional_research)` where `additional_research` is already a string, inserting a space between every character.
Trigger: `source_urls` plus `complement_source_urls=True`.
Observable failure: Web half of the context reads "T h e  m a r k e t ..."; the report relies only on the given URLs or misquotes.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher)
Evidence: gpt_researcher/skills/researcher.py:155-158,385-392


---

# Risk page deep-agents-low-citation-precision.md

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


---

# Risk page deep-agents-recency-regression.md

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


---

# Risk page deep-research-citations-trimmed-or-unverified.md

# Deep research trims cited learnings first and accepts unverified source URLs

Mechanism: Learnings with citations are placed before raw context and `trim_context_to_word_limit` keeps from the end, so cited learnings are dropped first (deep_research.py:213-231,611-621); LLM-supplied `sourceUrl` is not checked against visited URLs (152-164); nested researchers drop query_domains and language (433-445) and lose the original query at depth > 1 (537-540).
Trigger: Large deep-research runs exceeding ~25k words of context; domain-restricted or non-English requests.
Observable failure: Report built on uncited raw text with possibly hallucinated citation URLs, drift from the original question, ignored domain restrictions.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: cite-only-provided-sources, write-in-requested-language
Found at: fae2317 (agent: gpt_researcher (deep research))
Evidence: gpt_researcher/skills/deep_research.py:152-164,213-231,433-445,537-540,611-621


---

# Risk page deep-research-cost-blowup-undercounted.md

# Deep research cost grows multiplicatively and is under-reported

Mechanism: Recursion runs per result per level (deep_research.py:514-551) with breadth floored at 2, each spawning full nested GPTResearcher runs whose costs are never added to the parent; several LLM calls pass no cost_callback, so `research_costs` (line 601) understates spend. Non-streaming LLM calls retry up to 10 times on any error (utils/llm.py:110) and failed attempts are not costed.
Trigger: deep_research_depth >= 3 or higher breadth; provider errors causing retries.
Observable failure: Unexpectedly large bills and long runtimes while the displayed cost is lower than actual.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: 
Found at: fae2317 (agent: gpt_researcher (deep research))
Evidence: gpt_researcher/skills/deep_research.py:433-445,514-551,601; gpt_researcher/utils/llm.py:110,137

Dollar magnitude not measured.


---

# Risk page deep-research-zero-queries-crash.md

# Deep research crashes when the model returns no search queries

Mechanism: The early return for `not serp_queries` (deep_research.py:406-414) references `all_learnings` etc., which are first assigned at lines 416-420.
Trigger: Query-generation output that parses to an empty list (malformed JSON or missing fields), more likely at depth > 1.
Observable failure: UnboundLocalError aborts the entire deep research job.
Impact: medium. Confidence: high. Triggerability: low.
Status: proposed
Threatens: 
Found at: fae2317 (agent: gpt_researcher (deep research))
Evidence: gpt_researcher/skills/deep_research.py:400-420


---

# Risk page detailed-report-subtopic-degradation.md

# Detailed reports silently lose subtopics or deduplication

Mechanism: `construct_subtopics` returns [] on any exception (utils/llm.py:213-217), leaving a report with only an intro, an empty table of contents and a conclusion; draft section titles (a list) are stringified before `extract_headers` (detailed_report.py:169-172), likely yielding no headers so cross-subtopic dedupe gets nothing; the abstain sentence is appended as a section when one subtopic has no context.
Trigger: Model or JSON failure in subtopic generation; normal detailed-report runs (dedupe).
Observable failure: Missing body sections or overlapping, repeated sections with no error.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: 
Found at: fae2317 (agent: gpt_researcher (detailed report))
Evidence: gpt_researcher/utils/llm.py:213-217; backend/report_type/detailed_report/detailed_report.py:102-118,165-172


---

# Risk page human-feedback-no-substring.md

# Human plan feedback containing "no" anywhere is treated as approval

Mechanism: human.py:47 discards feedback when `"no" in user_feedback.lower()`; the strict helper `is_human_plan_approval` (agents/utils/none_sentinels.py:30-42) exists but is unused.
Trigger: Feedback such as "not enough on cost", "nothing on Asia", "know the market".
Observable failure: Plan is not revised; the user's correction is silently dropped.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: multi-agent-follows-guidelines
Found at: fae2317 (agent: multi_agents)
Evidence: multi_agents/agents/human.py:39-48; multi_agents/agents/utils/none_sentinels.py:30-42


---

# Risk page hybrid-empty-context-bypasses-abstain.md

# Hybrid mode with no results bypasses the empty-context guard

Mechanism: The writer abstains only when the joined context is blank (skills/writer.py:77-90). In hybrid mode `join_local_web_documents` wraps both parts in labels (prompts.py:566), so two empty results become the non-blank string "Context from local documents: []\n\nContext from web sources: []".
Trigger: `report_source=hybrid` with no local docs matching and web search failing (bad key, rate limit, blocked).
Observable failure: A full-length report with citations is written from no source material.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: state-insufficient-evidence, cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher)
Evidence: gpt_researcher/skills/researcher.py:171-184; gpt_researcher/prompts.py:564-566; gpt_researcher/skills/writer.py:77-90


---

# Risk page mcp-llm-analysis-cited-as-source.md

# MCP model's own pre-tool prose enters context labelled as a source

Mechanism: `gpt_researcher/mcp/research.py:137-144` appends `response.content` of the tool-selecting LLM call as a result titled "LLM Analysis: {query}" with href `mcp://llm_analysis`; researcher.py renders it as `*Source: ...*` inside report context. Only a single `ainvoke` occurs, so the text was written without seeing tool results.
Trigger: Any research run with MCP retrievers configured where the model emits text alongside tool calls.
Observable failure: Unverified model-generated claims appear in the report cited as if retrieved; `mcp://` pseudo-URLs can appear in source lists.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher (MCP))
Evidence: gpt_researcher/mcp/research.py:79,137-144; gpt_researcher/skills/researcher.py:757-762


---

# Risk page mcp-silent-failure-and-duplication.md

# MCP failures are silent and fast mode pastes one result set into every sub-query

Mechanism: Tool errors are logged and skipped (mcp/research.py:133-135); the retriever returns [] on any error (retrievers/mcp/retriever.py:141-143,190-193); user-facing messages need VERBOSE (default False). In the default `fast` strategy the single cached MCP result is appended unfiltered to every sub-query context (researcher.py:327-341,552-562,747-768). The 300s timeout is not enforced because the executor `with` block waits for the thread (retriever.py:284-286).
Trigger: Misconfigured or down MCP server; any multi-sub-query report with MCP.
Observable failure: User believes a private data source was used when it returned nothing; the same MCP text is repeated across sections and can crowd out web sources; long hangs.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: 
Found at: fae2317 (agent: gpt_researcher (MCP))
Evidence: gpt_researcher/mcp/research.py:133-135; gpt_researcher/retrievers/mcp/retriever.py:141-143,190-193,284-286; gpt_researcher/skills/researcher.py:552-562,747-768


---

# Risk page mcp-tool-selection-no-readonly.md

# MCP tool selection can choose mutating tools

Mechanism: The LLM picks "EXACTLY" max_tools tools from untrusted descriptions (prompts.py:61,82) and research.py:100-113 executes them with model-chosen arguments; the fallback matches substrings like `get`/`list`/`view` (tool_selector.py:175-199). No read-only allowlist exists.
Trigger: An MCP server exposing write/delete tools alongside search tools, or a poisoned tool description.
Observable failure: A mutating tool is called during research.
Impact: high. Confidence: medium. Triggerability: low.
Status: proposed
Threatens: 
Found at: fae2317 (agent: gpt_researcher (MCP))
Evidence: gpt_researcher/prompts.py:54-83; gpt_researcher/mcp/tool_selector.py:56-69,175-199; gpt_researcher/mcp/research.py:100-113


---

# Risk page multi-agent-fact-check-unreliable.md

# Multi-agent fact-check has no sources and treats LLM failure as approval

Mechanism: fact_checker.py:18-27 sends only the draft, not the research context, so checks rely on model memory. `call_model` returns None on any exception (agents/utils/llms.py:34-36); the fact-checker then returns `fact_check_notes: None`, which routes as accept. The writer may revise only intro/conclusion (writer.py:40), so section-body issues cannot be fixed.
Trigger: Any API error, rate limit or context overflow during fact-checking; errors located in section bodies.
Observable failure: Report ships as fact-checked when it was not, or revision loops without progress.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: multi-agent-follows-guidelines
Found at: fae2317 (agent: multi_agents)
Evidence: multi_agents/agents/fact_checker.py:18-27; multi_agents/agents/utils/llms.py:29-36; multi_agents/agents/writer.py:40

Currently masked by multi-agent-graph-undefined-routers; becomes live once the routers are wired.


---

# Risk page multi-agent-graph-undefined-routers.md

# Multi-agent pipeline wires graph edges to methods that do not exist

Mechanism: `ChiefEditorAgent._add_workflow_edges` passes `self._route_fact_check` (multi_agents/agents/orchestrator.py:100-104) and `EditorAgent._create_workflow` passes `self._route_draft_review` (multi_agents/agents/editor.py:138-142); neither method is defined. The real routers `route_fact_check` / `route_draft_review` in fact_review.py / draft_review.py are never imported.
Trigger: Any run of `python -m multi_agents.main` or `report_type=multi_agents` from the backend.
Observable failure: AttributeError while building the graph; no report is produced.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-follows-guidelines
Found at: fae2317 (agent: multi_agents)
Evidence: multi_agents/agents/orchestrator.py:100-106; multi_agents/agents/editor.py:138-142; grep shows the names only at call sites

Static verification only: an import attempt failed earlier on a missing dependency (`json_repair`), so the AttributeError was not observed at runtime.


---

# Risk page multi-agent-guidelines-off-by-default.md

# Shipped multi-agent task disables guideline review

Mechanism: multi_agents/task.json:11 sets `follow_guidelines: false` while listing guidelines (APA, hyperlinks, Spanish); reviewer.py:70-80 skips review and writer.py:60 omits guidelines when false. README example sets it true.
Trigger: Running the multi-agent pipeline with the default task.json.
Observable failure: Report ignores the listed guidelines (for example written in English, not Spanish) with no review pass.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-follows-guidelines, write-in-requested-language
Found at: fae2317 (agent: multi_agents)
Evidence: multi_agents/task.json:11-17; multi_agents/agents/reviewer.py:70-80; multi_agents/agents/writer.py:60; multi_agents/README.md:91


---

# Risk page multi-agent-revision-caps-unwired.md

# Multi-agent revision caps are not enforced

Mechanism: The plan edge checks `revisions_count`, which nothing writes (HumanAgent writes `plan_revision_count`); `max_fact_check_revisions` / `max_draft_revisions` are never read; the routers that do read caps raise errors instead of force-accepting.
Trigger: Human keeps giving feedback, or a reviewer/fact-checker keeps flagging issues.
Observable failure: Unbounded loop, LangGraph recursion-limit error, or crash that discards a nearly finished report.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: multi-agent-follows-guidelines
Found at: fae2317 (agent: multi_agents)
Evidence: multi_agents/agents/orchestrator.py:88-99; multi_agents/agents/fact_review.py:16-21; multi_agents/agents/draft_review.py:24-29


---

# Risk page prompt-injection-from-retrieved-content.md

# Retrieved web, document and MCP text is spliced unfenced into prompts

Mechanism: Context goes into `Information: "{context}"` (prompts.py:294) with no delimiter or instruction to treat it as data; search snippets go into the query-planning prompt (prompts.py:241); MCP tool descriptions go into tool selection (prompts.py:59). clean_soup does not strip hidden text.
Trigger: A page ranking for the query (or a user-supplied URL / uploaded doc / MCP result) containing instructions.
Observable failure: Steered report content (promotion, misinformation, injected links), attacker-chosen sub-queries, or a different MCP tool selected.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher, deep_agents, chat)
Evidence: gpt_researcher/prompts.py:241,294,346; gpt_researcher/scraper/utils.py:108-120; backend/chat/chat.py:216

Mechanism confirmed; exploitability against a given model not probed.


---

# Risk page references-list-visited-not-cited.md

# Source lists include every visited URL, not the cited ones

Mechanism: URLs join `visited_urls` when chosen for scraping, before fetch or relevance filtering (researcher.py:809-811). Detailed reports append `add_references(report, visited_urls)` (detailed_report.py:200); `get_source_urls()` returns all visited URLs to the API (agent.py:733-739, backend/server/app.py:310) and deep_agents appends them as Sources (deep_agents/tools.py:73-75).
Trigger: Any run where some scrapes fail or pages are filtered as irrelevant.
Observable failure: Authoritative-looking reference/source lists containing pages never read or cited.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: single-deduplicated-reference-list
Found at: fae2317 (agent: gpt_researcher, deep_agents, backend)
Evidence: gpt_researcher/skills/researcher.py:809-811; gpt_researcher/actions/markdown_processing.py:94-113; backend/report_type/detailed_report/detailed_report.py:200


---

# Risk page requested-settings-silently-ignored.md

# Requested tone, prompt family and report options are silently replaced

Mechanism: A non-enum tone becomes Objective (agent.py:146), yet the pip docs pass `tone="formal and objective"` (pip-package.md:228) and the detailed-report example uses the non-existent `Tone.FORMAL`; `prompt_family` is not passed to `generate_report` (skills/writer.py:124) so the main body uses the default family; an invalid prompt family crashes on `PromptFamily()` without config (prompts.py:903); unknown report_type and retriever names fall back with only a Python warning or log (prompts.py:862-877, actions/retriever.py:166-170); custom and outline prompts drop language, tone and citation rules (prompts.py:392-415, report_generation.py:256).
Trigger: Library users following the docs; Granite users; custom_prompt or outline_report users; typos in configuration.
Observable failure: Report in the wrong tone, language or format, or uncited, with no error visible to the user.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: honor-requested-tone, write-in-requested-language, cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher)
Evidence: gpt_researcher/agent.py:146; docs/docs/gpt-researcher/gptr/pip-package.md:228; docs/docs/examples/detailed_report.md:61; gpt_researcher/prompts.py:392-415,903


---

# Risk page thin-context-full-length-report.md

# Thin or partial context still yields a long, opinionated report

Mechanism: Retrieval failures are swallowed at every layer (tavily_search.py:145-147, scraper.py:168-170, researcher.py:393-396) and the 0.42 relevance threshold can drop most chunks (compression.py:134-136). The guard fires only on a completely empty context. The report prompt demands at least TOTAL_WORDS (1200) words, "as long as you can", and that the model "MUST determine your own concrete and valid opinion", with no instruction to flag insufficient evidence.
Trigger: One or two short snippets survive (partial rate limiting, bot-blocked pages, niche or non-English query).
Observable failure: A confident 1200-word report padded from model knowledge, with claims lacking or misattributing citations.
Impact: high. Confidence: medium. Triggerability: high.
Status: proposed
Threatens: state-insufficient-evidence, cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher)
Evidence: gpt_researcher/prompts.py:296-302; gpt_researcher/config/variables/default.py:6,23; gpt_researcher/retrievers/tavily/tavily_search.py:145-147; gpt_researcher/skills/researcher.py:393-396
