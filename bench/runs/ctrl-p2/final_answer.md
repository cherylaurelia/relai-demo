I read the core `gpt_researcher/` package, the detailed-report flow and the prompts myself. A background agent read `multi_agents/`, `backend/server/`, MCP and the retrievers; I re-checked its four "certain crash" claims against the code and they hold. I couldn't run the test suite: there's no virtualenv and I didn't install dependencies. Two of my claims I confirmed with small Python snippets; everything else comes from reading the code.

## 1. Certain crashes

| # | Where | What fails |
|---|---|---|
| 1 | `multi_agents/agents/orchestrator.py:102`, `editor.py:140` | Both call `self._route_fact_check` / `self._route_draft_review`, which are never defined. The functions exist as `route_fact_check` / `route_draft_review` in `fact_review.py` / `draft_review.py`, but are never imported. **Every multi-agent run fails while the graph is being built.** |
| 2 | `backend/server/server_utils.py:321` | `stream_output` is never imported, so `/api/multi_agents` raises `NameError`. The query is also hard-coded to "Is AI in a hype cycle?". |
| 3 | `backend/server/app.py:303-304` | For `multi_agents`, `report_information` is a plain string, so `report_information[0]` is its first character. The DOCX and PDF each contain one character. |
| 4 | `gpt_researcher/skills/deep_research.py:406` | When no search queries come back, the early `return` uses `all_learnings` and friends, which aren't assigned until line 416. That's an `UnboundLocalError`. It triggers whenever the LLM's JSON can't be parsed or leaves out `researchGoal`. |

## 2. Runs that finish with wrong output and no error (the most likely real-world failures)

1. **Detailed report with `source_urls` gives empty subtopic sections** (`detailed_report.py:154`). Each subtopic researcher gets the same `source_urls`, but those URLs are already in the shared `visited_urls`. `_get_new_urls` therefore returns nothing and the context comes back empty. The writer's empty-context guard (`writer.py:79`) then makes every subtopic section read "I could not gather any source material for…".
2. **Draft section titles never parse, so subtopics repeat each other** (`detailed_report.py:170`). `generate_draft_section_titles` returns a list, and the code calls `str(list)` on it. That gives `"['## A', '## B']"`, which has no markdown headers, so `extract_headers` returns `[]`. The "avoid repeating earlier sections" lookup only ever uses the subtopic name.
3. **Deep research drops its cited learnings** (`deep_research.py:624`). The learnings that carry citations go at the front of the list and raw context is appended after it. `trim_context_to_word_limit` keeps the end of the list, and the 25k-word cap is easily exceeded (about 9 nested researchers). So the cited learnings are the first thing thrown away.
4. **`complement_source_urls=True` garbles the web context** (`researcher.py:158`). `research_data += ' '.join(additional_research)` runs on a string, which puts a space between every character. I confirmed this: `"Hello world"` becomes `"H e l l o   w o r l d"`.
5. **A custom `prompt_family` is ignored for the main report and for query planning.** `ReportGenerator.research_params` (`writer.py:39`) never passes it to `generate_report`. `plan_research_outline` (`query_processing.py`) doesn't forward it to `generate_sub_queries`. Both fall back to the base `PromptFamily`.
6. **`MCP_SERVERS` and `MCP_ALLOWED_ROOT_PATHS` from config are always wiped** (`config/config.py:53-54`). Both are reset to `[]` after the config file has been loaded.
7. **Search failures look the same as "no results":**
   - Tavily and Serper catch or print API errors and return `[]`; this includes 401s and 429s.
   - `_search_relevant_source_urls` (`researcher.py:839`) builds retrievers without passing `headers`, so API keys supplied per request (e.g. `tavily_api_key` in headers) are ignored on the main search path.
   - The empty-context guard catches the worst case. A partial failure still produces a thin report that reads as confident.
