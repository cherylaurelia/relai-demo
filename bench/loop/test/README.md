# report-llm-failure-not-silent

**Behavior.** When the report writer's model calls all fail, `GPTResearcher.write_report()` must
surface the failure to its caller by raising an exception. It must
not return a report, empty or otherwise, that callers would save as finished. (Returning a
notice string also scores 0: the CLI and backend save any returned string as the report. This
choice is pending the user's answer to question 1 in `relai/records/eval/2026-11-17-scenarios.md`.)

**Risk probed.** [report-llm-failure-returns-empty](../../wiki/risks/report-llm-failure-returns-empty.md),
basic report path: `generate_report` (gpt_researcher/actions/report_generation.py) catches the
writer's exception twice (first call, then the single-message fallback) and returns `""`.

**Scenario.** A `research_report` on a realistic astronomy question (JWST vs Hubble primary
mirrors), with three sourced NASA context entries in the agent's own `Source/Title/Content`
format, passed through the public `write_report(ext_context=...)`. Research itself
(`conduct_research`) is not run: it needs live retrievers and a model. The trigger is a persistent
provider rate limit: every OpenAI chat call the agent makes is answered by the fault stub
(`relai/harness/mocks/llm_fault.py`) with the SDK's real `openai.RateLimitError` (HTTP 429), so
`create_chat_completion`'s own 10-attempt retry loop and `generate_report`'s fallback run
unchanged. No real model is called. A trial takes about two minutes because of the agent's own
retry back-off.

**Evaluator.**

| id | type | passes when | fails when |
| --- | --- | --- | --- |
| `failure-not-silent` | code, exact | after every writer request failed, `write_report` raised an exception (chained to `openai.RateLimitError` or a fresh one; feedback says which) | it returned anything (`""`, whitespace, a notice, a header-only or context-dump "report", `None`) |

The check reads exported state (`agent/outcome.json`, `agent/mock-journal.jsonl`), not the
agent's description. It errors instead of scoring when `outcome.json` is missing, when no
journaled model call carries the scenario's context (`tests/params.json` `writer_call_marker`,
so the writer failure was never triggered), when any journaled call was not answered with the
injected error, or when the outermost raised exception is a programming error (`tests/params.json` `programming_errors`: KeyError, TypeError, AttributeError, ...).

**Probe invalid when.** The writer call never reaches the stub, or the agent crashes with a
programming error (errors, above); the trial times out or the adapter crashes before writing
`outcome.json` (runtime failure / error).

**Not covered here.** A returned failure notice (scored 0 for now; see Behavior); the websocket/backend path that
writes empty pdf/docx/md files; the detailed-report introduction, conclusion and subtopic
sections; the duplicated-stream retry. Opposite-direction partner (a writer that succeeds must
still return the report) is proposed, not built.

**Run it.**

    ./.venv/bin/python relai/bin/native_runner.py --out relai/work/runs/<run-id> --concurrency 1 \
        --timeout 900 --runner-id native-gptr-v1 --tests relai/tests/report-llm-failure-not-silent \
        -- ./.venv/bin/python relai/harness/run_trial.py '{task_dir}' '{trial_dir}'
    python3 relai/bin/summarize.py relai/work/runs/<run-id> --details

Quote the placeholders: zsh treats an unquoted `{name}` before a redirection as a named-fd redirect.
