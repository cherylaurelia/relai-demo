# Human plan feedback is applied unless the human replies "no"

With `include_human_feedback`, the planner revises the outline from any feedback other than an explicit "no".

Source: prompt to the human `multi_agents/agents/human.py:25` ("If not, please reply with 'no'"); `multi_agents/README.md`.
