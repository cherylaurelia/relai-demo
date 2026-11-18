# Page and tool text can instruct the report writer

Mechanism: Scraped page text, PDFs and MCP tool output are interpolated raw into the report and curation prompts (`Information: "{context}"`). There are no delimiters and no instruction to treat the text as data. `Source:` and `Title:` lines in page text look the same as real ones.
Trigger: A page in the results that contains instructions or forged `Source:` lines.
Observable failure: Biased content or forged citations in the report, or curation that drops real sources.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/prompts.py:293-296,555-561; gpt_researcher/skills/curator.py:64. Susceptibility of current models is unmeasured.

## Probes

None yet.
