#!/usr/bin/env python3
"""Allowlist HTTPS proxy for the offline runs.

usage: proxy.py <portfile> <logfile> <allowed-host> [<allowed-host> ...]

Listens on 127.0.0.1 (a free port, written to <portfile>). A CONNECT to an allowed host on
port 443 is tunnelled; anything else (another host, another port, a plain-HTTP request) gets
"403 Forbidden" and is logged. One JSON line per request in <logfile>: time, method, host,
port, allowed. The sandbox profile (offline.sb) lets the agent's process tree open TCP
connections only to this port, so the proxy is the only way out.
"""
import asyncio, json, sys, time

PORTFILE, LOGFILE, ALLOWED = sys.argv[1], sys.argv[2], {h.lower() for h in sys.argv[3:]}

def log(method, host, port, allowed):
    with open(LOGFILE, "a") as f:
        f.write(json.dumps({"t": round(time.time(), 1), "method": method, "host": host,
                            "port": port, "allowed": allowed}) + "\n")

async def pipe(r, w):
    try:
        while True:
            b = await r.read(65536)
            if not b:
                break
            w.write(b)
            await w.drain()
    except Exception:
        pass
    finally:
        try:
            w.close()
        except Exception:
            pass

async def handle(cr, cw):
    try:
        head = await asyncio.wait_for(cr.readuntil(b"\r\n\r\n"), 30)
    except Exception:
        cw.close(); return
    line = head.split(b"\r\n", 1)[0].decode("latin-1")
    parts = line.split()
    method = parts[0].upper() if parts else "?"
    target = parts[1] if len(parts) > 1 else ""
    if method == "CONNECT":
        host, _, port = target.rpartition(":")
        host = host.strip("[]").lower()
        port = int(port) if port.isdigit() else 0
    else:  # plain HTTP through the proxy: never allowed
        host = target.split("//", 1)[-1].split("/", 1)[0].lower(); port = 80
    ok = method == "CONNECT" and host in ALLOWED and port == 443
    log(method, host, port, ok)
    if not ok:
        cw.write(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
        await cw.drain(); cw.close(); return
    try:
        ur, uw = await asyncio.wait_for(asyncio.open_connection(host, port), 30)
    except Exception:
        cw.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n"); await cw.drain(); cw.close(); return
    cw.write(b"HTTP/1.1 200 Connection established\r\n\r\n"); await cw.drain()
    await asyncio.gather(pipe(cr, uw), pipe(ur, cw))

async def main():
    srv = await asyncio.start_server(handle, "127.0.0.1", 0)
    with open(PORTFILE, "w") as f:
        f.write(str(srv.sockets[0].getsockname()[1]))
    async with srv:
        await srv.serve_forever()

asyncio.run(main())
