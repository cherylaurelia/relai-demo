# Harness (native, sandboxed host)

- `run_trial.py`: the per-trial command for `relai/bin/native_runner.py`. It runs `adapter.py`
  under macOS `sandbox-exec` (outbound IP denied; writes limited to the trial, temp and `/dev`),
  then the test's `tests/check.py`.
- `adapter.py`: drives `GPTResearcher(...).write_report(ext_context=...)` from the checkout's live
  `gpt_researcher/`. Writes `agent/outcome.json`, `agent/trajectory.json` (ATIF) and the mock
  journal.
- `mocks/`: see `MOCKS.md`.
- `smoke/`: harness smoke test (not an eval, not frozen).

Run the smoke test (quote the placeholders under zsh):

    ./.venv/bin/python relai/bin/native_runner.py --out relai/work/runs/<id> --concurrency 1 --timeout 900 \
        --runner-id native-gptr-v1 --tests relai/harness/smoke \
        -- ./.venv/bin/python relai/harness/run_trial.py '{task_dir}' '{trial_dir}'

## Checks done (2026-11-17)

- Live source: in a scratch worktree, editing the abstain message in
  `gpt_researcher/skills/writer.py` changed that worktree's smoke result. This was the earlier
  smoke variant, which checked that literal; the trial imports the checkout's `gpt_researcher/`.
- Containment: under the trial's sandbox profile, connections to `api.openai.com:443` and
  `1.1.1.1:443` were refused, and a write to `relai/` outside the trial was denied. Without the
  sandbox, this host does reach the internet.
- Smoke: `relai/work/runs/smoke-3` scored 1.0. 20 stubbed calls were recorded in order. The
  smoke check scored as expected on synthetic cases: order swapped, no journal and a wrong last
  step each scored 0, and a missing outcome errored.
- Reviews: `relai/records/reviews/harness-2026-11-17.md`.
