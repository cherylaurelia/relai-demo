# Some report types ignore the configured language

Mechanism: the outline prompt accepts `language` but never uses it; custom prompts carry no language line; draft-title prompts have no language line.
Trigger: `LANGUAGE` other than English with outline, custom or detailed reports.
Observable failure: English outline or headers in an otherwise non-English report.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: report-in-configured-language
Found at: 9ad2148 (agent: gpt_researcher)
Evidence: gpt_researcher/prompts.py:398-415; gpt_researcher/actions/report_generation.py:255-256 (reviewer-reported). Issue #1767.
