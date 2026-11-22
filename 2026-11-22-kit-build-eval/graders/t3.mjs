// T3 logs. Five tool calls over stdio and the same five over HTTP (if the HTTP entry starts), with
// canaries in a note body, an email field and an update body.
// (a) every call has a structured line (JSON or key=value) naming the tool, with ok/error and a
//     duration, and the failing call is marked as an error (in at least one transport);
// (b) the server logs tool calls at all, and no canary appears anywhere in what it wrote:
//     stderr/stdout, MCP log notifications, or files it created (the notes file excepted).
// usage: node t3.mjs <workspace copy> <scratch dir>
import { join } from "node:path";
import { readFileSync, mkdirSync } from "node:fs";
import { build, stdioClient, startHttp, httpSession, filesChangedSince, print, withTimeout } from "./lib.mjs";

const [ws, scratch] = process.argv.slice(2);
const out = { task: "t3", checks: {}, detail: {} };
const CANARIES = ["Kq7Zr3", "Wm4Tx8", "Pz9Lc2"];
const TOOLS = ["list_notes", "create_note", "get_note", "update_note", "delete_note"];
out.detail.build = build(ws);

const plan = (id) => [
  ["list_notes", {}, false],
  ["create_note", { title: "Dentist", body: "Call the dentist about canary-body-Kq7Zr3 tomorrow", authorEmail: "canary.wm4tx8@example.org" }, false],
  ["get_note", { id: "n_doesnotexist0" }, true],
  ["update_note", () => ({ id: id(), body: "Moved to Friday, ref canary-upd-Pz9Lc2" }), false],
  ["delete_note", () => ({ id: id() }), false],
];

function parseLines(text) {
  const recs = [];
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) continue;
    const i = line.indexOf("{");
    if (i >= 0) { try { recs.push({ line, rec: JSON.parse(line.slice(i)) }); continue; } catch {} }
    const kv = [...line.matchAll(/([\w.-]+)=("[^"]*"|\S+)/g)];
    if (kv.length >= 2) recs.push({ line, rec: Object.fromEntries(kv.map((m) => [m[1], m[2].replace(/^"|"$/g, "")])) });
  }
  return recs;
}
const flat = (o, pre = "", acc = {}) => { for (const [k, v] of Object.entries(o ?? {})) { if (v && typeof v === "object" && !Array.isArray(v)) flat(v, pre + k + ".", acc); else acc[(pre + k).toLowerCase()] = v; } return acc; };
const DUR = /(duration|latency|elapsed|took|_ms$|^ms$|\.ms$|time_?ms|durationms|response_?time)/;
const STAT = /(^|\.)(ok|success|status|outcome|result|error|iserror|is_error|level|severity|err|event|evt)$/;
const ERRVAL = /error|fail|^warn(ing)?$|fatal|not_?found|denied|refused|rejected|invalid/i;
function isErrish(f) {
  for (const [k, v] of Object.entries(f)) {
    const s = String(v);
    if (/(^|\.)(ok|success)$/.test(k) && (v === false || s === "false")) return true;
    if (/(iserror|is_error)$/.test(k) && (v === true || s === "true")) return true;
    if (/(^|\.)(status|outcome|result|level|severity|event|evt)$/.test(k) && ERRVAL.test(s)) return true;
    if (/(^|\.)(error|err|error_?kind|error_?code|errorcode|errorkind)$/.test(k) && v !== null && v !== undefined && v !== false && s !== "" && s !== "null" && s !== "false") return true;
  }
  return false;
}
function judge(recs, name, isErr) {
  for (const { line, rec } of recs) {
    const f = flat(rec);
    const vals = Object.values(f).map((v) => String(v));
    if (!vals.includes(name) && !line.includes(`"${name}"`) && !line.includes(`=${name}`)) continue;
    const hasDur = Object.keys(f).some((k) => DUR.test(k) && !isNaN(Number(f[k])));
    const statKeys = Object.keys(f).filter((k) => STAT.test(k));
    if (!hasDur || statKeys.length === 0) continue;
    const errish = isErrish(f);
    if (isErr ? errish : !errish) return { ok: true, line: line.slice(0, 300) };
  }
  return { ok: false };
}

