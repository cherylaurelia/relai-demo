# What should happen when a multi-agent revision cap is reached?

Unclear: the draft-review helper "force-accepts gracefully" (multi_agents/agents/draft_review.py:14); fact-check and plan helpers raise; README says the reviser continues "until satisfactory" and that plan cap gives "a clear error".
Why it matters: determines the pass condition for tests of [loop termination](../requirements/multi-agent-revision-loops-terminate.md) — publish with a warning vs fail the run.
Choices: (a) publish the latest draft with a visible warning — recommended for users; (b) fail with a clear error.
