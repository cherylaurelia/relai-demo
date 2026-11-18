#!/bin/zsh
# usage: run_arm.sh <arm relai|ctrl> <dir-name>
set -u
ARM=$1; NAME=$2; B=~/scratch-relai/bench
cd $B/$NAME || exit 1
NOQ="I'm not available to answer questions during this run: where you would ask me, record the question in your output instead and continue to the end."
if [ $ARM = relai ]; then
  PROMPT="Use RELAI's discover skill to read this agent's code, prompts and docs, and tell me where it is likely to fail. $NOQ"
  EXTRA=(--plugin-dir $HOME/agent-eval-loop)
else
  PROMPT="Read this agent's code, prompts and docs, and tell me where it is likely to fail. $NOQ"
  EXTRA=()
fi
echo "$PROMPT" > $B/logs/$NAME.prompt.txt
date -u +%FT%TZ > $B/logs/$NAME.start
caffeinate -i claude -p --setting-sources project --model claude-opus-5-5 "${EXTRA[@]}" \
  --output-format stream-json --verbose \
  --allowedTools "Read,Glob,Grep,Write,Edit,MultiEdit,Bash,Skill,Task,Agent,TodoWrite" \
  --disallowedTools "WebFetch,WebSearch,Bash(curl:*),Bash(wget:*),Bash(gh:*),Bash(git fetch:*),Bash(git pull:*),Bash(git clone:*),Bash(pip:*),Bash(pip3:*),Bash(uv:*),Bash(npm:*),Bash(npx:*)" \
  -- "$PROMPT" > $B/logs/$NAME.jsonl 2> $B/logs/$NAME.err
echo $? > $B/logs/$NAME.exit
date -u +%FT%TZ > $B/logs/$NAME.end
