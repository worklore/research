#!/usr/bin/env bash
# Builds the agents' environment outside the home folder (two lane profiles deny reading it):
#   $ENVD/bin      symlinks to every /opt/homebrew/bin entry EXCEPT the hidden tools below
#   $ENVD/zdotdir  an empty ZDOTDIR, so zsh (Claude Code's and Codex's shells) reads no user startup
#                  file and cannot put /opt/homebrew/bin back on PATH
# and writes the three sandbox profiles from the template, with exec/read denies for the hidden tools.
# Hidden: tools that would do a check's work (mcp-publisher: server.json/namespace/publishing;
# mcporter: an MCP client), credentials (gh: `gh auth token`; aws), and other agents/model CLIs
# (claude, codex, gemini) that could reach a model or the web by another route.
set -eu
D="$(cd "$(dirname "$0")" && pwd)"
ENVD=${ENVD:-/tmp/kitbuild-env}
HIDE=(mcp-publisher mcporter gh claude codex gemini aws aws_completer)
rm -rf "$ENVD"; mkdir -p "$ENVD/bin" "$ENVD/zdotdir"
for f in /opt/homebrew/bin/*; do
  n=$(basename "$f"); skip=0
  for h in "${HIDE[@]}"; do [ "$n" = "$h" ] && skip=1; done
  [ $skip = 1 ] && continue
  ln -s "$(readlink -f "$f")" "$ENVD/bin/$n"
done
printf '%s\n' "${HIDE[@]}" > "$D/hidden-tools.txt"
DENY=""
for h in mcp-publisher gh; do r=$(readlink -f "/opt/homebrew/bin/$h"); DENY+="(deny process-exec (literal \"$r\") (literal \"/opt/homebrew/bin/$h\"))"$'\n'; done
DENY+='(deny file-read-data (subpath "/opt/homebrew/lib/node_modules/mcporter"))'$'\n'
DENY+='(deny file-read-data (subpath "/opt/homebrew/lib/node_modules/@openai/codex"))'$'\n'
DENY+='(deny file-read-data (subpath "/opt/homebrew/lib/node_modules/@google/gemini-cli"))'$'\n'
common() { cat <<SB
(version 1)
(allow default)
;; Network: TCP only to the per-run allowlist proxy (proxy.py) on 127.0.0.1:PROXYPORT.
(deny network-outbound)
(allow network-outbound (remote ip (string-append "localhost:" (param "PROXYPORT"))))
(allow network-outbound (remote unix-socket))
(deny process-exec (literal "/bin/launchctl") (literal "/usr/bin/osascript"))
;; Hidden tools (see hidden-tools.txt).
$DENY
SB
}
{ echo ";; haiku/sonnet lanes: Claude Code with its real login (keychain, ~/.claude)."; common; cat <<'SB'
(deny file-write* (subpath (param "HOME")))
(allow file-write* (subpath (string-append (param "HOME") "/.claude")))
(allow file-write* (regex (string-append "^" (param "HOME") "/\\.claude\\.json")))
(allow file-write* (subpath (string-append (param "HOME") "/Library/Keychains")))
(allow file-write* (subpath (string-append (param "HOME") "/Library/Caches")))
(deny file-read-data (subpath (string-append (param "HOME") "/projects")))
(deny file-read-data (subpath (string-append (param "HOME") "/.ssh")))
(deny file-read-data (subpath (string-append (param "HOME") "/.aws")))
(deny file-read-data (subpath (string-append (param "HOME") "/.config")))
(deny file-read-data (subpath (string-append (param "HOME") "/.codex")))
(deny file-read-data (subpath (string-append (param "HOME") "/.gemini")))
(deny file-read-data (subpath (string-append (param "HOME") "/.kimi-code")))
(deny file-read-data (subpath (string-append (param "HOME") "/Documents")))
(deny file-read-data (subpath (string-append (param "HOME") "/Downloads")))
(deny file-read-data (subpath (string-append (param "HOME") "/Desktop")))
(deny file-read-data (literal (string-append (param "HOME") "/.zshenv")))
SB
} > "$D/claude.sb"
{ echo ";; deepseek lane: Claude Code on DeepSeek's API, scratch HOME and config dir; the real home is unreadable."; common; cat <<'SB'
(deny file-read-data (subpath (param "HOME")))
(deny file-write* (subpath (param "HOME")))
SB
} > "$D/deepseek.sb"
{ echo ";; kimi lane: Kimi Code, scratch HOME; only ~/.kimi-code (its login) is reachable in the real home."; common; cat <<'SB'
(deny file-read-data (subpath (param "HOME")))
(deny file-write* (subpath (param "HOME")))
(allow file-read-data (subpath (string-append (param "HOME") "/.kimi-code")))
(allow file-write* (subpath (string-append (param "HOME") "/.kimi-code")))
SB
} > "$D/kimi.sb"
echo "env in $ENVD: $(ls "$ENVD/bin" | wc -l) tools linked, hidden: ${HIDE[*]}"
