# Requested tone, prompt family and report options are silently replaced

Mechanism: A non-enum tone becomes Objective (agent.py:146), yet the pip docs pass `tone="formal and objective"` (pip-package.md:228) and the detailed-report example uses the non-existent `Tone.FORMAL`; `prompt_family` is not passed to `generate_report` (skills/writer.py:124) so the main body uses the default family; an invalid prompt family crashes on `PromptFamily()` without config (prompts.py:903); unknown report_type and retriever names fall back with only a Python warning or log (prompts.py:862-877, actions/retriever.py:166-170); custom and outline prompts drop language, tone and citation rules (prompts.py:392-415, report_generation.py:256).
Trigger: Library users following the docs; Granite users; custom_prompt or outline_report users; typos in configuration.
Observable failure: Report in the wrong tone, language or format, or uncited, with no error visible to the user.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: honor-requested-tone, write-in-requested-language, cite-only-provided-sources
Found at: fae2317 (agent: gpt_researcher)
Evidence: gpt_researcher/agent.py:146; docs/docs/gpt-researcher/gptr/pip-package.md:228; docs/docs/examples/detailed_report.md:61; gpt_researcher/prompts.py:392-415,903
