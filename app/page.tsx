import hindcastJson from "@/data/hindcast.json";
import loopJson from "@/data/loop.json";
import { daysBetween, minutes, runsThatCaught, summarize, type Bug, type Run } from "@/lib/hindcast";

interface Loop {
  riskPage: string;
  riskQuote: string;
  snapshotDate: string;
  issue: number;
  issueDate: string;
  issueQuote: string;
  fixPr: number;
  fixMerged: string;
  testId: string;
  frozenAt: string;
  frozenCommit: string;
  trials: { snapshot: number[]; withPr2219: number[]; relaiImprove: number[] };
  riskPageExcerpt: string;
  controlLine: string;
  controlRun: string;
}

interface Hindcast {
  snapshot: { repo: string; commit: string; date: string };
  window: string[];
  counts: { issues: number; bugs: number; agent_bugs: number; classes: { bug: number; setup: number; other: number } };
  runs: Run[];
  bugs: Bug[];
}

const data: Hindcast = {
  ...hindcastJson,
  runs: hindcastJson.runs.map((run) => ({ ...run, arm: run.arm === "relai" ? "relai" : "control" })),
  bugs: hindcastJson.bugs.map((bug) => ({ ...bug, scope: bug.scope === "agent" ? "agent" : "ordinary" })),
};

const loop: Loop = loopJson;

const REPO = "https://github.com/cherylaurelia/relai-demo";
const RELAI_REPO = "https://github.com/relai-ai/agent-eval-loop";
const GPTR = "https://github.com/assafelovic/gpt-researcher";
const BLOB = `${REPO}/blob/main`;

const lead = daysBetween(loop.snapshotDate, loop.issueDate);
const relaiScoped = summarize(data.runs, "relai", true);
const controlScoped = summarize(data.runs, "control", true);
const relaiAll = summarize(data.runs, "relai", false);
const controlAll = summarize(data.runs, "control", false);
const controlCaught2218 = runsThatCaught(data.runs, "control", loop.issue);
const agentBugs = data.bugs.filter((bug) => bug.scope === "agent");
const ordinaryBugs = data.bugs.filter((bug) => bug.scope === "ordinary");

function passed(trials: number[]): string {
  return `${trials.filter((score) => score === 1).length} of ${trials.length}`;
}

function Code({ children }: { children: string }) {
  return <code className="rounded bg-white/10 px-1 py-0.5 font-mono text-[0.85em]">{children}</code>;
}

/** Renders `code` spans in quoted text as inline code. */
function Inline({ text }: { text: string }) {
  return (
    <>
      {text.split("`").map((part, index) => (index % 2 === 1 ? <Code key={index}>{part}</Code> : part))}
    </>
  );
}

function Step({ label, title, children }: { label: string; title: string; children: React.ReactNode }) {
  return (
    <li className="rounded-[10px] border border-line bg-panel p-5">
      <p className="font-mono text-xs uppercase tracking-wider text-teal">{label}</p>
      <h3 className="mt-1 font-semibold">{title}</h3>
      <div className="mt-2 text-sm leading-relaxed text-soft">{children}</div>
    </li>
  );
}

function ArmRow({ name, scoped, all }: { name: string; scoped: ReturnType<typeof summarize>; all: ReturnType<typeof summarize> }) {
  return (
    <tr className="border-t border-line">
      <th scope="row" className="py-3 pr-4 text-left font-medium">{name}</th>
      <td className="py-3 pr-4 tabular-nums">{scoped.perRun.join(" · ")}</td>
      <td className="py-3 pr-4 tabular-nums">{scoped.inEveryRun.length}</td>
      <td className="py-3 pr-4 tabular-nums">{scoped.inAnyRun.length}</td>
      <td className="py-3 pr-4 tabular-nums text-muted">{all.perRun.join(" · ")}</td>
      <td className="py-3 tabular-nums text-muted">{all.inAnyRun.length}</td>
    </tr>
  );
}

