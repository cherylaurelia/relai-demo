# What should the agent do when research yields little or no source material?

The only stated behavior is a code guard: `writer.py:79-88` returns "I could not gather any source material…" when the context is blank. Code is evidence, not intent. The report prompt meanwhile demands "at least {total_words} words", "as long as you can" and "your own concrete and valid opinion" (`prompts.py:297-303`). That pushes the model to pad from memory when context is thin. The guard does not cover hybrid mode (see [hybrid-empty-context-bypasses-abstain](../risks/hybrid-empty-context-bypasses-abstain.md)). In detailed reports it becomes a section body (`detailed_report.py:116`).

Why it matters: this decides whether the abstain/disclose tests and the "answer from memory" grader count a thin-context report as a pass or a fail.

Choices: (a) abstain whenever no usable sources were gathered, in every mode and section; (b) also disclose partial coverage when some sub-queries or sections found nothing; (c) allow answering from model knowledge if it is clearly labeled as unsourced.

Recommended: (b). It is consistent with the existing guard and the README's "factual … with citations" claim.
Blocking: no
