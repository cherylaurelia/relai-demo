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