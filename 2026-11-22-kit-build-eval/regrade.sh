#!/usr/bin/env bash
# usage: regrade.sh [glob]   Regrades finished runs from their saved workspace (runs/<id>/private/repo),
# e.g. after a grader fix (listed in plan.md, Deviations). Default: every s-* and f-* run.
D="$(cd "$(dirname "$0")" && pwd)"; PAT=${1:-[sf]-t*}
for R in "$D"/runs/$PAT/; do R=${R%/}; [ -f "$R/meta.json" ] && [ -d "$R/private/repo" ] || continue
  T=$(python3 -c "import json;print(json.load(open('$R/meta.json'))['task'])")
  python3 "$D/graders/grade.py" "$R" "$T" "$R/private/repo" > "$R/grade.json.new" 2> "$R/grade.err" && mv "$R/grade.json.new" "$R/grade.json"
done; echo regraded
