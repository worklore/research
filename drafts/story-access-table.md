---
title: "One table decides what answers without a token: how I stopped re-deciding auth tool by tool"
date: 2026-10-06
tags: mcp, authorization, api-design, testing, oauth
type: success
status: n/a
reproducible: true
stack: Python 3.12 on AWS Lambda; remote MCP server (Streamable HTTP) plus a REST API; the pattern is language-agnostic
agent: Claude Code
model: claude-opus-5-5
---

# One table decides what answers without a token: how I stopped re-deciding auth tool by tool

In plain words: every endpoint of a server answers one question, "may a stranger without an account use this?" If you answer it separately each time you add something, the answers drift apart, and nothing tells you.

That's what happened to my MCP server over two weeks. First the whole endpoint sat behind a login, tool list included, without my ever deciding that, so a directory showed my server with no tools. I opened the tool list. Search still required signing in, although a stranger could only ever get public stories from it. Then I ran my own read-only checkup against the live server, and it found something I hadn't: `initialize` told every client "I have resources", and `resources/list` answered those same clients with 401. Each decision had been made in a different place: a list of public method names in the MCP handler, checks inside individual REST handlers, and the reasoning in the README.

The fix was not another decision but a place to keep them. I wrote the rule down once: anyone can search and read public stories without signing in; private stories and every write need a sign-in. Then one table in the code says, for every MCP method, every tool and every REST route, whether it's public, needs sign-in, or is admin-only, with a one-line reason. Both the MCP handler and the REST router read their decisions from it. Anything missing from the table counts as sign-in.

What makes it stick is the test: if a tool or a route has no entry, the build fails. The next time I add a tool, the question gets answered when the tool is written, by the rule, not weeks later by a confused client. A readable manifest is generated from the same table, and the deploy probes the live MCP server without a token and compares the answers with it.

The result: search and reading work in any MCP client without signing in, writes still need one, and a private story answers exactly like a missing one. 28 more tests. The next tool I add will have to answer the question the day it's written.

## Reproduce this

Prerequisites: a server with a mix of public and signed-in endpoints (an MCP server, a REST API, or both), a test suite, and one place every request passes through before it runs.

Your agent will need from you: the access rule in one or two sentences (what a stranger may do, what needs an account, what is admin-only), and the list of edge cases you already know about, such as anonymous actions that act as nobody (a like, a report form) or sign-in endpoints, which must be public by necessity.

Steps:

1. Write the rule down in plain words first. Classify by what the endpoint touches, not by habit: reads only public data → public; private data, any write, anything that acts as a person or is per-user → sign-in. Something that costs you resources on a stranger's behalf (for example, fetching an arbitrary URL from your server) counts as sign-in.
2. Inventory every entry point from the code, not from memory: each protocol method (`initialize`, `tools/list`, `resources/list`, `tools/call`, …), each tool, each REST route with its HTTP method. For tools whose risk depends on an argument, note the condition (my capability checker is public with pasted text and needs sign-in with a `url`).
3. Create one module holding a table: entry point → level (`public` | `auth` | `admin`) + a one-line reason. Make the default for anything unlisted `auth`.
4. Make every gate read from the table: the MCP handler (which methods and tools answer without a token), the REST router (check access before running a handler). Delete the old scattered lists and per-handler checks so there is no parallel copy.
5. Keep a second check inside every write path, so a request that somehow passes the outer gate without a token is still refused before it runs.
6. Run anonymous reads through your single visibility rule: without a token, public data only; a private item must answer exactly like a missing one, so nothing can be probed.
7. A batch of JSON-RPC messages is public only if every message in it is public; otherwise the whole batch needs a token.
8. Add the guard test: enumerate the tools your server lists and the routes your router knows, and fail if any has no table entry.
9. Generate a human-readable manifest (for example `docs/ACCESS.md`) from the table, with a test that fails when the generated file is stale.
10. If you publish your server's surface (a registry entry, a version), record which methods and tools answer without a token as part of that surface, and bump the version when it changes.

Verify:

- With no `Authorization` header, a public read tool returns public data, and a private item's id returns the same answer as a nonexistent id.
- With no token, every write tool answers 401 with a `WWW-Authenticate` header, and a batch that mixes a public method with a write is refused.
- Add a dummy tool without a table entry: the test suite fails. Remove it: it passes.
- Edit the table without regenerating the manifest: the test suite fails.
- After deploy, an anonymous probe of the live server matches the table.
