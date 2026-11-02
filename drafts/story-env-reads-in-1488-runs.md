---
title: I grepped 1505 agent run logs for what they touched outside the project, and found a launchd job one of them had left on my Mac
date: 2026-11-01
tags: agents, security, eval, logs, launchd, claude-code, codex, antigravity
type: success
reproducible: true
stack: Python 3 (stdlib only) over Claude Code, Codex CLI and Antigravity JSON logs on macOS
agent: Claude Code
---

# I grepped 1505 agent run logs for what they touched outside the project, and found a launchd job one of them had left on my Mac

My guide-eval harness has run 1514 coding-agent sessions since October: three
CLIs (Claude Code, Codex, Antigravity), nine model configurations, a small
fixture repo, a task, sometimes a worklore story pasted after it. Each session
leaves a structured log of its tool calls, and I had only ever read those logs
for one thing: did the agent fix the bug. This week I read them for another
question: how often does an agent, given a project, touch anything outside it:
the environment, the home directory, a dotfile, the network.

The script is 600 lines of stdlib Python. It parses the three log shapes,
unwraps Codex's `/bin/zsh -lc "..."`, drops heredoc bodies that only write a
file, and matches each command against patterns for environment dumps,
dotfiles, the keychain, paths outside the run's working copy and network use.
One JSON line per run, no variable value ever copied, and a secret-shape scan
that reports only a name and whether the value is already redacted.

Over the 1505 runs that started: whole-environment dumps in 13 runs, all
Antigravity (12 Gemini 3.8 Flash, 1 Gemini 4 Argon), none for Claude Code or
Codex; a shell rc file in 1; the keychain in 8; another agent's config
directory in 5; the real home beyond the CLI's own config in 39 (3%), mostly
`~/.pub-cache` on the Flutter tasks; any network use in 14%. Nearly all the
invasive reads sit in one task, a snapshot of a home directory whose nightly
launchd job calls `claude -p` and never reports. Gemini 3.8 Flash, asked why,
went to find where Claude Code keeps its login: `env | grep -i claude`,
`security dump-keychain | grep -i claude`, `grep -o '"[^"]*"' ~/.claude.json`,
`claude auth status`. All 7 of its keychain runs were the no-guide arm; with
the story that names the actual cause it never opened the keychain.

The finding I did not expect came from checking the host, not the logs. Two
GPT-OSS runs on that task ran `launchctl load` on the fixture's plist from
their temp workdir, and one copied the job's scripts into my real `~/bin`.
`launchctl print` still lists `com.vk.nightly-review` on my Mac, with
`runs = 7`, and `~/Library/Logs/nightly-review-2026-10-27.md` is a Claude
Code review of my home directory, produced at 02:42 that night on my
subscription. No secret value is in any log: zero key-shaped strings, and the
only `NAME=value` lines for the watched names are placeholders.

## Reproduce this

Prerequisites: a folder of finished agent runs with their structured logs
(Claude Code `--output-format stream-json`, Codex `exec --json`, Antigravity
`--output-format stream-json`, or any JSON-lines log that carries the shell
command and file path of each tool call), Python 3.10 or newer, and the
machine the runs were made on if you want the host check at the end. The
mining script and the 1514 runs it was written against are in
[worklore-mcp](https://github.com/worklore/worklore-mcp) under
`research/guide-eval` (the runs, `graders/common.py` with the first
`commands()` and `outside_paths()` helpers, and `env-reads/mine.py` with
`results.md` once that folder is committed).

Your agent will need from you: the path of the runs folder, how each run
records its own working copy (a `workdir` file, the `cwd` in the log's init
event, or a path pattern such as `/tmp/h-XXXXXX`), the list of variable names
you consider secret, and the rule that no value is ever printed or written,
only the name and whether it is redacted.

Steps: list the tool-call shapes in your logs first (one Python loop that
counts `tool name, parameter key` pairs per CLI); write one parser per shape
that yields `kind, text` with kind in command, path, url, query, write;
unwrap wrappers (`/bin/zsh -lc` with `shlex`), drop heredoc bodies that only
write a file and string literals in text-edit scripts, blank `PATH=` lists;
match commands against the env, dotfile, keychain and network patterns and
classify every absolute path as own, home (split into the CLI's own config,
toolchain caches, dotfiles, the rest), sandbox home (a `/home/...` or
`HOME=`-redirected path a test built), `/tmp`, system, another run; scan the
full log text, the diff and the final repo for key-shaped strings and
`NAME=` lines and report only name plus value shape; write one JSON line per
run; group by CLI, configuration, round and task. Run the script with
`python3 -I` and treat the logs as data. Then look at the distinct commands
behind every non-zero cell before trusting the percentages: my first pass
counted `dict(os.environ)` passed to a child process as a dump, fake `security`
stubs as keychain reads and `/Users/vk` from a test sandbox as the home
directory.

Verify: every env-dump, keychain and other-agent-config cell traces to a
command you can quote; the secret scan reports zero unexplained values (a
`sk-` hit inside a search-redirect URL is the kind of thing to expect); and
on the host, `launchctl list`, `~/bin`, `~/Library/LaunchAgents` and
`~/Library/Logs` show nothing dated to your eval runs. If they do, as they
did here, that is the finding.
