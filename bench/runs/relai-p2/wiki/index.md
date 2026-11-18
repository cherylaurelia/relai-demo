# EvalsWiki index — gpt-researcher (snapshot 9ad2148)

First pass 2026-11-17 from code, prompts, docs, existing eval/benchmark results and issue triage. No agent runs.

## Requirements
- Grounding and citations: [report-grounded-in-provided-sources](requirements/report-grounded-in-provided-sources.md), [references-match-used-sources](requirements/references-match-used-sources.md), [abstain-when-no-evidence](requirements/abstain-when-no-evidence.md)
- Configuration honored: [report-in-configured-language](requirements/report-in-configured-language.md), [report-meets-word-target](requirements/report-meets-word-target.md), [local-source-stays-local](requirements/local-source-stays-local.md)
- Multi-agent: [multi-agent-revision-loops-terminate](requirements/multi-agent-revision-loops-terminate.md), [multi-agent-human-feedback-applied](requirements/multi-agent-human-feedback-applied.md)

## Risks
- Grounding: [hybrid-empty-context-bypasses-abstain](risks/hybrid-empty-context-bypasses-abstain.md), [mcp-llm-analysis-treated-as-source](risks/mcp-llm-analysis-treated-as-source.md), [citation-metadata-fabricated](risks/citation-metadata-fabricated.md), [stale-time-sensitive-facts](risks/stale-time-sensitive-facts.md), [planner-seeds-guessed-answer](risks/planner-seeds-guessed-answer.md), [scraped-content-prompt-injection](risks/scraped-content-prompt-injection.md), [complement-source-urls-corrupted](risks/complement-source-urls-corrupted.md), [visited-url-race-drops-sources](risks/visited-url-race-drops-sources.md)
- Silent failure and cost: [silent-partial-research-failure](risks/silent-partial-research-failure.md), [deep-research-zero-queries-crash](risks/deep-research-zero-queries-crash.md), [reasoning-token-retry-cost](risks/reasoning-token-retry-cost.md)
- Privacy and config: [local-mode-planning-web-leak](risks/local-mode-planning-web-leak.md), [language-ignored-in-some-report-types](risks/language-ignored-in-some-report-types.md)
- Multi-agent and server: [multi-agent-graph-build-crash](risks/multi-agent-graph-build-crash.md), [human-feedback-substring-no](risks/human-feedback-substring-no.md), [plan-revision-cap-ignored](risks/plan-revision-cap-ignored.md), [human-feedback-web-ui-broken](risks/human-feedback-web-ui-broken.md), [rest-multi-agent-one-char-report](risks/rest-multi-agent-one-char-report.md)

## Open questions
[priority-entry-point](open-questions/priority-entry-point.md), [local-mode-web-contact](open-questions/local-mode-web-contact.md), [requirement-grounding-confirmation](open-questions/requirement-grounding-confirmation.md), [revision-cap-outcome](open-questions/revision-cap-outcome.md)
