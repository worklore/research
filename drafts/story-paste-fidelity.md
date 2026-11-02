---
title: "Cut Claude Code token cost 4×: let your MCP tool take a URL instead of the pasted file"
date: 2026-10-15
tags: [mcp, token-costs, claude-code, tool-design, tool-calls, benchmark]
type: success
status: n/a
reproducible: true
stack: Any MCP server with a tool that takes long text or data (hosted or local); measured with Claude Code, Codex CLI and Antigravity
agent: Claude Code
model: claude-opus-5-5
---

# Cut Claude Code token cost 4×: let your MCP tool take a URL instead of the pasted file

When an agent gives a tool a long piece of text, the model usually types that text out again as the tool's argument. Arhan Canli found his agent passed 756 numbers and only 500 arrived, with no error, and fixed it by accepting a file path ([his article](https://dev.to/arhancanli/my-agent-kept-dropping-numbers-when-it-copied-data-into-a-tool-call-a-file-path-fixed-it-46gf)).

My MCP tool `check_capability` takes a skill's text and says what that skill can do. I measured how agents feed it: 8 public skills from [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (1.2 to 75 KB), three agents, three runs each, with a proxy logging exactly what arrived.

The copies were mostly exact, and that was the surprise: the problem was cost. Claude Code (Opus 5.5) typed out the 75 KB skill every time: 27,600 output tokens, $1.03 and over three minutes per check. Gemini 3.8 Flash changed a final newline in 3 of 3 runs on one file, so the check described a slightly different file, and on the 75 KB file it never managed a check at all. Codex never copied: its code mode read the file into a variable and passed that.

My server is hosted, so it can't read a path on the user's disk. Most skills come from GitHub, though, so I let the tool take a GitHub link without sign-in. I also made it report what it actually scanned (size and a plain sha256), refuse files that are too big instead of cutting them, and accept the hash the caller expects, returning an error on a mismatch.

Then I ran the same 72 runs again, telling the agent where the skill was downloaded from:

- Claude Code passed the link in 24 of 24 runs. The 75 KB check went from $1.03 to $0.25, and from 187 to 21 seconds.
- Gemini Flash used the link first in every run and finished the 75 KB check it had failed 3 of 3 times before.
- Codex kept its own way and sent the hash it computed in its shell in 48 of 48 runs.

The hash check helps less than I hoped. An agent can only send the right hash if it can compute it. Gemini took hashes from my server's earlier answers, which caught 4 changed copies when the earlier answer came from the link, and still let a few changed copies through when no hash was sent.

## Check if this applies to you

Applies if: you run an MCP server (hosted or local) whose tools agents call. Does not apply if you only use other people's servers.

Read-only steps:
1. Get your server's tool list (`tools/list`, or the tool definitions in your source).
2. For every tool, list the parameters that carry bulk content rather than a choice: a string meant for a document, file, page or code (names like `text`, `content`, `body`, `markdown`, `code`, `csv`, `data`), or an array of many values.
3. For each such tool, check whether it also accepts a reference to the same content: a file path, a URL, or an ID your server can resolve.
4. Ask the human (or look at real calls in your logs) how big the content usually is.

Has the problem: a tool takes bulk content, has no reference option, and real inputs are over a few KB, or anything is lost silently (the tool cuts long input instead of refusing it).
Doesn't have it: every bulk input has a reference option, or real inputs are small.

Change nothing while checking.

## Reproduce this

Prerequisites: an MCP server you can change, with at least one tool that takes bulk content (see the check above); a few real inputs of different sizes, including one over 50 KB.

Your agent will need from you: which tool to fix; where that content usually lives (the user's disk, GitHub, your own storage); whether your server runs locally (it can read paths) or hosted (it cannot); which hosts you are willing to fetch from without sign-in.

Steps:

1. **Add a reference input next to the content input**, without removing the old one. Local server: a file path, read on the server (Arhan's fix). Hosted server: a URL, limited to hosts where that content really lives, with an allow-list. If anonymous users may use it, fetch only from those hosts and refuse a redirect that leaves them. For GitHub, turn a `github.com/…/blob/…` page link into its `raw.githubusercontent.com` file.
2. **Refuse instead of truncating.** Read one byte past your size limit; if the content is bigger, return an error that says so. A partial input must never get a normal answer.
3. **Report what arrived** in every result: bytes, lines and a plain sha256 of the exact bytes you processed, the same value `shasum -a 256 FILE` gives. If you already return a hash computed differently, keep it and add this one.
4. **Accept the hash the caller expects** (`expected_sha256`). If it doesn't match what arrived, return an error result (`isError: true`, not a JSON-RPC error, so the model reads it) naming the hash and size that arrived, and process nothing.
5. **Say it in the tool description**: prefer the reference; when pasting, also send the file's sha256. Agents follow the description: in my runs Claude Code switched to the link as soon as it had one.
6. Keep the change additive (new optional parameters, new result fields), so clients that cached the old tool definition keep working. Bump your server version if you publish one.

Verify:
- A call with a reference to your 50 KB+ input reports a sha256 equal to `shasum -a 256` of the file.
- The same content with its last character removed, sent as text with the original file's hash, returns an error and is not processed.
- An input over your size limit returns an error, not a result.
- If you allow-listed hosts: a URL on another host is refused (or needs sign-in), and so is a redirect from an allowed host to another one.
- Run one real agent headless with a prompt that mentions where the file comes from, and check your server log: the call carries the reference, not the content.

My runs, scripts and all 216 transcripts: [research/paste-fidelity in worklore-mcp](https://github.com/worklore/worklore-mcp/tree/main/research/paste-fidelity). The fix in my server: [worklore MCP 0.7.0](https://github.com/worklore/worklore-mcp).
