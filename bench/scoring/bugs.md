## #2055 (2026-08-07): v3.6.0 broken as shipped: stray committed gitlink breaks git-URL Docker builds; missing typing import crashes the server at boot

Thanks for the project — we run it self-hosted (fully local: Ollama LLMs + SearXNG retriever) and hit two independent defects in the `v3.6.0` release (commit `5d84d2f5553e70a2765a8ff3a0d2672d60437ce8`). Both look like artifacts of a release cut from a dirty working tree. Details and one-line fixes below.

### Defect 1 — stray committed gitlink breaks Docker git-URL builds

The v3.6.0 tree contains a gitlink (submodule-mode entry) with no corresponding `.gitmodules`:

```
$ git ls-files -s | awk '$1==160000'
160000 6c75117d27b866163aac44ce0e2360958ffbe825 0   .claude/worktrees/crazy-curie-e43899

$ ls .gitmodules
ls: cannot access '.gitmodules': No such file or directory
```

Docker/BuildKit git-URL build contexts initialize submodules unconditionally, so any build that consumes the repo as a git URL hard-fails:

```
$ docker build https://github.com/assafelovic/gpt-researcher.git#v3.6.0
...
fatal: No url found for submodule path '.claude/worktrees/crazy-curie-e43899' in .gitmodules
```

The same applies to any CI/workflow that runs `git submodule update --init`. (Plain `git clone` still works — the gitlink is just left uninitialized as an empty directory.)

**Fix:** `git rm --cached .claude/worktrees/crazy-curie-e43899` and commit; consider adding `.claude/` to `.gitignore` so a local agent worktree can't be committed again.

### Defect 2 — `query_processing.py` missing its typing import; the server cannot boot

`gpt_researcher/actions/query_processing.py` in v3.6.0 uses `Any` / `Dict` / `List` in annotations but never imports them (and has no `from __future__ import annotations`), e.g.:

```python
def _normalize_sub_queries(parsed: Any, fallback_query: str) -> List[str]:
```

Annotations are evaluated at import time, so the backend dies at startup:

```
NameError: name

## #2060 (2026-08-11): multi_agents: both review-loop routers reference undefined methods — workflow crashes at graph construction (regression around #1909)


## Summary

At current master (checked at `5d84d2f`), the `multi_agents` workflow cannot be constructed: both conditional-edge routers are wired to methods that do not exist.

1. **Fact-check loop.** `multi_agents/agents/orchestrator.py`, line 102:

   ```python
   workflow.add_conditional_edges(
       'fact_checker',
       self._route_fact_check,
       {"accept": "visualizer", "revise": "writer"}
   )
   ```

   `ChiefEditorAgent` defines no `_route_fact_check` (no base class, no assignment anywhere in the package) — `self._route_fact_check` raises `AttributeError` the moment `_add_workflow_edges` runs, i.e. on every `run_research_task` call.

2. **Draft-review loop.** `multi_agents/agents/editor.py`, line 140: the inner reviewer/reviser workflow wires `self._route_draft_review`; `EditorAgent` defines no such method either.

The intended routers appear to exist already: `plan_review.route_human_feedback`, `fact_review.route_fact_check`, and `draft_review.route_draft_review` are complete, documented free functions (with bounds and graceful-exceed errors) — but nothing imports `fact_review` or `draft_review`, and the two `self._route_*` bindings that would call them are missing. It looks like the modules landed in the #1909 era while the one-line bindings did not.

## Reproduction sketch

```python
from multi_agents.agents import ChiefEditorAgent
ChiefEditorAgent(task={"query": "x"}).init_research_team()
# AttributeError: 'ChiefEditorAgent' object has no attribute '_route_fact_check'
```

(And after fixing that one, the same again for `_route_draft_review` when the editor's inner workflow is built.)

## Suggested fix

Bind the existing routers where they were meant to be used:

```python
# orchestrator.py
from .fact_review import route_fact_check
def _route_fact_chec

## #2061 (2026-08-11): multi_agents: strict sentinel parsers from #1909 are not used at the human gate, and the new visualizer reintroduces substring matching


## Summary

#1909 added `agents/utils/none_sentinels.py` with two strict parsers (`is_none_accept_response`, `is_human_plan_approval`) and wired the first into `reviewer.py` and `fact_checker.py`. Two call sites still do substring matching — one of them the exact case #1882 reported:

1. **Human plan gate still substring-matches "no".** `multi_agents/agents/human.py`, line 47:

   ```python
   if user_feedback and "no" in user_feedback.strip().lower():
       user_feedback = None
   ```

   Any feedback *containing* the letters "no" is treated as approval and silently discarded: "**no**t enough on cost data", "add a section on **no**vel methods", "**No**vember data is missing" all read as "no changes". `is_human_plan_approval` exists precisely for this (its docstring names these cases) but `human.py` never imports it.

