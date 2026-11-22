// T1 tools: (a) output schemas reject a corrupted result, (b) a retried create makes one note,
// (c) annotations match behaviour. usage: node t1.mjs <workspace copy> <scratch dir>
import { join } from "node:path";
import { readFileSync, existsSync } from "node:fs";
import Ajv from "ajv";
import addFormats from "ajv-formats";
import { build, stdioClient, print, withTimeout } from "./lib.mjs";

const [ws, scratch] = process.argv.slice(2);
const NAMES = ["list_notes", "create_note", "update_note", "delete_note"];
const out = { task: "t1", checks: {}, detail: {} };
const fail = (why) => { for (const c of ["t1a_output_schema_rejects_wrong", "t1b_retry_no_duplicate", "t1c_annotations_match"]) out.checks[c] ??= false; out.detail.error = why; print(out); process.exit(0); };

const b = build(ws); out.detail.build = b;
const notesFile = join(scratch, "t1-notes.json");
let s;
try { s = await stdioClient(ws, { NOTES_FILE: notesFile }); } catch (e) { fail("connect: " + e.message); }
const tools = (await withTimeout(s.client.listTools(), 15000, "tools/list")).tools;
const byName = Object.fromEntries(tools.map((t) => [t.name, t]));
out.detail.tools = tools.map((t) => t.name);
const missing = NAMES.filter((n) => !byName[n]);
out.detail.missing_tools = missing;

// (a) mcp-drill style corruption: keep the structure, only required properties (all if none are
// required), first branch of anyOf/oneOf/allOf; strings -> "mcp-drill-corruption", integers ->
// -999999999, numbers -> -1.5e308, booleans -> false. Local $refs are followed (mcp-drill does not;
// following them avoids the misfire the story describes).
function deref(schema, root) {
  let s = schema, guard = 0;
  while (s && s.$ref && guard++ < 20) {
    if (!s.$ref.startsWith("#")) break;
    s = s.$ref.slice(1).split("/").filter(Boolean).reduce((o, k) => o?.[decodeURIComponent(k.replace(/~1/g, "/").replace(/~0/g, "~"))], root);
  }
  return s ?? {};
}
function corrupt(schema, root, depth = 0) {
  const s = deref(schema, root);
  if (depth > 12) return null;
  for (const k of ["anyOf", "oneOf", "allOf"]) if (Array.isArray(s[k]) && s[k].length) {
    const first = s[k].find((x) => deref(x, root).type !== "null") ?? s[k][0];
    return corrupt({ ...s, [k]: undefined, ...deref(first, root) }, root, depth + 1);
  }
  let t = s.type;
  if (Array.isArray(t)) t = t.find((x) => x !== "null") ?? t[0];
  if (!t) {
    if (s.properties) t = "object"; else if (s.items) t = "array";
    else if ("const" in s) t = typeof s.const === "number" ? "number" : typeof s.const;
    else if (Array.isArray(s.enum)) t = typeof s.enum[0];
  }
  switch (t) {
    case "object": {
      const props = s.properties ?? {};
      const keys = Array.isArray(s.required) && s.required.length ? s.required : Object.keys(props);
      const o = {};
      for (const k of keys) o[k] = corrupt(props[k] ?? {}, root, depth + 1);
      return o;
    }
    case "array": return s.items ? [corrupt(Array.isArray(s.items) ? s.items[0] : s.items, root, depth + 1)] : [];
    case "string": return "mcp-drill-corruption";
    case "integer": return -999999999;
    case "number": return -1.5e308;
    case "boolean": return false;
    case "null": return null;
    default: return "mcp-drill-corruption";
  }
}
const ajv = new Ajv({ strict: false, allErrors: true, validateSchema: false });
addFormats(ajv);
const a = {};
for (const n of NAMES) {
  const t = byName[n];
  if (!t) { a[n] = { ok: false, why: "missing tool" }; continue; }
  if (!t.outputSchema) { a[n] = { ok: false, why: "no outputSchema" }; continue; }
  try {
    const bad = corrupt(t.outputSchema, t.outputSchema);
    const valid = ajv.validate(t.outputSchema, bad);
    a[n] = { ok: !valid, why: valid ? "accepts the corrupted result" : (ajv.errors ?? []).slice(0, 3).map((e) => `${e.instancePath} ${e.keyword}`).join("; ") };
  } catch (e) { a[n] = { ok: false, why: "schema error: " + e.message }; }
}
out.detail.t1a = a;
out.checks.t1a_output_schema_rejects_wrong = NAMES.every((n) => a[n].ok);

