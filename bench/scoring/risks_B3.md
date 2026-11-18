# Final answer to the user

I read the core research loop, prompts and docs myself and had two reviewers cover scrapers/retrievers and multi-agent/backend. I spot-checked their main claims. I didn't install the dependencies, so the test suite wasn't run; the import failure was checked on the bare interpreter, and the string-joining bug was reproduced in isolation.

## Bottom line

On the standard deployment, `import gpt_researcher` fails before any research starts. Past that, the most likely failures are crashes in deep research and multi-agent mode, and reports that look complete but are built from damaged or missing context.

## 1. Hard failures (all checked)

| # | Where | What happens |
|---|---|---|
| 1 | `gpt_researcher/actions/query_processing.py:6` | `Any` and `List` are used in a type hint before they are imported (line 37). On Python 3.11–3.13 this raises `NameError` at import, and the package's import chain brings it in, so nothing loads. The Dockerfile uses `python:3.12`. I reproduced it on the system Python; it only works on 3.14+. |
| 2 | `skills/deep_research.py:406-414` | The "zero search queries" guard returns `all_learnings` and other names that are only assigned at line 416, so it raises `UnboundLocalError`. This is exactly the case it was written for: the planning model returns output that can't be parsed. It's outside the per-query `try`, so the whole deep-research run crashes. |
| 3 | `multi_agents/agents/orchestrator.py:102`, `editor.py:140` | They call `self._route_fact_check` and `self._route_draft_review`, which don't exist. Every `multi_agents` run fails with `AttributeError` while the graph is being built. |
| 4 | `prompts.py:903` | An unknown `PROMPT_FAMILY` should fall back to the default with a warning, but the fallback calls `PromptFamily()` without its required `config`, so a typo crashes with `TypeError`. |
| 5 | `backend/server/server_utils.py:321` | `/api/multi_agents` uses `stream_output`, which isn't imported there, so the endpoint fails with `NameError`. |

## 2. Reports that look fine but aren't

- **Damaged context with `complement_source_urls=True`** (`skills/researcher.py:158`). `research_data += ' '.join(additional_research)` joins a string, which puts a space between every character ("S o u r c e : h t t p s : / / …"). Every web URL and fact in that part reaches the model unreadable. Reproduced.
- **Deep research drops its own conclusions** (`deep_research.py:611-624`). The final context is the distilled, cited learnings followed by the raw page text. The trimmer keeps items from the end, so once the raw text passes 25,000 words (likely with default breadth and depth), the learnings are what gets cut.
- **MCP results repeated many times** (`researcher.py:557`). In the default "fast" MCP mode, the cached MCP results are added to every sub-query's context, so the same material appears about 4–5 times and uses up context.
- **Custom prompt families are partly ignored.**
  - `plan_research_outline` doesn't pass `prompt_family` on (`query_processing.py:204`).
  - `writer.py` doesn't pass it into `generate_report`.
  - Sub-query planning and the main report prompt therefore always use the default prompts. Issue #1572 already notes this.
- **Deep research sub-researchers lose settings** (`deep_research.py:433`).
  - They are forced to web search (`report_source=Web`), so deep research over local documents goes to the web anyway.
  - They don't get `prompt_family` or `query_domains`.
  - Their costs are never added to the parent, and the deep-research LLM calls pass no cost callback, so reported deep-research cost is far too low.
- **Source curation (`CURATE_SOURCES=true`) gives the model a near-impossible task** (`skills/curator.py`, prompt at `prompts.py:319`).
  - It receives the whole joined context as one string and must return it verbatim as JSON within 8,000 output tokens.
  - On a normal run the output gets cut off, `json.loads` fails, and it quietly returns the input, so you pay for a call that does nothing.
  - It also `print`s the entire source text to stdout.
- **User-supplied search API keys are ignored** (`researcher.py:839`, `query_processing.py:73`). Retrievers are created without `headers`, so a Tavily key sent per request is dropped. The server's key is used instead, or a blank one, which gives a 401 and an empty report.
- **Scraper error text treated as page content** (`scraper/browser/nodriver_scraper.py:207`). With `SCRAPER=nodriver` and zendriver not installed, the 103-character install message passes the "at least 100 characters" check and becomes the "content" of every page.
- **Missing language models' quirks aren't handled.** There's no stripping of `<think>` tags anywhere (issues #1303 and #1306), and `chunk.content` is assumed to be a string (`llm_provider/generic/base.py:381`), which is likely related to the Gemini 3 failure in #1628. I didn't run this one.

