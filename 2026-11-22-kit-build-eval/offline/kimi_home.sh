#!/usr/bin/env bash
# usage: kimi_home.sh <dir>  A scratch KIMI_CODE_HOME for one run. config.toml is a copy of the real one
# with the search and fetch services removed and WebSearch/FetchURL disabled ([tools] disabled), so the
# shipped system prompt stays as it is (an --agent-file would replace it). The login (credentials/,
# oauth/, device_id, region) is symlinked, so a token refresh lands in the real login, not a copy.
set -eu
KH=$1; K="$HOME/.kimi-code"
python3 - "$K/config.toml" "$KH/config.toml" <<'PY'
import re, sys
src = open(sys.argv[1]).read()
# drop [services.moonshot_search...] and [services.moonshot_fetch...] tables
out, skip = [], False
for line in src.splitlines():
    m = re.match(r"^\s*\[([^\]]+)\]\s*$", line)
    if m:
        skip = m.group(1).startswith(("services.moonshot_search", "services.moonshot_fetch"))
    if not skip:
        out.append(line)
text = "\n".join(out).rstrip() + '\n\n[tools]\ndisabled = ["WebSearch", "FetchURL"]\n'
open(sys.argv[2], "w").write(text)
PY
for f in credentials oauth device_id region; do [ -e "$K/$f" ] && ln -s "$K/$f" "$KH/$f"; done
exit 0
