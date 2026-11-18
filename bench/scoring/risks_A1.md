# Final answer to the user

GPT Researcher is most likely to fail quietly: when a step breaks, it usually still returns a report that looks finished but is empty, unsourced or has wrong references. I found 20 ways this can happen, and I checked every one against the code. None has been triggered in a real run yet. There were no traces to read and I ran nothing: no models, no tests.

**Highest-impact failures, all confirmed in the code**
1. **Multi-agent mode cannot start.** The graph points at two routing methods that don't exist (`multi_agents/agents/orchestrator.py:102`, `editor.py:140`), so it fails before any research runs. Even if it started:
   - Plan feedback that contains "no" anywhere ("add a section on technology") is treated as approval (`human.py:47`).
   - The documented `max_plan_revisions` limit reads a counter that nothing sets.
   - A reviewer or fact-checker error counts as approval.
2. **Hybrid mode writes reports from model memory when it finds nothing.** The empty result is turned into the text `"Context from local documents: []…"`. That isn't blank, so the "could not gather sources" check never fires (`researcher.py:180-184`, `prompts.py:566`).
3. **Detailed reports can lose their body or sections without any message.**
   - If subtopic generation fails, it returns an empty list. The report still gets an introduction, a contents list and a conclusion around nothing (`utils/llm.py:213-217`).
   - If a writing call fails, that section, the introduction or the conclusion comes back as `""` and is simply dropped.
   - Cut-off model output is never detected; nothing checks `finish_reason`.
4. **The appended References list is every URL seen, not every URL used.** It includes pages that failed to load or were filtered out (`markdown_processing.py:111`). Local-document reports get an empty References heading. Online documents are cited by a temporary file path that no longer exists.
5. **Deep research:**
   - It crashes and loses everything gathered so far if query generation returns nothing (`deep_research.py:406-414`).
   - When the context is trimmed, it drops the cited learnings first.
   - Its displayed cost leaves out nested research and several model calls, and nothing caps its spend.
6. **`python cli.py … --report_type detailed_report` gathers nothing.** It passes `report_source="web_search"`, but the valid value is `"web"` (`cli.py:279`).
7. **Smaller but common:**
   - Sub-queries run at the same time and compete for the same URLs, so later ones often end up with no sources.
   - Captcha and cookie-wall pages count as content.
   - Page text and MCP tool output go into the report prompt raw.
   - The MCP retriever's own pre-tool model text is stored as a source.
   - With `complement_source_urls`, the extra web research arrives with a space between every character (`' '.join` on a string, `researcher.py:158`).

**What the repo's existing results already show.** The tracked evals are very small: 1 of 2 reports judged hallucinated, and 3 of 3 correct on SimpleQA. In the deep_agents benchmark, 56% of citations were supported. Its raw result files include runs that `BENCHMARK.md` doesn't report, where GPT Researcher trails the baseline. In one FRAMES run it scored 65% against 75% and never declined to answer.

**Questions I would have asked you** (recorded in the wiki, none blocking):
1. **No or thin sources:** should the agent decline to answer whenever it found nothing, also flag partial coverage, or answer from model knowledge with a label? I recommend declining plus flagging partial coverage. The report prompt's "at least N words" and "as long as you can" push it to pad instead.
2. **Multi-agent mode:** supported, experimental, or deprecated? I recommend experimental, with a single startup test.
3. **Instructions inside web pages and MCP tool output:** should the agent treat them as data only? The backlog's "no built-in auth by design" decision covers who can call the server, not this. I recommend treating them as data and testing with a couple of planted pages.
4. **What to evaluate first:** I recommend research and detailed reports on the default Tavily + OpenAI setup.
5. **Which risks to test first:** I recommend 7 that are cheap to trigger with simulated search results or model errors. They're listed in `relai/STATUS.md`.

