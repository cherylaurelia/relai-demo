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