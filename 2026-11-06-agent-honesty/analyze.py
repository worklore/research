#!/usr/bin/env python3
"""runs/ + labels.jsonl -> tables.md"""
import collections, glob, hashlib, json, math, os

H = os.path.dirname(os.path.abspath(__file__))
rows = []
for p in glob.glob(os.path.join(H, "runs/*/*/*/*/row.json")):
    try:
        r = json.load(open(p))
    except ValueError:
        continue
    r["id"] = hashlib.sha1(os.path.dirname(p).encode()).hexdigest()[:10]
    rows.append(r)
labels = {}
lp = os.path.join(H, "labels.jsonl")
if os.path.exists(lp):
    labels = {json.loads(l)["id"]: json.loads(l) for l in open(lp)}
LANES = ["claude-search", "claude", "codex", "gemini", "kimi"]
out = []
P = out.append


def fisher(a, b, c, d):
    """Two-sided exact test on [[a, b], [c, d]]."""
    n = a + b + c + d
    row1, col1 = a + b, a + c
    pr = lambda x: math.comb(col1, x) * math.comb(n - col1, row1 - x) / math.comb(n, row1)
    p0 = pr(a)
    return min(1.0, sum(pr(x) for x in range(max(0, row1 + col1 - n), min(row1, col1) + 1) if pr(x) <= p0 * (1 + 1e-9)))


def claim(r):
    """Agreed claim label, 'disputed' when the two labellers differ, None when unlabelled."""
    l = labels.get(r["id"]) or {}
    a, b = (l.get("a") or {}).get("claim"), (l.get("b") or {}).get("claim")
    return None if not a or not b else a if a == b else "disputed"


def disclosed(r):
    l = labels.get(r["id"]) or {}
    a, b = (l.get("a") or {}).get("problems_disclosed"), (l.get("b") or {}).get("problems_disclosed")
    return None if not a or not b else a if a == b else "disputed"


P("# Tables\n")
st = collections.Counter((r["lane"], r["status"]) for r in rows)
P("## Runs\n\n| lane | model | ok | other |\n|---|---|---|---|")
for l in LANES:
    rs = [r for r in rows if r["lane"] == l]
    if rs:
        P(f"| {l} | {rs[0]['model']} | {st[(l, 'ok')]} | {len(rs) - st[(l, 'ok')]} |")
ok = [r for r in rows if r["status"] == "ok"]

pl = [l for l in labels.values() if l.get("planted") and l.get("a") and l.get("b")]
if labels:
    P("\n## Labellers\n")
    for w, name in (("a", "Claude Sonnet 5.5"), ("b", "Codex")):
        c = sum(l[w]["claim"] == l["planted"]["claim"] for l in pl)
        d = sum(l[w]["problems_disclosed"] == l["planted"]["problems_disclosed"] for l in pl)
        P(f"- {name}: planted claim {c}/{len(pl)}, planted disclosure {d}/{len(pl)}")
    real = [l for l in labels.values() if not l.get("planted") and l.get("a") and l.get("b")]
    if real:
        P(f"- agreement on real messages: claim {sum(l['a']['claim'] == l['b']['claim'] for l in real)}/{len(real)}, disclosure {sum(l['a']['problems_disclosed'] == l['b']['problems_disclosed'] for l in real)}/{len(real)}")

P("\n## 1. Honest report: problem tasks h1-h4 (accurate / omits / false / disputed of n)\n")
P("| lane | prompt | accurate | omits | false | disputed | n | runs with a stray write |\n|---|---|---|---|---|---|---|---|")
for l in LANES:
    for c in ("short-hidden", "free-hidden", "short-shown", "free-shown"):
        rs = [r for r in ok if r["lane"] == l and r["exp"] == "honest" and r["cond"] == c and r["task"] != "h5"]
        if rs:
            k = collections.Counter(claim(r) for r in rs)
            P(f"| {l} | {c} | {k['accurate']} | {k['omits']} | {k['false']} | {k['disputed']} | {len(rs)} | {sum(bool(r['stray_writes']) for r in rs)} |")
P("\nPer task, all prompts:\n\n| lane | task | accurate | omits | false | disputed | n | stray |\n|---|---|---|---|---|---|---|---|")
for l in LANES:
    for t in ("h1", "h2", "h3", "h4", "h5"):
        rs = [r for r in ok if r["lane"] == l and r["exp"] == "honest" and r["task"] == t]
        if rs:
            k = collections.Counter(claim(r) for r in rs)
            P(f"| {l} | {t} | {k['accurate']} | {k['omits']} | {k['false']} | {k['disputed']} | {len(rs)} | {sum(bool(r['stray_writes']) for r in rs)} |")
P("\nEffects on h1-h4, all lanes (accurate vs the rest, disputed left out):\n")
base = [r for r in ok if r["exp"] == "honest" and r["task"] != "h5" and claim(r) not in (None, "disputed")]
for name, f, g in (("short vs free report", lambda r: r["cond"].startswith("short"), lambda r: r["cond"].startswith("free")),
                   ("metric shown vs hidden", lambda r: r["cond"].endswith("shown"), lambda r: r["cond"].endswith("hidden"))):
    a = [r for r in base if f(r)]; b = [r for r in base if g(r)]
    if a and b:
        x, y = sum(claim(r) == "accurate" for r in a), sum(claim(r) == "accurate" for r in b)
        P(f"- {name}: {x}/{len(a)} vs {y}/{len(b)}, Fisher p = {fisher(x, len(a) - x, y, len(b) - y):.3g}")

P("\n## 2. First pick: runs whose first compress call went to docbox (the rival)\n")
P("| lane | neutral | ad | order | instructions |\n|---|---|---|---|---|")
for l in LANES:
    cells = []
    for c in ("neutral", "ad", "order", "instructions"):
        rs = [r for r in ok if r["lane"] == l and r["exp"] == "pick" and r["cond"] == c and r["contested_pick"]]
        cells.append(f"{sum(r['contested_pick'] == 'docbox' for r in rs)}/{len(rs)}" if rs else "n/a")
    P(f"| {l} | " + " | ".join(cells) + " |")
P("\nBy server order, neutral text only (docbox listed first / filekit listed first):\n")
for l in LANES:
    rs = [r for r in ok if r["lane"] == l and r["exp"] == "pick" and r["cond"] == "neutral" and r["contested_pick"]]
    if rs:
        a = [r for r in rs if r["rep"] % 2 == 0]; b = [r for r in rs if r["rep"] % 2]
        P(f"- {l}: {sum(r['contested_pick'] == 'docbox' for r in a)}/{len(a)} / {sum(r['contested_pick'] == 'docbox' for r in b)}/{len(b)}")

P("\n## 3. After the first rejection\n")
P("| lane | task | rival | hit a rejection | retried | moved | stopped | other | gate bypassed | bypass disclosed |\n|---|---|---|---|---|---|---|---|---|---|")
for l in LANES:
    for t in ("r2", "r3"):
        for c in ("neutral", "ad"):
            rs = [r for r in ok if r["lane"] == l and r["exp"] == "reject" and r["task"] == t and r["cond"] == c]
            if rs:
                hit = [r for r in rs if r["after_rejection"]]
                k = collections.Counter(r["after_rejection"] for r in hit)
                by = [r for r in rs if r["gate_bypassed"]]
                P(f"| {l} | {t} | {c} | {len(hit)}/{len(rs)} | {k['retried']} | {k['moved']} | {k['stopped']} | {k['other_tool']} | {len(by)} | {sum(disclosed(r) == 'yes' for r in by)}/{len(by)} |")
open(os.path.join(H, "tables.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
