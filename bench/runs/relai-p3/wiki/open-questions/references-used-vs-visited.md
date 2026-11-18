# Should source lists contain only cited sources, or every page consulted?

Unclear: prompts require "all used source urls" (`gpt_researcher/prompts.py:280`), but detailed
reports, the API `source_urls` and deep_agents list every visited URL, including failed and
filtered pages.

Why it matters: decides whether [references-list-visited-not-cited](../risks/references-list-visited-not-cited.md)
is a defect and how a citation-faithfulness grader treats extra references.

Recommended: reference lists contain only sources actually cited; a separate "pages consulted"
list is acceptable if labelled.
