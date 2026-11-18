# Detailed reports silently lose subtopics or deduplication

Mechanism: `construct_subtopics` returns [] on any exception (utils/llm.py:213-217), leaving a report with only an intro, an empty table of contents and a conclusion; draft section titles (a list) are stringified before `extract_headers` (detailed_report.py:169-172), likely yielding no headers so cross-subtopic dedupe gets nothing; the abstain sentence is appended as a section when one subtopic has no context.
Trigger: Model or JSON failure in subtopic generation; normal detailed-report runs (dedupe).
Observable failure: Missing body sections or overlapping, repeated sections with no error.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: 
Found at: fae2317 (agent: gpt_researcher (detailed report))
Evidence: gpt_researcher/utils/llm.py:213-217; backend/report_type/detailed_report/detailed_report.py:102-118,165-172
