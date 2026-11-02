#!/usr/bin/env python3
"""Second round on the same random 1,000 (random-1000/): still anonymous, still no tools/call.

Open servers (answered initialize):
  - tool descriptions scanned with skill-xray's behavioral signals (injection / exfil / manipulation phrasing)
    plus a few MCP-specific "tool poisoning" patterns; hits are saved for a human to read
  - weight of tools/list (bytes, ~tokens = bytes/4)
  - protocol hygiene: ping; unknown method -> JSON-RPC error; malformed JSON -> JSON-RPC parse error
    (not HTML / 500); a made-up Mcp-Session-Id -> 404 (only if the server issues sessions)
  - Origin: initialize with Origin: https://evil.example (spec says servers MUST validate Origin;
    for public remote servers rejecting foreign origins is debatable, so this is reported as an observation)
Closed servers (401/403 at initialize): can a client discover how to sign in?
  WWW-Authenticate resource_metadata -> protected-resource metadata -> authorization-server metadata
  -> PKCE S256 + a way to register a client (DCR registration_endpoint or client ID metadata documents).
"""
import concurrent.futures as cf, json, os, re, sys, urllib.error, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan import rpc, INIT, UA
import importlib.util
sys.path.insert(1, os.path.expanduser("~/projects/skill-xray/scanner"))  # for its behavioral_signals import
spec = importlib.util.spec_from_file_location("sx", os.path.expanduser("~/projects/skill-xray/scanner/scan.py"))
sx = importlib.util.module_from_spec(spec); sys.modules["sx"] = sx; spec.loader.exec_module(sx)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "random-1000")
POISON = [
    ("hidden-tag", re.compile(r"<\s*(important|system|instructions?|secret|hidden)\s*>", re.I)),
    ("ignore-previous", re.compile(r"ignore (all |any )?(previous|prior|above|other) (instructions|rules)", re.I)),
    ("do-not-tell", re.compile(r"(do not|don't|never) (tell|inform|mention|reveal|show)( this)? (to )?(the )?user", re.I)),
    ("secret-paths", re.compile(r"~/\.ssh|id_rsa|\.aws/credentials|\.env\b|mcp\.json|claude_desktop_config", re.I)),
    ("other-tools", re.compile(r"(instead of|before (using|calling)) (any )?other tools?|always (call|use) this tool (first|before)", re.I)),
]

