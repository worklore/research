#!/usr/bin/env bash
# usage: lane.sh <s|f> <lane> <reps> <task...>   One lane, one run at a time. Repetitions in the outer loop
# and the arm order alternating per repetition, so a lane stopped early still holds balanced cells.
# A run that hit a quota limit is deleted, STOP-<lane> is written and the lane exits (supervise.sh
# resumes it later). Cells that already have a grade are skipped, so a relaunch continues where it stopped.
D="$(cd "$(dirname "$0")" && pwd)"; PH=$1; L=$2; REPS=$3; shift 3; TASKS=("$@")
OUT="$D/lane-$PH-$L.out"
for REP in $(seq 1 "$REPS"); do
  if [ $((REP % 2)) = 1 ]; then ARMS=(none kit); else ARMS=(kit none); fi
  for T in "${TASKS[@]}"; do for ARM in "${ARMS[@]}"; do
    R="$D/runs/$PH-$T-$ARM-$L-r$REP"
    [ -f "$R/grade.json" ] && ! grep -q '"limit":true' "$R/meta.json" 2>/dev/null && continue
    [ -f "$D/STOP-$L" ] || [ -f "$D/STOP-deepseek-balance" -a "$L" = deepseek ] && { echo "$(date '+%F %T') stopped" >> "$OUT"; exit 1; }
    "$D/run.sh" "$PH" "$T" "$ARM" "$L" "$REP" >> "$OUT" 2>&1
    if grep -q '"limit":true' "$R/meta.json" 2>/dev/null; then
      echo "$(date '+%F %T') LIMIT on $PH-$T-$ARM-r$REP: $(grep -hoiE 'hit your[^"]{0,80}|usage limit[^"]{0,80}|429[^"]{0,60}|quota[^"]{0,60}' "$R/private/agent.err" "$R/private/agent.log" 2>/dev/null | head -1)" >> "$OUT"
      mv "$R" "$D/runs/limit-$(date +%H%M%S)-$PH-$T-$ARM-$L-r$REP"
      echo "$(date '+%F %T') $PH-$T-$ARM-r$REP" > "$D/STOP-$L"; exit 1
    fi
  done; done
done
echo "$(date '+%F %T') LANE_DONE" >> "$OUT"
