# Checkup run (a): deliberately broken local server

Run 2026-10-06 with `claude -p` (claude-opus-5-5; MCP servers, hooks and slash commands off; WORKLORE_TOKEN unset) against research/drafts/broken_mcp_server.py on 127.0.0.1:8791, token available, source in ./server/. Prompt = task + the story draft (research/drafts/run_checkup.sh). Wall time 39 s. All seven planted failures were found, each with the right story link; the one thing the server does right (C3) passed. The agent's final report, verbatim:

The server is closed and has the problem: 6 of the 9 checks FAIL, 1 is a warning that counts as a FAIL, 2 pass, and none are NOT CHECKED. I used your token for everything after C1.

## Checkup report: `broken-shop` at `http://127.0.0.1:8791/mcp`

| # | Check | Result | Evidence | Fix |
|---|---|---|---|---|
| C1 | Tool list answers without a token | **FAIL** | No `Authorization` header: `initialize` → **HTTP 401** `{"error": "authentication required"}`; `tools/list` → **HTTP 401**, same body. With the token: 200, **3 tools** (`get_item`, `search.items`, `delete_item`). In the source, every POST checks the token before it reads the method. | [My MCP server hid its own tool list behind a login](https://worklore.dev/s/2026-09-27-my-mcp-server-hid-its-own-tool-list-behind-a-login) |
| C2 | A tool refusal comes back as a result | **FAIL** | `get_item {"id":"does-not-exist-zz9"}` → HTTP 200, `"error": {"code": -32602, "message": "item not found: does-not-exist-zz9"}`. `get_item {}` → HTTP 200, `"error": {"code": -32602, "message": "missing required argument: id"}`. Neither came back as a `result` with `isError: true`. | [My live MCP test asserted the bug](https://worklore.dev/s/2026-10-02-my-live-mcp-test-asserted-the-bug-a-real-client-threw-where-) |
| C3 | The session survives an error | PASS | Same session (`Mcp-Session-Id: sess-1`), right after the two refusals: `search.items {"q":"mug"}` → 200, `structuredContent: {"count": 1, "ids": ["a1"]}` | — |
| C4 | The published outputSchema is honoured | **FAIL** | `get_item {"id":"a1"}` is a valid call but came back `isError: true`, `"error: Object of type Decimal is not JSON serializable"`, with no `structuredContent`. `search.items {"q":""}` passed: `{"count": 2, "ids": ["a1","b2"]}` matches its schema (count is an integer, ids is an array of strings, both required fields present). One tool failing is enough for FAIL. | [My tests passed because they agreed with me](https://worklore.dev/s/2026-09-28-my-tests-passed-because-they-agreed-with-me) |
| C5 | Results survive serialisation | **FAIL** | Every body parsed as JSON, and where `structuredContent` existed the `content` text matched it. But `get_item` returned the text "Object of type Decimal is not JSON serializable": the database's `Decimal` type (in `price.amount`) is leaking into the response. | Same story as C4 |
| C6 | The version moves when the surface moves | **WARN → FAIL** | `serverInfo.version` = `1.2.0`. Fingerprint (initialize result without version, plus tools/list, sorted keys, SHA-256): `9d51968ce78217f30e5f40d258a01337353a4e0e6dd466b1eba00b78b5de3e5b`. `resources/list` and `prompts/list` answered -32601, so they are not in the fingerprint. The server isn't in the Registry, so I had nothing to compare the version against. No surface lock: `./server/` contains only `broken_mcp_server.py`, with no lock file and no test. | [My MCP listing said read-only. My server could write.](https://worklore.dev/s/2026-09-30-my-mcp-listing-said-read-only-my-server-could-write) |
| C7 | Calls are logged | **FAIL** | Source: the request handler's `log_message` is overridden to `pass`, and `handle_rpc` (the place every call goes through) writes nothing. So the server keeps no per-call log, not even an HTTP access log. | [Your MCP server is one URL — getting per-tool, per-user analytics anyway](https://worklore.dev/s/2026-09-23-your-mcp-server-is-one-url-getting-per-tool-per-user-analyti) |
| C8 | Tool count and names | **FAIL** | 3 tools. `search.items` has a dot, so it does not match `^[a-zA-Z0-9_-]{1,64}$`. `get_item` and `delete_item` are fine. | [An MCP server for the price of one more endpoint](https://worklore.dev/s/2026-09-25-an-mcp-server-for-the-price-of-one-more-endpoint) (step 1); [Submitting an MCP server to the directories](https://worklore.dev/s/2026-09-23-submitting-an-mcp-server-to-the-directories-one-cli-one-gith) |
| C9 | Version negotiation is honest | **FAIL** | `initialize` with `"protocolVersion": "banana"` → HTTP 200, `"protocolVersion": "banana"`. The server echoes whatever version it is sent. | [An MCP server for the price of one more endpoint](https://worklore.dev/s/2026-09-25-an-mcp-server-for-the-price-of-one-more-endpoint) (Verify section) |

**Result: has the problem** (C1, C2, C4, C5, C7, C8 and C9 are FAIL, and C6 is WARN, which counts as FAIL).

**Not checked:** nothing. The only gap is C6's registry comparison: the server isn't in the MCP Registry, so there was nothing to compare against. That part would only become possible once the server is listed.

**How the rules were kept:**
- **Read-only:** I called only `get_item` and `search.items`, both marked `readOnlyHint: true`. I never called `delete_item`.
- **No edits:** I edited no files in `./server/`. The only file I wrote was a scratch script in `/tmp`. The work directory is not a git repository, so I couldn't run `git status`.
- **Token:** it was read from `BROKEN_MCP_TOKEN` into the header and never printed.
- **Not recorded:** I didn't record anything in worklore or with MCP tools.
