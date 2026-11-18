import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { daysBetween, runsThatCaught, summarize, type Bug, type Run } from "./hindcast.ts";

const data: { runs: Run[]; bugs: Bug[]; counts: { bugs: number; agent_bugs: number } } = JSON.parse(
  readFileSync(new URL("../data/hindcast.json", import.meta.url), "utf8"),
);

function run(arm: Run["arm"], index: number, hits: number[], agentHits: number[]): Run {
  return { arm, run: index, start: "2026-11-18T03:30:00Z", end: "2026-11-18T03:35:00Z", risks: 0, hits, agent_hits: agentHits };
}

test("summarize keeps per-run counts, every-run and any-run sets", () => {
  const runs = [run("relai", 1, [1, 2, 3], [1, 2]), run("relai", 2, [2, 3], [2]), run("control", 1, [9], [])];
  const all = summarize(runs, "relai", false);
  assert.deepEqual(all.perRun, [3, 2]);
  assert.equal(all.mean, 2.5);
  assert.deepEqual(all.inEveryRun, [2, 3]);
  assert.deepEqual(all.inAnyRun, [1, 2, 3]);
  assert.deepEqual(summarize(runs, "relai", true).inEveryRun, [2]);
  assert.deepEqual(summarize(runs, "control", true), { perRun: [0], mean: 0, inEveryRun: [], inAnyRun: [] });
});

test("an arm with no runs has mean 0", () => {
  assert.equal(summarize([], "relai", false).mean, 0);
});

test("days from the snapshot to issue #2218", () => {
  assert.equal(daysBetween("2026-07-14", "2026-10-18"), 96);
});

test("runsThatCaught lists runs or says none", () => {
  const runs = [run("relai", 1, [5], []), run("relai", 3, [5], [])];
  assert.equal(runsThatCaught(runs, "relai", 5), "1, 3");
  assert.equal(runsThatCaught(runs, "control", 5), "none");
});

test("recorded hindcast: counts match the graders' files", () => {
  assert.equal(data.counts.bugs, 30);
  assert.equal(data.counts.agent_bugs, 14);
  assert.deepEqual(summarize(data.runs, "relai", false).perRun, [7, 7, 6]);
  assert.deepEqual(summarize(data.runs, "control", false).perRun, [8, 9, 10]);
  assert.deepEqual(summarize(data.runs, "relai", true).perRun, [7, 7, 6]);
  assert.deepEqual(summarize(data.runs, "control", true).perRun, [5, 8, 6]);
  assert.deepEqual(summarize(data.runs, "relai", true).inEveryRun.length, 6);
});
