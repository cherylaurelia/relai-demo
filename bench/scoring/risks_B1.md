# Final answer to the user

Both claims hold up:
- `retriever.py:284-286` calls `future.result()` on the event-loop thread, even though the comment above it says the thread pool is there to avoid blocking.
- MCP configs from the websocket go straight into the stdio `command`/`args`.

# Where gpt-researcher is likely to fail

The worst problem: the core package probably can't be imported on Python 3.11–3.13, which covers the Docker image. Beyond that, the LangGraph multi-agent graph can't be built, and the MCP path freezes the server.

**How I checked:** I read the core research pipeline myself. Three sub-agents read `multi_agents/`, `deep_agents/` and the backend/MCP/retriever/scraper layers, and I re-checked their high-severity claims myself before including them. I didn't call any LLM or the network. The sandbox also blocked me from running a Python 3.12 interpreter, so finding 1 comes from reading the code rather than reproducing it. "Confirmed" below means I followed the code path through.

## Will break on most runs

1. **Probably can't import on Python 3.11–3.13.** `gpt_researcher/actions/query_processing.py:6` uses `Any`/`List` in a function signature, but the typing import is at line 37, and the file has no `from __future__ import annotations`.
   - Python 3.11–3.13 evaluates those annotations when the function is defined, so it would raise `NameError`.
   - `actions/__init__.py:2` imports this module, so plain `import gpt_researcher` would fail.
   - It runs on this Mac only because it has Python 3.15, which defers annotations.
   - The repo pins 3.11 (`.python-version`) and the Dockerfile uses `python:3.12-slim`.
   - The only CI workflow I checked, `build.yml`, builds and pushes the image and never runs the tests, so this would ship unnoticed.
   - Fix: move the imports above the function, or add the `__future__` line.

2. **The multi-agent graph can't be built.** `multi_agents/agents/orchestrator.py:102` refers to `self._route_fact_check` and `editor.py:140` to `self._route_draft_review`; neither method exists (confirmed by grep).
   - `route_fact_check` and `route_draft_review` exist as plain functions but are never connected.
   - The tests load those modules by file path, so they pass without ever building the graph.
   - The backend's fallback to the ag2 version only catches import errors, not this runtime error.

3. **MCP freezes the whole server.** `retrievers/mcp/retriever.py:284-286` waits on a background thread for up to 300 s, but it does so on the event-loop thread. It's called synchronously from async code at `skills/researcher.py:688`.
   - Every websocket and request on the server stalls until the MCP run finishes.

4. **Websocket clients may be able to run commands on the server (likely, depending on deployment).** `mcp_configs` comes straight from websocket JSON (`server_utils.py:410`) and becomes the stdio `command`/`args` (`mcp/client.py:83-89`). My sub-agent reports that `/ws` has no authentication, but I didn't trace that part myself.

## Wrong output with no error

5. **`complement_source_urls=True` garbles the web context.** At `researcher.py:158`, `research_data += ' '.join(additional_research)` runs on a string, so every character gets a space between it ("a b c"). Confirmed.

6. **The context comes from whichever pages happened to come first.**
   - URLs are shuffled (`researcher.py:868`).
   - Without a `k` setting, LangChain's `EmbeddingsFilter` keeps matching chunks in document order, not by score. This is from memory of LangChain, not checked against the installed version.
   - `pretty_print_docs` then takes the first 10 chunks.
   - The result: each sub-query's context is often one or two long pages, and it changes from run to run.

7. **The References list includes pages that were never used.** URLs are added to `visited_urls` before scraping (`researcher.py:810`), and `add_references` lists all of them. Failed and irrelevant pages show up as citations.

8. **Driver error messages can be treated as page content.** The nodriver scraper returns `str(e)` as the page text, and the only filter is a 100-character minimum (`scraper.py:134`). Longer error messages pass into the report context.

9. **Rate limits look the same as "no results."** Most retrievers turn HTTP errors into `[]`. The writer's empty-context guard (`writer.py:79-88`) only fires when *every* source is empty, so a partial outage still produces a confident report from thin evidence.