function BugRow({ bug }: { bug: Bug }) {
  const relai = runsThatCaught(data.runs, "relai", bug.number);
  const control = runsThatCaught(data.runs, "control", bug.number);

  return (
    <li className="border-t border-line py-3">
      <details>
        <summary className="grid cursor-pointer grid-cols-[4.5rem_1fr] gap-x-3 gap-y-1 sm:grid-cols-[4.5rem_1fr_7rem_7rem]">
          <a href={bug.url} className="font-mono text-sky underline-offset-2 hover:underline">#{bug.number}</a>
          <span>
            {bug.title}
            <span className="ml-2 text-xs text-muted">{bug.created} · {bug.scope === "agent" ? "agent bug" : "ordinary bug"}</span>
          </span>
          <span className={`col-start-2 text-sm sm:col-start-auto ${relai === "none" ? "text-muted" : "text-teal"}`}>RELAI: {relai}</span>
          <span className={`col-start-2 text-sm sm:col-start-auto ${control === "none" ? "text-muted" : "text-sky"}`}>Bare: {control}</span>
        </summary>
        <div className="mt-2 space-y-2 pl-0 text-sm sm:pl-[5.25rem]">
          <p className="text-soft">Mechanism: <Inline text={bug.mechanism} /></p>
          {bug.quotes.length === 0 ? (
            <p className="text-muted">No run named this component and mechanism.</p>
          ) : (
            bug.quotes.map((quote) => (
              <p key={quote.run} className="text-soft">
                <span className="font-mono text-xs text-muted">{quote.run}</span> risk: “<Inline text={quote.risk} />” · issue: “<Inline text={quote.issue} />”
              </p>
            ))
          )}
        </div>
      </details>
    </li>
  );
}

