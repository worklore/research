#!/usr/bin/env python3
"""Privacy-policy pilot: the three checks from the story
https://worklore.dev/s/2026-10-27-a-reader-found-three-gaps-in-my-privacy-policy-the-same-thre
run over remote MCP servers from the 2026-10-06 registry scan (random-1000/contracts.jsonl).

Per server (website + MCP endpoint), without reading any source code:
  door      the policy URL, and how many pages of the site link to it in the HTML (no JS)
  negatives every "do not / never / not used" sentence, and whether a sentence in the same
            section says what IS done with the same data (a model judges; the script lists)
  freetext  tools/list without sign-in: the string arguments of each tool, and whether the
            policy names the tools, their inputs, and any outward destination at all

Outputs in this folder: results.jsonl (one row per host), report.md, run.log.
python3 pilot.py [N] [--no-model]
"""
import concurrent.futures as cf, html, json, os, random, re, subprocess, sys, time, urllib.parse, urllib.request
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SCAN = os.path.join(HERE, "..", "2026-10-06-mcp-scan", "random-1000", "contracts.jsonl")
N = int(next((a for a in sys.argv[1:] if a.isdigit()), "100"))
USE_MODEL = "--no-model" not in sys.argv
UA = "worklore-privacy-check/1 (+https://worklore.dev; three read-only checks of a public privacy page)"
TIMEOUT = 15
PATHS = ["/privacy", "/privacy.html", "/privacy-policy", "/privacy-policy.html", "/legal/privacy", "/legal/privacy-policy", "/policies/privacy", "/privacy/"]
NEG = re.compile(r"\b(do not|does not|don't|doesn't|never|not used|not use|no longer|will not|won't|isn't|aren't|is not|are not)\b", re.I)
OUTWARD = re.compile(r"\b(public|publicly|publish|post|posted|share|shared|third[- ]part|display|visible|forum|feed)\b", re.I)
LOG = open(os.path.join(HERE, "run.log"), "a")


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


