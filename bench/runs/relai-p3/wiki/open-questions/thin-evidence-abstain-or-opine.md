# On thin evidence: abstain, hedge, or give a concrete opinion?

Unclear: the research-report prompt says the model "MUST determine your own concrete and valid
opinion" and write at least TOTAL_WORDS words (`gpt_researcher/prompts.py:298-302`), while the
quick-summary prompt says to state clearly when results are insufficient (`prompts.py:550`) and
the writer abstains only on fully empty context (`skills/writer.py:77-90`).

Why it matters: decides whether a hedged or short report on partial evidence is a pass or a
failure, which grades [thin-context-full-length-report](../risks/thin-context-full-length-report.md)
and [hybrid-empty-context-bypasses-abstain](../risks/hybrid-empty-context-bypasses-abstain.md).

Recommended: require the report to flag weak or missing evidence and allow a shorter report
rather than meet the word count; keep the concrete-opinion rule only where sources support it.
