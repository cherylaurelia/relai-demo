# RELAI discover: a hindcast on gpt-researcher

Unofficial demo by Cheryl Aurelia, not affiliated with RELAI.

[RELAI's agent-eval-loop](https://github.com/relai-ai/agent-eval-loop) plugin says its `discover`
skill finds "where this agent can fail". This repo tests that against real bug reports:

1. Run `discover` on [gpt-researcher](https://github.com/assafelovic/gpt-researcher) as it was on
   2026-07-14 (commit 5d84d2f, git history removed), with no network.
2. Check its risks against the 52 issues users filed from 2026-08-01 to 2026-11-17: 30 are bugs in
   code that existed at the snapshot, and 14 of those are agent bugs (the scope discover claims).
3. Run the same sentence on bare Claude Code (same model, same sandbox) as a control. Each arm gets 3 runs.
4. For one hit (#2218, `generate_report` returns `""` when the writer LLM fails), use RELAI's
   `eval` skill to build and freeze a test from the risk page. Then check it against PR #2219's
   fix and against a patch from RELAI's `improve` skill that never saw the fix.

## Results

| | Agent bugs per run (of 14) | In every run | All bugs per run (of 30) |
| --- | --- | --- | --- |
| RELAI discover | 7 · 7 · 6 | 6 | 7 · 7 · 6 |
| Bare Claude Code | 5 · 8 · 6 | 4 | 8 · 9 · 10 |

- **Agent bugs:** the two arms are about even, and discover is steadier from run to run.
- **All bugs:** bare Claude Code finds more. Its extra hits are ordinary bugs, such as import-time
  `NameError`s, retriever calls with no timeout and a config reset. Discover's description says
  it excludes these.
- **The #2218 frozen test:**
  - The July code fails it in 3 of 3 trials.
  - PR #2219's two lines alone pass it in 3 of 3.
  - RELAI improve's blind patch passes it in 3 of 3.
- **Bare Claude Code also flagged #2218,** in runs 1 and 2.

## Limits

- One agent and one model (Claude Opus 5.5).
- No traces were available, and discover is built to use them, so read these numbers as a lower bound.
- The agent-bug split was added after the arm results were known. Both graders labelled it, with
  no disagreements.
- The graders are models, so every match is quoted in `bench/scoring/grades_*.jsonl` and on the
  page for you to check.

## Layout

- `bench/scoring/PREREG.md`: the matching rule, written before any risk list was read.
- `bench/scoring/`:
  - `issues.json`: the issue texts.
  - `classes.jsonl`: bug, setup or other.
  - `scope_*.jsonl`: agent bug or ordinary bug.
  - `grades_<run>_<grader>.jsonl`: the graders' matches.
  - `risks_<run>.md`: what each run produced (A = RELAI, B = bare).
- `bench/runs/<run>/`: the prompt, start and end times, the final answer, every tool call, and
  RELAI's wiki output.
- `bench/loop/`:
  - `test/`: the frozen test.
  - `harness/`: the stubbed runner.
  - `runs/`: trial rewards and feedback.
  - `relai-improve.diff` and `pr2219.diff`: the two fixes.
- `bench/run_arm.sh`, `bench/run_loop.sh`: how each session was launched (headless `claude -p`,
  `--setting-sources project`, web and network tools denied).

## Rerun

```sh
git clone https://github.com/assafelovic/gpt-researcher src
mkdir relai-p1 && git -C src archive 5d84d2f | tar -x -C relai-p1
git clone https://github.com/relai-ai/agent-eval-loop ~/agent-eval-loop && git -C ~/agent-eval-loop checkout 374f8ed
./bench/run_arm.sh relai relai-p1            # paths in the scripts assume ~/scratch-relai/bench
python3 -I bench/scoring/extract.py relai-p1 A1 && bench/scoring/grade.sh A1 claude-opus-5-5
```

## The page

Next.js with Tailwind. `scripts/build_data.py <bench-dir> <scoring-dir>` built `data/hindcast.json` from the
scoring files, and `npm test` checks the counts. Run `npm run build && npm start` to serve it.
