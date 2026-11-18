# A failed subtopic step gives a detailed report with no body

Mechanism: `construct_subtopics` catches every exception and returns the input `subtopics`. `DetailedReport` never passes its subtopics through, so that fallback is always `[]`. `_get_all_subtopics` only prints a message. `run()` still writes an introduction, a table of contents and a conclusion over the empty body.
Trigger: Subtopic generation fails: a bad structured-output parse, output truncated at `SMART_TOKEN_LIMIT`, or a provider error.
Observable failure: A detailed report with an introduction and conclusion but no sections. Nothing tells the user the failure happened.
Impact: high. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/utils/llm.py:213-217; backend/report_type/detailed_report/detailed_report.py:98-108; tests/test_construct_subtopics_error_log.py pins the fallback only

## Probes

None yet.
