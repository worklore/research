# Kit build round: does a folder of MCP-server stories change what an agent builds?

The spec is `plan.md`, committed before any run (commit 5941d3d), with every later change under
"Deviations". The results are in `results.md`, and the full tables are in `results-table.md`
(built by `make_table.py`).

## Layout

| Path | What |
|---|---|
| `plan.md` | the plan, written and committed before the first run; Deviations at the end |
| `fixtures/notes/` | the project: a TypeScript MCP "notes" server (5 tools over a JSON file, stdio `src/index.ts` and stateless Streamable HTTP `src/http.ts`), one store test. `node_modules` is installed here once and cloned into each run (not committed) |
| `fixtures/t1-overlay/` | T1 starts from the same project with only `get_note` registered (the store already has the other operations) |
| `prompts/` | the five task prompts and the common suffix, verbatim; `verify.txt` is the offline check |
| `make_ws.sh` | builds one run's workspace: fixture (+ T1 overlay), cloned `node_modules`, the kit for the kit arm (`canon_install.py`, the install round's reference install: folder at the root plus the INSTALL.md block in AGENTS.md and CLAUDE.md), and git init with one commit |
| `run.sh` | one run: `run.sh <s\|f> <t1..t5> <none\|kit> <lane> <rep>` |
| `lane.sh`, `supervise.sh` | one lane (one run at a time), and all lanes in parallel; a lane that hits a quota limit is resumed 45 min later, at most 6 times |
| `graders/` | the hidden graders (`t1.mjs` ... `t5.mjs`, `lib.mjs`), run by `grade.py` on a copy of the final workspace, outside it, under `grader.sb` (no network except localhost). `schema/` holds the registry's server.json schema for T5 (below). `kitreads.py` reads the transcript to find which kit files the agent opened |
| `refs/` | reference solutions (every check must pass) and `refs/traps/` (a plausible solution that falls into the trap; its trap checks must fail). No kit text |
| `controls.sh`, `controls.out` | the proof: untouched fixture fails every check, the reference passes every check, the trap fails its trap checks |
| `offline/` | the network fence: `setup.sh` (agent PATH without the hidden tools, empty ZDOTDIR, sandbox profiles), `proxy.py`, `kimi_home.sh`, and the proofs `verify-<lane>.txt` |
| `regrade.sh` | regrade finished runs from their saved workspaces after a grader fix |
| `make_table.py`, `results-table.md`, `kept-tasks.txt` | all tables, the screening decision and the kept tasks, from `runs/*/grade.json` |
| `results.template.md`, `fill_results.py` | results.md with its data cells as placeholders, and the script that fills them |
| `deviations-log.txt`, `home-check.txt` | timestamped log of the changes listed in plan.md's Deviations; home-folder snapshots before and after each phase |
| `runs/` | **local only** (repo `.gitignore`): per run `grade.json`, `meta.json`, `prompt.txt`, `proxy.log`, `diffstat.txt`, and `private/` with the transcript and the final workspace, which contain the paid kit text in the kit arm |

The kit under test is the frozen 22-story build of the install round
(`../2026-11-21-kit-install-offline/kit/`, gitignored; sha256 in `kit.sha256`).

## Fixture versions (pinned, exact)

`@modelcontextprotocol/sdk` 1.32.2, `zod` 3.25.76, `typescript` 5.9.3, `vitest` 3.2.7,
`@types/node` 22.20.5 (esbuild 0.28.2 comes with vitest). Node 26.13.0, npm 11.20.0. I chose the
well-known major versions (TypeScript 5, vitest 3, zod 3) over the newest (TS 7, vitest 5, zod 4).

## T5 schema

`graders/schema/server.schema.2025-12-11.json`, fetched 2026-11-22 from
https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json (the `$schema` URL the
registry docs use, at registry repo commit 9432a0a). sha256
`3fba09590c99f61735d234822279f4223fab9e300c0a81e81c91ab62a4114de0`.

## Agents

