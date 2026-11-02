---
title: "Benchmark your MCP server in Claude Code, Codex and Gemini: one fake server, its call log as the judge"
date: 2026-10-07
tags: mcp, benchmarking, claude-code, codex, gemini, evaluation
type: success
status: n/a
reproducible: true
stack: Any MCP server design (tool count, grouping, naming); a Python stdlib fake server over stdio; Claude Code, Codex CLI and Antigravity CLI on their own subscriptions
agent: Claude Code
model: claude-opus-5-5
---

# Benchmark your MCP server in Claude Code, Codex and Gemini: one fake server, its call log as the judge

In plain words: before you decide how many tools your MCP server should have, whether to group them, or how to name them, you can test the decision on the clients your users actually run, instead of trusting the advice. The catch is that the three big clients don't show your tools to the model the same way, so the same server costs and behaves differently in each.

It started with a dev.to post arguing that 6 grouped tools beat 26 separate ones. Its measurement compared a server against no tools at all, not tool counts, so I measured that myself: one fake server exposing 5 to 100 file tools plus a grouped variant, 18 tasks with known answers, three clients on my own subscriptions, 1,404 runs. The kit is public: [worklore-mcp/research/tools-count](https://github.com/worklore/worklore-mcp/tree/main/research/tools-count).

The hard part wasn't the server. It was the clients, and almost none of it is documented:

- **Each client loads tools differently.** Claude Code defers MCP tools by default and finds them with its `ToolSearch` built-in; with tool search off it sends every tool's full schema on every model call (linear: +169 tokens per tool). Codex in code mode keeps schemas out of the prompt; the model searches them with code. Antigravity sends only names and reads each schema from a cache file on demand.
- **Isolation flags can change what you measure.** My first Claude Code runs used `--tools ""` to switch off the shell, and that also switched off `ToolSearch`, so every schema loaded upfront: 20.3k first-call tokens at 100 tools instead of 5.5k by default. Allow the search built-in (`--tools "ToolSearch"`) unless you mean to test the no-search case.
- **Isolation is per client.** Antigravity needs a workspace plugin and a custom agent, and if that agent file's header is invalid it silently falls back to the default agent, which has a shell.
- **The judge must be the server's own call log**, never the model's "done".
- **Fake tools must keep state.** In my pilot, an info tool still reported the old size after a resize, and the models fell into verify-and-retry loops.
- **Subscriptions run out.** Codex stopped after about 300 runs, Gemini later; the runner had to resume after each reset.
- **Two traps I only found by measuring:** the Gemini API rejected tool schemas with integer enums, and at 100 tools Codex's own output cap truncated its tool search.

What came out: accuracy held at 100% for separate tools up to 100, and the cost depended on the client, not the model. That's for the article. This story is the method, and you don't need a real server to use it: the fake one is built from the tool list you're planning, so you can test a design before writing any of it.

## Reproduce this

Prerequisites: Python 3; `jq`; at least one of Claude Code (`claude`), Codex CLI (`codex`) and Antigravity CLI (`agy`), each signed in with its own subscription; the list of tools your server exposes or plans to (names, descriptions, input schemas).

Your agent will need from you: your tool list; 10–20 tasks a real user would give, written as a user would say them, each with the tool calls and key arguments you consider correct (include ambiguous ones, where a look-alike tool is tempting); which design variants to compare (tool counts, a grouped version, renamed tools); which clients to test; a run budget (how many hours, how many repetitions).

Steps:

1. Start from the kit: fetch `server.py`, `tasks.json`, `run.sh`, `score.py` and `analyze.py` from https://github.com/worklore/worklore-mcp/tree/main/research/tools-count. Read them with the user before running anything, and say plainly what the runner does on this machine: it launches each CLI with permission prompts skipped (safe only because the fake server is the only tool), deletes its own run and temp folders, moves Codex session files out of `~/.codex/sessions` into the results, and clears Antigravity's MCP schema cache. Its capability tier is T3 for those reasons; change any of it before running if the user prefers.
2. Replace the fake tool pool in `server.py` with your real tool names, descriptions and input schemas. Keep every tool fake: no file, network or account access; each returns a plausible deterministic result and appends `{tool, args, result}` to the call log named by `TC_LOG`.
3. Keep per-run state in the fake server, so a read-back tool agrees with earlier edits (after a resize, the info tool reports the new size). Without this, agents retry forever.
4. Make each design variant selectable by an environment variable (`TC_VARIANT`). For tool-count sweeps, always expose the task's needed tools and fill the rest with distractors in one fixed seeded order, so each size is a superset of the smaller one.
5. Write `tasks.json`: the user-style prompt, the expected calls in order, and the key arguments to check. Never put this file next to the server the agents run: copy the server to a neutral path and pass only the needed tool names (`TC_NEED`).
6. Run each case in a fresh temporary folder, with secrets unset, using exactly one MCP server and no built-in shell or file tools. The kit's `run.sh` has working flags for Claude Code 2.1.x (`--strict-mcp-config --mcp-config …`, with `--tools "ToolSearch"` for the default deferred loading or `--tools ""` to test loading everything upfront), Codex CLI 0.160 (`--ignore-user-config`, `-s read-only`, the built-ins disabled, `-c mcp_servers.<name>…`) and Antigravity 1.2.x (a workspace plugin holding `mcp_config.json`, plus a custom main agent whose only built-in is `view_file`, which lazy schemas need). Check each CLI's `--help` first: flags change between versions.
7. Prove the isolation before trusting any number: one probe run per client asking the model to list its tools must name only your server's tools; in Antigravity, a run with zero calls to `view_file` outside the schema cache confirms the custom agent loaded.
8. Pilot on one client with three sizes or variants and one repetition. Check: every task passes at the smallest size (if not, the task is wrong, not hard); tokens move the way the client should make them move; read three transcripts end to end. Fix and re-pilot until clean.
9. Run the full grid with a resumable runner (skip finished cases), at most two parallel runs per CLI. On a usage-limit error, stop that client's lane, note the reset time, and resume after it; never let a missing run pass as a failure.
10. Score only from the call logs (right tools, order for chains, key arguments, wrong or extra calls) and record tokens, time and cost from each client's own output. Plot accuracy and input tokens against each variant, per client.

Verify: each client's probe run lists only your server's tools; every task passes at the smallest size; every score in the results comes from a call log, not from the model's final message; for Claude Code with `--tools ""`, first-call input tokens grow by roughly a fixed amount per added tool (if they don't, the server isn't the only thing in the prompt); with `ToolSearch` allowed they should stay nearly flat.