export default function Page() {
  const relaiMinutes = data.runs.flatMap((run) => (run.arm === "relai" ? [minutes(run)] : []));

  return (
    <main>
      <header className="hero text-white">
        <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5 text-sm">
          <span className="font-semibold tracking-[0.2em]">RELAI · hindcast</span>
          <span className="flex gap-5">
            <a href={REPO} className="hover:underline">Results repo</a>
            <a href={RELAI_REPO} className="hover:underline">agent-eval-loop</a>
          </span>
        </nav>
        <div className="mx-auto max-w-5xl px-6 pb-14 pt-10">
          <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
            Given gpt-researcher’s July code, RELAI found a bug a user reported {lead} days later, then wrote a test for it and a patch that passes it.
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-relaxed text-white/90">
            Discover named the empty-report bug (issue #{loop.issue}) in 2 of its 3 runs; eval turned that risk page into a frozen test that fails
            before the real fix and passes after it; improve, without seeing the fix, wrote a patch that passes it too.
          </p>
          <p className="mt-3 max-w-3xl text-white/90">
            Against bare Claude Code (same model, same sandbox): the same hit rate on agent bugs, but the same {relaiScoped.inEveryRun.length} agent bugs in every run and a runnable test at the end. Bare Claude also named #{loop.issue} (runs {controlCaught2218} of 3) and finds more ordinary bugs.
          </p>
          <p className="mt-4 text-sm text-white/80">
            One agent · one model (Claude Opus 5.5) · no traces (code and docs only) · no network · model graders
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <a href={REPO} className="rounded-[10px] bg-white px-4 py-2 font-medium text-[#0a0b0d]">Data, prompts and logs</a>
            <a href={`${BLOB}/bench/scoring/PREREG.md`} className="rounded-[10px] border border-white/60 px-4 py-2 font-medium">Pre-registered scoring</a>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-5xl px-6 py-12" aria-labelledby="loop">
        <h2 id="loop" className="text-2xl font-semibold">One bug, end to end</h2>
        <ol className="mt-6 grid gap-4 md:grid-cols-2">
          <Step label={`discover · code as of ${loop.snapshotDate}`} title="The risk">
            “<Inline text={loop.riskQuote} />” <a href={`${BLOB}/${loop.riskPage}`} className="text-sky underline">risk page</a>{" "}
            <span className="text-muted">(its “Found at: 0595cd3” is the local commit of snapshot {data.snapshot.commit}, made after history was removed)</span>
          </Step>
          <Step label={`issue #${loop.issue} · ${loop.issueDate} · ${lead} days later`} title="The user report">
            “<Inline text={loop.issueQuote} />” <a href={`${GPTR}/issues/${loop.issue}`} className="text-sky underline">#{loop.issue}</a>, fixed by{" "}
            <a href={`${GPTR}/pull/${loop.fixPr}`} className="text-sky underline">PR #{loop.fixPr}</a> on {loop.fixMerged}.
          </Step>
          <Step label={`eval · frozen ${loop.frozenAt.slice(0, 16).replace("T", " ")} UTC`} title="A frozen test, written from the risk page">
            <p>
              <Code>{loop.testId}</Code> calls the real <Code>write_report</Code> with every model call answered by a 429 stub,
              and passes only if the failure reaches the caller. Frozen and committed ({loop.frozenCommit}) before any fix was applied to the snapshot. This was 2026-11-18, after PR #{loop.fixPr} merged upstream; the run had no network and the snapshot no git history, so the skills could not see the fix.{" "}
              <a href={`${REPO}/tree/main/bench/loop/test`} className="text-sky underline">Test</a> ·{" "}
              <a href={`${REPO}/tree/main/bench/loop/harness`} className="text-sky underline">429 stub</a>
            </p>
            <p className="mt-2">
              July code: <strong className="text-miss">{passed(loop.trials.snapshot)} pass</strong> (it returns an empty
              report). With only PR #{loop.fixPr}’s two lines: <strong className="text-teal">{passed(loop.trials.withPr2219)} pass</strong>.
            </p>
          </Step>
          <Step label="improve · without seeing the fix" title="A blind patch that passes the same test">
            <p>
              The improve skill wrote the same core change as PR #{loop.fixPr} (log, then raise):{" "}
              <strong className="text-teal">{passed(loop.trials.relaiImprove)} pass</strong>. Its reviewer also rejected a first
              version that would have dropped a whole detailed report when one section failed, so section writers keep returning
              “”. <a href={`${BLOB}/bench/loop/relai-improve.diff`} className="text-sky underline">Diff</a>
            </p>
          </Step>
        </ol>
      </section>

      <section className="mx-auto max-w-5xl px-6 pb-12" aria-labelledby="artifact">
        <h2 id="artifact" className="text-xl font-semibold">What each arm left for #{loop.issue}</h2>
        <div className="mt-4 grid items-start gap-4 md:grid-cols-2">
          <figure className="rounded-[10px] border border-line bg-panel p-4">
            <figcaption className="font-mono text-xs uppercase tracking-wider text-teal">RELAI discover · wiki risk page</figcaption>
            <pre className="mt-3 whitespace-pre-wrap font-mono text-xs leading-relaxed text-soft">{loop.riskPageExcerpt}</pre>
            <p className="mt-3 text-xs text-muted">Linked to a requirement, rated, with file:line evidence. Eval built the test from this page.</p>
          </figure>
          <figure className="rounded-[10px] border border-line bg-panel p-4">
            <figcaption className="font-mono text-xs uppercase tracking-wider text-sky">Bare Claude Code · one line in its report</figcaption>
            <p className="mt-3 font-mono text-xs leading-relaxed text-soft">
              <Inline text={loop.controlLine} />
            </p>
            <p className="mt-3 text-xs text-muted">
              Correct, as one line of a longer report; this arm’s findings were not run through eval. <a href={`${BLOB}/${loop.controlRun}`} className="text-sky underline">Full report</a>
            </p>
          </figure>
        </div>
      </section>

      <section className="border-t border-line bg-panel/40" aria-labelledby="hindcast">
        <div className="mx-auto max-w-5xl px-6 py-12">
          <h2 id="hindcast" className="text-2xl font-semibold">The hindcast: 3 runs of discover, 3 of bare Claude Code</h2>
          <p className="mt-3 text-lg">
            Takeaway: the same hit rate as bare Claude Code on agent bugs ({relaiScoped.mean.toFixed(1)} vs{" "}
            {controlScoped.mean.toFixed(1)} per run), steadier across runs, and it leaves a wiki eval can build tests from. On all
            bugs bare Claude finds more ({controlAll.mean.toFixed(1)} vs {relaiAll.mean.toFixed(1)}), mostly ordinary bugs discover
            excludes by design.
          </p>
          <p className="mt-3 max-w-3xl leading-relaxed text-soft">
            Of {data.counts.issues} issues filed {data.window[0]} to {data.window[1]}, {data.counts.bugs} are bugs in code that
            already existed on {data.snapshot.date} (classified blind, before any risk list was read). {data.counts.agent_bugs} of
            them are agent bugs, the scope discover’s description claims; the rest are ordinary bugs it says it excludes. That split was
            made after the arm results were known (two graders, no disagreements), so the all-bugs columns are shown too. A bug counts
            only if both graders (Opus and Sonnet) found a risk naming the same function and the same failure.
          </p>
          <div className="mt-6 overflow-x-auto">
            <table className="w-full min-w-[40rem] text-sm">
              <caption className="pb-3 text-left text-xs text-muted">
                Bugs both graders matched, per run. Agent vs ordinary split decided after the results were known.
              </caption>
              <thead className="text-left text-muted">
                <tr>
                  <th scope="col" className="pb-2 pr-4 font-normal">Arm</th>
                  <th scope="col" className="pb-2 pr-4 font-normal">Agent bugs per run (of {data.counts.agent_bugs})</th>
                  <th scope="col" className="pb-2 pr-4 font-normal">In every run</th>
                  <th scope="col" className="pb-2 pr-4 font-normal">In any run</th>
                  <th scope="col" className="pb-2 pr-4 font-normal">All bugs per run (of {data.counts.bugs})</th>
                  <th scope="col" className="pb-2 font-normal">All, any run</th>
                </tr>
              </thead>
              <tbody>
                <ArmRow name="RELAI discover" scoped={relaiScoped} all={relaiAll} />
                <ArmRow name="Bare Claude Code" scoped={controlScoped} all={controlAll} />
              </tbody>
            </table>
          </div>
          <ul className="mt-6 space-y-2 text-sm leading-relaxed text-soft">
            <li>
              <strong className="text-ink">Within its scope, about even, and steadier (n = 3 runs each).</strong> Discover named{" "}
              {relaiScoped.inEveryRun.length} of its {relaiScoped.inAnyRun.length} agent bugs in every run; bare Claude Code{" "}
              {controlScoped.inEveryRun.length} of {controlScoped.inAnyRun.length}. Frozen evals need a risk set that doesn’t change each time you ask.
            </li>
            <li>
              <strong className="text-ink">Outside its scope, bare Claude Code finds more.</strong> Its extra hits are import-time
              NameErrors, retriever calls with no timeout and a config reset, which are ordinary bugs the skill’s description excludes, plus one agent bug discover never named (#2100, prefetched sources missing from References).
            </li>
            <li>
              <strong className="text-ink">What discover leaves behind.</strong> Each run wrote{" "}
              {data.runs.flatMap((run) => (run.arm === "relai" ? [run.risks] : [])).join(", ")} risk pages with file:line
              evidence, plus requirements and open questions, in {relaiMinutes.join(", ")} minutes; that wiki is what eval built
              the test from.
            </li>
          </ul>

          <h3 className="mt-10 font-semibold">The {agentBugs.length} agent bugs, and which runs named them</h3>
          <ul className="mt-2">
            {agentBugs.map((bug) => (
              <BugRow key={bug.number} bug={bug} />
            ))}
          </ul>
          <details className="mt-6">
            <summary className="cursor-pointer font-semibold">The {ordinaryBugs.length} ordinary bugs (outside discover’s scope)</summary>
            <ul className="mt-2">
              {ordinaryBugs.map((bug) => (
                <BugRow key={bug.number} bug={bug} />
              ))}
            </ul>
          </details>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 py-12" aria-labelledby="method">
        <h2 id="method" className="text-2xl font-semibold">How it was run</h2>
        <ul className="mt-4 space-y-2 text-sm leading-relaxed text-soft">
          <li>
            Snapshot: <Code>{`${data.snapshot.repo}@${data.snapshot.commit}`}</Code>, the last main commit before 2026-08-01,
            with git history removed. The model’s training cutoff (June 2026) is before every scored issue.
          </li>
          <li>
            RELAI arm: unchanged plugin (<Code>relai-ai/agent-eval-loop@374f8ed</Code>) loaded with{" "}
            <Code>--plugin-dir</Code>, prompt “Use RELAI’s discover skill to read this agent’s code, prompts and docs, and tell
            me where it is likely to fail.” Control: the same sentence without the skill.
          </li>
          <li>
            Headless <Code>claude -p</Code>, web tools and network commands denied, every tool call logged and checked: no run
            fetched anything.
          </li>
          <li>
            Limits: one agent and one model; no traces, which discover is built to use, so read these as a lower bound; the
            agent-bug split was added after the arm results were known (both graders, no disagreements); graders are models,
            so every match is quoted for you to check.
          </li>
        </ul>
        <pre className="mt-6 overflow-x-auto rounded-[10px] border border-line bg-panel p-4 font-mono text-xs leading-relaxed text-soft">
{`git clone ${REPO} && git clone ${GPTR} src
git clone ${RELAI_REPO} ~/agent-eval-loop && git -C ~/agent-eval-loop checkout 374f8ed
mkdir -p ~/scratch-relai/bench/relai-p1 && git -C src archive 5d84d2f | tar -x -C ~/scratch-relai/bench/relai-p1
cp -R relai-demo/bench/. ~/scratch-relai/bench/ && cd ~/scratch-relai/bench
./run_arm.sh relai relai-p1
python3 -I scoring/extract.py relai-p1 A1 && scoring/grade.sh A1 claude-opus-5-5`}
        </pre>
      </section>

      <footer className="border-t border-line px-6 py-8 text-center text-sm text-muted">
        Unofficial demo by Cheryl Aurelia: not affiliated with RELAI. gpt-researcher issues are linked, not copied beyond short quotes.
      </footer>
    </main>
  );
}
