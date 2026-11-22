#!/usr/bin/env bash
# usage: run.sh <s|f> <t1..t5> <none|kit> <haiku|sonnet|codex|deepseek|kimi> <rep>
#   s = screening, f = full round. One run: build the workspace (make_ws.sh), run the agent offline,
#   save the transcript and final workspace under runs/<id>/private/ (gitignored), grade with the
#   hidden graders (graders/grade.py, outside the workspace).
# Offline (README.md): every lane but codex runs under a sandbox profile from offline/setup.sh that
# allows TCP only to a per-run proxy (offline/proxy.py) tunnelling to the lane's model host; codex uses
# its own sandbox with network off. All lanes get the env allowlist of guide-eval/sandbox/env.sh, a
# PATH without the hidden tools (offline/hidden-tools.txt) and an empty ZDOTDIR.
set -u
D="$(cd "$(dirname "$0")" && pwd)"
PH=$1; T=$2; ARM=$3; L=$4; REP=$5
case $PH in s|f|p) ;; *) echo "phase s|f|p"; exit 2;; esac
case $T in t1|t2|t3|t4|t5|verify) ;; *) echo "task t1..t5|verify"; exit 2;; esac
case $ARM in none|kit) ;; *) echo "arm none|kit"; exit 2;; esac
ID="$PH-$T-$ARM-$L-r$REP"; R="$D/runs/$ID"; rm -rf "$R"; mkdir -p "$R/private"
ENVD=${ENVD:-/tmp/kitbuild-env}; [ -d "$ENVD/bin" ] || "$D/offline/setup.sh" >/dev/null
SANE="$ENVD/bin:/opt/homebrew/opt/coreutils/libexec/gnubin:/opt/homebrew/opt/findutils/libexec/gnubin:/opt/homebrew/opt/gnu-sed/libexec/gnubin:/opt/homebrew/opt/grep/libexec/gnubin:/usr/bin:/bin:/usr/sbin:/sbin"
TOP=$(mktemp -d /tmp/kitb-XXXXXX); W="$TOP/ws"
"$D/make_ws.sh" "$([ $T = verify ] && echo t2 || echo $T)" "$ARM" "$W" || { echo "$ID: make_ws failed"; exit 3; }
git -C "$W" rev-parse HEAD > "$R/base_commit"
if [ $T = verify ]; then cp "$D/prompts/verify.txt" "$R/prompt.txt"; else cat "$D/prompts/$T.txt" "$D/prompts/suffix.txt" > "$R/prompt.txt"; fi; P="$(cat "$R/prompt.txt")"
. "$HOME/projects/worklore-mcp/research/guide-eval/sandbox/env.sh"
TMO=${TMO:-1200}
LG="$R/private/agent.log"; X="$R/private/agent.err"; REAL="$HOME"
start_proxy() { # start_proxy <hosts...>  -> sets PP, PORT
  local PF="$R/private/proxy.port"; python3 "$D/offline/proxy.py" "$PF" "$R/proxy.log" "$@" & PP=$!
  for _ in $(seq 50); do [ -s "$PF" ] && break; sleep 0.1; done; PORT=$(cat "$PF"); }
PROXY_ENV() { echo HTTPS_PROXY="http://127.0.0.1:$PORT" HTTP_PROXY="http://127.0.0.1:$PORT" ALL_PROXY="http://127.0.0.1:$PORT"; }
CLAUDE_FLAGS=(--dangerously-skip-permissions --disallowedTools WebFetch WebSearch RemoteTrigger CronCreate CronDelete CronList ScheduleWakeup
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' --disable-slash-commands --setting-sources project,local
  --settings '{"disableAllHooks":true}' --output-format stream-json --verbose)