| lane | agent | model | network allowed (proxy) |
|---|---|---|---|
| haiku | Claude Code 2.1.329 | claude-haiku-5-5 | api.anthropic.com |
| sonnet | Claude Code 2.1.329 | claude-sonnet-5-5 | api.anthropic.com |
| codex | Codex CLI 0.160.0 | gpt-6.1-sol, reasoning low | Codex's own sandbox, network off |
| deepseek | Claude Code 2.1.329 with `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic` | deepseek-flash | api.deepseek.com |
| kimi | Kimi Code 2.5.2 | kimi-code/k3.1-pro (K3.1 Pro) | api.kimi.ai, auth.kimi.ai |

## How offline is enforced

- **Claude Code lanes (haiku, sonnet, deepseek):** web tools removed
  (`--disallowedTools WebFetch WebSearch RemoteTrigger Cron* ScheduleWakeup`). The sandbox profile lets
  the agent and everything it starts reach only a per-run proxy (`offline/proxy.py`), which tunnels to
  the lane's model host and refuses the rest.
- **DeepSeek:** runs as round 12 did. The key comes from `~/.zshenv` and is passed to Claude Code as
  `ANTHROPIC_AUTH_TOKEN`; HOME and the config dir are scratch, the real home is unreadable, and the key
  is scrubbed from the run folder.
- **Kimi:** WebSearch and FetchURL are disabled through `[tools] disabled` in a scratch
  `KIMI_CODE_HOME` (`offline/kimi_home.sh`), with its login symlinked in. This leaves Kimi's own
  system prompt as shipped, which an `--agent-file` would replace. Its search and fetch services go
  through the same host as the model (`api.kimi.ai/coding/v1/search` and `/fetch`), so the proxy cannot
  block them; that is why they are also removed from that config. The real home is unreadable except
  `~/.kimi-code`. The hosts come from its config.toml and were confirmed by the proxy log
  (`telemetry-logs.kimi.ai` was refused).
- **Codex:** `-s workspace-write` with `network_access=false`, `web_search="disabled"`, browser, apps
  and plugins features off, `--ignore-user-config`, as in the install round.
- **Every lane** gets the env allowlist (`guide-eval/sandbox/env.sh`) and a PATH built by
  `offline/setup.sh`: every `/opt/homebrew/bin` tool except those in `offline/hidden-tools.txt`
  (mcp-publisher, mcporter, gh, claude, codex, gemini, aws, aws_completer). It also gets an empty
  ZDOTDIR, so zsh login shells read no user file and cannot put the hidden tools back. The sandbox
  profiles also deny running mcp-publisher and gh by absolute path. Codex has no such deny, because
  its own seatbelt cannot be extended; there, hiding them from PATH is the only measure. `/usr/local/bin`
  (docker, firebase, aws) comes back through macOS `path_helper` in Codex's login shell; none of these
  does a check's work.
- **Proof** (`offline/verify-*.txt`, one run per lane, same code path as the real runs): in all five
  lanes both `curl https://worklore.dev` (through the proxy and around it) fail, no web tool is offered,
  `command -v` finds none of the hidden tools, and writes to the real home are denied (deepseek and kimi
  run with a scratch HOME).

## Rerun

```bash
cd worklore-research/2026-11-22-kit-build-eval
(cd fixtures/notes && npm ci) && (cd graders && npm ci)   # node_modules, once
offline/setup.sh                       # agent PATH, ZDOTDIR, sandbox profiles
./controls.sh                          # graders: none fails, ref passes, trap fails its checks
for l in haiku sonnet codex deepseek kimi; do ./run.sh s verify none $l 0; done   # offline proofs
./supervise.sh s 2 haiku,deepseek t1 t2 t3 t4 t5       # screening, 40 runs
python3 make_table.py                  # screening decision -> kept-tasks.txt
./supervise.sh f 3 haiku,sonnet,codex,deepseek,kimi $(cat kept-tasks.txt)   # full round
python3 make_table.py && python3 fill_results.py   # tables, then results.md
```

Needs macOS (`sandbox-exec`), Claude Code, Codex and Kimi Code logged in, a DeepSeek key in
`~/.zshenv`, and `worklore-mcp/research/guide-eval/sandbox/env.sh`.

Do not edit `run.sh` or `lane.sh` while lanes are running. Bash reads a script as it runs, so an
in-place edit corrupts the run in progress (install round). Write a new file and `mv` it into place.
