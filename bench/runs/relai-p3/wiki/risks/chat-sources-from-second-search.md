# Chat shows sources from a second search, not the one the model read

Mechanism: After the model's tool-using answer, chat.py:170-176 calls quick_search again to get metadata; results may differ, and on tool errors utils/tools.py:206-227 retries without tools and may answer current-events questions from memory without telling the user.
Trigger: Any chat turn that uses search.
Observable failure: Displayed sources do not match what the answer was based on; doubled search cost.
Impact: medium. Confidence: high. Triggerability: high.
Status: proposed
Threatens: cite-only-provided-sources
Found at: fae2317 (agent: backend chat)
Evidence: backend/chat/chat.py:170-176; gpt_researcher/utils/tools.py:188-227
