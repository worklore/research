#!/usr/bin/env python3
"""Builds results-table.md from runs/*/grade.json. usage: make_table.py
Screening keep rule (plan.md, step 1): a task goes into the full round when the kit arm passes at least
one check more often than the none arm in either screening lane, or when the none arm already fails a
check (in either lane). Story verdict (plan.md, "What would count"): a check's kit-arm pass count must
be above the none arm by 2 or more of 3 runs (one run is noise) in more than one lane to count as "helps"."""
import collections, glob, json, os
D = os.path.dirname(os.path.abspath(__file__))
G = []
for p in sorted(glob.glob(os.path.join(D, "runs", "*", "grade.json"))):
    try:
        g = json.load(open(p))
    except ValueError:
        continue
    if g.get("id", "").split("-")[0] in ("s", "f") and g.get("task") != "verify" and not g.get("limit"):
        g["phase"] = g["id"].split("-")[0]
        G.append(g)
TASKS = ["t1", "t2", "t3", "t4", "t5"]
LANES_ALL = ["haiku", "sonnet", "codex", "deepseek", "kimi"]
L = []
def frac(xs): return f"{sum(xs)}/{len(xs)}" if xs else "-"
def checks_of(task, runs):
    ks = []
    for g in runs:
        if g["task"] == task:
            for k in g.get("checks", {}):
                if k not in ks: ks.append(k)
    return ks
def cell(runs, task, check, lane, arm):
    return [bool(g["checks"].get(check)) for g in runs if g["task"] == task and g["lane"] == lane and g["arm"] == arm and check in g.get("checks", {})]

def table(phase, lanes, title):
    runs = [g for g in G if g["phase"] == phase]
    if not runs: return runs
    L.append(f"## {title}\n")
    L.append("Passes / runs for each check, none arm vs kit arm.\n")
    L.append("| task | check | " + " | ".join(f"{l} none | {l} kit" for l in lanes) + " | all none | all kit |")
    L.append("|---|---|" + "---|" * (2 * len(lanes) + 2))
    for t in TASKS:
        for c in checks_of(t, runs):
            row = [t, c.split("_", 1)[1]]; an, ak = [], []
            for l in lanes:
                n, k = cell(runs, t, c, l, "none"), cell(runs, t, c, l, "kit")
                an += n; ak += k
                row += [frac(n), frac(k)]
            row += [frac(an), frac(ak)]
            L.append("| " + " | ".join(row) + " |")
    L.append("")
    return runs

# ---------- screening
srun = table("s", ["haiku", "deepseek"], "Screening (haiku, deepseek; 2 runs per cell)")
if srun:
    L.append("### Screening decision (keep rule from plan.md)\n")
    keep = []
    for t in TASKS:
        why = []
        for c in checks_of(t, srun):
            for l in ("haiku", "deepseek"):
                n, k = cell(srun, t, c, l, "none"), cell(srun, t, c, l, "kit")
                if not n and not k: continue
                if sum(k) > sum(n): why.append(f"{c.split('_')[0]} {l}: kit {sum(k)}/{len(k)} > none {sum(n)}/{len(n)}")
                if n and sum(n) < len(n): why.append(f"{c.split('_')[0]} {l}: none fails ({sum(n)}/{len(n)})")
        have = any(g["task"] == t for g in srun)
        kept = bool(why)
        if kept: keep.append(t)
        L.append(f"- **{t}: {'KEEP' if kept else ('DROP' if have else 'no data')}**" + (f". {'; '.join(why[:6])}" + (" ..." if len(why) > 6 else "") if why else ". Both arms pass every check in both lanes: nothing to measure."))
    L.append("")
    open(os.path.join(D, "kept-tasks.txt"), "w").write(" ".join(keep) + "\n")

# ---------- full round
frun = table("f", LANES_ALL, "Full round (5 lanes, 3 runs per cell)")
if frun:
    # kit use in the kit arm
    L.append("### What the kit-arm runs opened\n")
    L.append("| lane | kit runs | opened START-HERE | opened any story | stories opened (median) |"); L.append("|---|---|---|---|---|")
    for l in LANES_ALL:
        k = [g for g in frun if g["lane"] == l and g["arm"] == "kit"]
        if not k: continue
        ns = sorted(len(g["kit"]["stories_read"]) for g in k)
        L.append(f"| {l} | {len(k)} | {frac([bool(g['kit']['read_start_here']) for g in k])} | {frac([bool(g['kit']['stories_read']) for g in k])} | {ns[len(ns)//2]} |")
    L.append("")
    # source-story reads vs the check
    L.append("### Did a kit run that opened the check's source story pass that check?\n")
    L.append("| check | kit runs that opened a source story: passed | kit runs that did not open it: passed | none arm: passed |"); L.append("|---|---|---|---|")
    for t in TASKS:
        for c in checks_of(t, frun):
            k = [g for g in frun if g["task"] == t and g["arm"] == "kit" and c in g.get("story_vs_check", {})]
            o = [g["story_vs_check"][c]["passed"] for g in k if g["story_vs_check"][c]["opened_source"]]
            no = [g["story_vs_check"][c]["passed"] for g in k if not g["story_vs_check"][c]["opened_source"]]
            nn = [bool(g["checks"].get(c)) for g in frun if g["task"] == t and g["arm"] == "none" and c in g.get("checks", {})]
            L.append(f"| {c} | {frac(o)} | {frac(no)} | {frac(nn)} |")
    L.append("")
    # verdict per check
    L.append("### Verdict per check (plan.md: helps = kit above none by 2+ of 3 runs in more than one lane)\n")
    L.append("| check | lanes where kit > none by 2+ | lanes where none > kit by 2+ | verdict |"); L.append("|---|---|---|---|")
    for t in TASKS:
        for c in checks_of(t, frun):
            up, down = [], []
            for l in LANES_ALL:
                n, k = cell(frun, t, c, l, "none"), cell(frun, t, c, l, "kit")
                if not n or not k: continue
                if sum(k) - sum(n) >= 2: up.append(l)
                if sum(n) - sum(k) >= 2: down.append(l)
            kr = [g for g in frun if g["task"] == t and g["arm"] == "kit" and c in g.get("story_vs_check", {})]
            opened = [g for g in kr if g["story_vs_check"][c]["opened_source"]]
            opened_fail = [g for g in opened if not g["story_vs_check"][c]["passed"]]
            if len(up) >= 2: v = "helps"
            elif opened and len(opened_fail) >= max(2, len(opened) // 2): v = "opened but not applied"
            else: v = "no difference"
            if down: v += " (kit worse in " + ", ".join(down) + ")"
            L.append(f"| {c} | {', '.join(up) or '-'} | {', '.join(down) or '-'} | {v} |")
    L.append("")
    walls = [g.get("wall_s") or 0 for g in frun]
    L.append(f"Full round: {len(frun)} graded runs, {sum(walls)//60} min of agent time.")
sw = [g.get("wall_s") or 0 for g in srun] if srun else []
L.append(f"Screening: {len(srun or [])} graded runs, {sum(sw)//60} min of agent time.")
open(os.path.join(D, "results-table.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
