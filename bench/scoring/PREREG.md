# Pre-registered scoring (written 2026-11-17, before any risk list was read)

## Inputs
- Snapshot: assafelovic/gpt-researcher @ 5d84d2f (2026-07-14), the last first-parent main commit before 2026-08-01. Git history removed.
- Later issues: all 52 issues created 2026-08-01..2026-11-17 (`issues.json`, fetched 2026-11-17 via the GitHub API).

## Step 1: classify issues (blind to every run)
Each issue gets exactly one class:
- **bug**: a defect in the agent's code or behavior present in the snapshot's code (wrong output, crash, lost data, unbounded call, wrong accounting, security hole), as described in the issue.
- **setup**: install, packaging, Docker, dependency versions, deployment, or a regression introduced after 2026-07-14 (code that did not exist in the snapshot).
- **other**: feature request, integration pitch, question, listing, proposal.
Only **bug** issues are scored. Code introduced after the snapshot can't be anticipated, so issues about it are setup/other, not misses.

## Step 2: match risks to bugs
A run "anticipates" a bug if one of its listed risks names:
1. the same component, at file or function/class level (a module path, class or function in the snapshot), and
2. the same failure mechanism (e.g. "returns empty string instead of raising on LLM failure", not "LLM calls may fail").
Catch-all risks ("error handling is weak", "external APIs may fail") never match. One risk can match several bugs only if it names each component.
A match whose risk text is copied from the snapshot's `ISSUE_BACKLOG.md` or `PR_*.md` files is flagged `known-in-snapshot` and reported separately.

## Graders
Two independent model graders (Opus and Sonnet, fresh context), each sees the run's risk list with arm labels removed and the bug list, and outputs per bug: matched risk id + quoted risk text + quoted issue text, or none. Disagreements are listed, not resolved silently; the headline counts only matches both graders agree on.

## Reported per arm
Risks listed (count), bugs anticipated (agreed), in all runs / in any run, known-in-snapshot matches apart, risks stable across runs.