def get(url, accept="text/html,*/*", data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept": accept, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.geturl(), r.status, r.read(1_500_000).decode("utf-8", "ignore")


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self._a = None
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._a = [dict(attrs).get("href") or "", ""]
    def handle_data(self, d):
        if self._a: self._a[1] += d
    def handle_endtag(self, tag):
        if tag == "a" and self._a:
            self.links.append((self._a[0], self._a[1].strip())); self._a = None


def links_of(page, base):
    p = Links()
    try: p.feed(page)
    except Exception: pass
    return [(urllib.parse.urljoin(base, h), t) for h, t in p.links if h and not h.startswith(("mailto:", "javascript:", "tel:"))]


def norm(u):
    p = urllib.parse.urlsplit(u)
    path = re.sub(r"(index\.html?|\.html?|/)$", "", p.path.lower()) or "/"
    return p.netloc.lower().replace("www.", "") + path


def text_of(page):
    page = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", page, flags=re.S | re.I)
    page = re.sub(r"<(h[1-3])[^>]*>", r"\n\n## ", page, flags=re.I)
    page = re.sub(r"</(p|li|h[1-6]|div|tr|br)[^>]*>", "\n", page, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", page))
    t = re.sub(r"[ \t]+", " ", t); t = re.sub(r"\n\s*\n+", "\n\n", t)
    return t.strip()


def find_policy(site):
    try:
        final, _, home = get(site)
    except Exception as e:
        return None, None, f"home: {type(e).__name__}"
    host = urllib.parse.urlsplit(final).netloc
    PW = ("privacy", "integritet", "datenschutz", "privacidad", "confidentialit", "プライバシー", "конфиденциальност", "privatlivs", "personvern", "tietosuoja", "gizlilik", "隐私")
    isp = lambda u, t: any(w in (u + " " + t).lower() for w in PW)
    cands = [u for u, t in links_of(home, final) if isp(u, t) and urllib.parse.urlsplit(u).netloc.replace("www.", "") == host.replace("www.", "")]
    cands += [u for u, t in links_of(home, final) if isp(u, t)]  # off-host (legal subdomain, notion) as a fallback
    for u in cands + [urllib.parse.urljoin(final, p) for p in PATHS]:
        try:
            pf, st, body = get(u)
            if st == 200 and any(w in body.lower() for w in PW) and len(text_of(body)) > 600:
                return pf, (final, home), None
        except Exception:
            continue
    return None, (final, home), "no policy page found"


def site_pages(final, home, cap=40):
    pages = []
    try:
        _, _, sm = get(urllib.parse.urljoin(final, "/sitemap.xml"), accept="application/xml,text/xml,*/*")
        pages = re.findall(r"<loc>\s*([^<\s]+)", sm)
        if pages and pages[0].endswith(".xml"):  # a sitemap index: take the first child
            _, _, sm = get(pages[0], accept="application/xml,*/*"); pages = re.findall(r"<loc>\s*([^<\s]+)", sm)
    except Exception:
        pages = []
    if not pages:
        host = urllib.parse.urlsplit(final).netloc.replace("www.", "")
        pages = [u for u, _ in links_of(home, final) if urllib.parse.urlsplit(u).netloc.replace("www.", "") == host and "#" not in u]
    seen, out = set(), []
    for u in [final] + pages:
        k = norm(u)
        if k not in seen:
            seen.add(k); out.append(u)
    return out[:cap]


def door(policy_url, final, home):
    pages = site_pages(final, home)
    pk = norm(policy_url)
    without, checked = [], 0
    def one(u):
        try:
            pf, _, body = get(u)
        except Exception:
            return u, None
        hit = any(norm(h) == pk for h, _ in links_of(body, pf))
        return u, hit
    with cf.ThreadPoolExecutor(6) as ex:
        for u, hit in ex.map(one, pages):
            if hit is None: continue
            checked += 1
            if not hit: without.append(u)
    return {"pages_checked": checked, "pages_without_link": len(without), "without": without[:10]}


def negatives(ptxt):
    out, section = [], "(top)"
    for block in ptxt.split("\n\n"):
        if block.startswith("## "):  # the heading line, then that section's first paragraph
            head, _, block = block[3:].partition("\n")
            section = head.strip()[:80]
        for s in re.split(r"(?<=[.!?])\s+", block.replace("\n", " ")):
            s = s.strip()
            if 25 < len(s) < 600 and NEG.search(s):
                out.append({"section": section, "sentence": s})
    return out[:40]


def tools_list(url):
    if not url: return {"status": "no endpoint"}
    body = lambda o: json.dumps(o).encode()
    H = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    try:
        _, st, r = get(url, data=body({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "worklore-privacy-check", "version": "1"}}}), headers=H)
    except urllib.error.HTTPError as e:
        return {"status": "auth required" if e.code in (401, 403) else f"http {e.code}"}
    except Exception as e:
        return {"status": f"error: {type(e).__name__}"}
    try:
        _, st, r = get(url, data=body({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}), headers=H)
        m = re.search(r"\{.*\}", r, re.S); d = json.loads(m.group(0))
        tools = d.get("result", {}).get("tools", [])
    except urllib.error.HTTPError as e:
        return {"status": "auth required" if e.code in (401, 403) else f"http {e.code}"}
    except Exception as e:
        return {"status": f"error: {type(e).__name__}"}
    out = []
    for t in tools:
        props = (t.get("inputSchema") or {}).get("properties") or {}
        strs = [k for k, v in props.items() if (v or {}).get("type") == "string" or "string" in str((v or {}).get("type", ""))]
        out.append({"name": t["name"], "string_args": strs, "desc": (t.get("description") or "")[:200]})
    return {"status": "ok", "tools": out}


def freetext(ptxt, tl):
    low = ptxt.lower()
    res = {"mentions_agent_or_mcp": bool(re.search(r"\b(mcp|agent|tool call|assistant|connector)\b", low)),
           "outward_words": sorted(set(w.lower() for w in OUTWARD.findall(ptxt)))[:12]}
    if tl.get("status") == "ok":
        names = [t["name"] for t in tl["tools"]]
        args = sorted(set(a for t in tl["tools"] for a in t["string_args"]))
        res.update({"tools": len(names), "tools_named_in_policy": [n for n in names if n.lower() in low or n.replace("_", " ").lower() in low],
                    "string_args": len(args), "string_args_named_in_policy": [a for a in args if len(a) > 3 and (a.lower() in low or a.replace("_", " ").lower() in low)]})
    return res