10. **The prompts push the model to pad.** The main report prompt says "MUST determine your own concrete opinion", "write as long as you can" and "at least 1200 words". Unlike the quick-summary prompt, it never allows "the evidence is insufficient".

11. **Deep research:**
    - Nested researchers always use web search (`deep_research.py:436`), so `local` and `hybrid` are silently ignored.
    - Their costs aren't rolled up to the parent, so the reported cost is understated.
    - The final trim keeps items from the end (`deep_research.py:624`), so the citation-bearing learnings at the front are dropped first.
    - Deeper levels run one after another, which makes it slow.

12. **Hybrid reports aren't told to cite URLs.** The URL-citation instructions only apply when `report_source == "web"` (`prompts.py:278`), so hybrid reports are only asked for document names.

## Reliability, cost and smaller bugs

- **`choose_agent` can crash the run.** In the regex fallback (`agent_creator.py:96`), a JSON object with different keys raises an uncaught `KeyError`.
- **Custom prompt families are ignored for sub-query generation.** `plan_research_outline` never passes `prompt_family` on (`query_processing.py:204`).
- **Cost-update events never reach the log handler.** `add_costs` calls the async `_log_event` without awaiting it (`agent.py:790`).
- **Failed LLM calls are retried even when retrying can't help.** `create_chat_completion` tries 10 times with backoff (about 60 s) even for auth or context-length errors. The streamed final report gets only one attempt, and `generate_report` returns `""` if both tries fail.
- **Source curation is fragile when enabled.** It sends the whole context to stdout via `print` and parses the reply with strict `json.loads`. The default config has curation turned off.
- **Detailed reports:** one failing subtopic discards the whole report, and a failed subtopic list produces an empty body with no error.
- **Server:** a client disconnect leaks connection state and kills the run. `write_report` for `multi_agents` keeps only the first character of the report (`app.py:303`). Duplicate routes make the LLM chat endpoint unreachable. A corrupt `reports.json` is read as empty and the next save wipes all reports.
- **Scrapers and retrievers:**
  - Several HTTP calls have no timeout (Bing, Google, Searx, Semantic Scholar, PubMed).
  - Infinite-scroll pages never finish scrolling.
  - Selenium hard-codes port 9222 on Linux, so concurrent scrapers would likely collide.
  - Missing scraper packages trigger a `pip install` at runtime.
- **Other multi-agent bugs** (the review loops only become reachable once item 2 is fixed):
  - The plan-revision limit reads a state key nothing sets, so plan revisions are unbounded.
  - "None." isn't accepted as "no notes", so review loops run until LangGraph's recursion limit.
  - LLM failures become `None` and crash later.
  - The human-feedback check `"no" in feedback` treats "nonprofits" as approval.
  - `agent.py` is missing `publish_formats`.

## The benchmark docs overstate deep_agents

- **Recency:** I confirmed GPTR lost all three recency runs to plain Tavily (coverage 0.583 / 0.702 / 0.643 vs 0.833 / 0.786 / 0.821). "Recency" doesn't appear in BENCHMARK.md, the README or SHARE_SUMMARY.md.
- **Breadth:** GPTR also lost the breadth runs at budgets 40 and 60.
- **SimpleQA:** the "83% parity" figure came after the prompt was tuned on the same 30 questions.
- **DRB "7/10 wins":** no per-task results are in the repo to back it.
- **Step limit:** the shipped `main.py` uses a limit of 200 but was benchmarked at 60, and it doesn't handle `GraphRecursionError`.

## Questions I'd have asked you

1. Which surface matters most: the library, the FastAPI server, `multi_agents`, or `deep_agents`? That decides whether item 1 or item 4 is the top fix.
2. Which Python do you actually run on? If it's 3.14+, item 1 won't affect you locally, but it still breaks the Docker image.
3. Is the server exposed beyond localhost? If so, item 4 is a security issue, not just a bug.
4. Are the `deep_agents` benchmark docs going to be published? If so, they need the losing runs added.
5. Is there a CI workflow that runs pytest somewhere I didn't see? `build.yml` doesn't.

I didn't change any files.