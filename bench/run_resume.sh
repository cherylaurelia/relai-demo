#!/bin/zsh
B=~/scratch-relai/bench; NAME=$1; SID=$2; cd $B/loop
caffeinate -i claude -p --setting-sources project --model claude-opus-5-5 --plugin-dir $HOME/agent-eval-loop \
  --resume $SID --output-format stream-json --verbose \
  --allowedTools "Read,Glob,Grep,Write,Edit,MultiEdit,Bash,Skill,Task,Agent,TodoWrite" \
  --disallowedTools "WebFetch,WebSearch,Bash(curl:*),Bash(wget:*),Bash(gh:*),Bash(git fetch:*),Bash(git pull:*),Bash(git clone:*),Bash(pip:*),Bash(pip3:*),Bash(uv:*),Bash(npm:*),Bash(npx:*)" \
  -- "Your previous turn was interrupted by a process limit. Continue from the current state to the end of the request: finish the pending checks, freeze the test, record the baseline, and commit with git." > $B/logs/$NAME.jsonl 2> $B/logs/$NAME.err
echo $? > $B/logs/$NAME.exit