// A retry key the way a client that reads the inputSchema would pick one: the first candidate that
// validates against the property's own schema (format, pattern, length).
function keyValue(prop, t) {
  if (t === "integer" || t === "number") return 7301;
  const cands = ["3f1c9a52-7d4e-4b8a-9c21-5e6f7a8b9c0d", "retry-7f3a-0001", "retry7f3a0001", "n_7f3a00010203", "RETRY7F3A0001", "7f3a0001",
    "retry-7f3a-0001-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "r"];
  for (const c of cands) { try { if (ajv.validate(prop, c)) return c; } catch {} }
  return cands[0];
}

// (b) the same create request sent twice
const KEYLIKE = /(^id$|_id$|Id$|key|token|nonce|request|^op|dedup|client|idempot)/i;
const c = byName.create_note;
if (!c) out.checks.t1b_retry_no_duplicate = false;
else {
  const props = c.inputSchema?.properties ?? {};
  const req = new Set(c.inputSchema?.required ?? []);
  const args = { title: "Retry check 7f3a", body: "The same request, sent twice." };
  const filled = [];
  for (const [k, v] of Object.entries(props)) {
    if (k in args) continue;
    const t = Array.isArray(v.type) ? v.type[0] : v.type;
    if (KEYLIKE.test(k)) { args[k] = keyValue(v, t); filled.push(k); }
    else if (req.has(k)) { args[k] = t === "array" ? [] : t === "integer" || t === "number" ? 1 : t === "boolean" ? false : "x"; filled.push(k); }
  }
  const r1 = await withTimeout(s.client.callTool({ name: "create_note", arguments: args }), 15000, "create 1").catch((e) => ({ thrown: String(e) }));
  const r2 = await withTimeout(s.client.callTool({ name: "create_note", arguments: args }), 15000, "create 2").catch((e) => ({ thrown: String(e) }));
  let count;
  if (existsSync(notesFile)) {
    try {
      const data = JSON.parse(readFileSync(notesFile, "utf8"));
      const arr = Array.isArray(data) ? data : Object.values(data).find(Array.isArray) ?? Object.values(data);
      count = arr.filter((x) => x && x.title === args.title).length;
    } catch {}
  }
  if (count === undefined && byName.list_notes) {
    const l = await s.client.callTool({ name: "list_notes", arguments: {} }).catch(() => undefined);
    const txt = JSON.stringify(l ?? {});
    count = (txt.match(/Retry check 7f3a/g) ?? []).length / ((l?.structuredContent && l?.content) ? 2 : 1);
  }
  out.detail.t1b = { args_keys: Object.keys(args), filled, first_isError: !!(r1.isError || r1.thrown), second_isError: !!(r2.isError || r2.thrown), notes_with_title: count };
  out.checks.t1b_retry_no_duplicate = !(r1.isError || r1.thrown) && count === 1;
}

// (c) annotations
const ann = (n) => byName[n]?.annotations ?? {};
const cdet = Object.fromEntries(NAMES.map((n) => [n, ann(n)]));
out.detail.t1c = cdet;
out.checks.t1c_annotations_match = NAMES.every((n) => byName[n]) &&
  ann("list_notes").readOnlyHint === true &&
  // MCP spec defaults: readOnlyHint false, destructiveHint true. So delete counts as destructive unless it says otherwise.
  ann("delete_note").destructiveHint !== false && ann("delete_note").readOnlyHint !== true &&
  ann("create_note").readOnlyHint !== true && ann("update_note").readOnlyHint !== true;

await s.close();
print(out);
process.exit(0);
