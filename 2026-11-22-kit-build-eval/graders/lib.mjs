// Shared helpers for the hidden graders. They run on a COPY of the agent's final workspace,
// outside it, under graders/grader.sb (no network except localhost). Nothing here is visible
// to the agents.
import { spawn, spawnSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, realpathSync, statSync } from "node:fs";
import { createServer } from "node:net";
import { join, relative, resolve } from "node:path";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export function readJson(p) {
  try { return JSON.parse(readFileSync(p, "utf8")); } catch { return undefined; }
}

export function pkg(ws) { return readJson(join(ws, "package.json")) ?? {}; }

/** npm run build if there is a build script. */
export function build(ws) {
  const p = pkg(ws);
  if (!p.scripts?.build) return { ok: true, skipped: true };
  const r = spawnSync("npm", ["run", "build"], { cwd: ws, encoding: "utf8", timeout: 240_000, env: baseEnv() });
  return { ok: r.status === 0, status: r.status, tail: ((r.stdout ?? "") + (r.stderr ?? "")).slice(-1500) };
}

export function baseEnv(extra = {}) {
  return { PATH: process.env.PATH, HOME: process.env.HOME, TMPDIR: process.env.TMPDIR, NODE_ENV: "production", ...extra };
}

/** The stdio entry: package.json bin, then main, then dist/index.js. */
export function stdioEntry(ws) {
  const p = pkg(ws);
  const cands = [];
  if (typeof p.bin === "string") cands.push(p.bin);
  else if (p.bin && typeof p.bin === "object") cands.push(...Object.values(p.bin));
  if (p.main) cands.push(p.main);
  cands.push("dist/index.js");
  for (const c of cands) if (existsSync(join(ws, c))) return realpathSync(resolve(ws, c));
  return undefined;
}

/** The HTTP entry: the start:http script's file, then dist/http.js. */
export function httpEntry(ws) {
  const p = pkg(ws);
  const cands = [];
  for (const [k, v] of Object.entries(p.scripts ?? {})) {
    if (/http/i.test(k) && typeof v === "string") {
      const m = v.match(/node\s+(?:--[\w-]+(?:=\S+)?\s+)*([^\s&|;]+\.m?js)/);
      if (m) cands.push(m[1]);
    }
  }
  cands.push("dist/http.js");
  for (const c of cands) if (existsSync(join(ws, c))) return realpathSync(resolve(ws, c));
  return undefined;
}

/** Connect an SDK client over stdio. Returns { client, stderr(), close() }. */
export async function stdioClient(ws, env, { onNotification } = {}) {
  const entry = stdioEntry(ws);
  if (!entry) throw new Error("no stdio entry (bin/main/dist/index.js)");
  const transport = new StdioClientTransport({ command: process.execPath, args: [entry], cwd: realpathSync(ws), env: baseEnv(env), stderr: "pipe" });
  let err = "";
  transport.stderr?.on("data", (d) => { err += d.toString(); });
  const client = new Client({ name: "grader", version: "1.0.0" }, { capabilities: {} });
  if (onNotification) client.fallbackNotificationHandler = async (n) => onNotification(n);
  await withTimeout(client.connect(transport), 20_000, "stdio connect");
  return { client, stderr: () => err, close: async () => { try { await client.close(); } catch {} } };
}

export function withTimeout(p, ms, what) {
  return Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error(`timeout: ${what}`)), ms))]);
}

export async function freePort() {
  return new Promise((res) => { const s = createServer(); s.listen(0, "127.0.0.1", () => { const p = s.address().port; s.close(() => res(p)); }); });
}

/** Start the HTTP server. Returns { url, out(), stop() } or throws. */
export async function startHttp(ws, env) {
  const entry = httpEntry(ws);
  if (!entry) throw new Error("no http entry");
  const port = await freePort();
  const child = spawn(process.execPath, [entry], { cwd: realpathSync(ws), env: baseEnv({ PORT: String(port), ...env }), stdio: ["ignore", "pipe", "pipe"] });
  let out = "";
  child.stdout.on("data", (d) => { out += d.toString(); });
  child.stderr.on("data", (d) => { out += d.toString(); });
  const url = `http://127.0.0.1:${port}/mcp`;
  for (let i = 0; i < 100; i++) {
    if (child.exitCode !== null) throw new Error("http server exited: " + out.slice(-500));
    try { await fetch(`http://127.0.0.1:${port}/`, { method: "GET" }); break; } catch { await sleep(150); }
  }
  return { url, out: () => out, stop: async () => { child.kill("SIGTERM"); await sleep(200); try { child.kill("SIGKILL"); } catch {} } };
}

/** One JSON-RPC POST. Parses a JSON or an SSE body. */
export async function rpc(url, message, headers = {}) {
  let res;
  try {
    res = await withTimeout(fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json, text/event-stream", ...headers },
      body: JSON.stringify(message),
    }), 15_000, "http rpc");
  } catch (e) { return { status: 0, error: String(e) }; }
  const text = await res.text();
  let json;
  try { json = JSON.parse(text); } catch {
    const datas = text.split(/\r?\n/).filter((l) => l.startsWith("data:")).map((l) => l.slice(5).trim());
    for (const d of datas) { try { const j = JSON.parse(d); if (j.id !== undefined || j.result || j.error) { json = j; } } catch {} }
  }
  return { status: res.status, headers: Object.fromEntries(res.headers.entries()), json, text: text.slice(0, 2000) };
}

export const INIT = (id = 1) => ({ jsonrpc: "2.0", id, method: "initialize", params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "grader", version: "1.0.0" } } });

/** An HTTP MCP "session": initialize (with optional headers), keep a session id if the server issues one. */
export async function httpSession(url, headers = {}) {
  const init = await rpc(url, INIT(1), headers);
  const sid = init.headers?.["mcp-session-id"];
  const h = { ...headers, ...(sid ? { "mcp-session-id": sid } : {}), "mcp-protocol-version": "2025-06-18" };
  if (init.status >= 200 && init.status < 300) await rpc(url, { jsonrpc: "2.0", method: "notifications/initialized" }, h);
  let n = 10;
  return {
    init, sid,
    call: (method, params, extra = {}) => rpc(url, { jsonrpc: "2.0", id: ++n, method, params }, { ...h, ...extra }),
    headersWithoutAuth: () => { const c = { ...h }; delete c.Authorization; delete c.authorization; return c; },
  };
}

/** Files under ws (excluding node_modules, .git) changed after `since` (ms). */
export function filesChangedSince(ws, since, skip = []) {
  const out = [];
  const walk = (d) => {
    for (const e of readdirSync(d, { withFileTypes: true })) {
      if (e.name === "node_modules" || e.name === ".git") continue;
      const p = join(d, e.name);
      if (e.isDirectory()) walk(p);
      else { try { if (statSync(p).mtimeMs >= since && !skip.includes(p)) out.push(p); } catch {} }
    }
  };
  if (existsSync(ws)) walk(ws);
  return out.map((p) => ({ path: p, rel: relative(ws, p) }));
}

export function print(obj) { process.stdout.write(JSON.stringify(obj, null, 1) + "\n"); }