def model_pass(host, ptxt, negs, tl):
    if not USE_MODEL or not negs: return None
    tools = [{"name": t["name"], "string_args": t["string_args"]} for t in tl.get("tools", [])][:40]
    prompt = f"""You are checking a privacy policy with three read-only checks. Answer in JSON only, no prose.

POLICY TEXT (sections start with "## "):
{ptxt[:14000]}

NEGATIVE SENTENCES FOUND (index, section, sentence):
{json.dumps(negs, ensure_ascii=False)}

MCP TOOLS THE SERVER EXPOSES WITHOUT SIGN-IN (name, string arguments), may be empty:
{json.dumps(tools)}

Return this JSON:
{{"negatives": [{{"i": <index>, "has_positive": true|false, "positive": "<the sentence in the SAME section that says what IS done with the same data, or empty>"}}],
 "conflicts": [{{"a": "<sentence>", "b": "<sentence>", "data": "<what both could govern>"}}],
 "unnamed_inputs": ["<tool or string argument whose text is never described in the policy: where it goes, who sees it>"],
 "outward_unnamed": "<one sentence: any place the policy's own text implies user text goes outward (public page, another network, a third party) without naming it, or empty>",
 "register": "<one sentence: does the policy mostly say what is NOT done, or what IS done?>"}}
Rules: a positive must be in the same section and about the same data. Boilerplate negatives (children, selling data) count as having a positive only if the section says what is done instead. Be literal; do not invent sentences."""
    try:
        r = subprocess.run(["claude", "-p", "--model", "haiku", "--tools", "", "--output-format", "text"], input=prompt, capture_output=True, text=True, timeout=240,
                           env={**os.environ, "EVAL_NO_SECRETS": "1"})
        m = re.search(r"\{.*\}", r.stdout, re.S)
        return json.loads(m.group(0)) if m else {"error": "no json", "raw": r.stdout[:300], "stderr": r.stderr[:200]}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"[:200]}


def one_host(row):
    s = row["server"]; site = s["website"]; host = urllib.parse.urlsplit(site).netloc
    res = {"host": host, "server": s["name"], "website": site, "endpoint": s.get("url"), "repo": s.get("repo")}
    policy, homeinfo, err = find_policy(site)
    res["policy_url"] = policy; res["policy_error"] = err
    if homeinfo and policy:
        final, home = homeinfo
        res["door"] = door(policy, final, home)
        try:
            _, _, pbody = get(policy); ptxt = text_of(pbody)
        except Exception as e:
            ptxt = ""; res["policy_error"] = f"policy fetch: {type(e).__name__}"
        res["policy_chars"] = len(ptxt)
        res["negatives"] = negatives(ptxt)
    else:
        ptxt = ""
    res["tools_list"] = tools_list(s.get("url"))
    if ptxt:
        res["freetext"] = freetext(ptxt, res["tools_list"])
        res["_ptxt"] = ptxt
    return res


def main():
    rows = [json.loads(l) for l in open(SCAN) if l.strip()]
    rows = [r for r in rows if r.get("server", {}).get("website")]
    random.Random(8).shuffle(rows)
    seen, pick = set(), []
    for r in rows:
        h = urllib.parse.urlsplit(r["server"]["website"]).netloc.replace("www.", "")
        if h and h not in seen:
            seen.add(h); pick.append(r)
        if len(pick) >= N: break
    out = os.path.join(HERE, "results.jsonl")
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["host"] for l in open(out) if l.strip()}
    log(f"pilot: {len(pick)} hosts, {len(done)} already done, model={'on' if USE_MODEL else 'off'}")
    todo = [r for r in pick if urllib.parse.urlsplit(r["server"]["website"]).netloc not in done]
    with cf.ThreadPoolExecutor(5) as ex, open(out, "a") as f:
        for res in ex.map(lambda r: _safe(one_host, r), todo):
            if res is None: continue
            ptxt = res.pop("_ptxt", "")
            if ptxt and res.get("negatives"):
                res["model"] = model_pass(res["host"], ptxt, res["negatives"], res["tools_list"])
            f.write(json.dumps(res, ensure_ascii=False) + "\n"); f.flush()
            d = res.get("door") or {}
            log(f"{res['host']}: policy={'yes' if res.get('policy_url') else 'NO'} door={d.get('pages_without_link','-')}/{d.get('pages_checked','-')} without link, negatives={len(res.get('negatives') or [])}, tools={res['tools_list'].get('status')}")
    log("fetch+model done; writing report")
    report()


