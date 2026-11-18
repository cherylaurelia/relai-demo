# Changes

## 2026-11-17 · generate_report raises when both writer attempts fail (non-subtopic reports)

- **Where:** branch `relai-improve`, `gpt_researcher/actions/report_generation.py` (`generate_report`).
- **Diagnosis:** in the development run `improve-before` (and the earlier baseline), `generate_report` caught
  the fallback writer call's exception, printed it, and returned the initial `report = ""`, so
  `write_report` returned `''` after all 20 writer requests failed.
- **Candidates:**
  1. v1: the fallback's `except` logs and re-raises for every report type. Target 1.00, smoke 1.00
     (`relai/work/runs/improve-after`). **Rejected** by the fresh change review
     (`records/reviews/change-2026-11-17.md`, B1). `subtopic_report` is called from
     `DetailedReport._generate_subtopic_reports`, which has no error handling, and websocket writer calls
     get only one attempt. So one failed section would discard a detailed report's finished
     introduction and sections, where before it was dropped as an empty section.
  2. v2 (kept): same, but `subtopic_report` keeps returning `""`. That path's behavior is deferred
     to the user (STATUS item 4).
- **Tests:** target `tests/report-llm-failure-not-silent`; guardrail `harness/smoke` (it also
  fails every model call, so it does not check a successful report). An offline direction check
  stubs `create_chat_completion` (`/tmp/claude-improve-check/check_generate_report.py`, not
  committed): research/custom report with writer success → report returned, one writer failure → fallback
  report returned, two writer failures → raises; subtopic report with writer success → report returned, two writer failures → `""`. All 6 pass on v2. On the
  unchanged code the double-failure case returned `''`. The repository `tests/` suite was not
  run: pytest is not installed in `.venv`. `tests/report-types.py` and `tests/documents-report-source.py` reach `generate_report` through `write_report` but need live API keys, and neither pins the old `""` behavior.
- **Runs:** native runner `native-gptr-v1`, the same frozen test and harness, 1 attempt per test per side.
  Before: `relai/work/runs/improve-before` on 53934d8 (clean `gpt_researcher/`). After v2:
  `relai/work/runs/improve-after-v2`, 53934d8 plus exactly the `gpt_researcher/` diff of the commit that adds this entry (patch sha256 `a3d66b03…`, checked unchanged during the run).
  The runs are not committed (`relai/work/`).

  | Test | Before | After (v2) |
  | --- | --- | --- |
  | tests/report-llm-failure-not-silent | 0.00 (1/1) | 1.00 (1/1) |
  | harness/smoke | 1.00 (1/1) | 1.00 (1/1) |

  After: `write_report` raised `RuntimeError("Failed to get response from openai API")` chained to
  `openai.RateLimitError`. The stub fails every call, so this path is deterministic, but one
  attempt per side gives no variance estimate.
- **Visible behavior changes for callers of non-subtopic reports** (from the review; not measured):
  - The websocket client gets an error instead of empty files.
  - `POST /report/` returns 500 instead of 200 with an empty report.
  - The CLI exits with a traceback instead of writing empty files.
  - `simple_evals` counts the failure as a failed query.
  - multi_agents: a failed initial research step (`research_report`) now stops the run. Sections use `subtopic_report` and are unchanged.
  - deep_agents: `deep_research` raises only when called without `parent_query`. The researcher prompt always passes it, so the normal flow is unchanged. Not run, because `deepagents` is not installed.
- **Still silent:** `write_report_introduction` and `write_conclusion` return `""` on failure, and
  `generate_draft_section_titles` returns `[]`. Every `subtopic_report` stays silent: detailed-report
  sections, multi-agent sections, deep-agent sections and the CLI's top-level `--report_type subtopic_report`,
  which still writes empty files. The risk is fixed only for non-subtopic reports. A possible
  follow-up would raise unless the subtopic has a parent (`main_topic`), which would also cover the CLI case.
  It needs its own run and review.
- **Verdict:** kept (v2). The fresh re-review passes checks 1–6; its record-only blocker R1 is fixed in this entry ([review](records/reviews/change-2026-11-17.md)).
