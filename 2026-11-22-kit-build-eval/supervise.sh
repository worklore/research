#!/usr/bin/env bash
# usage: supervise.sh <s|f> <reps> <lanes (comma-separated)> <task...>
# Starts every lane in parallel. When a lane stops on a quota limit (STOP-<lane>), waits 45 minutes and
# relaunches it, at most 6 times per lane; it never retries in a tight loop. A DeepSeek lane that ran
# out of balance (STOP-deepseek-balance) is not relaunched. Writes supervise-<phase>.out.
D="$(cd "$(dirname "$0")" && pwd)"; PH=$1; REPS=$2; IFS=, read -ra LANES <<< "$3"; shift 3; TASKS=("$@")
LOG="$D/supervise-$PH.out"
lane_loop() { local L=$1 n=0
  while :; do
    rm -f "$D/STOP-$L"
    "$D/lane.sh" "$PH" "$L" "$REPS" "${TASKS[@]}" && { echo "$(date '+%F %T') $L done" >> "$LOG"; return; }
    [ "$L" = deepseek ] && [ -f "$D/STOP-deepseek-balance" ] && { echo "$(date '+%F %T') $L: balance gone, not relaunched" >> "$LOG"; return; }
    n=$((n+1)); [ $n -gt 6 ] && { echo "$(date '+%F %T') $L: gave up after $n limits" >> "$LOG"; return; }
    echo "$(date '+%F %T') $L: limit ($(cat "$D/STOP-$L" 2>/dev/null)), relaunch $n in 45 min" >> "$LOG"; sleep 2700
  done; }
echo "$(date '+%F %T') start $PH reps=$REPS lanes=${LANES[*]} tasks=${TASKS[*]}" >> "$LOG"
snap() { { echo "## $1 $(date '+%F %T')"; launchctl list | awk '{print $3}' | grep -v mdworker | sort | md5sum;
  for d in "$HOME/bin" "$HOME/.local/bin" "$HOME/Library/LaunchAgents"; do echo "$(basename "$d"): $(ls -A "$d" 2>/dev/null | md5sum)"; done; } >> "$D/home-check.txt"; }
snap "before $PH"
for L in "${LANES[@]}"; do lane_loop "$L" & done; wait
snap "after $PH"
echo "$(date '+%F %T') all lanes finished" >> "$LOG"
