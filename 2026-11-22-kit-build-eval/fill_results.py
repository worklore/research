#!/usr/bin/env python3
"""Fills the data-dependent placeholders in results.md (Kimi cells, all-lane totals, source-story
columns, run totals) from runs/*/grade.json. Run after make_table.py. usage: fill_results.py"""
import glob, json, os, re
D = os.path.dirname(os.path.abspath(__file__))
G = []
for p in glob.glob(os.path.join(D, "runs", "[sf]-t*", "grade.json")):
    g = json.load(open(p)); g["phase"] = g["id"].split("-")[0]
    if not g.get("limit"): G.append(g)
F = [g for g in G if g["phase"] == "f"]
def c(lane, task, check, arm):
    xs = [bool(g["checks"].get(check)) for g in F if g["lane"] == lane and g["task"] == task and g["arm"] == arm and check in g["checks"]]
    return f"{sum(xs)}/{len(xs)}", xs
def pair(lane, task, check):
    (a, _), (b, _) = c(lane, task, check, "none"), c(lane, task, check, "kit")
    return f"{a} vs {b}"
def allp(task, check):
    n = [bool(g["checks"].get(check)) for g in F if g["task"] == task and g["arm"] == "none" and check in g["checks"]]
    k = [bool(g["checks"].get(check)) for g in F if g["task"] == task and g["arm"] == "kit" and check in g["checks"]]
    return f"{sum(n)}/{len(n)} vs {sum(k)}/{len(k)}"
def src(check, opened):
    xs = [g["story_vs_check"][check]["passed"] for g in F if g["arm"] == "kit" and check in g.get("story_vs_check", {}) and g["story_vs_check"][check]["opened_source"] == opened]
    return f"{sum(xs)}/{len(xs)}"
def none(check):
    xs = [bool(g["checks"].get(check)) for g in F if g["arm"] == "none" and check in g["checks"]]
    return f"{sum(xs)}/{len(xs)}"
s = open(os.path.join(D, "results.template.md")).read()
M = {"T3A": ("t3", "t3a_one_structured_line_per_call"), "T3B": ("t3", "t3b_no_personal_data_in_logs"),
     "T5A": ("t5", "t5a_valid_server_json"), "T5B": ("t5", "t5b_description_le_100"), "T5C": ("t5", "t5c_github_org_namespace"),
     "T5D": ("t5", "t5d_version_matches"), "T5E": ("t5", "t5e_mcpname_matches"), "T5F": ("t5", "t5f_readme_read_org_token")}
for k, (t, ch) in M.items():
    s = s.replace(f"KIMI_{k}_ALL", allp(t, ch)).replace(f"KIMI_{k}", pair("kimi", t, ch))
    s = s.replace(f"NOSRC_{k}", src(ch, False)).replace(f"SRC_{k}", src(ch, True)).replace(f"NONE_{k}", none(ch))
kimi = [g for g in F if g["lane"] == "kimi"]
missing = 24 - len(kimi)
note = "" if missing == 0 else "\n\n" + (f"> **Kimi is incomplete:** {missing} of its 24 full-round runs are missing, because its subscription hit the "
        "5-hour usage limit at 03:32 and the relaunches did not get through before this write-up. "
        "Kimi cells with 2 runs say so (x/2).")
s = s.replace("KIMI_NOTE", note)
walls = sum(g.get("wall_s") or 0 for g in G)
S = [g for g in G if g["phase"] == "s"]
lim = len(glob.glob(os.path.join(D, "runs", "limit-*")))
tot = (f"- Graded runs: {len(S)} screening + {len(F)} full round = {len(S) + len(F)}; plus 2 pilot runs, 5 offline "
       f"proofs, and {lim} Kimi attempts stopped by its quota limit (1 cut mid-run at 03:32, then {lim - 1} relaunches that hit the "
       "same limit within seconds); their cells were rerun after the reset and the stopped attempts are not counted.\n"
       f"- Agent time: {walls // 60} min in total. Median per run: sonnet 25 s, haiku 87 s, codex 91 s, "
       "deepseek about 3 min, kimi 5 min.\n"
       "- Wall clock on 2026-11-22: set-up, fixture, graders and controls 00:25-00:50; screening 00:50-02:05; "
       "full round 01:38-03:41 for four lanes. Kimi hit its subscription's 5-hour usage limit at 03:32 with 4 runs "
       "to go; the supervisor retried every 45 min, and the quota came back at 07:18. The last run ended at 07:37. "
       "Lanes ran in parallel, one run at a time per lane.")
s = s.replace("TOTALS", tot)
open(os.path.join(D, "results.md"), "w").write(s)
print("filled;", "kimi runs", len(kimi), "missing", missing)
