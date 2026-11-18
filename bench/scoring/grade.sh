#!/bin/zsh
# usage: grade.sh <anon> <model>
cd ~/scratch-relai/bench/scoring
P=$(sed "s/RISKS_FILE/risks_$1.md/" grade_prompt.txt)
timeout 1800 claude -p --setting-sources project --model $2 --allowedTools "Read" -- "$P" 2>/dev/null | grep '"bug"' | sed 's/^```json//' > grades_$1_$2.jsonl
echo "$1 $2 $(grep -c '"match": *true' grades_$1_$2.jsonl)/$(wc -l < grades_$1_$2.jsonl)"
