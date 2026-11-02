# Issue drafts: initialize echoes any protocolVersion — SENT 2026-10-06 from @Yahhi

Re-verified 2026-10-06: each server answered `"banana"` and `"2099-01-01"` with exactly the value sent.
Skipped: volo-knowledge (ai.flyvolo/knowledge) — its registry repo weihermans/VOLO no longer exists, so there is no channel.

## Common template

**Title:** `initialize echoes any protocolVersion back (e.g. "banana")`

**Body:**

Hi! I'm checking public MCP servers from the official registry for a few protocol-level issues: read-only, `initialize` and `tools/list` only, no tool calls. One thing showed up on {URL}:

```
curl -s -X POST {URL} \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"banana","capabilities":{},"clientInfo":{"name":"check","version":"1"}}}'
```
returns `"protocolVersion": "banana"` (same with `"2099-01-01"`).

The spec's [version negotiation](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle#version-negotiation) says the server answers with the requested version only if it supports it, and otherwise with a version it does support. Echoing tells a client on a newer revision that everything it expects is there, and it breaks later on features the server doesn't have.

{WHERE}

A small fix:
```js
const SUPPORTED = ['2025-06-18', '2025-03-26', '2024-11-05']; // only versions you actually implement
const requested = params.protocolVersion;
// in the initialize result:
protocolVersion: SUPPORTED.includes(requested) ? requested : SUPPORTED[0],
```

This is one of the checks in a short read-only checkup I run against my own MCP server; if it's useful, your agent can run the whole thing against yours: https://worklore.dev/s/2026-10-06-check-your-mcp-server-in-a-few-minutes-the-failures-real-cli

Feel free to close if the echo is intentional. Thanks for publishing the server!

## Per repository

| # | Repo | URL | {WHERE} |
|---|---|---|---|
| 1 | Agentic-Private-Office/fo-kg-door | https://mcp.familyofficeknowledgegraph.ai/mcp | It comes from [worker/mcp.js line 162](https://github.com/Agentic-Private-Office/fo-kg-door/blob/3ef2003ed3f0/worker/mcp.js#L162): `protocolVersion: (m.params && m.params.protocolVersion) \|\| SERVER.protocolVersion`. |
| 2 | TheNonduality/gregbenza-ai | https://gregbenza.ai/mcp/meet | It comes from [netlify/functions/meet-mcp.mjs line 78](https://github.com/TheNonduality/gregbenza-ai/blob/945593a9e151/netlify/functions/meet-mcp.mjs#L78): `protocolVersion: params.protocolVersion \|\| '2025-06-18'`. The same line is in `openhouse-mcp.mjs` (line 215), so that server likely has it too. |
| 3 | agent-bev/bev-door | https://mcp.bev-buyer.ai/mcp | The server code isn't in this repo, so I can't point at the line, but the usual cause is a handler that returns `params.protocolVersion \|\| <default>`. |
| 4 | bkrigmo1/robinhood-chain-x402 | https://x402-services-production.up.railway.app/mcp | same as #3 |
| 5 | CanaryUsers-ai/canaryusers-mcp | https://www.canaryusers.ai/api/mcp | same as #3 |

## Sent 2026-10-06 (re-verified "banana" echo right before sending)
- https://github.com/Agentic-Private-Office/fo-kg-door/issues/1
- https://github.com/TheNonduality/gregbenza-ai/issues/2
- https://github.com/agent-bev/bev-door/issues/1
- https://github.com/bkrigmo1/robinhood-chain-x402/issues/2
- https://github.com/CanaryUsers-ai/canaryusers-mcp/issues/1
