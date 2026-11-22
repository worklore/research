# Does a folder of MCP-server stories change what a coding agent builds?

Plan written 2026-11-22, before any run. It is committed to this public repository before the
first run, and the result will be published whatever it is. Changes made after the first run are
listed at the end under "Deviations", with the reason.

Disclosure: the folder under test is the worklore MCP Server Kit, which I (Valentina Koniukhova)
sell for $5 at https://worklore.dev/kits/mcp-server/. Every story in it is free to read on
worklore.dev. The kit page says a round like this one comes next and that its numbers will be
published there, whatever they are.

## The question

An agent can find notes on disk. The install round (`../2026-11-21-kit-install-offline/`) showed
that: after installing the kit, 24 of 24 fresh sessions opened its START-HERE.md before the first
edit. Finding is not applying. This round asks the second half:

> Given the same ordinary task, does an agent with the kit installed build an MCP server that
> passes checks it fails without the kit?

The checks are facts from the kit's stories that the official docs don't state, or state where an
agent won't look. Earlier rounds (worklore guide-eval 1 to 11) found that a story changes an
agent's result only when it carries such a fact; a story that retells the docs scores like no
story. So this round should show which stories carry a fact an agent applies, and which don't.

## Setup

- **Offline.** No network except the agent's own model API, with the fence from the install round
  (sandbox profile plus a logging proxy for Claude Code and Claude-Code-based lanes; Codex's own
  sandbox with network off). This makes the "no kit" arm clean: earlier rounds found agents
  without a story reading it through web search.
- **The project.** A small TypeScript MCP server ("notes": a few tools over a JSON file), with
  `node_modules` already installed (MCP TypeScript SDK, zod, typescript, a test runner), so the
  build and tests run offline. The install round saw offline agents lose minutes trying npm.
- **Arms.** `none`: the project as it is. `kit`: the same project after the reference install of
  the kit (folder at the root, the INSTALL.md block in AGENTS.md, and in CLAUDE.md). Nothing in the
  prompt mentions the kit.
- **The prompt** states the requirement in plain words, as a product owner would. It never names
  the trap.
- **Grading** is by hidden scripts after the run, on the final workspace: the agent never sees
  them. A check either passes or fails. Each grader is tested first on a reference solution
  (must pass) and on the untouched project (must fail).

## Tasks and checks

| task | prompt (short) | hidden checks | story the fact comes from |
|---|---|---|---|
| T1 tools | Add create/update/delete/list tools for notes, with output schemas. Clients may retry a call after a timeout: make that safe. | (a) a wrong-shaped output is rejected by each tool's output schema; (b) a retried create with the same request does not make a second note; (c) annotations match behaviour: list is read-only, delete is destructive, nothing that writes says read-only | "My MCP server's output schemas accepted wrong answers: 7 of 8 tools"; "I sent every write tool ... a second time, and 8 of 31 duplicated"; "My MCP listing said read-only. My server could write." |
| T2 auth | Add bearer-token sign-in to the HTTP transport: only signed-in users may change notes. | (a) initialize and tools/list answer without a token; (b) a write without a token is refused with 401; (c) a read-only tool decided to be public answers without a token, the rest are refused (one consistent rule) | "My MCP server hid its own tool list behind a login"; "One table decides what answers without a token" |
| T3 logs | Add logging so we can see in production which tools are used and how they fail. Don't log personal data. | (a) one structured line per tool call with tool name, ok/error and duration; (b) a canary value sent in a note body or an email-like field never appears in the logs | "Your MCP server is one URL: getting per-tool, per-user analytics anyway"; "A canary read back from the log store found the one field my masker skipped" |
| T4 tests | Add tests that prove the server works for real MCP clients. | the grader plants client-visible defects one at a time (structured output that doesn't match the output schema; a tool that throws instead of returning isError; a missing tool in tools/list) and counts how many the agent's own tests catch | "My tests passed because they agreed with me"; "My live MCP test asserted the bug: a real client threw where my test passed" |
| T5 publish | Prepare the server for the official MCP Registry. | server.json valid against the registry schema shipped offline in the grader; description within the limit; name in the io.github.<owner>/ namespace; version equal to package.json; package.json carries the matching mcpName; README says what the publishing token needs | "Getting into the MCP Registry: server.json, a read:org token, and why listed is not discoverable" |

## Agents

| lane | agent | model | why |
|---|---|---|---|
| haiku | Claude Code | claude-haiku-5-5 | small fast model; screening |
| sonnet | Claude Code | claude-sonnet-5-5 | strong model people use daily |
| codex | Codex CLI | gpt-6.1-sol, low effort | a different vendor's agent |
| deepseek | Claude Code with the DeepSeek Anthropic-compatible API | deepseek flash | open-weight model; screening; cheap |
| kimi | Kimi Code | K3.1 | open-weight model in its own agent |

The open-weight lanes are here for a specific reader: people who can't or won't send code to the
big US vendors (blocked regions, privacy rules, cost), and who run an open model in a coding
agent. Gemini is left out: the install round found its search still answers through the model
connection, so it can't be made offline.

## Steps

1. **Screening** (her standing rule: keep only what changes a weak model's result). haiku and
   deepseek, every task, both arms, 2 runs each: 40 runs. A task goes into the full round when the
   kit arm passes at least one check more often than the none arm in either lane, or when the none
   arm already fails a check (a ceiling of 100% in both arms means nothing to measure). Screening
   results are published with the round, including dropped tasks.
2. **Full round.** The kept tasks, all five lanes, both arms, 3 runs each (up to 150 runs). Lanes
   run in parallel, one run at a time per lane.
3. **Grade, table, write-up.** Per check: passes with the kit vs without, per lane. Also: did the
   agent open the kit, and which story; did the run that opened the story pass that story's check.

## What would count as a result

- The kit helps where its stories carry an undocumented fact: kit-arm pass rate clearly above the
  none arm on that check, in more than one lane.
- No difference on a check means that story does not change what an agent builds; it gets fixed or
  leaves the kit.
- The agent opened the story and still failed the check: the story doesn't say the fact plainly
  enough. That is a finding about the writing, reported as such.
- With 3 runs per cell this is a small sample. Differences of one run are reported as noise.

## Not measured

Code quality beyond the checks, cost, and whether the server would pass a directory's human
review. Agents online (with web search) are a different question.

## Deviations

(none yet)
