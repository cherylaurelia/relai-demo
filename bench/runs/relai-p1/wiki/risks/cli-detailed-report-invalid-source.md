# CLI detailed reports use an invalid report source and gather nothing

Mechanism: `cli.py` builds `DetailedReport(report_source="web_search")`, but the valid value is `"web"`. No source branch matches, so the context stays empty. That path also ignores `--tone` and `--report_source`.
Trigger: `python cli.py "<query>" --report_type detailed_report`.
Observable failure: Every subtopic section is the "could not gather any source material" text, wrapped in a report structure.
Impact: high. Confidence: high. Triggerability: high.
Status: proposed
Threatens: source-urls-only-by-default
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: cli.py:274-280; gpt_researcher/utils/enum.py:45; gpt_researcher/skills/researcher.py:144-205

## Probes

None yet.
