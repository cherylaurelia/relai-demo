// Numbers behind the page. Inputs are data/hindcast.json (built by scripts/build_data.py from
// the graders' files in bench/scoring) and data/loop.json (trial rewards in bench/loop/runs).

export type Arm = "relai" | "control";

export interface Run {
  arm: Arm;
  run: number;
  start: string;
  end: string;
  risks: number;
  hits: number[];
  agent_hits: number[];
}

export interface Quote {
  run: string;
  risk: string;
  issue: string;
}

export interface Bug {
  number: number;
  title: string;
  created: string;
  url: string;
  scope: "agent" | "ordinary";
  mechanism: string;
  quotes: Quote[];
}

export interface ArmSummary {
  perRun: number[];
  mean: number;
  inEveryRun: number[];
  inAnyRun: number[];
}

/** Bugs both graders matched, per run of one arm; `agentOnly` keeps discover's documented scope. */
export function summarize(runs: Run[], arm: Arm, agentOnly: boolean): ArmSummary {
  const sets = runs.flatMap((run) => (run.arm === arm ? [new Set(agentOnly ? run.agent_hits : run.hits)] : []));
  const union = new Set(sets.flatMap((set) => [...set]));
  const every = [...union].filter((bug) => sets.every((set) => set.has(bug)));
  const perRun = sets.map((set) => set.size);

  const mean = perRun.length === 0 ? 0 : perRun.reduce((sum, n) => sum + n, 0) / perRun.length;

  return {
    perRun,
    mean,
    inEveryRun: every.toSorted((a, b) => a - b),
    inAnyRun: [...union].toSorted((a, b) => a - b),
  };
}

/** Whole days from one ISO date (YYYY-MM-DD) to another. */
export function daysBetween(from: string, to: string): number {
  return Math.round((Date.parse(`${to}T00:00:00Z`) - Date.parse(`${from}T00:00:00Z`)) / 86_400_000);
}

/** Runs of an arm whose matches include this bug, as "1, 3" or "none". */
export function runsThatCaught(runs: Run[], arm: Arm, bug: number): string {
  const caught = runs.flatMap((run) => (run.arm === arm && run.hits.includes(bug) ? [run.run] : []));

  return caught.length === 0 ? "none" : caught.join(", ");
}

export function minutes(run: Run): number {
  return Math.round((Date.parse(run.end) - Date.parse(run.start)) / 60_000);
}
