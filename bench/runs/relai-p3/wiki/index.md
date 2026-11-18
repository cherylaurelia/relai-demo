# EvalsWiki index

Agent: GPT Researcher (core report agent, deep research, detailed reports, multi_agents, deep_agents, backend chat, MCP). Found at fae2317.

## Requirements
- [Cite only sources present in the gathered information](requirements/cite-only-provided-sources.md)
- [Write in the requested tone](requirements/honor-requested-tone.md)
- [Multi-agent reports follow the task guidelines when enabled](requirements/multi-agent-follows-guidelines.md)
- [One deduplicated reference list of used sources](requirements/single-deduplicated-reference-list.md)
- [Say so when search results cannot answer the query](requirements/state-insufficient-evidence.md)
- [Write in the requested language](requirements/write-in-requested-language.md)

## Risks
- [REST API saves only the first character of multi-agent reports](risks/backend-multi-agent-report-first-char.md)
- [Chat shows sources from a second search, not the one the model read](risks/chat-sources-from-second-search.md)
- [Complementing source URLs with web search garbles the web context](risks/complement-source-urls-garbled.md)
- [Deep-agents reports: about 44% of citations fail verification](risks/deep-agents-low-citation-precision.md)
- [Deep-agents GPTR config is worse than raw search on recent facts](risks/deep-agents-recency-regression.md)
- [Deep research trims cited learnings first and accepts unverified source URLs](risks/deep-research-citations-trimmed-or-unverified.md)
- [Deep research cost grows multiplicatively and is under-reported](risks/deep-research-cost-blowup-undercounted.md)
- [Deep research crashes when the model returns no search queries](risks/deep-research-zero-queries-crash.md)
- [Detailed reports silently lose subtopics or deduplication](risks/detailed-report-subtopic-degradation.md)
- [Human plan feedback containing "no" anywhere is treated as approval](risks/human-feedback-no-substring.md)
- [Hybrid mode with no results bypasses the empty-context guard](risks/hybrid-empty-context-bypasses-abstain.md)
- [MCP model's own pre-tool prose enters context labelled as a source](risks/mcp-llm-analysis-cited-as-source.md)
- [MCP failures are silent and fast mode pastes one result set into every sub-query](risks/mcp-silent-failure-and-duplication.md)
- [MCP tool selection can choose mutating tools](risks/mcp-tool-selection-no-readonly.md)
- [Multi-agent fact-check has no sources and treats LLM failure as approval](risks/multi-agent-fact-check-unreliable.md)
- [Multi-agent pipeline wires graph edges to methods that do not exist](risks/multi-agent-graph-undefined-routers.md)
- [Shipped multi-agent task disables guideline review](risks/multi-agent-guidelines-off-by-default.md)
- [Multi-agent revision caps are not enforced](risks/multi-agent-revision-caps-unwired.md)
- [Retrieved web, document and MCP text is spliced unfenced into prompts](risks/prompt-injection-from-retrieved-content.md)
- [Source lists include every visited URL, not the cited ones](risks/references-list-visited-not-cited.md)
- [Requested tone, prompt family and report options are silently replaced](risks/requested-settings-silently-ignored.md)
- [Thin or partial context still yields a long, opinionated report](risks/thin-context-full-length-report.md)

## Open questions
- [How should a no-sources abstention reach the user?](open-questions/abstention-delivery.md)
- [Is the MCP "LLM Analysis" result meant to be a citable source?](open-questions/mcp-llm-analysis-intended.md)
- [Is defending against instructions in retrieved content a requirement?](open-questions/prompt-injection-threat-model.md)
- [Should source lists contain only cited sources, or every page consulted?](open-questions/references-used-vs-visited.md)
- [On thin evidence: abstain, hedge, or give a concrete opinion?](open-questions/thin-evidence-abstain-or-opine.md)
- [Which entry points should evaluation cover?](open-questions/which-entrypoints-in-scope.md)
