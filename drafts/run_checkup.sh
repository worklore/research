#!/usr/bin/env bash
# usage: run_checkup.sh <a|b>
#   a  the deliberately broken local server (source available, token available)
#   b  the live worklore.dev/mcp, NO token, read-only
set -u
D=/private/tmp/claude-501/-Users-valentinakoniukhova-projects-worklore/3bfdd3c9-cfe2-4fd1-a8b7-ce52b613a3aa/scratchpad/checkup
WT=/Users/valentinakoniukhova/projects/worklore/.claude/worktrees/agent-a7175e68d167f5ea2
STORY=$WT/research/drafts/mcp-checkup-story.md
R=$D/run-$1; rm -rf "$R"; mkdir -p "$R/work"
if [ "$1" = a ]; then
  mkdir -p "$R/work/server"; cp "$WT/research/drafts/broken_mcp_server.py" "$R/work/server/"
  TASK="Run this read-only checkup against my MCP server at http://127.0.0.1:8791/mcp.
A bearer token for it is in the environment variable BROKEN_MCP_TOKEN (send it as the header 'Authorization: Bearer <value>'; never print it). Do C1 without it first.
The server's source code is in ./server/ — you may read it, never edit it.
The server is not listed in the MCP Registry."
  EXTRA=(env BROKEN_MCP_TOKEN=test-token)
else
  TASK="Run this read-only checkup against the MCP server at https://worklore.dev/mcp.
I have NO token for it and no access to its source or logs: check what can be checked without them, and say exactly what could not be checked and what would unlock it.
Its name in the official MCP Registry is io.github.worklore/worklore."
  EXTRA=(env)
fi
{ printf '%s\n\nDo not record the result anywhere (no worklore API calls, no MCP tools) — just give me the report.\n\nFollow this guide:\n\n' "$TASK"; cat "$STORY"; } > "$R/prompt.txt"
P="$(cat "$R/prompt.txt")"
cd "$R/work" || exit 1
start=$(date +%s)
timeout 1200 env -u WORKLORE_TOKEN -u WORKLORE_API -u GEMINI_API_KEY "${EXTRA[@]}" \
  claude -p "$P" --model claude-opus-5-5 --dangerously-skip-permissions \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' --disable-slash-commands \
  --setting-sources project,local --settings '{"disableAllHooks":true}' \
  --output-format stream-json --verbose < /dev/null > "$R/agent.log" 2> "$R/agent.err"
rc=$?
echo "run-$1 rc=$rc wall=$(( $(date +%s) - start ))s"
python3 - "$R/agent.log" > "$R/report.md" <<'PY'
import json, sys
last = ""
for line in open(sys.argv[1]):
    try:
        ev = json.loads(line)
    except Exception:
        continue
    if ev.get("type") == "result":
        last = ev.get("result") or last
print(last)
PY