def _safe(fn, r):
    try: return fn(r)
    except Exception as e:
        log(f"FAILED {r['server'].get('website')}: {type(e).__name__}: {e}"); return None


def report():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "results.jsonl")) if l.strip()]
    n = len(rows); withp = [r for r in rows if r.get("policy_url")]
    lines = [f"# Privacy checks pilot: {n} remote MCP servers from the registry scan\n",
             f"Run {time.strftime('%Y-%m-%d')}. Checks from https://worklore.dev/s/2026-10-27-a-reader-found-three-gaps-in-my-privacy-policy-the-same-thre, no source read.\n",
             f"- policy page found: {len(withp)} of {n}",
             f"- tools/list answered without sign-in: {sum(1 for r in rows if r['tools_list'].get('status') == 'ok')} of {n}; auth required: {sum(1 for r in rows if r['tools_list'].get('status') == 'auth required')}",
             f"- door: policy linked from every checked page on {sum(1 for r in withp if (r.get('door') or {}).get('pages_without_link') == 0)} of {len(withp)} sites; home page without a link on {sum(1 for r in withp if (r.get('door') or {}).get('without') and norm(r['door']['without'][0]) == norm(r['website']))}",
             f"- negatives: {sum(len(r.get('negatives') or []) for r in withp)} negative sentences across {len(withp)} policies; the model's 'without a positive counterpart' count ({sum(1 for r in withp for x in ((r.get('model') or {}).get('negatives') or []) if not x.get('has_positive'))}) held for 1 of 8 in the hand check (hand-check.md), so it is not a result",
             f"- conflicting sentence pairs: {sum(len((r.get('model') or {}).get('conflicts') or []) for r in withp)} across {sum(1 for r in withp if (r.get('model') or {}).get('conflicts'))} policies (hand check: 4 of 7 hold); typed text going somewhere unnamed: {sum(1 for r in withp if ((r.get('model') or {}).get('outward_unnamed') or '').strip())} policies (hand check: 4 of 5 hold)",
             f"- policies that mention an agent, MCP or tool calls at all: {sum(1 for r in withp if (r.get('freetext') or {}).get('mentions_agent_or_mcp'))} of {len(withp)}",
             "", "| host | policy | pages without link / checked | negatives (no positive) | conflicts | tools (named in policy) | unnamed inputs (model) |", "|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r.get("policy_url") is None, -((r.get("door") or {}).get("pages_without_link") or 0))):
        d = r.get("door") or {}; m = r.get("model") or {}; ft = r.get("freetext") or {}; tl = r["tools_list"]
        nneg = len(r.get("negatives") or []); nnop = sum(1 for x in (m.get("negatives") or []) if not x.get("has_positive"))
        tools = f"{ft.get('tools')} ({len(ft.get('tools_named_in_policy') or [])})" if tl.get("status") == "ok" and ft else tl.get("status", "-")
        lines.append(f"| {r['host']} | {'[yes](' + r['policy_url'] + ')' if r.get('policy_url') else 'none'} | {d.get('pages_without_link','-')} / {d.get('pages_checked','-')} | {nneg} ({nnop}) | {len(m.get('conflicts') or [])} | {tools} | {', '.join((m.get('unnamed_inputs') or [])[:4])} |")
    open(os.path.join(HERE, "report.md"), "w").write("\n".join(lines) + "\n")
    log(f"report.md written: {n} rows")


if __name__ == "__main__":
    main()
