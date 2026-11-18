# May local-document research contact the web at all?

Unclear: docs describe local mode as local-only research, but the planner always runs one web search and deep_agents' scoping tool is always web.
Why it matters: decides whether [the planning leak](../risks/local-mode-planning-web-leak.md) is a privacy defect (any query leaving the machine fails) or acceptable (only report evidence must be local), and so what a local-mode eval checks.
Choices: (a) no web contact at all in local mode — recommended, matches the docs' wording and private-data users; (b) web planning allowed, evidence and citations local only.
Evidence: docs/docs/gpt-researcher/gptr/config.md:96; gpt_researcher/skills/researcher.py:64-70; issues #1004, #1334.
