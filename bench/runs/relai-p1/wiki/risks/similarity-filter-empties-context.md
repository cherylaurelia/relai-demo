# Similarity threshold can filter out all relevant chunks

Mechanism: The configured `SIMILARITY_THRESHOLD` of 0.42 is applied to cosine similarity between a short query and 1000-character chunks. With some embedding models, scores for relevant chunks can fall below it, so `EmbeddingsFilter` returns nothing. At most 10 chunks per sub-query reach the writer, and pages are truncated at 50000 characters with no log.
Trigger: Non-OpenAI embedding models (Ollama, HuggingFace), terse queries, or long PDFs whose key facts appear late.
Observable failure: The context is empty or thin, so the agent abstains or writes an under-grounded report. Late-document facts are missed.
Impact: medium. Confidence: medium. Triggerability: medium.
Status: proposed
Threatens: cites-only-provided-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/config/variables/default.py:6; gpt_researcher/context/compression.py:123,135,188; gpt_researcher/context/retriever.py:13,29. Score distributions are unmeasured.

## Probes

None yet.