8. **The References list is wrong both ways.** `visited_urls` is filled before scraping, so URLs that failed to scrape or were filtered out still get listed. Results that arrive with `raw_content` already fetched never enter `visited_urls`, so they're missing. On top of that, the LLM writes its own reference list (the prompt demands one) and `add_references` appends a second.
9. **Source curation (off by default) is broken if turned on** (`curator.py`, `prompts.py:319`):
   - It receives one concatenated string, but the prompt asks the model to return "the EXACT sources JSON list format as the original sources".
   - The code then reads capitalised `Title`/`Content`/`Source` keys that the prompt never mentions.
   - Output is capped at 8000 tokens, while the model is asked to reproduce all the content verbatim.
   - If the model returns lowercase keys, the context becomes empty `Title:/Content:` stubs. These are not empty strings, so they get past the empty-context guard and the report is written from nothing.
10. **Cost reporting understates real spend.**
    - Deep research's own LLM calls pass no `cost_callback`.
    - Costs from the nested researchers are never added to the parent.
    - In `agent.py:790`, `self._log_event(...)` is called without `await`, so cost-update events never fire.

## 3. Fragility under real load or real configurations

- **The temperature and reasoning-effort model lists use exact string matches** (`llm_provider/generic/base.py:43-90`). A dated snapshot (`gpt-5.4-2026-…`) or an unlisted model gets sent `temperature`, which reasoning models reject.
- **`create_chat_completion` retries every error 10 times with backoff** (`utils/llm.py`), including auth failures and context-length errors. That is roughly a minute per call before it fails. `generate_sub_queries` wraps it in three fallback layers, so up to 30 attempts.
- **Report streaming:** the first attempt sends partial output to the websocket. The fallback in `generate_report` streams again, so the UI shows duplicated text. If both attempts fail, the error is only printed and an empty report is returned.
- **The MCP retriever's `search()` blocks the event loop for up to 300s** (`retrievers/mcp/retriever.py:224-292`, called synchronously from `researcher.py:688`). The background agent found this; I didn't trace it myself.
- **The similarity threshold is 0.42 for every embedding provider** (`default.py`). With non-OpenAI embeddings, whose scores sit on a different scale, the filter can drop every chunk and the context comes back empty.
- **Deep research:**
  - Recursion into deeper levels runs one branch at a time.
  - Child researchers lose `query_domains` and `prompt_family`, and are forced to web as the source.
  - Each child builds its own `WorkerPool` with a 15-thread `ThreadPoolExecutor` that is never shut down, so threads leak on a long-running server.
- **Multi-agent (background agent's findings):**
  - `call_model` swallows exceptions and returns `None`, and the reviewer and fact-checker treat `None` as "accept". A failed LLM call therefore approves the draft.
  - Human feedback is approved whenever it contains the substring `"no"` ("add a section on **no**des").
  - The feedback loop's cap reads `revisions_count`, which doesn't exist (the key is `plan_revision_count`).
  - Human feedback can't actually arrive over the websocket, because the main loop is already reading it. With feedback enabled, the run hangs.

## 4. Prompt problems (`gpt_researcher/prompts.py`)

- **Made-up citations:** the report prompt asks for APA references in the form "Author, A. A. (Year, Month Date)…" and to "prioritize new articles". The context only contains `Source/Title/Content`, with no authors or dates, so the model invents them.
- **Padding:** "At least {total_words} words… as long as you can", together with "You MUST determine your own concrete and valid opinion", pushes the model to pad and speculate when sources are thin.
- **Prompt injection:** scraped web text is pasted straight into `Information: "{context}"`, with no delimiter and no instruction to treat it as data. Instructions planted in a web page reach the report writer.
- **Brittle agent selection:** `auto_agent_instructions` never says "respond only with JSON". It works today only because `handle_json_error` falls back to `json_repair` and a regex.

## Questions I'd have asked you

1. Which entry points matter most: the pip library or CLI, the FastAPI server, or `multi_agents`? Section 1 shows `multi_agents` can't currently run at all, which may mean it's unused.
2. Is `CURATE_SOURCES` turned on in any deployment? If not, item 9 in section 2 is low priority.
3. Which LLM and embedding providers do you run? That decides how much the model-list and similarity-threshold risks matter.
4. Is prompt injection from scraped pages in scope? `ISSUE_BACKLOG.md` says the backend is operator-run with no auth by design.
5. Are the two `PR_*.md` drafts meant to be checked here? The Brave snippet fix is already in `researcher.py:853`.

The quickest wins are sections 1 and 2: each is a one- to five-line fix. I haven't edited anything.