claude_lane() { # claude_lane <model>
  start_proxy api.anthropic.com
  ( cd "$W" && sandbox_exec sandbox-exec -D HOME="$REAL" -D PROXYPORT="$PORT" -f "$D/offline/claude.sb" \
      env $(PROXY_ENV) PATH="$SANE" ZDOTDIR="$ENVD/zdotdir" CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
      timeout $TMO /opt/homebrew/bin/claude -p "$P" --model "$1" "${CLAUDE_FLAGS[@]}" < /dev/null > "$LG" 2> "$X" )
  local rc=$?; kill $PP 2>/dev/null; wait $PP 2>/dev/null; return $rc; }
deepseek_lane() { # as round 12's deepseek_run, plus the network fence; the key is never printed
  if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
    DEEPSEEK_API_KEY="$(env -u EVAL_NO_SECRETS bash -c 'source ~/.zshenv >/dev/null 2>&1; printf %s "$DEEPSEEK_API_KEY"')"
    [ -n "$DEEPSEEK_API_KEY" ] || { echo "no DEEPSEEK_API_KEY in ~/.zshenv" > "$X"; return 98; }
    export DEEPSEEK_API_KEY
  fi
  start_proxy api.deepseek.com
  local SH CH; SH=$(mktemp -d /tmp/khome-XXXXXX); CH=$(mktemp -d /tmp/ccfg-XXXXXX)
  ( cd "$W" && export HOME="$SH" && sandbox_exec sandbox-exec -D HOME="$REAL" -D PROXYPORT="$PORT" -f "$D/offline/deepseek.sb" \
      env $(PROXY_ENV) PATH="$SANE" ZDOTDIR="$ENVD/zdotdir" CLAUDE_CONFIG_DIR="$CH" \
      ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY" \
      ANTHROPIC_MODEL=deepseek-flash ANTHROPIC_SMALL_FAST_MODEL=deepseek-flash ANTHROPIC_DEFAULT_HAIKU_MODEL=deepseek-flash \
      ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-flash CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
      timeout $TMO /opt/homebrew/bin/claude -p "$P" --model deepseek-flash "${CLAUDE_FLAGS[@]}" < /dev/null > "$LG" 2> "$X" )
  local rc=$?; kill $PP 2>/dev/null; wait $PP 2>/dev/null; chmod -R u+w "$SH" "$CH" 2>/dev/null; rm -rf "$SH" "$CH"; return $rc; }
kimi_lane() { # Kimi Code K3.1 Pro, scratch HOME and KIMI_CODE_HOME (login files linked from the real one)
  start_proxy api.kimi.ai auth.kimi.ai
  local SH KH SK; SH=$(mktemp -d /tmp/khome-XXXXXX); KH=$(mktemp -d /tmp/kimih-XXXXXX); SK=$(mktemp -d /tmp/noskills-XXXXXX)
  "$D/offline/kimi_home.sh" "$KH"
  ( cd "$W" && export HOME="$SH" && sandbox_exec sandbox-exec -D HOME="$REAL" -D PROXYPORT="$PORT" -f "$D/offline/kimi.sb" \
      env $(PROXY_ENV) PATH="$SANE" ZDOTDIR="$ENVD/zdotdir" KIMI_CODE_HOME="$KH" KIMI_CODE_NO_AUTO_UPDATE=1 \
      timeout $TMO "$REAL/.kimi-code/bin/kimi" -m kimi-code/k3.1-pro -p "$P" --output-format stream-json --skills-dir "$SK" \
      < /dev/null > "$LG" 2> "$X" )
  local rc=$?; kill $PP 2>/dev/null; wait $PP 2>/dev/null; rm -rf "$SH" "$KH" "$SK"; return $rc; }
codex_lane() {
  ( cd "$W" && PATH="$SANE" sandbox_exec env PATH="$SANE" ZDOTDIR="$ENVD/zdotdir" timeout $TMO /opt/homebrew/bin/codex exec \
      --ignore-user-config --ephemeral --skip-git-repo-check -s workspace-write -c sandbox_workspace_write.network_access=false \
      -c 'web_search="disabled"' --disable browser_use --disable browser_use_external --disable computer_use --disable apps \
      --disable image_generation --disable plugins --disable remote_plugin --disable in_app_browser \
      -m gpt-6.1-sol -c 'model_reasoning_effort="low"' -C "$W" --json -o "$R/private/final.txt" "$P" < /dev/null > "$LG" 2> "$X" ); }
