# Is defending against instructions in retrieved content a requirement?

Unclear: maintainers decided the backend is operator-run with no built-in auth
(`ISSUE_BACKLOG.md`, Bucket A session log), but that decision covers who can call the server, not
web pages, documents or MCP results that the agent reads for any user.

Why it matters: decides whether [prompt-injection-from-retrieved-content](../risks/prompt-injection-from-retrieved-content.md)
gets adversarial tests and whether a mitigation is expected.

Recommended: yes for web-retrieved content (any public page can reach the prompt); test with a
planted instruction page.
