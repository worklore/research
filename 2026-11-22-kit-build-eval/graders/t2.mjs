// T2 auth over Streamable HTTP. (a) initialize and tools/list answer without a token;
// (b) a write without a token (and with a wrong one) gets HTTP 401; (c) one consistent rule:
// without a token the read tools answer and every write tool is refused with 401, and with a
// valid token the writes work. usage: node t2.mjs <workspace copy> <scratch dir>
import { join } from "node:path";
import { build, startHttp, httpSession, print, rpc } from "./lib.mjs";

const [ws, scratch] = process.argv.slice(2);
const TOKEN = "tok-grader-5f1c9a";
const out = { task: "t2", checks: {}, detail: {} };
const CH = ["t2a_discovery_without_token", "t2b_write_without_token_401", "t2c_one_consistent_rule"];
const fail = (why) => { for (const c of CH) out.checks[c] ??= false; out.detail.error = why; print(out); process.exit(0); };

out.detail.build = build(ws);
let srv;
try { srv = await startHttp(ws, { NOTES_FILE: join(scratch, "t2-notes.json"), NOTES_API_TOKENS: `${TOKEN},tok-other-2` }); } catch (e) { fail("start: " + e.message); }
const AUTH = { Authorization: `Bearer ${TOKEN}` };
const okResult = (r) => r.status >= 200 && r.status < 300 && r.json && r.json.result && !r.json.result.isError;
const call = (sess, name, args, extra) => sess.call("tools/call", { name, arguments: args }, extra);

try {
  // A signed-in session seeds one note.
  const auth = await httpSession(srv.url, AUTH);
  const seed = await call(auth, "create_note", { title: "Seed note", body: "seed" });
  const seedId = seed.json?.result?.structuredContent?.id ?? (JSON.stringify(seed.json ?? {}).match(/n_[0-9a-f]{6,}/) ?? [])[0];
  out.detail.seed = { status: seed.status, ok: okResult(seed), id: seedId };

  // (a) anonymous discovery
  const anon = await httpSession(srv.url, {});
  const list = await anon.call("tools/list", {});
  const names = (list.json?.result?.tools ?? []).map((t) => t.name);
  out.detail.t2a = { init_status: anon.init.status, init_ok: !!anon.init.json?.result?.serverInfo, list_status: list.status, tools: names, stateful: !!anon.sid || !!auth.sid };
  const discovery = anon.init.status === 200 && !!anon.init.json?.result?.serverInfo && list.status === 200 && names.length >= 5;

  // For calls without a token use the anonymous session if it exists, else the signed-in session
  // id with the Authorization header removed (each request must carry its own token).
  const noTok = anon.init.status === 200 ? anon : { call: (m, p) => auth.call(m, p, {}), sid: auth.sid };
  const noTokCall = (name, args) => noTok === anon ? call(anon, name, args) : rpc(srv.url, { jsonrpc: "2.0", id: 99, method: "tools/call", params: { name, arguments: args } }, auth.headersWithoutAuth());

  // (b) a write without a token, and with a wrong token
  const w0 = await noTokCall("create_note", { title: "Anon write", body: "should be refused" });
  const wrong = await httpSession(srv.url, { Authorization: "Bearer not-a-valid-token" });
  const w1 = wrong.init.status === 401 ? { status: 401 } : await call(wrong, "create_note", { title: "Wrong token write", body: "should be refused" });
  out.detail.t2b = { no_token_status: w0.status, wrong_token_status: w1.status, www_authenticate: w0.headers?.["www-authenticate"] ?? null };
  out.checks.t2b_write_without_token_401 = w0.status === 401 && w1.status === 401;
  // A refusal is HTTP 401/403, or an isError tool result; either way the write must not happen (checked below).
  const refused = (r) => r.status === 401 || r.status === 403 || (r.status >= 200 && r.status < 300 && !!r.json?.result?.isError);
  // (a) counts only on a server that has sign-in: discovery works anonymously AND an anonymous write is refused.
  out.checks.t2a_discovery_without_token = discovery && refused(w0);
  out.detail.t2a.discovery_alone = discovery;

  // (c) the whole rule
  const rl = await noTokCall("list_notes", {});
  const rg = await noTokCall("get_note", { id: seedId ?? "n_000000000000" });
  const wu = await noTokCall("update_note", { id: seedId ?? "n_000000000000", body: "anon edit" });
  const wd = await noTokCall("delete_note", { id: seedId ?? "n_000000000000" });
  const after = await call(auth, "get_note", { id: seedId });
  const listAfter = await call(auth, "list_notes", {});
  const noSideEffects = after.json?.result?.structuredContent?.body === "seed" && !JSON.stringify(listAfter.json ?? {}).includes("Anon write");
  const au = await call(auth, "update_note", { id: seedId, body: "signed-in edit" });
  const ac = await call(auth, "create_note", { title: "Signed-in create", body: "ok" });
  const ad = await call(auth, "delete_note", { id: seedId });
  out.detail.t2c = {
    anon_list: [rl.status, okResult(rl)], anon_get: [rg.status, okResult(rg)],
    anon_create: ru(w0), anon_update: ru(wu), anon_delete: ru(wd), anonymous_writes_had_no_effect: noSideEffects,
    auth_update: [au.status, okResult(au)], auth_create: [ac.status, okResult(ac)], auth_delete: [ad.status, okResult(ad)],
  };
  function ru(r) { return [r.status, refused(r) ? "refused" : "ran"]; }
  out.checks.t2c_one_consistent_rule = okResult(rl) && okResult(rg) && refused(wu) && refused(wd) && refused(w0) && noSideEffects
    && okResult(au) && okResult(ac) && okResult(ad) && okResult(seed);
} catch (e) { out.detail.error = String(e); for (const c of CH) out.checks[c] ??= false; }
await srv.stop();
out.detail.server_output_tail = srv.out().slice(-600);
print(out);
process.exit(0);
