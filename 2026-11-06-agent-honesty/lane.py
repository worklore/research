#!/usr/bin/env python3
"""Run one lane's full matrix, in shuffled order so time of day doesn't line up with a condition. Resumable:
finished runs are skipped. Stops after 3 usage-limit answers in a row, so a limit can't eat the rest of the lane.
usage: lane.py <lane> <parallel>"""
import itertools, json, os, random, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

H = os.path.dirname(os.path.abspath(__file__))
HONEST = [f"{a}-{b}" for a, b in itertools.product(("short", "free"), ("hidden", "shown"))]


def matrix(lane):
    jobs = []
    if lane != "claude":
        jobs += [("honest", c, t, r) for c in HONEST for t in ("h1", "h2", "h3", "h4", "h5") for r in range(1, 4)]
        jobs += [("reject", c, t, r) for c in ("neutral", "ad") for t in ("r2", "r3") for r in range(1, 5)]
    jobs += [("pick", c, "p1", r) for c in ("neutral", "ad", "order", "instructions") for r in range(1, 9)]
    random.Random(f"honesty-{lane}").shuffle(jobs)
    return jobs


def status(lane, job):
    exp, cond, task, rep = job
    try:
        return json.load(open(os.path.join(H, "runs", lane, exp, cond, f"{task}-r{rep}", "row.json")))["status"]
    except (OSError, ValueError, KeyError):
        return None


def main(lane, parallel):
    jobs = [j for j in matrix(lane) if status(lane, j) in (None, "ratelimited")]
    print(f"{lane}: {len(jobs)} runs to do", flush=True)
    state = {"limited": 0, "stop": False}

    def one(job):
        if state["stop"]:
            return
        subprocess.run([sys.executable, os.path.join(H, "run.py"), lane, job[0], job[1], job[2], str(job[3])])
        if status(lane, job) == "ratelimited":
            state["limited"] += 1
            if state["limited"] >= 3:
                state["stop"] = True
                print(f"{lane}: STOPPED, usage limit", flush=True)
        else:
            state["limited"] = 0

    with ThreadPoolExecutor(parallel) as pool:
        list(pool.map(one, jobs))
    print(f"LANE_DONE {lane}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
