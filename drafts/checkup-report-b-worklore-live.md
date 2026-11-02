# Checkup run (b): live https://worklore.dev/mcp, no token, read-only

Run 2026-10-06 with `claude -p` (claude-opus-5-5; MCP servers, hooks and slash commands off; WORKLORE_TOKEN unset), no token, no source, registry name given. Wall time 154 s, about 20 requests, all tools/call refused with 401 before any tool ran. The agent's final report, verbatim:

## Checkup report: `https://worklore.dev/mcp` (`io.github.worklore/worklore`)

I sent about 20 requests, one at a time, with no `Authorization` header: `initialize` (×4, one with "banana"), `notifications/initialized`, `ping`, `tools/list`, `resources/list`, `prompts/list`, and 5 `tools/call` requests to read-only tools only (`get_story`, `search_stories`) plus one made-up tool name. Every `tools/call` was refused with 401 before reaching a tool, so nothing ran on the server. I made one registry GET. No write tool was called and nothing was recorded on worklore. My helper files in `/tmp/ck` have been deleted.

| # | Check | Result | Evidence |
|---|---|---|---|
| C1 | Tool list answers without a token | **PASS** | `initialize` → 200, JSON, no `Mcp-Session-Id`. `notifications/initialized` → 202. `ping` → 200 `{"result": {}}`. `tools/list` → 200 with **7 tools**: 4 marked `readOnlyHint: true` (`check_capability`, `get_story`, `search_stories`, `suggest_for_project`) and 3 marked as writing (`report_reproduction`, `publish_story`, `edit_story`). All 7 declare an `outputSchema`. |
| C2 | A tool refusal comes back as a result | **NOT CHECKED** | Every `tools/call` → **401** `{"error": "authentication required", "authorization_servers": ["https://worklore.dev"]}` with `WWW-Authenticate: Bearer resource_metadata="https://worklore.dev/.well-known/oauth-protected-resource"`. That happened for a slug that doesn't exist, a missing `slug`, and an unknown tool name alike. The login check runs before any tool code, so I couldn't see how the server refuses. |
| C3 | The session survives an error | **NOT CHECKED** | A valid `search_stories {"query":"mcp"}` → 401, same reason. Note: the server issues no session ID, so it appears to be stateless. |
| C4 | The published outputSchema is honoured | **NOT CHECKED** | I saved the schemas from `tools/list`, but couldn't get any result to check them against (401). |
| C5 | Results survive serialisation | **NOT CHECKED** | No tool results. Every body I did receive (200, 202 and 401) was valid JSON. |
| C6 | The version moves when the surface moves | **PASS (registry part) / lock NOT CHECKED** | Live `serverInfo.version` = **0.3.0**. Registry lists 0.1.0, 0.2.0 and **0.3.0 (`isLatest: true`, published 2026-09-30)**, so they match. Surface fingerprint (initialize without version + tools/list, sorted keys, SHA-256): `3b9c6da788bfa2a35df4b0db10c28e769f9864e99b9da80d20c5c8ec0418e776`. resources/prompts are left out because they returned 401. Without the source I can't tell whether a committed surface lock exists. |
| C7 | Calls are logged | **NOT CHECKED** | I have no source and no logs. |
| C8 | Tool count and names | **PASS** | 7 tools, and all names match `^[a-zA-Z0-9_-]{1,64}$`. |
| C9 | Version negotiation is honest | **PASS** | `"protocolVersion": "banana"` → 200, answered `"2025-06-18"`. I also tried `2025-11-25` → `2025-06-18`: the server offers the version it implements instead of copying whatever the client asks for. |

**Verdict: doesn't have it.** That covers only what I could check. No row is FAIL, but 5 of the 9 checks (C2–C5, C7) and the lock half of C6 couldn't be run. That leaves out the most serious failures in the guide (refusals coming back as protocol errors, schema mismatches, serialisation leaks), so this is not a clean bill of health.

### Side observation (not one of the nine checks)
- `initialize` advertises `capabilities.resources`, but `resources/list` returns **401** without a token. Prompts aren't advertised, and `prompts/list` also returns 401. A client that trusts the advertised capability and lists resources will hit a login it wasn't expecting. That's fine if it's deliberate, but it's worth a sentence in the docs or listing.

### What couldn't be checked and what would unlock it
- **C2, C3, C4, C5** need a **bearer token** the server accepts, read from an environment variable. The 401 points to OAuth via `https://worklore.dev/.well-known/oauth-protected-resource`. With a token, the 4 read-only tools are safe to call. For C2 I'd use `get_story` with a made-up slug and with `slug` missing.
- **C6 lock** needs **read access to the server's source**, to look for a committed version + surface-hash file checked by a test. The registry entry names `https://github.com/worklore/worklore-mcp` as the repository. I didn't open it because you said I have no source access. If it's public and it really is the server's source, saying so would unlock this check.
- **C7** needs **the source** (to find the single place every JSON-RPC call passes through and check its per-call logging) **or log access** (to look for the requests from this run, around 2026-10-06).
