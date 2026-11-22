#!/usr/bin/env bash
# usage: make_ws.sh <t1..t5> <none|kit> <dest>   Builds one run's workspace: the notes fixture (with the
# T1 overlay for t1), node_modules cloned from fixtures/notes/node_modules (APFS clone, offline), the kit
# installed with canon_install.py for the kit arm, then git init with one commit (node_modules ignored).
set -eu
D="$(cd "$(dirname "$0")" && pwd)"; T=$1; ARM=$2; W=$3
ZIP=${KIT_ZIP:-$D/../2026-11-21-kit-install-offline/kit/worklore-mcp-server-kit-1.1.0.zip}
mkdir -p "$W"
( cd "$D/fixtures/notes" && tar --exclude=node_modules --exclude=dist --exclude=data -cf - . ) | ( cd "$W" && tar -xf - )
[ "$T" = t1 ] && cp -R "$D/fixtures/t1-overlay/." "$W/"
/bin/cp -cR "$D/fixtures/notes/node_modules" "$W/node_modules" 2>/dev/null || /bin/cp -R "$D/fixtures/notes/node_modules" "$W/node_modules"
[ "$ARM" = kit ] && python3 "$D/canon_install.py" "$W" "$ZIP"
cd "$W" && git init -q && git add -A && git -c user.name=dev -c user.email=dev@local commit -qm base
