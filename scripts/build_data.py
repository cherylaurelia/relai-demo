"""Build data/hindcast.json from the bench's scoring files.

usage: python3 -I scripts/build_data.py <bench-dir> <scoring-dir>
Counts only matches that both graders (Opus 5.5, Sonnet 5.5) marked as a match.
"""
import json
import pathlib
import re
import sys

bench, scoring = map(pathlib.Path, sys.argv[1:3])
GRADERS = ("claude-opus-5-5", "claude-sonnet-5-5")
RUNS = {"A1": ("relai", 1, "relai-p1"), "A2": ("relai", 2, "relai-p2"), "A3": ("relai", 3, "relai-p3"),
        "B1": ("control", 1, "ctrl-p1"), "B2": ("control", 2, "ctrl-p2"), "B3": ("control", 3, "ctrl-p3")}


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


issues = {i["number"]: i for i in json.loads((scoring / "issues.json").read_text())}
classes = {c["number"]: c for c in jsonl(scoring / "classes.jsonl")}
scope = {g: {s["bug"]: s["scope"] for s in jsonl(scoring / f"scope_{g}.jsonl")} for g in GRADERS}
bugs = sorted(n for n, c in classes.items() if c["class"] == "bug")
agent_bugs = [n for n in bugs if all(scope[g][n] == "agent" for g in GRADERS)]

runs = []
quotes = {}
for anon, (arm, idx, name) in RUNS.items():
    grades = {g: {r["bug"]: r for r in jsonl(scoring / f"grades_{anon}_{g}.jsonl")} for g in GRADERS}
    agreed = [n for n in bugs if all(grades[g][n]["match"] for g in GRADERS)]
    for n in agreed:
        r = grades[GRADERS[0]][n]
        quotes.setdefault(n, []).append({"run": f"{arm}-{idx}", "risk": r["risk_quote"], "issue": r["issue_quote"]})
    log = bench / "logs" / name
    start, end = (log.with_suffix(s).read_text().strip() for s in (".start", ".end"))
    wiki = bench / name / "relai" / "wiki" / "risks"
    if wiki.is_dir():
        risks = len(list(wiki.glob("*.md")))
    else:
        text = (scoring / f"risks_{anon}.md").read_text()
        risks = len(re.findall(r"^(?:#+\s*)?\d+\.\s", text, flags=re.M))
    runs.append({"arm": arm, "run": idx, "start": start, "end": end, "risks": risks,
                 "hits": agreed, "agent_hits": [n for n in agreed if n in agent_bugs]})

out = {
    "snapshot": {"repo": "assafelovic/gpt-researcher", "commit": "5d84d2f", "date": "2026-07-14"},
    "window": ["2026-08-01", "2026-11-17"],
    "counts": {"issues": len(issues), "bugs": len(bugs), "agent_bugs": len(agent_bugs),
               "classes": {k: sum(1 for c in classes.values() if c["class"] == k) for k in ("bug", "setup", "other")}},
    "runs": runs,
    "bugs": [{"number": n, "title": issues[n]["title"], "created": issues[n]["created_at"][:10],
              "url": issues[n]["url"], "scope": "agent" if n in agent_bugs else "ordinary",
              "mechanism": classes[n]["mechanism"], "quotes": quotes.get(n, [])} for n in bugs],
}
pathlib.Path("data/hindcast.json").write_text(json.dumps(out, indent=1) + "\n")
print(len(bugs), "bugs,", len(agent_bugs), "agent;", [(r["arm"], len(r["hits"]), len(r["agent_hits"]), r["risks"]) for r in runs])
