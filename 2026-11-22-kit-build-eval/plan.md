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

Each change below was made after the first real run (the two pilot runs, 00:46). After every grader
change all affected runs were regraded from their saved final workspaces, so every number in
results.md comes from the final graders. The controls (`controls.out`) were rerun after each change:
the untouched project still fails every check, the reference solution still passes every check, and
the trap solutions still fail their trap checks.

1. **Two pilot runs before screening** (`p-t3-kit-haiku-r1`, `p-t1-none-deepseek-r1`, 00:46) to test
   the pipeline end to end. They are not counted, and nothing was changed because of them.
2. **Grader: the server is started from its real path** (01:09, after 12 screening runs). Several
   agents start the HTTP listener only when `import.meta.url` equals `process.argv[1]`. The grader ran
   the server from `/tmp/...`, which macOS resolves to `/private/tmp/...`, so the guard was false and
   the server exited: those runs failed T2 for the grader's reason, not theirs.
3. **Grader T2(a) and T2(c): a refusal can be an `isError` result** (01:48). Several agents refuse an
   anonymous write inside the tool (HTTP 200 with `isError: true`, and the write does not happen)
   instead of answering HTTP 401. Check (b) still requires 401, as the plan says ("refused with 401").
   Check (c) only says "refused", and (a)'s precondition "the server has sign-in" was refined before
   the first run to "an anonymous write is refused"; both had wrongly counted 401 against isError a
   second time. (c) now also checks that the refused writes had no effect.
4. **Grader T3(a): more ways of marking a failed call** (02:25). The grader recognised a failed call
   only from `ok: false` or a status equal to `error`/`fail`. Agents also wrote `outcome: "not_found"`,
   `outcome: "tool_error"`, `level: "warn"` with `event: "tool_error"`, or an `error` field. These mark
   the failure plainly and now count.
   **Consequence for the screening decision:** with the corrected grader, T3 passes both checks in both
   arms in both screening lanes, so by the keep rule it should have been dropped. It was kept on the
   uncorrected grader, and its full round had already run when the bug was found. Its full-round
   numbers are reported below as a ceiling (both arms pass), not as a result about the kit.
5. **Grader T1(b): the retry key respects the tool's input schema** (02:29). The grader filled a
   key-like argument (`id`, `requestId`, `idempotencyKey`...) with a fixed string. Two runs declared a
   format for that key, so even the first create was refused. The grader now picks the first of a few
   candidate values (a UUID first) that validates against the property's own schema, as a client that
   reads the published inputSchema would.
6. **Grader T1(c): spec defaults for annotations** (03:02). `delete_note` counted as destructive only
   with an explicit `destructiveHint: true`. The MCP spec's defaults make a tool that is not read-only
   destructive unless it says `destructiveHint: false`, and a client reads it that way. The check now
   uses the defaults; `list_notes` still needs an explicit `readOnlyHint: true`.
7. **T4 refusal plant** (grader detail fixed before the first run, recorded here because it shapes
   what T4 measures). In SDK 1.32.2, McpServer turns any exception in a tool handler into an
   `isError` result, so "a tool that throws instead of returning isError" is invisible to a client.
   The plant therefore throws the one error code the SDK passes through as a JSON-RPC error
   (`UrlElicitationRequired`): a refusal that reaches the client as a protocol error, which is the
   story's own failure ("a real client threw where my test passed").
8. **Scheduling.** The full round started at 01:38, before the last DeepSeek screening runs, for the
   four tasks whose keep condition was already met by finished cells (an observed none-arm failure
   cannot be undone by later runs). T4's drop was decided after the last screening run. The DeepSeek
   full lane started when its screening lane ended.
9. **Kimi web tools** were disabled with `[tools] disabled` in a scratch config rather than an agent
   file. An agent file replaces Kimi's system prompt with its own body; the config keeps the shipped
   prompt. This was decided before the first run; recorded because the coordinator's brief suggested
   an agent file.