**What I added to the repo** (all new and uncommitted, under `relai/`):
- `wiki/index.md` with 5 requirements, 20 risks and 3 open questions, each page citing file and line. The risks are all marked as unconfirmed.
- `STATUS.md`, `decisions.md` (my stated assumptions, since you weren't available), `UPSTREAM.md` and a short `README.md`.
- The wiki checker passes on all 28 pages.

Copying RELAI's full template README in from the plugin folder was blocked by a permission prompt. I left a short pointer instead and ran the checker from the plugin folder.

**How thorough this was.** I read the core agent loop, query planning, context compression, the report prompts and the writer myself. Three parallel readers covered retrieval and scraping; deep research, multi-agent and MCP; and the backend, CLI, config and backlog. I re-checked their main claims against the code. What I didn't cover:
- the frontend
- each retriever's internals beyond the error handling
- runtime behavior in general, for example whether the similarity threshold actually removes everything for a given embedding model

The next step would be the `eval` skill, building tests for whichever risks you choose.

---

# Risk page block-pages-counted-as-content.md

# Captcha, cookie-wall and error pages count as scraped content

Mechanism: The only scraper quality gates are HTTP status below 400 and at least 100 characters. A 200-status bot check or consent page passes. When there are 10 or fewer documents under 8000 characters, the compression fast path skips relevance filtering entirely.
Trigger: Sites behind Cloudflare or consent walls, especially when few results are scraped.
Observable failure: Boilerplate is treated as evidence, and that happens most in exactly the sparse cases where it matters most.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/scraper/scraper.py:134; gpt_researcher/context/compression.py:163-181; ISSUE_BACKLOG.md #1684

## Probes

None yet.


---

# Risk page cli-detailed-report-invalid-source.md

# CLI detailed reports use an invalid report source and gather nothing

Mechanism: `cli.py` builds `DetailedReport(report_source="web_search")`, but the valid value is `"web"`. No source branch matches, so the context stays empty. That path also ignores `--tone` and `--report_source`.
Trigger: `python cli.py "<query>" --report_type detailed_report`.
Observable failure: Every subtopic section is the "could not gather any source material" text, wrapped in a report structure.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: source-urls-only-by-default
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: cli.py:274-280; gpt_researcher/utils/enum.py:45; gpt_researcher/skills/researcher.py:144-205

## Probes

None yet.


---

# Risk page complement-source-urls-context-corrupted.md

# Complementing source URLs spaces out every character of the web context

Mechanism: `research_data += ' '.join(additional_research)` is applied to a string, which puts a space between every character. The "unable to find relevant context in the provided sources" message sits behind the condition `research_data and len(research_data) == 0`, which can never be true.
Trigger: `source_urls` together with `complement_source_urls=True`.
Observable failure: The complementary web research reaches the writer unreadable ("T h e  a n s w e r"), and an empty result from the provided URLs gives no warning.
Impact: medium. Confidence: high. Triggerability: low.
Status: proposed
Threatens: source-urls-only-by-default
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/researcher.py:148,155-158

## Probes

None yet.


---

# Risk page cross-subquery-url-dedup-starves.md

# Concurrent sub-queries race for URLs, leaving later ones without sources

Mechanism: Sub-queries run concurrently and share `visited_urls`. The first sub-query to claim a URL scrapes it and compresses it against its own query only. Other sub-queries that found the same URL get nothing. A URL whose scrape failed is never retried.
Trigger: Related sub-queries whose search results overlap. That is the normal case.
Observable failure: Some sub-queries log "No content found". Their aspects of the question are covered thinly or not at all, with no warning in the report.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/researcher.py:379-385,801-822,867

## Probes

None yet.


---

# Risk page deep-research-cited-learnings-trimmed-first.md

# Deep research drops its cited learnings first when context is trimmed

Mechanism: The final context is `[learnings with [Source: url]] + raw context`. `trim_context_to_word_limit` keeps the most recent items, so the cited learnings at the front are dropped first. Citations are also keyed by learning text, and an LLM-returned `sourceUrl` is never checked against the URLs actually visited.
Trigger: Any deep research run whose raw context exceeds about 25k words. That is common at the default breadth and depth.
Observable failure: The writer sees only uncited raw text, or citations to URLs that were never visited. The report's citations become thin or wrong.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/deep_research.py:154-164,213-231,611-624; deep_agents/BENCHMARK.md:38 (56% citation precision in a 10-task run of the deep_agents variant)

## Probes

None yet.


---

# Risk page deep-research-cost-untracked-unbounded.md

# Deep research spend is under-reported and has no cap

Mechanism: Nested `GPTResearcher` costs are never added to the parent. Query generation, planning and result processing calls pass no `cost_callback`. Failed or retried calls are not counted. The breadth × depth recursion has no budget or time limit, its floor is 2 branches, and levels below the first run serially.
Trigger: Any deep research run, especially with breadth or depth above the defaults.
Observable failure: The displayed "Total Research Costs" is well below the real spend. Long runs cannot be stopped by budget.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/deep_research.py:249,280,320,366,425-445,543,601-608; gpt_researcher/utils/llm.py:138

## Probes

None yet.


---

# Risk page deep-research-zero-queries-crash.md

# Deep research crashes when query generation returns nothing

Mechanism: When `generate_search_queries` returns `[]`, `deep_research` returns `all_learnings` and other locals before assigning them, which raises `UnboundLocalError`. The recursive call is not wrapped in a try.
Trigger: The strategic model returns JSON the parser rejects (wrong keys, plain strings), or reasoning uses up the 4000-token budget.
Observable failure: The whole deep research run aborts after its spend, and all learnings gathered so far are lost.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/deep_research.py:400-420,543; ISSUE_BACKLOG.md #1787

## Probes

None yet.


---

# Risk page detailed-report-empty-body-on-subtopic-failure.md

# A failed subtopic step gives a detailed report with no body

Mechanism: `construct_subtopics` catches every exception and returns the input `subtopics`. `DetailedReport` never passes its subtopics through, so that fallback is always `[]`. `_get_all_subtopics` only prints a message. `run()` still writes an introduction, a table of contents and a conclusion over the empty body.
Trigger: Subtopic generation fails: a bad structured-output parse, output truncated at `SMART_TOKEN_LIMIT`, or a provider error.
Observable failure: A detailed report with an introduction and conclusion but no sections. Nothing tells the user the failure happened.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/utils/llm.py:213-217; backend/report_type/detailed_report/detailed_report.py:98-108; tests/test_construct_subtopics_error_log.py pins the fallback only

## Probes

None yet.


---

# Risk page hybrid-empty-context-bypasses-abstain.md

# Hybrid research with no sources writes a report from model memory

Mechanism: When nothing is gathered, `_get_context_by_web_search` returns `[]`. `join_local_web_documents` interpolates it, so the context becomes the literal text "Context from local documents: []\n\nContext from web sources: []". The writer's no-source guard only abstains on blank context, so it does not fire.
Trigger: `report_source=hybrid` while retrieval fails or the similarity filter drops everything (a bad search key, rate limiting, an unreachable document URL).
Observable failure: A confident-looking report with no real sources, instead of the "could not gather any source material" message the other modes return.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/researcher.py:180-184, 393-396; gpt_researcher/prompts.py:566; gpt_researcher/skills/writer.py:82-88

## Probes

None yet.


---

# Risk page language-tone-prompt-family-dropped.md

# Language, tone and prompt family are dropped on some paths

Mechanism: The writer's `research_params` omit `prompt_family`, so the report body uses the default prompts while the introduction and conclusion use the configured family. The outline and custom report prompts ignore `language` and `tone`. Detailed subtopic researchers do not inherit `config_path`. A non-`Tone` tone silently becomes Objective.
Trigger: A non-English `LANGUAGE`, a custom `PROMPT_FAMILY` (Granite), or outline, custom and detailed report types.
Observable failure: Parts of the report come out in the wrong language or tone, or mixed formats appear across sections.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: report-in-requested-language
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/writer.py:38-47; gpt_researcher/prompts.py:392-399; gpt_researcher/agent.py:146; ISSUE_BACKLOG.md #1767, #1572

## Probes

None yet.


---

# Risk page llm-output-truncation-undetected.md

# Truncated model output is accepted as a finished report

Mechanism: Nothing checks `finish_reason` or `stop_reason`. `SMART_TOKEN_LIMIT` (12000) and `STRATEGIC_TOKEN_LIMIT` (8000) also cover reasoning tokens on the default reasoning models, and deep research uses 4000 with high reasoning effort. Empty completions are retried up to 10 times, and each retry is billed.
Trigger: A large `TOTAL_WORDS`, a long section or conclusion, or high reasoning effort.
Observable failure: The report ends mid-sentence, or an empty response is retried and billed repeatedly before the run fails.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/utils/llm.py:110,128-138; gpt_researcher/config/variables/default.py:10-13; ISSUE_BACKLOG.md #1271

## Probes

None yet.


---

# Risk page mcp-llm-analysis-as-evidence.md

# MCP's pre-tool LLM text is injected as a source

Mechanism: MCP research makes one tool-bound LLM call, runs the tools, and never returns their output to the model. It then adds the model's own pre-tool `response.content` as a result titled "LLM Analysis". The researcher stores that result next to the real tool results as MCP context.
Trigger: Any research with an MCP retriever where the model writes text along with its tool calls.
Observable failure: Planning text or claims from model memory enter the context as evidence and can be cited as "LLM Analysis".
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/mcp/research.py:79-144; gpt_researcher/skills/researcher.py:444-457,757

## Probes

None yet.


---

# Risk page multi-agent-feedback-substring-no.md

# Plan feedback containing "no" anywhere is discarded as approval

Mechanism: `human.py` treats any feedback where `"no" in feedback.lower()` as approval. A strict `is_human_plan_approval` helper exists and is tested, but it is not used. The revision cap reads `revisions_count`, while the human node writes `plan_revision_count`, so `max_plan_revisions` never applies. `receive_text()` has no timeout.
Trigger: Feedback such as "add a section on technology", "not enough data" or "economy".
Observable failure: The feedback is ignored and the original plan proceeds. The documented revision cap never fires. A silent client hangs the run.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-human-feedback
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: multi_agents/agents/human.py:29,47; multi_agents/agents/orchestrator.py:89-97; tests/test_none_accept_sentinels.py:52-62

## Probes

None yet.


---

# Risk page multi-agent-graph-missing-router.md

# Multi-agent workflow references router methods that do not exist

Mechanism: The orchestrator and editor pass `self._route_fact_check` and `self._route_draft_review` to `add_conditional_edges`. Neither method is defined. The real routers (`route_fact_check`, `route_draft_review`) are module functions that are never wired in.
Trigger: Building the research team graph (`multi_agents/main.py`).
Observable failure: `AttributeError` before any research runs, so multi-agent mode cannot start. Existing tests exercise only the helper functions.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-human-feedback
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: multi_agents/agents/orchestrator.py:102; multi_agents/agents/editor.py:140; multi_agents/agents/fact_review.py:8; multi_agents/agents/draft_review.py:8

## Probes

None yet.


---

# Risk page multi-agent-review-error-treated-as-approval.md

# Reviewer or fact-checker errors count as approval

Mechanism: `call_model` logs and returns `None` on any exception. The reviewer and fact-checker treat a `None` response as "no revisions needed", and the router accepts the draft.
Trigger: An API error, rate limit or wrong model or provider pairing during review (`task['model']` is paired with `cfg.smart_llm_provider`).
Observable failure: A draft is published as reviewed and fact-checked although no check ran.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: multi_agents/agents/utils/llms.py:20-36; multi_agents/agents/reviewer.py:44,61-63; multi_agents/agents/fact_checker.py:31,49-55

## Probes

None yet.


---

# Risk page online-docs-cited-by-temp-path.md

# Online documents are cited by temporary file path

Mechanism: `OnlineDocumentLoader` downloads each document into a `NamedTemporaryFile` and loads it by path, so `source` is `/tmp/tmpXXXX.pdf`. The file is then deleted. Local files are cited by basename only.
Trigger: `document_urls` in hybrid mode.
Observable failure: Citations point at temporary files that no longer exist, and the original URL is lost.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: references-list-used-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/document/online_document.py:28,48-52,85; gpt_researcher/document/document.py:55

## Probes

None yet.


---

# Risk page references-list-all-visited-urls.md

# Appended References list every URL seen, not the ones used

Mechanism: URLs are added to `visited_urls` before they are scraped. `add_references` then appends the whole sorted set as "## References". Failed scrapes, short or blocked pages and pages whose chunks were all filtered out stay in the set. Detailed reports also seed it with the user's `source_urls`. For local documents the set is empty, so a bare heading is appended.
Trigger: Any detailed report, or any caller using `add_references`.
Observable failure: The reference list names pages that were never read or used. A reader cannot tell which reference supports which claim. Local-document reports get an empty References section.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: references-list-used-sources, cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/researcher.py:809-810; gpt_researcher/actions/markdown_processing.py:111; backend/report_type/detailed_report/detailed_report.py:89,200-201; ISSUE_BACKLOG.md #1276, #1119, #565

## Probes

None yet.


---

# Risk page report-llm-failure-returns-empty.md

# Writer LLM failures silently drop report parts

Mechanism: `generate_report`, `write_report_introduction` and `write_conclusion` catch exceptions and return `""`. Detailed reports skip an empty subtopic section without notice. A basic report becomes empty pdf, docx and md files. A streamed retry after a mid-stream failure re-streams into the same websocket.
Trigger: A provider error, timeout or rate limit while writing.
Observable failure: The report is missing its introduction, conclusion or sections, or is empty, and looks finished. Streamed output can be duplicated.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/actions/report_generation.py:58-60,110-112,155-157,290-307; backend/report_type/detailed_report/detailed_report.py:116

## Probes

None yet.


---

# Risk page similarity-filter-empties-context.md

# Similarity threshold can filter out all relevant chunks

Mechanism: The configured `SIMILARITY_THRESHOLD` of 0.42 is applied to cosine similarity between a short query and 1000-character chunks. With some embedding models, scores for relevant chunks can fall below it, so `EmbeddingsFilter` returns nothing. At most 10 chunks per sub-query reach the writer, and pages are truncated at 50000 characters with no log.
Trigger: Non-OpenAI embedding models (Ollama, HuggingFace), terse queries, or long PDFs whose key facts appear late.
Observable failure: The context is empty or thin, so the agent abstains or writes an under-grounded report. Late-document facts are missed.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/config/variables/default.py:6; gpt_researcher/context/compression.py:123,135,188; gpt_researcher/context/retriever.py:13,29. Score distributions are unmeasured.

## Probes

None yet.


---

# Risk page untrusted-page-prompt-injection.md

# Page and tool text can instruct the report writer

Mechanism: Scraped page text, PDFs and MCP tool output are interpolated raw into the report and curation prompts (`Information: "{context}"`). There are no delimiters and no instruction to treat the text as data. `Source:` and `Title:` lines in page text look the same as real ones.
Trigger: A page in the results that contains instructions or forged `Source:` lines.
Observable failure: Biased content or forged citations in the report, or curation that drops real sources.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/prompts.py:293-296,555-561; gpt_researcher/skills/curator.py:64. Susceptibility of current models is unmeasured.

## Probes

None yet.