async function runStdio() {
  const notes = join(scratch, "t3-stdio-notes.json");
  const notifs = [];
  const since = Date.now() - 1000;
  const s = await stdioClient(ws, { NOTES_FILE: notes, LOG_LEVEL: "info" }, { onNotification: (n) => notifs.push(JSON.stringify(n)) });
  let created;
  for (const [name, a] of plan(() => created)) {
    const args = typeof a === "function" ? a() : a;
    const r = await withTimeout(s.client.callTool({ name, arguments: args }), 15000, name).catch((e) => ({ thrown: String(e) }));
    if (name === "create_note") created = r?.structuredContent?.id ?? (JSON.stringify(r).match(/n_[0-9a-f]{6,}/) ?? [])[0];
  }
  await new Promise((r) => setTimeout(r, 300));
  await s.close();
  await new Promise((r) => setTimeout(r, 300));
  const files = filesChangedSince(ws, since).filter((f) => !f.rel.startsWith("dist/"));
  const fileText = files.map((f) => { try { return readFileSync(f.path, "utf8"); } catch { return ""; } }).join("\n");
  return { text: s.stderr() + "\n" + notifs.join("\n"), fileText, files: files.map((f) => f.rel) };
}
async function runHttp() {
  const notes = join(scratch, "t3-http-notes.json");
  const since = Date.now() - 1000;
  const srv = await startHttp(ws, { NOTES_FILE: notes, LOG_LEVEL: "info" });
  const sess = await httpSession(srv.url, {});
  let created;
  for (const [name, a] of plan(() => created)) {
    const args = typeof a === "function" ? a() : a;
    const r = await sess.call("tools/call", { name, arguments: args });
    if (name === "create_note") created = r.json?.result?.structuredContent?.id ?? (JSON.stringify(r.json ?? {}).match(/n_[0-9a-f]{6,}/) ?? [])[0];
  }
  await new Promise((r) => setTimeout(r, 300));
  await srv.stop();
  const files = filesChangedSince(ws, since).filter((f) => !f.rel.startsWith("dist/"));
  const fileText = files.map((f) => { try { return readFileSync(f.path, "utf8"); } catch { return ""; } }).join("\n");
  return { text: srv.out(), fileText, files: files.map((f) => f.rel) };
}

const res = {};
for (const [k, fn] of [["stdio", runStdio], ["http", runHttp]]) {
  try { res[k] = await fn(); } catch (e) { res[k] = { error: String(e), text: "", fileText: "", files: [] }; }
}
const perTransport = {};
let anyToolLine = false, leaks = [];
for (const [k, r] of Object.entries(res)) {
  const all = r.text + "\n" + r.fileText;
  const recs = parseLines(all);
  const calls = plan(() => "x").map(([name, , isErr]) => ({ name, isErr, ...judge(recs, name, isErr) }));
  perTransport[k] = { error: r.error, files: r.files, structured_lines: recs.length, calls: calls.map((c) => ({ name: c.name, ok: c.ok, line: c.line })) };
  if (all.split(/\r?\n/).some((line) => TOOLS.some((t) => line.includes(t)))) anyToolLine = true;
  for (const c of CANARIES) if (all.toLowerCase().includes(c.toLowerCase())) {
    const at = all.toLowerCase().indexOf(c.toLowerCase());
    leaks.push({ transport: k, canary: c, context: all.slice(Math.max(0, at - 120), at + 40) });
  }
}
out.detail.transports = perTransport;
out.detail.leaks = leaks;
out.checks.t3a_one_structured_line_per_call = Object.values(perTransport).some((t) => t.calls.every((c) => c.ok));
out.checks.t3b_no_personal_data_in_logs = anyToolLine && leaks.length === 0;
out.detail.t3b_logs_tool_calls_at_all = anyToolLine;
print(out);
process.exit(0);
