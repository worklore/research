#!/usr/bin/env python3
"""Writes the public proof for one lane's offline check: the agent's final answer, its tool calls and
the proxy log, with the home path masked. usage: verify_report.py <run dir> <lane>"""
import json, os, re, sys
R, L = sys.argv[1], sys.argv[2]
HOME = os.environ["HOME"]
def mask(s): return re.sub(r"/(?:private/)?tmp/[A-Za-z0-9._-]+", "<tmp>", s.replace(HOME, "~"))
log = open(os.path.join(R, "private", "agent.log"), errors="replace").read().splitlines()
answer, calls = "", []
for line in log:
    try: d = json.loads(line)
    except ValueError: continue
    if d.get("type") == "result" and isinstance(d.get("result"), str): answer = d["result"]
    if d.get("type") == "assistant":
        for c in d.get("message", {}).get("content", []) or []:
            if c.get("type") == "tool_use": calls.append(f"{c['name']} {json.dumps(c.get('input'))[:200]}")
            if c.get("type") == "text": answer = answer or ""
    if d.get("role") == "assistant":
        if d.get("content"): answer = d["content"] if isinstance(d["content"], str) else json.dumps(d["content"])
        for tc in d.get("tool_calls") or []: calls.append(f"{tc['function']['name']} {tc['function'].get('arguments','')[:200]}")
    if d.get("type") == "item.completed" and d.get("item", {}).get("type") == "command_execution": calls.append("shell " + d["item"]["command"][:200])
    if d.get("type") == "item.completed" and d.get("item", {}).get("type") in ("web_search", "web_fetch"): calls.append("WEB " + json.dumps(d["item"])[:200])
f = os.path.join(R, "private", "final.txt")
if os.path.exists(f): answer = open(f).read()
print(f"# offline check, lane {L}\n\n## tool calls\n" + "\n".join(mask(c) for c in calls))
print("\n## final answer\n" + mask(answer))
p = os.path.join(R, "proxy.log")
print("\n## proxy log (host, allowed)\n" + ("\n".join(mask(l) for l in open(p).read().splitlines()) if os.path.exists(p) else "(no proxy: codex uses its own sandbox)"))
