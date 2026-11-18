# Language, tone and prompt family are dropped on some paths

Mechanism: The writer's `research_params` omit `prompt_family`, so the report body uses the default prompts while the introduction and conclusion use the configured family. The outline and custom report prompts ignore `language` and `tone`. Detailed subtopic researchers do not inherit `config_path`. A non-`Tone` tone silently becomes Objective.
Trigger: A non-English `LANGUAGE`, a custom `PROMPT_FAMILY` (Granite), or outline, custom and detailed report types.
Observable failure: Parts of the report come out in the wrong language or tone, or mixed formats appear across sections.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: report-in-requested-language
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/writer.py:38-47; gpt_researcher/prompts.py:392-399; gpt_researcher/agent.py:146; ISSUE_BACKLOG.md #1767, #1572

## Probes

None yet.
