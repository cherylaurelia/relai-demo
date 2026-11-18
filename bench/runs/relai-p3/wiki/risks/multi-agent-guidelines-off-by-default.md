# Shipped multi-agent task disables guideline review

Mechanism: multi_agents/task.json:11 sets `follow_guidelines: false` while listing guidelines (APA, hyperlinks, Spanish); reviewer.py:70-80 skips review and writer.py:60 omits guidelines when false. README example sets it true.
Trigger: Running the multi-agent pipeline with the default task.json.
Observable failure: Report ignores the listed guidelines (for example written in English, not Spanish) with no review pass.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: multi-agent-follows-guidelines, write-in-requested-language
Found at: fae2317 (agent: multi_agents)
Evidence: multi_agents/task.json:11-17; multi_agents/agents/reviewer.py:70-80; multi_agents/agents/writer.py:60; multi_agents/README.md:91
