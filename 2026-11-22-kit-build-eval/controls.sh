#!/usr/bin/env bash
# Grader controls, no agent: for every task, the untouched fixture must FAIL every check and the
# reference solution in refs/ must PASS every check. A trap (refs/traps/<task>: a plausible solution
# that falls into the stories' trap) must fail the trap checks. Output: controls.out
D="$(cd "$(dirname "$0")" && pwd)"
for T in t1 t2 t3 t4 t5; do for K in none ref trap; do
  [ $K = trap ] && [ ! -d "$D/refs/traps/$T" ] && continue
  R=$(mktemp -d /tmp/kitctl-R-XXXXXX); W=$(mktemp -d /tmp/kitctl-W-XXXXXX)/ws; mkdir -p "$R/private"; : > "$R/private/agent.log"
  "$D/make_ws.sh" $T none "$W" >/dev/null
  if [ $K = trap ]; then
    [ -d "$D/refs/traps/$T/src" ] && cp -R "$D/refs/traps/$T/src/." "$W/src/"
    [ -d "$D/refs/traps/$T/test" ] && cp -R "$D/refs/traps/$T/test/." "$W/test/"
  fi
  if [ $K = ref ]; then
    [ -d "$D/refs/$T/src" ] && cp -R "$D/refs/$T/src/." "$W/src/"
    [ -d "$D/refs/$T/test" ] && cp -R "$D/refs/$T/test/." "$W/test/"
    if [ $T = t5 ]; then cp "$D/refs/t5/server.json" "$W/"; cat "$D/refs/t5/README.publish.md" >> "$W/README.md"
      node -e 'const f=process.argv[1];const p=require(f);p.mcpName="io.github.notesco/notes-mcp";require("fs").writeFileSync(f,JSON.stringify(p,null,2)+"\n")' "$W/package.json"; fi
  fi
  echo "{\"id\":\"control-$T-$K\",\"task\":\"$T\",\"arm\":\"control\",\"lane\":\"none\",\"rep\":0}" > "$R/meta.json"
  python3 "$D/graders/grade.py" "$R" $T "$W" > "$R/grade.json"
  python3 -c "
import json,sys; g=json.load(open(sys.argv[1])); c=g.get('checks',{})
print('$T', '$K'.ljust(4), ' '.join(('PASS ' if v else 'fail ')+k for k,v in c.items()) or ('NO CHECKS '+json.dumps(g.get('detail'))[:400]))" "$R/grade.json"
  [ -n "${KEEP:-}" ] && cp "$R/grade.json" "/tmp/kitctl-$T-$K.json"
  rm -rf "$R" "$(dirname "$W")"
done; done
