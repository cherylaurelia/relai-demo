# Captcha, cookie-wall and error pages count as scraped content

Mechanism: The only scraper quality gates are HTTP status below 400 and at least 100 characters. A 200-status bot check or consent page passes. When there are 10 or fewer documents under 8000 characters, the compression fast path skips relevance filtering entirely.
Trigger: Sites behind Cloudflare or consent walls, especially when few results are scraped.
Observable failure: Boilerplate is treated as evidence, and that happens most in exactly the sparse cases where it matters most.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/scraper/scraper.py:134; gpt_researcher/context/compression.py:163-181; ISSUE_BACKLOG.md #1684

## Probes

None yet.
