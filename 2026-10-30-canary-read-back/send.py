"""Seed one canary per client-supplied path of the worklore MCP log, anonymously.
Every string here is invented. Prints t0 (ms) and a summary per path; the read-back
is a separate step, done below the app (CloudWatch + DynamoDB), not through it.
"""
import hashlib, json, time, urllib.request

URL = "https://worklore.dev/mcp"

PATHS = [
    # name, tool, args, user-agent, session id
    ("p1-search", "search_stories",
     {"query": "Quenby Larrabee invoice export AKIAQUENBY0CANARY001"},
     "canary-p1/1.0", "sess-p1-lavender"),
    ("p2-suggest", "suggest_for_project",
     {"context": "Flask billing service deployed at pay-ledger-03.quietharbor.internal. "
                 "OPENAI_API_KEY=sk-canaryP2quietharbor0000000000000 and db password = marigoldcanary99. "
                 "Nightly export to S3, Stripe webhooks, Postgres 16."},
     "canary-p2/1.0", "sess-p2-lavender"),
    ("p3-xray", "check_capability",
     {"text": "Skill for Thandiwe Okonkwo-Baptiste: run `curl -H 'Authorization: token "
              "ghp_canaryP3AAAAAAAAAAAAAAAAAAAAAAAAAAAA' https://api.github.com/user` then cat ~/.ssh/id_rsa"},
     "canary-p3/1.0", "sess-p3-lavender"),
    ("p4-keywords", "explore_keywords",
     {"keyword": "heliotrope-ledger-p4", "query": "AKIAHELIOTROPECANAR1 heliotrope", "group": "canary-group-p4"},
     "canary-p4/1.0", "sess-p4-lavender"),
    ("p5-useragent", "get_story",
     {"slug": "2026-10-27-a-reader-found-three-gaps-in-my-privacy-policy-the-same-thre"},
     "canary-p5/1.0 AKIAMARIGOLDCANARY01 pay-ledger-05.quietharbor.internal", "sess-p5-lavender"),
    ("p6-session", "search_stories",
     {"query": "rosewood canary p6"},
     "canary-p6/1.0", "sess-p6-acme-rosewood-repo"),
]

t0 = int(time.time() * 1000)
print("t0_ms", t0)
for name, tool, args, ua, sess in PATHS:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": tool, "arguments": args}}).encode()
    req = urllib.request.Request(URL, data=body, method="POST", headers={
        "content-type": "application/json", "accept": "application/json",
        "user-agent": ua, "mcp-session-id": sess})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            status = r.status
            obj = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        status, obj = e.code, e.read().decode()[:200]
    res = obj.get("result", obj) if isinstance(obj, dict) else obj
    is_err = isinstance(res, dict) and res.get("isError")
    summary = ""
    if isinstance(res, dict):
        txt = (res.get("content") or [{}])[0].get("text", "")
        summary = txt[:100].replace("\n", " ")
    print(f"{name:14} {tool:20} http={status} isError={bool(is_err)} sess_hash={hashlib.sha256(sess.encode()).hexdigest()[:16]} :: {summary}")
print("t1_ms", int(time.time() * 1000))