## 3. Prompt-level weaknesses

- Scraped page text is pasted straight into the report prompt (`Information: "{context}"`) with nothing marking it as untrusted, so a web page can inject instructions into the report.
- The report prompt says "You MUST determine your own concrete and valid opinion" and "write as long as you can". Combined with thin context, that pushes the model toward padding and overclaiming.
- `LANGUAGE` defaults to `"english"` and is stated as a hard requirement, so non-English questions get English reports (#1767).
- The agent-selection prompt (`auto_agent_instructions`) never says "reply with JSON only". It works because of the `json_repair` fallback; when that fails it quietly uses "Default Agent".
- The search-results list passed into sub-query planning can include full page text, which bloats the planning prompt.

## 4. Hangs and stalls

- **MCP search blocks the server** (`researcher.py:688`). The synchronous MCP search is called directly from async code; it starts a thread and waits on `future.result(timeout=300)`, which freezes the whole server's event loop (every client, not just one request) for up to 5 minutes. The other retrievers correctly use `asyncio.to_thread`.
- **LLM calls have no overall time limit** (`utils/llm.py:110`).
  - There are 10 attempts with backoff and no per-call deadline, including for errors that will never succeed, like a bad API key or wrong model name.
  - `generate_sub_queries` chains three of these, so one bad config means roughly 30 calls before failing.
  - Only OpenRouter sets a request timeout.
  - This matches #1764 ("stuck with no logs").
- **Several search retrievers have no HTTP timeout** (Google, Bing, Searx, Semantic Scholar, PubMed). The BeautifulSoup and WebBaseLoader scrapers have per-read timeouts or none, so a slow server can hold a worker indefinitely.
- **Multi-agent human feedback loops can't finish.**
  - The revision cap reads a `revisions_count` key that nothing ever sets.
  - The feedback receive competes with the server's main receive loop.
  - Approval is a substring check: `"no" in feedback` treats "not enough detail" as approval.

## 5. Smaller confirmed issues

- `add_costs` calls the async `_log_event` without `await` (`agent.py:790`), so cost updates never reach the log handler.
- `if research_data and len(research_data) == 0` (`researcher.py:148`) can never be true, so the "no relevant context" message is never shown.
- Prefetched retriever results skip URL de-duplication, and URLs are only de-duplicated by exact string, so the same page with a trailing slash or `utm_` parameters is scraped again.
- `_check_pkg` runs `pip install` at runtime when a provider package is missing. That fails in read-only containers and installs whatever the index serves.
- From the backend review:
  - WebSocket disconnects are caught too early, so connections and queues leak.
  - `POST /report/` with `multi_agents` writes only the first character of the report to DOCX/PDF.
  - Reports without an id all share `temp_id` and overwrite each other.
  - Duplicate route definitions in `app.py` make the chat handler unreachable.

Already handled in this snapshot: the Brave snippet bug described in `PR_pr_fix-brave-snippet-bypasses-scraper.md` is fixed (`researcher.py:851-861`), and deep research no longer loops forever on empty retrievers.

## Questions for you

1. **Which Python version do you deploy on?** If it's the Docker image or anything below 3.14, #1 is a total outage, and adding `from __future__ import annotations` (or moving the imports up) is the one-line fix. If it's only 3.14+, #1 just blocks everyone else.
2. **Is this review for the gpt-researcher maintainers (the `ISSUE_BACKLOG.md` workflow) or for your own use?** It changes whether the security items in section 5 and the backlog's Bucket A (SSRF, MCP command execution) matter, given the backlog says the backend is "operator-run, no auth by design".
3. **Do you want me to install the dependencies in a venv and run `tests/`?** I held off without your go-ahead. It would confirm the provider-format findings in section 2.
4. **Do you want fixes?** I made no changes. The highest-value small fixes are #1, #2, #4, the `' '.join` line, and the trimming order in deep research; each is a few lines.