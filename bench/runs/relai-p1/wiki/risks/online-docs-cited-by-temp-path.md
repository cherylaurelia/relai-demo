# Online documents are cited by temporary file path

Mechanism: `OnlineDocumentLoader` downloads each document into a `NamedTemporaryFile` and loads it by path, so `source` is `/tmp/tmpXXXX.pdf`. The file is then deleted. Local files are cited by basename only.
Trigger: `document_urls` in hybrid mode.
Observable failure: Citations point at temporary files that no longer exist, and the original URL is lost.
Impact: medium. Confidence: high. Triggerability: medium.
Status: proposed
Threatens: references-list-used-sources
Found at: 0595cd3 (agent: gpt-researcher)
Evidence: gpt_researcher/document/online_document.py:28,48-52,85; gpt_researcher/document/document.py:55

## Probes

None yet.