start=$(date +%s)
case $L in
  haiku) claude_lane claude-haiku-5-5;;
  sonnet) claude_lane claude-sonnet-5-5;;
  deepseek) deepseek_lane;;
  kimi) kimi_lane;;
  codex) codex_lane;;
  *) echo "unknown lane $L"; exit 2;;
esac
rc=$?; end=$(date +%s)
cd "$W" && git add -A >/dev/null 2>&1
git diff --cached "$(cat "$R/base_commit")" -- . ':(exclude)worklore-mcp-server-kit' > "$R/private/diff.full.patch"
git diff --cached --stat "$(cat "$R/base_commit")" -- . ':(exclude)worklore-mcp-server-kit' > "$R/diffstat.txt"
git diff --cached --name-only "$(cat "$R/base_commit")" -- worklore-mcp-server-kit > "$R/kit-files-changed.txt"; git reset -q
cd /; /bin/cp -cR "$W" "$R/private/repo" 2>/dev/null || /bin/cp -R "$W" "$R/private/repo"; rm -rf "$TOP"
# secrets: the DeepSeek key must not survive anywhere in the run folder
key_hits=0
if [ -n "${DEEPSEEK_API_KEY:-}" ]; then key_hits=$(python3 - "$R" <<'EOF'
import os, sys
k = os.environ["DEEPSEEK_API_KEY"].encode(); n = 0
for root, dirs, files in os.walk(sys.argv[1]):
    dirs[:] = [d for d in dirs if d != "node_modules"]
    for f in files:
        p = os.path.join(root, f)
        if os.path.islink(p): continue
        try: b = open(p, "rb").read()
        except OSError: continue
        if k in b: n += b.count(k); open(p, "wb").write(b.replace(k, b"[REDACTED-DEEPSEEK-KEY]"))
print(n)
EOF
); fi
limit=false
if grep -v rate_limit_info "$X" "$LG" 2>/dev/null | grep -qiE "hit your (usage )?limit|usage limit|limit reached|rate limit exceeded|too many requests|out of credits|resource.?exhausted|insufficient_quota|quota exceeded|status code 429|\"status\": ?429|overloaded_error|exceeded_current_quota|5-hour" \
   && [ $((end-start)) -lt 180 ]; then limit=true; fi
grep -qE "provider.api_error: You've reached your 5-hour usage limit|exceeded_current_quota_error" "$X" "$LG" 2>/dev/null && limit=true
if [ "$L" = deepseek ] && grep -qiE "Insufficient Balance|API Error: 40[12]|authentication_error|invalid api key" "$LG" "$X" 2>/dev/null; then
  limit=true; echo "$(date '+%F %T') $ID: DeepSeek key rejected or balance gone" >> "$D/STOP-deepseek-balance"; fi
echo "{\"id\":\"$ID\",\"phase\":\"$PH\",\"task\":\"$T\",\"arm\":\"$ARM\",\"lane\":\"$L\",\"rep\":$REP,\"exit_code\":$rc,\"wall_s\":$((end-start)),\"limit\":$limit,\"key_hits\":$key_hits}" > "$R/meta.json"
if [ $T = verify ]; then python3 "$D/offline/verify_report.py" "$R" "$L" > "$D/offline/verify-$L.txt"; echo "verify $L done: offline/verify-$L.txt"; exit 0; fi
python3 "$D/graders/grade.py" "$R" "$T" "$R/private/repo" > "$R/grade.json" 2> "$R/grade.err"
echo "$ID rc=$rc wall=$((end-start))s limit=$limit $(python3 -c "import json;g=json.load(open('$R/grade.json'));print(' '.join(k.split('_')[0]+('+' if v else '-') for k,v in g.get('checks',{}).items()), 'kit_read='+str(bool(g['kit']['files_read'])))" 2>/dev/null)"
