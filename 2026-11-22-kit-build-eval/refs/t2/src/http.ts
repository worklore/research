import { createServer as createHttpServer } from "node:http";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createServer } from "./server.js";

const PORT = Number(process.env.PORT ?? 3000);
const TOKENS = new Set((process.env.NOTES_API_TOKENS ?? "").split(",").map((t) => t.trim()).filter(Boolean));
// One table: what answers without a token. Everything else needs a valid bearer token.
const PUBLIC_METHODS = new Set(["initialize", "notifications/initialized", "ping", "tools/list"]);
const PUBLIC_TOOLS = new Set(["list_notes", "get_note"]);
function isPublic(msg: any): boolean {
  if (!msg || typeof msg !== "object") return false;
  if (PUBLIC_METHODS.has(msg.method)) return true;
  return msg.method === "tools/call" && PUBLIC_TOOLS.has(msg.params?.name);
}
function signedIn(h: string | undefined): boolean {
  const m = /^Bearer\s+(.+)$/i.exec(h ?? "");
  return !!m && TOKENS.has(m[1].trim());
}
const http = createHttpServer(async (req, res) => {
  if ((req.url ?? "").split("?")[0] !== "/mcp") { res.writeHead(404).end(); return; }
  if (req.method !== "POST") { res.writeHead(405, { Allow: "POST" }).end(); return; }
  const chunks: Buffer[] = [];
  for await (const c of req) chunks.push(c as Buffer);
  let body: unknown;
  try { body = JSON.parse(Buffer.concat(chunks).toString("utf8")); } catch { res.writeHead(400).end(); return; }
  const msgs = Array.isArray(body) ? body : [body];
  if (!(msgs.length > 0 && msgs.every(isPublic)) && !signedIn(req.headers.authorization)) {
    res.writeHead(401, { "Content-Type": "application/json", "WWW-Authenticate": 'Bearer realm="notes-mcp"' });
    res.end(JSON.stringify({ jsonrpc: "2.0", error: { code: -32001, message: "Sign-in required" }, id: null }));
    return;
  }
  const server = createServer();
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
  res.on("close", () => { void transport.close(); void server.close(); });
  await server.connect(transport);
  await transport.handleRequest(req, res, body);
});
http.listen(PORT, () => console.error(`notes-mcp listening on http://localhost:${PORT}/mcp`));