2. **The visualizer (new since #1909) repeats the class.** `multi_agents/agents/visualizer.py`, line 42:

   ```python
   if "None" not in diagram_output:
       diagrams.append(diagram_output)
   ```

   Inverted membership, same failure: a legitimate Mermaid diagram whose text contains the token "None" anywhere (a label like `"None reported"`, a legend entry) is discarded wholesale, and the report ships without its diagram. `is_none_accept_response` is right there in utils.

## Reproduction sketch

- Human gate: run with `include_human_feedback: true` and reply "not enough on evaluation" — the plan is accepted unchanged, feedback dropped.
- Visualizer: research data whose generated diagram contains a "None" label — `diagrams` comes back empty despite a valid diagram in the model output.

## Suggested fix

```python
# human.py
from .utils.none_sentinels import is_human_plan_approval
if is_human_plan_approval(user_feedback):
    user_feedback = None

# v

## #2062 (2026-08-11): multi_agents: plan-revision limit can never trigger — router reads `revisions_count`, which nothing writes (and two competing bounds disagree)


## Summary

The human plan-review loop's escape hatch is dead code, so the loop is effectively unbounded (until LangGraph's recursion limit kills the run).

1. **The router reads a key nothing writes.** `multi_agents/agents/orchestrator.py`, lines 88–96:

   ```python
   MAX_REVISIONS = 5
   workflow.add_conditional_edges(
       'human',
       lambda state: (
           "accept" if state['human_feedback'] is None
           else "force_accept" if state.get('revisions_count', 0) >= MAX_REVISIONS
           else "revise"
       ),
       {"accept": "researcher", "force_accept": "researcher", "revise": "planner"}
   )
   ```

   The state schema (`memory/research.py`) and `human.py` maintain `plan_revision_count`; no code in the package ever writes `revisions_count`. `state.get('revisions_count', 0)` is therefore always `0`, `force_accept` can never fire, and a user who keeps giving feedback loops planner→human until `GraphRecursionError`.

2. **Two competing implementations, neither effective.** `plan_review.route_human_feedback` (added in the #1909 era) reads the *correct* key and enforces `DEFAULT_MAX_PLAN_REVISIONS = 3` with a graceful error — and `ChiefEditorAgent._route_human_feedback` correctly delegates to it — but the conditional edge above uses the inline lambda instead, with a different constant (5 vs 3). Two sources of truth for the same bound; the wired one is broken, the correct one is unreachable.

## Reproduction sketch

Run with `include_human_feedback: true` and reply with substantive feedback more than 5 times: `force_accept` never triggers (counter stuck at 0); the run dies at the recursion limit instead of gracefully force-accepting.

## Suggested fix

Replace the inline lambda with the existing method (one line):

```python
workflow.add_conditional

## #2065 (2026-08-13): OpenAI cost tracking never reads input_token_details.cache_read, so prompt-cache-hit tokens are billed at full price

**Describe the bug**

`_extract_usage_tokens` in `gpt_researcher/utils/costs.py` only reads the flat `input_tokens`/`output_tokens` fields off LangChain's standardized `usage_metadata`, and `calculate_llm_cost`'s OpenAI branch prices the full `input_tokens` count at the standard rate. Neither ever looks at `input_token_details.cache_read`, the portion of input tokens that hit OpenAI's automatic prompt caching and are billed at a discount. Any research run that benefits from provider-side caching (gpt-researcher's large repeated system prompts routinely trigger it, since caching kicks in on any prompt over roughly 1024 tokens repeated within the cache window) gets its cost overreported.

This is the same class of gap as #1986/#1989 (Anthropic cache tokens priced at $0), but on the OpenAI/generic branch, which #1989's diff does not touch, and in the opposite direction: overcounted here instead of undercounted there.

**To Reproduce**

```python
import importlib.util
spec = importlib.util.spec_from_file_location("costs", "gpt_researcher/utils/costs.py")
costs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(costs)

usage_no_detail = {"input_tokens": 5000, "output_tokens": 200}
usage_with_cache = {
    "input_tokens": 5000,
    "output_tokens": 200,
    "input_token_details": {"cache_read": 4500},
}

print(costs.calculate_llm_cost("openai", "gpt-4o", "", "", usage_metadata=usage_no_detail))
print(costs.calculate_llm_cost("openai", "gpt-4o", "", "", usage_metadata=usage_with_cache))
```

Both calls print `0.0145`, even though the second usage dict reports 4500 of the 5000 input tokens as cache hits. Ran this in a clean `python:3.11-slim` container (`pip install tiktoken` only, no other deps) against current `master` (`5d84d2f`).

**Expected behavior**

The cac

## #2069 (2026-08-18): Import should be at the top of the file right?

I am not a python developer so I might be mistaken but this was throwing an error when booting the project through docker compose.
Shouldn't all imports be at the top of the file? Especially when the import for Any is defined underneath the place it is actually being used/called upon. If I remembered correctly Python is executed from top to bottom so order would matter and moving it to the top fixed the error so I guess so. 

https://github.com/assafelovic/gpt-researcher/blob/5d84d2f5553e70a2765a8ff3a0d2672d60437ce8/gpt_researcher/actions/query_processing.py#L35-L39


Looking at the commit history this just seems to be some merging mistake but I am surprised there are no CI jobs running to fix this very obvious bug. Just starting the app, not even running tests, would catch this immediately. 

Want me to send in a PR for the imports? (not CI)

## #2077 (2026-08-23): WebBaseLoaderScraper discards extracted content when image/title enrichment fetch fails

`WebBaseLoaderScraper.scrape()` extracts page content via `WebBaseLoader.load()`, then makes a second, independent request purely for image/title enrichment (`self.session.get(self.link)` at line 31). Both the primary extraction and the enrichment fetch sit inside the same `try` block, and the blanket `except Exception` at the end returns `"", [], ""`, discarding the content that was already extracted successfully.

Any failure in the enrichment step wipes real content: a transient `ConnectionError`/`SSLError` on the second request, a rate limit or WAF block hit only on that second round trip, or a parse failure inside `get_relevant_images`/`extract_title` on a malformed page.

Repro (isolates `web_base_loader.py` with `WebBaseLoader.load()` stubbed to return real content, and `self.session.get` raising a `ConnectionError`):

```
content, images, title = scraper.scrape()
# content == "" even though WebBaseLoader.load() returned real page content
```

