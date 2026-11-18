# Cite only sources present in the gathered information

Every substantive claim, figure or quote in a research report carries an in-text markdown
hyperlink citation to the source it came from, and the report cites no source that does not
appear in the gathered information.

Source: `gpt_researcher/prompts.py:309-310` (research report prompt). Subtopic, introduction,
conclusion and deep-research prompts require in-text hyperlinked citations
(`prompts.py:664,713,746,479`) but omit the "do not cite absent sources" clause.
