"""Per-trial command for relai/bin/native_runner.py (quote the placeholders in zsh):

  ./.venv/bin/python relai/harness/run_trial.py '{task_dir}' '{trial_dir}'

Runs the agent (adapter.py) on the test's scenario.json with the project's venv interpreter,
then the test's verifier (tests/check.py <trial_dir>), which writes verifier/reward.json,
feedback.json and errors.json.

Containment (authorized host execution, relai/decisions.md): the agent process runs under macOS
sandbox-exec with all outbound IP traffic denied (loopback included) and file writes limited to
the trial directory, the temp directory and /dev. It gets only PATH, HOME, LANG, TMPDIR and a
placeholder OPENAI_API_KEY (ChatOpenAI refuses to construct without one; the fault stub answers
every OpenAI chat call, and the sandbox stops anything else from leaving the machine). Without
sandbox-exec the trial refuses to run.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
AGENT_TIMEOUT = 600  # keep below the runner's --timeout (900 in the documented command)
PLACEHOLDER_KEY = "sk-relai-placeholder-not-a-key"


def profile(trial: Path, tmp: Path) -> str:
    def q(p: Path) -> str:
        return '"' + str(p.resolve()).replace('"', '\\"') + '"'
    return ("(version 1)(allow default)"
            "(deny network-outbound (remote ip))"
            "(deny file-write*)"
            f"(allow file-write* (subpath {q(trial)}) (subpath {q(tmp)}) (subpath \"/dev\")"
            " (subpath \"/private/var/folders\"))")


def main() -> int:
    task, trial = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    sandbox = shutil.which("sandbox-exec")
    if not sandbox:
        print("run_trial: sandbox-exec not found; refusing to run the agent uncontained", file=sys.stderr)
        return 2
    agent_dir, workdir, tmp = trial / "agent", trial / "workdir", trial / "tmp"
    for d in (agent_dir, workdir, tmp):
        d.mkdir(parents=True, exist_ok=True)
    version = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "gpt_researcher"], cwd=REPO,
                           capture_output=True, text=True).stdout.strip()
    env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG") if k in os.environ}
    env.update({"TMPDIR": str(tmp), "OPENAI_API_KEY": PLACEHOLDER_KEY, "PYTHONDONTWRITEBYTECODE": "1",
                "RELAI_AGENT_VERSION": f"{version}{'+dirty' if dirty else ''}"})
    command = [sandbox, "-p", profile(trial, Path(tempfile.gettempdir())), sys.executable,
               str(HERE / "adapter.py"), str(task / "scenario.json"), str(agent_dir)]
    with (agent_dir / "agent.log").open("w") as log:
        try:
            subprocess.run(command, cwd=workdir, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=AGENT_TIMEOUT)
        except subprocess.TimeoutExpired:
            log.write(f"\n[run_trial] agent exceeded {AGENT_TIMEOUT}s\n")
    verify = subprocess.run([sys.executable, str(task / "tests" / "check.py"), str(trial)],
                            cwd=task / "tests", env=env)
    return verify.returncode


if __name__ == "__main__":
    sys.exit(main())
