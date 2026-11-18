#!/bin/zsh
# usage: run_loop.sh <name> <prompt-file>
B=~/scratch-relai/bench; NAME=$1; cd $B/loop
PROMPT=$(cat $2); cp $2 $B/logs/$NAME.prompt.txt
date -u +%FT%TZ > $B/logs/$NAME.start
caffeinate -i claude -p --setting-sources project --model claude-opus-5-5 --plugin-dir $HOME/agent-eval-loop \
  --output-format stream-json --verbose \
  --allowedTools "Read,Glob,Grep,Write,Edit,MultiEdit,Bash,Skill,Task,Agent,TodoWrite" \
  --disallowedTools "WebFetch,WebSearch,Bash(curl:*),Bash(wget:*),Bash(gh:*),Bash(git fetch:*),Bash(git pull:*),Bash(git clone:*),Bash(pip:*),Bash(pip3:*),Bash(uv:*),Bash(npm:*),Bash(npx:*)" \
  -- "$PROMPT" > $B/logs/$NAME.jsonl 2> $B/logs/$NAME.err
echo $? > $B/logs/$NAME.exit; date -u +%FT%TZ > $B/logs/$NAME.end
