# Complementing source URLs spaces out every character of the web context

Mechanism: `research_data += ' '.join(additional_research)` is applied to a string, which puts a space between every character. The "unable to find relevant context in the provided sources" message sits behind the condition `research_data and len(research_data) == 0`, which can never be true.
Trigger: `source_urls` together with `complement_source_urls=True`.
Observable failure: The complementary web research reaches the writer unreadable ("T h e  a n s w e r"), and an empty result from the provided URLs gives no warning.
Impact: medium. Confidence: high. Triggerability: low.
Status: proposed
Threatens: source-urls-only-by-default
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/skills/researcher.py:148,155-158

## Probes

None yet.
