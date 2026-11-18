# GPT Researcher wiki

Static discovery from code, prompts and docs at 0595cd3 (2026-11-17). No traces. All risks are `proposed` and unprobed.

## Requirements

- [Report claims are cited to gathered sources](requirements/cites-only-provided-sources.md)
- [Multi-agent mode honours human plan feedback and its revision cap](requirements/multi-agent-human-feedback.md)
- [Reference list holds the sources actually used](requirements/references-list-used-sources.md)
- [Report is written in the requested language and tone](requirements/report-in-requested-language.md)
- [Given source URLs restrict research unless complementing is on](requirements/source-urls-only-by-default.md)

## Risks (impact / confidence / triggerability)

- [CLI detailed reports use an invalid report source and gather nothing](risks/cli-detailed-report-invalid-source.md) — high / high / high
- [Deep research drops its cited learnings first when context is trimmed](risks/deep-research-cited-learnings-trimmed-first.md) — high / high / high
- [Deep research spend is under-reported and has no cap](risks/deep-research-cost-untracked-unbounded.md) — high / high / high
- [Plan feedback containing "no" anywhere is discarded as approval](risks/multi-agent-feedback-substring-no.md) — high / high / high
- [Multi-agent workflow references router methods that do not exist](risks/multi-agent-graph-missing-router.md) — high / high / high
- [Appended References list every URL seen, not the ones used](risks/references-list-all-visited-urls.md) — high / high / high
- [Deep research crashes when query generation returns nothing](risks/deep-research-zero-queries-crash.md) — high / high / medium
- [A failed subtopic step gives a detailed report with no body](risks/detailed-report-empty-body-on-subtopic-failure.md) — high / high / medium
- [Hybrid research with no sources writes a report from model memory](risks/hybrid-empty-context-bypasses-abstain.md) — high / high / medium
- [Truncated model output is accepted as a finished report](risks/llm-output-truncation-undetected.md) — high / high / medium
- [Reviewer or fact-checker errors count as approval](risks/multi-agent-review-error-treated-as-approval.md) — high / high / medium
- [Writer LLM failures silently drop report parts](risks/report-llm-failure-returns-empty.md) — high / high / medium
- [Captcha, cookie-wall and error pages count as scraped content](risks/block-pages-counted-as-content.md) — medium / high / high
- [Concurrent sub-queries race for URLs, leaving later ones without sources](risks/cross-subquery-url-dedup-starves.md) — medium / high / high
- [MCP's pre-tool LLM text is injected as a source](risks/mcp-llm-analysis-as-evidence.md) — medium / high / high
- [Language, tone and prompt family are dropped on some paths](risks/language-tone-prompt-family-dropped.md) — medium / high / medium
- [Online documents are cited by temporary file path](risks/online-docs-cited-by-temp-path.md) — medium / high / medium
- [Page and tool text can instruct the report writer](risks/untrusted-page-prompt-injection.md) — medium / high / medium
- [Complementing source URLs spaces out every character of the web context](risks/complement-source-urls-context-corrupted.md) — medium / high / low
- [Similarity threshold can filter out all relevant chunks](risks/similarity-filter-empties-context.md) — medium / medium / medium

## Open questions

- [What should the agent do when research yields little or no source material?](open-questions/thin-or-empty-context-behavior.md)
- [Is the multi-agent (LangGraph) mode a supported surface to evaluate?](open-questions/multi-agent-mode-supported.md)
- [How should the agent treat instructions inside scraped pages and MCP tool output?](open-questions/untrusted-content-trust-boundary.md)

## Weaker signals (not given pages)

- Unknown `RETRIEVER` names fall back to Tavily with only a print (`config.py:79-83`). Bool env typos become False (`config.py:278-279`).
- `source_urls` override `report_source`, so local or hybrid documents are ignored when URLs are given (`researcher.py:145`).
- Empty `langchain_documents` silently fall back to web search (`researcher.py:594`).
- Chat takes `report` and `messages` (including roles) from the client, and runs one tool round with no cost tracking (`backend/chat/chat.py:230-245`).
- `<think>` tags from reasoning models are not stripped from reports (ISSUE_BACKLOG #1306/#1303).
- Non-OpenAI models are priced at a flat $5/$15 per million tokens (`utils/costs.py:236-239`).
- Sub-query generation ignores the configured prompt family (`actions/query_processing.py:204`, no `prompt_family` passed).
- MCP tool selection has no read-only allowlist, and its fallback scores tools by name substrings (`mcp/tool_selector.py:175-199`).

## Recorded eval evidence

- `evals/hallucination_eval/results/aggregate_results.json`: 1 of 2 reports judged hallucinated (n=2).
- `evals/simple_evals/logs/eval_2026-05-29_19-03-20_n3.jsonl`: 3/3 correct (n=3).
- `deep_agents/BENCHMARK.md`: 56% citation precision over 10 DRB tasks for the deep_agents variant. Raw files under `deep_agents/benchmark_results/` include runs where GPT Researcher trails the baseline (FRAMES, recency, breadth) that BENCHMARK.md does not report.
