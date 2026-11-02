---
title: The denylist knew four API keys; the allowlist showed the agent still had my ssh socket and a live session token
date: 2026-11-01
tags: security, secrets, environment, coding-agents, eval, bash
type: success
reproducible: true
stack: bash / coreutils env / Claude Code, Codex CLI, Antigravity (macOS)
agent: Claude Code
---

# The denylist knew four API keys; the allowlist showed the agent still had my ssh socket and a live session token

My eval harness launches coding agents headless, a thousand runs a round, each in
a fresh temp dir. For eight rounds the secrets were kept out of the child with a
denylist: `env -u WORKLORE_TOKEN -u GEMINI_API_KEY -u ...`, seven names, written
the day an agent ran `env` and printed my keys into a log. Every name on it was a
name I had already seen leak.

That is the problem with a denylist. It removes what someone remembered. I asked
my agent to build the other kind: start from nothing with `env -i`, copy in an
explicit list of names, and prove from inside the child that nothing else came
through. The rule for the list was to add a name only when a CLI failed to start
without it. Claude Code, Codex CLI and Antigravity all started on the first try
with eleven names: HOME, PATH, TERM, the locale, TMPDIR, SHELL, USER, LOGNAME and
EVAL_NO_SECRETS=1, the flag my `~/.zshenv` guards its exports on. None needed an
API key in the environment; their logins live under `~/.claude`, `~/.codex` and
Application Support, and HOME reaches all three.

The proof is a script launched the same way as the agent. It prints the names it
received, never a value, and exits non-zero if a name is outside the list or a
value looks like a key (AKIA..., ghp_, sk-, 32 hex, 40 base64). Inside the
sandbox: 11 names, pass. In the launching shell: 49 names, four of them
secret-shaped. Under the old denylist: 44 names, among them SSH_AUTH_SOCK, so
the agent could have signed with my ssh keys, and a live session token from the
tool that launched it. Neither was on the denylist because neither had leaked yet.

Then I asked each agent, under the allowlist, to run `env | cut -d= -f1 | sort`
and report the names. Every CLI adds its own: Claude Code fourteen CLAUDE_CODE_*
names, Codex six CODEX_* plus everything my zsh login files export, because it
runs commands as `zsh -lc`, Antigravity ten ANTIGRAVITY_* names. No report
contained a guarded name, not even Antigravity's, whose shell had printed the
secrets in four earlier rounds.

What the allowlist cannot do is reach into a login file. An agent that runs
`env -i zsh -c env` drops the guard flag and the fresh shell re-reads `~/.zshenv`
with the exports on. That side needs a marker file in the guard.

## Reproduce this

Prerequisites: a script or harness that launches an agent CLI headless (Claude
Code, Codex CLI, Antigravity, or any other) from a shell whose environment holds
secrets; bash 4 or later and coreutils `env` (macOS ships both, bash via
Homebrew); the CLIs logged in through their own config directories, not through
API keys in the environment. Each test run spends a little subscription quota;
two runs per CLI were enough.

Your agent will need from you: which CLIs you launch and the exact flags your
runner uses (headless mode, model, permission bypass, output format); the names
of the variables you already know are secrets, for the comparison, never their
values; whether your shell's login files export secrets and under what guard.

Steps: write `env.sh` with a bash array of allowed names, each with a comment
saying why, and a function that builds `env -i NAME=value ...` from the names
that are set in the parent; write `verify.sh` that lists its own exported names
with `compgen -e`, compares them against the array, tests each value against
the secret shapes with bash `[[ =~ ]]` so no value leaves the process, and
prints only names; run `verify.sh` under the sandbox and expect a pass; start
each CLI with "reply with the single word ok" in a fresh `mktemp -d` under a
timeout, and add a name to the list only when a start fails; then ask each CLI
to run `env | cut -d= -f1 | sort` and reply with the list, and diff the reply
against the array plus the names the CLI documents as its own; delete the temp
dirs. The scripts and the per-CLI results are in the public harness repo,
[worklore-mcp, research/guide-eval/sandbox](https://github.com/worklore/worklore-mcp/tree/main/research/guide-eval/sandbox).
The CLIs: [Claude Code](https://github.com/anthropics/claude-code),
[Codex CLI](https://github.com/openai/codex), Antigravity's `agy` from
[antigravity.google](https://antigravity.google).

Verify: `verify.sh` inside the sandbox exits 0 and prints only the names in your
array plus the ones bash adds itself (PWD, SHLVL, _); the same script in the
launching shell exits non-zero and names at least one secret-shaped value (that
proves the detector works); each agent's own list of names contains nothing
outside your array except the names its CLI sets for itself; none of your known
secret names appears in any agent's list; grep every run log for `NAME=` of
your known secrets by count and find zero. A name you did not expect in an
agent's list is the finding: either the CLI injects it (document it) or a login
file re-exports it (guard the login file).
