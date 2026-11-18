# How should a no-sources abstention reach the user?

Unclear: when no sources are gathered the writer returns a plain sentence
(`gpt_researcher/skills/writer.py:83-88`), which the backend saves and exports as a normal PDF/DOCX
report (`backend/server/server_utils.py:174-175`). It is always English and does not say *why*
(for example an unrecognised `report_source` value such as `"web_search"`, used in
`docs/docs/examples/detailed_report.md:58`, gathers nothing).

Why it matters: decides whether an eval should expect an error state, a localised message,
or the current text.

Recommended: surface as a distinct failure state with the cause; reject unknown `report_source`
values up front.