This is the same bug shape already fixed in `beautiful_soup.py` (#1684) and that other scraper backends (`firecrawl.py`, `tavily_extract.py`) have recently had fixed too: the enrichment fetch should be allowed to fail independently of the already-successful content extraction.

PR incoming: split the enrichment fetch into its own inner `try`/`except` so a failed image/title lookup degrades to empty `image_urls`/`title` instead of discarding `content`.


## #2093 (2026-08-31): Bug: complementary web context is split into space-separated characters

**Describe the bug**

`ResearchConductor.conduct_research` corrupts complementary web-search context when both `source_urls` and `complement_source_urls=True` are used.

The URL context and complementary web context are returned as strings. However, the implementation applies `" ".join(...)` directly to the complementary string, inserting a space between every character.

For example:

```text
Initial URL context:
source context

Complementary web context:
web context
```

produces:

```text
source contextw e b   c o n t e x t
```

instead of preserving the complementary text as a contiguous string.

The corrupted context is stored in `researcher.context` and returned by `conduct_research`.

**To Reproduce**

1. Check out GPT Researcher `main` at commit:

```text
6f998577d547b1e54ec662dac63583aa11e3b84b
```

2. Install the project and test dependencies:

```bash
python -m pip install -e ".[test]"
```

3. Create `tests/test_research_conductor_complement_context.py`:

```python
from types import SimpleNamespace

import pytest

from gpt_researcher.skills.researcher import ResearchConductor


@pytest.mark.asyncio
async def test_complementary_web_context_remains_contiguous():
    initial_context = "source context"
    additional_context = "web context"

    researcher = SimpleNamespace(
        query="test query",
        source_urls=["https://example.com/source"],
        complement_source_urls=True,
        agent="agent",
        role="role",
        retrievers=[type("Retriever", (), {})],
        cfg=SimpleNamespace(curate_sources=False),
        verbose=False,
        websocket=None,
        query_domains=[],
        parent_query=None,
        headers={},
        prompt_family=None,
        add_costs=lambda *args, **kwargs: None,
    )

    conductor = ResearchConductor(

## #2094 (2026-08-31): Bug: an all-blank retrievers header bypasses the default retriever

**Describe the bug**

`get_retrievers` returns an empty list when the `retrievers` header value contains only commas and whitespace.

For example:

```python
get_retrievers(
    {"retrievers": " , , "},
    cfg,
)
```

currently returns:

```python
[]
```

The function is documented to select retrievers from headers, configuration, or the default retriever. After the header value is split and blank entries are removed, no valid retriever remains, but the default fallback is not applied.

This leaves `GPTResearcher.retrievers` empty. Primary-search paths such as `quick_search` subsequently access `self.retrievers[0]`, so the returned value is not usable as a configured search backend.

**To Reproduce**

1. Check out GPT Researcher `main` at commit:

```text
6f998577d547b1e54ec662dac63583aa11e3b84b
```

2. Install the project and test dependencies:

```bash
python -m pip install -e ".[test]"
```

3. Create `tests/test_get_retrievers_all_blank.py`:

```python
from types import SimpleNamespace

from gpt_researcher.actions.retriever import (
    get_default_retriever,
    get_retrievers,
)


def test_all_blank_retriever_header_uses_default():
    cfg = SimpleNamespace(
        retrievers=None,
        retriever=None,
    )

    result = get_retrievers(
        {"retrievers": " , , "},
        cfg,
    )

    assert result == [get_default_retriever()]
```

4. Run:

```bash
python -m pytest \
  tests/test_get_retrievers_all_blank.py \
  -q
```

5. Observe that the test fails because the result is an empty list:

```text
AssertionError: assert [] == [<class '...TavilySearch'>]
```

**Expected behavior**

When an explicit retriever value contains no valid names after splitting and trimming, `get_retrievers` should fall back to the default retriever:

```python
[get_default_retri

## #2095 (2026-09-01): Bug: parse_search_queries_response accepts whitespace-only required fields

**Describe the bug**

`parse_search_queries_response` accepts JSON entries whose required `query` or `researchGoal` field contains only whitespace.

For example:

```python
parse_search_queries_response(
    '[{"query": "   ", "researchGoal": "goal"}]',
    num_queries=3,
)
```

returns:

```python
[
    {
        "query": "",
        "researchGoal": "goal",
    },
]
```

The reverse case is also accepted:

```python
parse_search_queries_response(
    '[{"query": "query", "researchGoal": "   "}]',
    num_queries=3,
)
```

returns:

```python
[
    {
        "query": "query",
        "researchGoal": "",
    },
]
```

The parser checks the truthiness of the original strings before applying `.strip()`. Whitespace-only strings therefore pass validation and become empty strings in the returned result.

These entries are subsequently treated as valid Deep Research branches.

**To Reproduce**

1. Check out GPT Researcher `main` at commit:

```text
6f998577d547b1e54ec662dac63583aa11e3b84b
```

2. Install the project and test dependencies:

```bash
python -m pip install -e ".[test]"
```

3. Create `tests/test_deep_research_blank_query_fields.py`:

```python
import json

import pytest

from gpt_researcher.skills.deep_research import (
    parse_search_queries_response,
)


@pytest.mark.parametrize(
    "item",
    [
        {
            "query": "   ",
            "researchGoal": "goal",
        },
        {
            "query": "query",
            "researchGoal": " \t ",
        },
    ],
)
def test_rejects_whitespace_only_search_query_fields(item):
    result = parse_search_queries_response(
        json.dumps([item]),
        num_queries=3,
    )

    assert result == []
```

4. Run:

```bash
python -m pytest \
  tests/test_deep_research_blank_query_fields.py \
  -q
```

5.

## #2096 (2026-09-01): Bug: MCP transport autodetection treats uppercase URL schemes as stdio

**Describe the bug**

`MCPClientManager.convert_configs_to_langchain_format` performs case-sensitive URL-prefix checks when automatically selecting the transport for a remote MCP server.

URI scheme names are case-insensitive. However, remote URLs using uppercase or mixed-case schemes are not recognized.

For example, this configuration:

```python
{
    "name": "remote",
    "connection_url": (
        "HTTPS://mcp.example.com/service"
    ),
    "connection_headers": {
        "Authorization": "Bearer test-token",
    },
}
```

is converted into:

```python
{
    "transport": "stdio",
}
```

instead of:

```python
{
    "transport": "streamable_http",
    "url": "HTTPS://mcp.example.com/service",
    "headers": {
        "Authorization": "Bearer test-token",
    },
}
```

The same behavior affects uppercase `HTTP`, `WS`, and `WSS` schemes.

The remote configuration is therefore reclassified as a local stdio configuration, and both its URL and connection headers are omitted.

**To Reproduce**

1. Check out GPT Researcher `main` at commit:

```text
6f998577d547b1e54ec662dac63583aa11e3b84b
```

2. Install the project and test dependencies:

```bash
python -m pip install -e ".[test]"
```

3. Create `tests/test_mcp_client_uppercase_url_schemes.py`:

```python
import pytest

from gpt_researcher.mcp.client import MCPClientManager


@pytest.mark.parametrize(
    ("url", "transport"),
    [
        (
            "HTTPS://mcp.example.com/service",
            "streamable_http",
        ),
        (
            "HTTP://mcp.example.com/service",
            "streamable_http",
        ),
        (
            "WSS://mcp.example.com/service",
            "websocket",
        ),
        (
            "WS://mcp.example.com/service",
            "websocket",
        ),
    ],
)
def te

## #2097 (2026-09-01): Bug: failed chat search reuses metadata from the previous successful search

**Describe the bug**

`ChatAgentWithMemory.process_chat_completion` can associate a failed search tool call with metadata from an earlier successful search.

When a completion contains multiple search tool calls, the method re-executes each search sequentially to populate `self.search_metadata`.

A successful search replaces that state. However, if a subsequent search raises an exception, `quick_search` returns an error result without updating or clearing `self.search_metadata`.

For this sequence:

```text
first query  -> succeeds
second query -> raises an exception
```

the returned metadata for `second query` contains:

```python
{
    "query": "first query",
    "sources": [
        {
            "title": "First source",
            "url": "https://example.com/first",
            "content": "First result",
        },
    ],
}
```

The failed search is therefore reported with the previous query and its sources.

**To Reproduce**

1. Check out GPT Researcher `main` at commit:

```text
6f998577d547b1e54ec662dac63583aa11e3b84b
```

2. Install the project and test dependencies:

```bash
python -m pip install -e ".[test]"
```

3. Create `tests/test_chat_search_metadata_failure.py`:

```python
from types import SimpleNamespace

import pytest

from backend.chat.chat import ChatAgentWithMemory


class SearchClient:
    def __init__(self):
        self.calls = 0

    def search(self, *, query, max_results):
        assert max_results == 5
        self.calls += 1

        if self.calls == 1:
            return {
                "results": [
                    {
                        "title": "First source",
                        "url": "https://example.com/first",
                        "content": "First result",
                    }
                ]
            }

   

## #2098 (2026-09-01): Bug: GoogleSearch YouTube filtering is case-sensitive

**Describe the bug**

`GoogleSearch.search` filters YouTube results using a case-sensitive substring comparison.

For example, a result with:

```text
https://youtube.com/watch?v=test
```

is excluded, while the equivalent valid URL:

```text
https://YouTube.com/watch?v=test
```

is retained.

URI host names are case-insensitive, so these URLs identify the same host. The filtering behavior should not depend on the casing used in the search result URL.

This can also affect result selection. `GoogleSearch.search` applies `max_results` after collecting the unfiltered results. If a mixed-case YouTube result appears before a normal article, it can occupy a limited result slot and cause the article to be omitted.

For this response order:

```text
1. https://YouTube.com/watch?v=test
2. https://example.com/article
```

with:

```python
max_results=1
```

the method currently returns the YouTube result instead of the article.

**To Reproduce**

1. Check out GPT Researcher `main` at commit:

```text
6f998577d547b1e54ec662dac63583aa11e3b84b
```

2. Install the project and test dependencies:

```bash
python -m pip install -e ".[test]"
```

3. Create:

```text
tests/test_google_youtube_host_case.py
```

4. Add this test:

```python
import json
from unittest.mock import MagicMock, patch

import pytest

from gpt_researcher.retrievers.google.google import (
    GoogleSearch,
)


@pytest.mark.parametrize(
    "youtube_host",
    [
        "youtube.com",
        "YouTube.com",
        "YOUTUBE.COM",
    ],
)
def test_google_search_filters_youtube_host_case_insensitively(
    youtube_host,
):
    payload = {
        "items": [
            {
                "title": "Video",
                "link": (
                    f"https://{youtube_host}"
                    "/watch?v=test"
      

## #2100 (2026-09-02): Prefetched sources (requires_scraping=False) never enter visited_urls, so they don't dedupe and drop out of References

`_search_relevant_source_urls` splits retriever results into `new_search_urls` (scraped, deduped via `_get_new_urls` against `visited_urls`) and `prefetched_content` (retrievers that declare `requires_scraping=False`, e.g. PubMed Central, or trip the legacy long-raw_content heuristic). The prefetched branch calls `add_research_sources()` but never touches `visited_urls`.

Two effects follow. A prefetched source hit by two different sub-queries gets merged into `scraped_content` twice instead of deduping the way a scraped URL would through `_get_new_urls`. And `add_references()` builds the report's References section purely from `visited_urls`, so the source's own citation never shows up even though its text is in the report.

Reproduced against the real `ResearchConductor._search_relevant_source_urls` and `add_references` at HEAD 6f99857: a retriever declaring `requires_scraping=False` returns the same URL across two sub-queries. `research_sources` grows to 2 entries for it, `visited_urls` stays `set()`, and the generated References section comes back empty.

Fix looks small: add the URL to `visited_urls` in the `requires_scraping is False` and legacy-heuristic branches too (researcher.py around lines 876-888), the same way `_get_new_urls` already does for scraped URLs. Happy to send a PR if that's useful.


## #2110 (2026-09-08): Deep research zero-query path raises NameError before fallback state is initialized

## Summary

`DeepResearchSkill.deep_research()` has a zero-query guard immediately after `generate_search_queries()`, but the guard returns variables that are initialized only **after** the guard.

On current `main`, the control flow is effectively:

```python
serp_queries = await self.generate_search_queries(query, num_queries=breadth)

if not serp_queries:
    return {
        "learnings": all_learnings,
        "visited_urls": all_visited_urls,
        "citations": all_citations,
        "context": all_context,
        "sources": all_sources,
    }

all_learnings = learnings.copy()
all_citations = citations.copy()
all_visited_urls = visited_urls.copy()
all_context = []
all_sources = []
```

Therefore, if query generation legitimately returns `[]`, the intended graceful-stop branch instead raises `NameError` because `all_learnings` (and the other `all_*` values) do not yet exist.

## Why this matters

The function explicitly tries to make the zero-query case a safe termination path:

```python
logger.warning("Deep research generated zero search queries; stopping descent.")
```

That condition can occur if the model returns malformed/empty output and `parse_search_queries_response()` yields no valid queries. In that situation, deep research should preserve the accumulated state and stop cleanly rather than failing in the fallback itself.

## Expected behavior

If `generate_search_queries()` returns no queries, `deep_research()` should return the current accumulated state:

- existing `learnings`;
- existing `citations`;
- existing `visited_urls`;
- empty context/sources for the current level.

No exception should be raised.

## Actual behavior

The zero-query branch references these names before assignment:

- `all_learnings`
- `all_visited_urls`
- `all_citations`
- `a

## #2115 (2026-09-08): Passing an empty visited_urls set breaks shared URL-dedup state

## Summary

`GPTResearcher.__init__()` currently initializes `visited_urls` with:

```python
self.visited_urls = visited_urls or set()
```

That replaces a caller-provided **empty set** with a new set because an empty set is falsy.

This matters because `visited_urls` is intentionally used as shared mutable state between parent/sub-researchers so already-scraped URLs can be deduplicated across related research runs. The researcher code explicitly documents that `visited_urls` may be shared with a parent researcher and is deliberately not cleared.

## Minimal reproduction

Conceptually:

```python
shared = set()
researcher = GPTResearcher(query="test", visited_urls=shared)

assert researcher.visited_urls is shared  # currently fails when shared is empty
```

If `shared` already contains at least one URL, the identity is preserved. The bug therefore only appears at the most common initial state: an empty shared set.

## Why this matters

Parent/sub-researcher flows can pass an empty accumulator expecting subsequent discoveries to be visible through the same set object. Because the constructor swaps that object out on first use, the parent does not observe the child’s first URL updates through shared-state identity.

That weakens cross-research URL deduplication and can lead to duplicate scraping/retrieval work, especially in deep/detailed research flows that create nested `GPTResearcher` instances.

## Expected behavior

Only `None` should allocate a new set. A caller-supplied set should be preserved even when empty:

```python
self.visited_urls = visited_urls if visited_urls is not None else set()
```

## Regression coverage

A focused test should verify both cases:

```python
shared = set()
researcher = GPTResearcher(..., visited_urls=shared)
assert researcher.visited_u

## #2125 (2026-09-13): multi_agents .env tracing settings are read before load_dotenv()

## Summary

`multi_agents/main.py` checks `MONOCLE_TRACING`, `MONOCLE_EXPORTERS`, `OKAHU_API_KEY`, and `LANGCHAIN_API_KEY` before calling `load_dotenv()`.

As a result, tracing settings placed in the project's `.env` file are invisible during those checks unless they are also exported in the parent shell.

## Current order

```python
from dotenv import load_dotenv
...

if os.environ.get("MONOCLE_TRACING", "").strip().lower() in (...):
    ...

...

if os.environ.get("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
load_dotenv()
```

The README and `.env.example` both present these as environment settings, so users can reasonably place them in `.env`. However, `load_dotenv()` runs only after both tracing gates have already executed.

## Expected behavior

Load `.env` before any tracing-related environment checks, while still keeping the Monocle setup before importing the multi-agent framework modules that need instrumentation.

A minimal fix is to call `load_dotenv()` immediately after imports and remove the later call.

## Regression coverage

A focused test can execute `multi_agents/main.py` with a temporary `.env` containing `MONOCLE_TRACING=true`, stub `monocle_apptrace.setup_monocle_telemetry`, and verify that the setup hook is invoked from the `.env` value without exporting it in the parent process.

The same ordering also restores `.env`-provided `LANGCHAIN_API_KEY` visibility before `LANGCHAIN_TRACING_V2` is derived.

I searched the issue/PR tracker for this specific `load_dotenv` ordering problem and did not find an existing report.

<sub>AI-assisted review disclosure: an AI coding assistant was used to inspect import/config ordering and help prepare this report.</sub>

## #2127 (2026-09-13): OpenAlex retriever crashes on malformed JSON responses

## Summary

`OpenAlexSearch.search()` catches request/HTTP failures, but parses the response body only after leaving that `try` block:

```python
try:
    response = requests.get(self.BASE_URL, params=params, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"An error occurred while accessing OpenAlex API: {e}")
    return []

payload = response.json()
```

If OpenAlex (or an intermediary) returns HTTP 200 with a malformed/non-JSON body, `response.json()` raises `ValueError`/`JSONDecodeError` and the retriever propagates the exception instead of degrading to an empty result set like the request-error path.

## Why this matters

Retriever responses are external input. A transient proxy/CDN response, HTML error page returned with 200, or otherwise invalid body should not abort the whole research workflow when the retriever already has a graceful-error convention.

Other retrievers in this repository already guard JSON parsing together with transport errors (for example by catching `ValueError` alongside `requests.RequestException`).

## Expected behavior

Malformed response JSON should be treated as a retriever failure and return `[]` rather than raising into the research pipeline.

A focused fix can keep the current behavior and message style while moving `response.json()` into the guarded block and catching `ValueError`:

```python
try:
    response = requests.get(...)
    response.raise_for_status()
    payload = response.json()
except (requests.RequestException, ValueError) as e:
    print(f"An error occurred while accessing OpenAlex API: {e}")
    return []
```

## Regression coverage

Stub a successful HTTP response whose `.json()` raises `ValueError("invalid json")` and assert that `OpenAlexSearch("q").search()` returns `

## #2129 (2026-09-13): Semantic Scholar retriever has an unbounded request and unguarded JSON parsing

## Summary

`SemanticScholarSearch.search()` currently performs its external request without a timeout and parses the response body outside the request-error guard:

```python
try:
    response = requests.get(self.BASE_URL, params=params)
    response.raise_for_status()
except requests.RequestException as e:
    print(...)
    return []

payload = response.json()
```

This leaves two reliability gaps in the same retrieval call path:

1. an unresponsive Semantic Scholar endpoint can block the research step indefinitely at the HTTP layer;
2. an HTTP 200 response with malformed/non-JSON content raises from `response.json()` instead of degrading to `[]`.

## Expected behavior

The scholarly retriever should have a bounded request duration and treat response-decoding failures the same way it already treats transport/HTTP failures.

A narrow fix would:

```python
try:
    response = requests.get(self.BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()
except (requests.RequestException, ValueError) as e:
    print(...)
    return []
```

This follows the existing timeout/error-handling patterns used by other retrievers without changing happy-path result normalization.

## Regression coverage

Focused offline tests can verify:

- `requests.get` receives a finite timeout;
- `.json()` raising `ValueError("invalid json")` returns `[]` rather than propagating;
- the existing happy path remains unchanged.

This is also a concrete instance of the broader external-call timeout concern in #1764, but scoped to the Semantic Scholar retriever so it can be fixed and tested independently.

I searched the PR tracker for a Semantic Scholar timeout / malformed-JSON fix and did not find an existing implementation. #2036 touches Semantic Scholar sor

## #2132 (2026-09-13): Bing retriever has an unbounded request and propagates transport failures

## Summary

`BingSearch.search()` currently calls the external Bing endpoint without a timeout or request-error guard:

```python
resp = requests.get(url, headers=headers, params=params)
```

That leaves two reliability gaps in a core retrieval path:

1. an unresponsive Bing endpoint can block a research step indefinitely at the HTTP layer;
2. DNS/connect/read/TLS failures raise `requests.RequestException` directly into the research pipeline instead of degrading to an empty retriever result, which is the behavior used by several sibling retrievers.

The method also continues parsing non-2xx responses as if they were normal search payloads.

## Expected behavior

The Bing retriever should have a bounded request duration and handle transport/HTTP failures consistently with other retrievers.

A narrow fix would be:

```python
try:
    resp = requests.get(url, headers=headers, params=params, timeout=20)
    resp.raise_for_status()
except requests.RequestException as exc:
    self.logger.error("Bing search request failed: %s", exc)
    return []
```

The existing payload normalization can remain unchanged.

## Regression coverage

Focused offline tests can verify:

- `requests.get` receives a finite timeout;
- a `requests.RequestException` returns `[]` rather than propagating;
- a non-2xx response handled by `raise_for_status()` also degrades to `[]`;
- the existing happy-path result shape is unchanged.

This is a concrete instance of the broader external-call timeout concern in #1764, scoped to one retriever so it can be fixed and tested independently.

I searched the current issue and PR trackers for a Bing request-timeout/error-boundary fix and did not find an existing implementation.

<sub>AI-assisted review disclosure: an AI coding assistant was used to inspect the retr

## #2144 (2026-09-23): Initial planning sources are lost when follow-up searches return empty or different results

## Observed behavior

`ResearchConductor.plan_research()` uses an initial search to plan follow-up queries, but those initial results are not passed into source fetching. If the follow-up searches return different results or fail, a source already seen by the planner can disappear entirely from the writer's context.

Observed on main at `6f998577d547b1e54ec662dac63583aa11e3b84b` with native `GPTResearcher.conduct_research()` / `write_report()`, DuckDuckGo, local BGE-small embeddings, and an experimental local Codex CLI model transport (requested `gpt-5.6-luna`). The deterministic reproduction below does not depend on that transport or a live model.

## Concrete trace

For SimpleQA's “What is the surname of the individual who won the Green Chemistry Award in 2016?”:

1. The initial search returned Yale and RSC pages about Paul Anastas, alongside an EPA award page about Paul Chirik.
2. The query-planning LLM explicitly generated `Paul Anastas 2016 Royal Society of Chemistry Green Chemistry Award`.
3. That targeted search and a repeated original-query search returned empty after DNS errors. Other queries returned EPA-related pages.
4. The initial Yale/RSC URLs were never scraped. The final writer prompt contained zero occurrences of `Anastas`, `Yale`, or `Royal Society of Chemistry`, and no retrieval-error notice. It answered Chirik.

The question omits the awarding organization, and Chirik did receive a different EPA award. This is incorrect against the SimpleQA target, not a fabricated person or award. The observation motivates preserving available evidence; it does not prove that preserving it will always change the final answer.

## Expected behavior

Sources that informed planning should remain available for normal page fetching and context retrieval even if later sea

## #2163 (2026-09-26): multi_agents: an empty console reply at plan review re-plans without counting toward max_plan_revisions

With `include_human_feedback` on and the plan reviewed in the console (no websocket), pressing Enter at the plan-review prompt returns `""`.

- `""` is not the `"no"` approval. `is_human_plan_approval("")` is `False`, as `tests/test_none_accept_sentinels.py` pins, so `route_human_feedback` sends it to `revise`.
- `review_plan` increments `plan_revision_count` only for truthy replies (`if user_feedback:` in `multi_agents/agents/human.py`), so that lap is never counted.
- The planner drops empty feedback, so each Enter re-plans with the same prompt, and `max_plan_revisions` cannot end a run of them.

The web feedback form maps a blank submit to `null` (`HumanFeedback.tsx`, "leave blank for 'no'"), which `route_human_feedback` accepts, so the two paths disagree. I found this reading the code and confirmed it with a unit test that feeds `""` to `review_plan`. I'm opening a PR with a one-line fix that makes the console match the web form, plus a regression test; it notes the alternative (counting the empty lap).


## #2192 (2026-10-04): MCP configuration lists are reset during Config initialization

**Describe the bug**

`Config` discards `MCP_SERVERS` and `MCP_ALLOWED_ROOT_PATHS` after loading them from a JSON file or environment variables. The stored lists become empty, so `get_mcp_server_config()` returns `{}` for a server that is present in the configuration.

**To Reproduce**

Run this from a checkout of `main` with the package installed:

```python
import json
import tempfile
from pathlib import Path
from gpt_researcher.config.config import Config

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "config.json"
    path.write_text(json.dumps({
        "MCP_SERVERS": [{"name": "local-search", "command": "python"}],
        "MCP_ALLOWED_ROOT_PATHS": ["/srv/research"],
    }))
    config = Config(str(path))
    print(config.mcp_servers)
    print(config.mcp_allowed_root_paths)
    print(config.get_mcp_server_config("local-search"))
```

Current output is `[]`, `[]`, `{}`. Setting the same lists through the two environment variables produces the same result.

**Expected behavior**

Keep the configured lists and return `{"name": "local-search", "command": "python"}` from the named-server lookup. Environment values should continue to take precedence over file values, and default lists should remain separate between instances.

**Desktop**

macOS, Python 3.12.15, `main@0957c301ed06c2a5857b834358c7227c739041d4`. This is a library configuration issue; no browser is involved.

**Additional context**

`_set_attributes()` loads the correct values. Later in `Config.__init__`, both attributes are assigned `[]`, followed by self-assignments that cannot recover the loaded values. Both settings already have empty-list defaults.


## #2214 (2026-10-17): GoogleSearch drops non-YouTube URLs containing youtube.com outside the hostname

**Describe the bug**
`GoogleSearch.search()` silently drops non-YouTube search results when `youtube.com` appears anywhere in the URL. The filter currently uses `"youtube.com" in link.lower()`, so an article about YouTube can disappear solely because its path, query string, or fragment mentions the domain.

**To Reproduce**
Run this offline reproduction against current main (`3582a6841fe7dc801e2a34e34ee408641aea9bce`); no API key or network request is needed:

```python
import json
from unittest.mock import MagicMock, patch
from gpt_researcher.retrievers.google.google import GoogleSearch

link = "https://example.com/news/youtube.com"
response = MagicMock(status_code=200, text=json.dumps({
    "items": [{"title": "Article", "link": link, "snippet": "Article about YouTube"}]
}))
search = GoogleSearch("YouTube news", headers={
    "google_api_key": "test-key", "google_cx_key": "test-cx"
})
with patch("gpt_researcher.retrievers.google.google.requests.get", return_value=response):
    print(search.search(max_results=1))
```

Actual result: `[]`.

The same problem occurs with `https://example.com/?source=youtube.com`, `https://example.com/#youtube.com`, and unrelated hostnames such as `notyoutube.com` or `youtube.com.example.org`.

**Expected behavior**
Retain the article with its original URL. Exclude results whose hostname is `youtube.com` or a subdomain of it, preserving the case-insensitive exclusion covered by #2098 and #2113.

**Environment**
Python 3.14.7 on Linux; reproduced with a mocked Google Custom Search response.

**Additional context**
The fix can stay within `gpt_researcher/retrievers/google/google.py` and the existing `tests/test_google_youtube_host_case.py`: inspect the parsed hostname instead of searching the entire URL. Six regression cases fail before thi

## #2218 (2026-10-18): generate_report returns an empty string when the LLM call fails, instead of raising an error

**Describe the bug**
If the LLM call fails while writing the final report (outage, invalid key, rate limit, request too large), `generate_report` in `gpt_researcher/actions/report_generation.py` retries once without the system message (the Gemini fix from 02d3afe5). If the retry also fails, the exception is swallowed with a `print()` and the function returns `""`.

The caller gets a blank report with no exception, and `ResearchWriter.write_report` still logs "📝 Report written" because it doesn't check for an empty report. So the run looks successful but produces nothing. The retry also catches every exception type, so a programming error on the first call (e.g. a bad kwarg) is silently retried rather than surfaced.

This may explain #1260]: the logs there show "Writing report" → "Report written" only 6 seconds apart with an empty document. On the code at that time (82b1487a), `generate_report` returned "" after both attempts failed, and `writer.py` logs "Report written" without checking for an empty report. A fast-failing LLM error (e.g. the request-too-large 429 from #1386) would produce exactly that. 

**To Reproduce**
Point the LLM at an address that refuses connections (no real API key needed):

```python
# repro.py, run from the repo root
import asyncio
from gpt_researcher.config import Config
from gpt_researcher.actions.report_generation import generate_report

async def main():
    report = await generate_report(
        query="What is solar power?",
        context="Solar panels turn sunlight into electricity.",
        agent_role_prompt="You are a research assistant.",
        report_type="research_report", tone=None, report_source="web",
        websocket=None, cfg=Config(),
    )
    print("RAISED AN ERROR? no")
    print(f"REPORT RETURNED: {report!r}")

asyn

## #2239 (2026-10-28): LangChainDocumentLoader.load() aborts the whole batch on a single malformed row

### Describe the bug

`LangChainDocumentLoader.load()` (gpt_researcher/document/langchain_document.py) walks the user-supplied `self.documents` list without any guards, so one malformed row raises out of `load()` and every other already-collected document is lost.

Three crash paths on current main (3582a684):

1. **`metadata=None`** (custom Document subclass or legacy loader omits the field) → `AttributeError: 'NoneType' object has no attribute 'get'` at `document.metadata.get(...)`.
2. **Non-Document row** (e.g. a dict left from a JSON round-trip) → `AttributeError: 'dict' object has no attribute 'page_content'`.
3. **Mixed valid + invalid rows** → the invalid row aborts the batch, so all good rows collected before it are lost too.

The sibling `DocumentLoader.load()` was hardened for this pattern in #2152; this loader was missed.

### To Reproduce

```python
from langchain_core.documents import Document
from gpt_researcher.document.langchain_document import LangChainDocumentLoader

# Path 1 — metadata=None on a duck-typed row
rows = [SimpleNamespace(page_content="orphan", metadata=None),
        Document(page_content="kept", metadata={"title": "http://kept"})]
await LangChainDocumentLoader(rows).load()
# AttributeError: 'NoneType' object has no attribute 'get'  <- "kept" is also lost

# Path 2 — non-Document row in the list
rows = [Document(page_content="real", metadata={"title": "http://real"}),
        {"page_content": "fake", "metadata": {"title": "http://fake"}}]
await LangChainDocumentLoader(rows).load()
# AttributeError: 'dict' object has no attribute 'page_content'  <- "real" is lost
```

### Expected behavior

Malformed rows should be skipped (mirroring the `DocumentLoader.load()` pattern from #2152): gate on `hasattr(document, "page_content")`, tolerate `met

## #2240 (2026-10-28): ExaSearch.find_similar() / get_contents() propagate client failures and abort the research loop

### Describe the bug

In `gpt_researcher/retrievers/exa/exa.py`, `find_similar()` and `get_contents()` propagate every failure into the research run, unlike the sibling `search()` which returns `[]` on client errors and malformed payloads.

The same hardening already landed for other retrievers: OpenAlex (#2128), Semantic Scholar (#2130), Bing (#2133). `exa.py` only hardened `search()`; these two methods were missed.

Two failure paths on current main (3582a684):

1. **Client raises** (transient HTTP failure, auth error, timeout, rate limit) — neither method wraps the client call, so the exception escapes the retriever and aborts the research loop.
2. **Client returns `None`** — `results.results or []` becomes `None.results` → `AttributeError: 'NoneType' object has no attribute 'results'`.

```python
class Boom:
    def find_similar(self, *a, **k): raise RuntimeError("api down")
s.client = Boom()
s.find_similar("https://seed")   # RuntimeError propagates

class N:
    def get_contents(self, *a, **k): return None
s.client = N()
s.get_contents(["1"])            # AttributeError propagates
```

### Expected behavior

Both methods should degrade to `[]` exactly like `search()` does: wrap the client call in `try/except` (logging per the file's existing `print(f"Error: ...")` convention), use `getattr(results, "results", None) or []`, and add an `isinstance(rows, list)` guard so non-list payloads degrade instead of crashing later.

### Additional context

A fix + 6 regression tests (mirroring tests/test_exa_search_errors.py) are already proposed in PR #2181.

## #2251 (2026-10-31): Deep research: gpt-5.4 returns empty responses (max_tokens=4000 + high reasoning), and the retries aren’t counted in costs

In deep_research.py, process_research_results uses reasoning_effort=High with max_tokens=4000. Since #1861, that limit actually applies to gpt-5.x. gpt-5.4 often spends all 4000 tokens on reasoning and returns an empty response. create_chat_completion then retries up to 10 times and drops the sub-query. These calls are billed, but they skip cost_callback, so get_costs() doesn’t include them.

In 13 runs with the default config (5 of them deep), this happened 202 times, all in deep mode. One deep report came out empty. Tracked cost was $4.74, while OpenAI billed $20.51 for gpt-5.4.

## #2277 (2026-11-09): PyMuPDFScraper returns empty titles for PDFs without document metadata

## Symptom

`get_research_sources()` returns entries with `title: ""` for PDFs that carry no `/Title` entry in their document metadata. In a 12-source run, 5 sources came back with blank titles.

## Root cause

`gpt_researcher/scraper/pymupdf/pymupdf.py`:

```python
title = doc[0].metadata.get("title", "") if doc else ""
```

Most PDFs published on the web have no document title metadata, so the scraper returns an empty string. `scrape_urls` passes only URLs to the scraper, so a search provider's title cannot be used as a fallback.

## Reproduction

```python
from gpt_researcher.scraper.pymupdf.pymupdf import PyMuPDFScraper

url = "https://susproc.jrc.ec.europa.eu/product-bureau/sites/default/files/2021-01/UM3_Indicator_6.1_v1.1_21pp.pdf"
content, images, title = PyMuPDFScraper(url).scrape()
print(len(content), repr(title))  # 54025 ''
```

## Suggested fix

Fall back to a readable title derived from the URL or file name when the metadata title is missing, and strip whitespace from metadata titles when present:

```python
def _fallback_title(link: str) -> str:
    parsed = urlparse(link)
    name = unquote(os.path.basename(parsed.path or link))
    stem = os.path.splitext(name)[0].replace("_", " ").replace("-", " ").strip()
    return stem or parsed.netloc


title = (doc[0].metadata.get("title") or "").strip() if doc else ""
if not title:
    title = _fallback_title(self.link)
```

Results with that patch:

- `UM3_Indicator_6.1_v1.1_21pp.pdf` → `UM3 Indicator 6.1 v1.1 21pp`
- `RMI_Document_Repository_Public-Reprts_2010-24_LCCA.pdf` → `RMI Document Repository Public Reprts 2010 24 LCCA`

Happy to open a PR if this direction is acceptable.

This is separate from #1824 / #1908, which made `extract_title` return `""` for empty HTML `<title>` tags, so HTML pages without a ti

## #2323 (2026-11-16): Detailed report: subtopic context seeding is overwritten by conduct_research, and global_context is replaced rather than accumulated

### Summary

In `backend/report_type/detailed_report/detailed_report.py`, the parent context that is carefully seeded into each subtopic researcher never reaches the subtopic report, because `ResearchConductor.conduct_research()` unconditionally overwrites `researcher.context` with fresh research. On top of that, `global_context` is *replaced* (not merged) with the last-written subtopic's context, so the initial research context is dropped from the pool after the first subtopic.

### Evidence

1. `_research_subtopic` seeds parent context and then immediately conducts research:

```python
subtopic_assistant.context = list(set(self._hashable_context(self.global_context)))
await subtopic_assistant.conduct_research()
```

2. `gpt_researcher/skills/researcher.py` (`conduct_research`, end of the source-type branches) assigns:

```python
self.researcher.context = research_data
```

There is no branch that merges a pre-seeded context, so the seed is dead work. `write_report` then uses `ext_context or self.researcher.context` — i.e. only the subtopic's own fresh research.

3. After each subtopic, `_write_subtopic_report` does:

```python
self.global_context = list(set(self._hashable_context(subtopic_assistant.context)))
```

This replaces the pool. Combined with (1)/(2), the initial research context (`_initial_research`) only survives for the first subtopic's seed — and is then lost.

4. Secondary observation: on the common `report_source=web` path, `global_context` is a plain string after `_initial_research`, so `_hashable_context(self.global_context)` iterates it character by character — even the intended seed content is per-character noise before being overwritten.

### Minimal reproduction (no LLM, no network)

```python
import asyncio
from gpt_researcher import GPTResearche
