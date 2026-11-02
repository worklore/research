#!/usr/bin/env python3
"""A tiny, DELIBERATELY BROKEN MCP server (Streamable HTTP, JSON responses).

Test target for the read-only MCP checkup (research/drafts/mcp-checkup-story.md).
Stdlib only:   python3 broken_mcp_server.py [port]      (default 8765)
Token:         Authorization: Bearer test-token

Planted failures, each one a story on the worklore MCP path:
  1. EVERY method needs the token, tools/list included        (hid-its-own-tool-list)
  2. a tool refusal ("not found", missing argument) is a
     JSON-RPC error -32602, not a result with isError: true   (live-mcp-test-asserted-the-bug)
  3. get_item returns a Decimal nested in its result; the
     dispatcher catches the TypeError and answers isError,
     so the declared outputSchema is never honoured           (tests-passed-because-they-agreed)
  4. initialize echoes whatever protocolVersion it is sent    (price-of-one-more-endpoint)
  5. one tool name has a dot: search.items                    (price-of-one-more-endpoint / directories)
  6. no call logging at all                                   (one-url-analytics)
  7. serverInfo.version never moves; there is no surface lock (listing-said-read-only)
What it does RIGHT: a second call in the same session works after an error.
"""
import json
import sys
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = "Bearer test-token"
ITEMS = {
    "a1": {"id": "a1", "name": "Blue mug", "stock": 4,
           "price": {"amount": Decimal("12.50"), "currency": "EUR"}},
    "b2": {"id": "b2", "name": "Green pot", "stock": 0,
           "price": {"amount": Decimal("30.00"), "currency": "EUR"}},
}

TOOLS = [
    {"name": "get_item",
     "description": "Get one item by id.",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}},
                     "required": ["id"]},
     "outputSchema": {"type": "object", "properties": {
         "id": {"type": "string"}, "name": {"type": "string"}, "stock": {"type": "integer"},
         "price": {"type": "object", "properties": {"amount": {"type": "number"},
                                                    "currency": {"type": "string"}}}},
         "required": ["id", "name"]},
     "annotations": {"readOnlyHint": True, "destructiveHint": False}},
    {"name": "search.items",
     "description": "Search items by name.",
     "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}},
     "outputSchema": {"type": "object", "properties": {
         "count": {"type": "integer"},
         "ids": {"type": "array", "items": {"type": "string"}}}, "required": ["count", "ids"]},
     "annotations": {"readOnlyHint": True, "destructiveHint": False}},
    {"name": "delete_item",
     "description": "Delete an item. Writes.",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}},
                     "required": ["id"]},
     "annotations": {"readOnlyHint": False, "destructiveHint": True}},
]


class ToolRefusal(Exception):
    pass


def tool_get_item(args):
    if "id" not in args:
        raise ToolRefusal("missing required argument: id")
    it = ITEMS.get(args["id"])
    if not it:
        raise ToolRefusal(f"item not found: {args['id']}")
    return it


def tool_search(args):
    q = (args.get("q") or "").lower()
    ids = [k for k, v in ITEMS.items() if q in v["name"].lower()]
    return {"count": len(ids), "ids": ids}


def tool_delete(args):
    raise ToolRefusal("this test server never deletes anything")


DISPATCH = {"get_item": tool_get_item, "search.items": tool_search, "delete_item": tool_delete}


def handle_rpc(msg):
    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            # BUG 4: echoes anything, "banana" included
            "protocolVersion": params.get("protocolVersion") or "2025-06-18",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "broken-shop", "version": "1.2.0"}}}
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        fn = DISPATCH.get(params.get("name"))
        if not fn:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32601, "message": f"unknown tool: {params.get('name')}"}}
        try:
            out = fn(params.get("arguments") or {})
        except ToolRefusal as e:
            # BUG 2: a refusal is a protocol error, so an SDK client throws
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": str(e)}}
        try:
            text = json.dumps(out)
        except TypeError as e:
            # BUG 3: the Decimal reaches json.dumps; the error is swallowed into isError
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": f"error: {e}"}], "isError": True}}
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "content": [{"type": "text", "text": text}], "structuredContent": out}}
    if mid is None:
        return None
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):   # BUG 6: no call logging whatsoever
        pass

    def _send(self, code, obj, extra=None):
        body = b"" if obj is None else json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Mcp-Session-Id", "sess-1")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(405, {"error": "POST JSON-RPC to /mcp"})

    def do_POST(self):
        if self.path != "/mcp":
            return self._send(404, {"error": "not found"})
        if self.headers.get("Authorization") != TOKEN:
            # BUG 1: even initialize and tools/list are closed
            return self._send(401, {"error": "authentication required"},
                              {"WWW-Authenticate": 'Bearer realm="broken-shop"'})
        try:
            payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"jsonrpc": "2.0", "id": None,
                                    "error": {"code": -32700, "message": "parse error"}})
        if isinstance(payload, list):
            out = [r for r in (handle_rpc(m) for m in payload) if r is not None]
            return self._send(200 if out else 202, out or None)
        r = handle_rpc(payload)
        return self._send(202 if r is None else 200, r)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"broken-shop MCP on http://127.0.0.1:{port}/mcp", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
