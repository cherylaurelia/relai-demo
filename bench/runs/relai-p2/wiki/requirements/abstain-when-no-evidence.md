# The agent says so instead of writing a sourced-looking report when it found nothing

When no source material was retrieved, the user gets a visible statement that no reliable report could be produced,
not a report written from model memory.

Source: abstain guard and its stated intent in `gpt_researcher/skills/writer.py:79-88`; quick-summary prompt
"state that the information is insufficient" (`gpt_researcher/prompts.py:541-550`). Grounded in developer-stated
intent in code comments; confirm with the team (see [scope of grounding](../open-questions/requirement-grounding-confirmation.md)).