def raw_post(url, data, headers):
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "User-Agent": UA}
    h.update(headers)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h, method="POST"), timeout=15)
        return r.status, r.headers.get("Content-Type", ""), r.read(20000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read(20000).decode("utf-8", "replace")
    except Exception as e:
        return None, "", type(e).__name__

def jsonrpc_error(body):
    for chunk in [body] + [l[5:] for l in body.splitlines() if l.startswith("data:")]:
        try:
            m = json.loads(chunk)
            if isinstance(m, dict) and "error" in m:
                return m["error"].get("code")
        except Exception:
            pass
    return None

def get_json(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"}), timeout=15)
        return json.loads(r.read(500000))
    except Exception:
        return None

def open_server(s):
    url = s["url"]; out = {"url": url, "name": s["name"], "repo": s["repo"]}
    init = rpc(url, "initialize", INIT); sid = init.get("sid")
    rpc(url, "notifications/initialized", None, sid, notify=True)
    tl = rpc(url, "tools/list", {}, sid)
    tools = (((tl.get("msg") or {}).get("result") or {}).get("tools") or [])
    blob = json.dumps(tools)
    out["tools"] = len(tools); out["tools_bytes"] = len(blob)
    hits = []
    for t in tools:
        text = f"{t.get('name','')}\n{t.get('description') or ''}\n{json.dumps(t.get('inputSchema') or {})}"
        for b in sx.behavioral_scan(text, t.get("name", "?")):
            hits.append({"tool": t.get("name"), "signal": b["id"], "evidence": b["evidence"][:200]})
        for pid, rx in POISON:
            m = rx.search(text)
            if m:
                hits.append({"tool": t.get("name"), "signal": "mcp-" + pid, "evidence": text[max(0, m.start()-80):m.end()+80].replace("\n", " ")[:240]})
    out["desc_hits"] = hits
    out["empty_descriptions"] = sum(1 for t in tools if len((t.get("description") or "").strip()) < 10)
    p = rpc(url, "ping", {}, sid)
    out["ping_ok"] = isinstance(p.get("msg"), dict) and "result" in p["msg"]
    hdr = {"Mcp-Session-Id": sid} if sid else {}
    st, ct, body = raw_post(url, json.dumps({"jsonrpc": "2.0", "id": 9, "method": "checkup/no-such-method"}).encode(), hdr)
    out["unknown_method"] = {"status": st, "code": jsonrpc_error(body)}
    st, ct, body = raw_post(url, b'{"jsonrpc": "2.0", "id": 1, "method": ', hdr)
    out["malformed"] = {"status": st, "code": jsonrpc_error(body), "html": "html" in ct.lower() or body.lstrip().lower().startswith("<"),
                        "trace": bool(re.search(r"Traceback \(most recent|at [\w.$]+\(.*:\d+\)|\.py\", line \d+|node_modules/", body))}
    if sid:
        st, _, _ = raw_post(url, json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}}).encode(), {"Mcp-Session-Id": "checkup-made-up-session"})
        out["bogus_session_status"] = st
    st, _, body = raw_post(url, json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": INIT}).encode(), {"Origin": "https://evil.example"})
    out["foreign_origin_status"] = st
    out["foreign_origin_accepted"] = st == 200 and '"result"' in body
    return out

def closed_server(s):
    url = s["url"]; out = {"url": url, "name": s["name"], "repo": s["repo"]}
    st, ct, body = raw_post(url, json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": INIT}).encode(), {})
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": INIT}).encode(),
                                   headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "User-Agent": UA}, method="POST"), timeout=15)
        www = r.headers.get("WWW-Authenticate") or ""
    except urllib.error.HTTPError as e:
        www = e.headers.get("WWW-Authenticate") or ""
    except Exception:
        www = ""
    out["status"] = st; out["www_authenticate"] = bool(www)
    m = re.search(r'resource_metadata="([^"]+)"', www)
    pu = urllib.parse.urlparse(url)
    prm_url = m.group(1) if m else None
    prm = get_json(prm_url) if prm_url else None
    if not prm:
        for cand in (f"{pu.scheme}://{pu.netloc}/.well-known/oauth-protected-resource{pu.path}",
                     f"{pu.scheme}://{pu.netloc}/.well-known/oauth-protected-resource"):
            prm = get_json(cand)
            if prm:
                break
    out["prm"] = bool(prm); out["prm_from_header"] = bool(m)
    asm = None
    for a in ((prm or {}).get("authorization_servers") or []):
        ap = urllib.parse.urlparse(a); base = f"{ap.scheme}://{ap.netloc}"; path = ap.path.rstrip("/")
        for cand in (f"{base}/.well-known/oauth-authorization-server{path}", f"{base}/.well-known/openid-configuration{path}",
                     f"{a.rstrip('/')}/.well-known/openid-configuration", f"{base}/.well-known/oauth-authorization-server"):
            asm = get_json(cand)
            if asm:
                break
        if asm:
            break
    out["as_metadata"] = bool(asm)
    out["pkce_s256"] = "S256" in ((asm or {}).get("code_challenge_methods_supported") or [])
    out["dcr"] = bool((asm or {}).get("registration_endpoint"))
    out["cimd"] = bool((asm or {}).get("client_id_metadata_document_supported"))
    out["usable"] = out["prm"] and out["as_metadata"] and out["pkce_s256"] and (out["dcr"] or out["cimd"])
    return out

if __name__ == "__main__":
    rows = [json.loads(l) for l in open(os.path.join(OUT, "results.jsonl"))]
    opened = [r["server"] for r in rows if not r["facts"].get("closed") and not r["facts"].get("unreachable")]
    closed = [r["server"] for r in rows if r["facts"].get("closed")]
    with cf.ThreadPoolExecutor(8) as ex:
        a = list(ex.map(open_server, opened))
        b = list(ex.map(closed_server, closed))
    json.dump({"open": a, "closed": b}, open(os.path.join(OUT, "checks2.json"), "w"), indent=1)
    print(f"open {len(a)} · closed {len(b)}")
