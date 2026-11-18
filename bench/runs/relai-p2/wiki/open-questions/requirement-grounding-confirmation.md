# Is abstaining with no evidence an intended product behavior?

Unclear: [abstain-when-no-evidence](../requirements/abstain-when-no-evidence.md) is grounded in a code comment and guard (gpt_researcher/skills/writer.py:79-88), not user-facing docs; the docs only promise "factual" reports.
Why it matters: if intended, [hybrid bypass](../risks/hybrid-empty-context-bypasses-abstain.md) and [silent partial failure](../risks/silent-partial-research-failure.md) are requirement violations and testable with a hard check; otherwise they are quality issues.
Recommendation: confirm as a requirement.
