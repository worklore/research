// T4 tests. The agent's own test suite must pass on its final code, then the grader plants one
// client-visible defect at a time and runs the suite again; a defect is caught when the suite fails.
//   m1 structured output that does not match the output schema (createdAt becomes a number)
//   m2 a tool refusal that comes back as a JSON-RPC error instead of an isError result
//      (SDK 1.32.2's McpServer turns ordinary throws into isError results, so the plant throws
//      the one McpError code the SDK passes through as a protocol error: a real client's callTool rejects)
//   m3 a tool missing from tools/list (delete_note no longer registered)
// usage: node t4.mjs <workspace copy> <scratch dir>
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync, readdirSync, rmSync } from "node:fs";
import { join, relative } from "node:path";
import { build, baseEnv, print } from "./lib.mjs";

const [ws, scratch] = process.argv.slice(2);
const out = { task: "t4", checks: {}, detail: {} };

const MUT = {
  m1_structured_output_mismatch: [{ file: "src/tools.ts", from: /createdAt: note\.createdAt,/, to: "createdAt: Date.parse(note.createdAt) as unknown as string," }],
  m2_refusal_as_protocol_error: [
    { file: "src/tools.ts", from: /export function notFound\(id: string\): CallToolResult \{[\s\S]*?\n\}/,
      to: "export function notFound(id: string): CallToolResult {\n  throw new McpError(ErrorCode.UrlElicitationRequired, `No note with id ${id}.`);\n}" },
    { file: "src/tools.ts", prepend: 'import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";\n' },
  ],
  m3_tool_missing_from_list: [{ file: "src/server.ts", from: /updateNoteTool,\s*deleteNoteTool\s*\]/, to: "updateNoteTool]" }],
};

function copy(dst) {
  rmSync(dst, { recursive: true, force: true });
  const r = spawnSync("/bin/cp", ["-cR", ws, dst]);
  if (r.status !== 0) spawnSync("/bin/cp", ["-R", ws, dst]);
}
function runTests(dir) {
  const b = build(dir);
  const t0 = Date.now();
  const r = spawnSync("npm", ["test"], { cwd: dir, encoding: "utf8", timeout: 300_000, env: baseEnv({ CI: "1", NODE_ENV: "test" }) });
  const tail = ((r.stdout ?? "") + (r.stderr ?? "")).slice(-1200);
  const counts = tail.match(/Tests\s+(.*)/)?.[1] ?? null;
  return { build_ok: b.ok, exit: r.status, signal: r.signal, timed_out: r.error?.code === "ETIMEDOUT", secs: Math.round((Date.now() - t0) / 1000), counts, tail: tail.slice(-500) };
}
function testFiles(dir) {
  const outF = [];
  const walk = (d) => { for (const e of readdirSync(d, { withFileTypes: true })) {
    if (["node_modules", ".git", "dist", "worklore-mcp-server-kit"].includes(e.name)) continue;
    const p = join(d, e.name);
    if (e.isDirectory()) walk(p); else if (/\.(test|spec)\.[cm]?[jt]s$/.test(e.name)) outF.push(relative(dir, p));
  } };
  walk(dir); return outF.sort();
}

const files = testFiles(ws);
out.detail.test_files = files;
out.detail.new_test_files = files.filter((f) => f !== "test/store.test.ts");
const base = join(scratch, "t4-base"); copy(base);
const b = runTests(base);
out.detail.baseline = b;
const baselineOk = b.exit === 0 && b.build_ok;

for (const [name, edits] of Object.entries(MUT)) {
  const dir = join(scratch, "t4-" + name); copy(dir);
  let planted = true;
  for (const e of edits) {
    const p = join(dir, e.file);
    if (!existsSync(p)) { planted = false; break; }
    let src = readFileSync(p, "utf8");
    if (e.prepend) src = e.prepend + src;
    else { if (!e.from.test(src)) { planted = false; break; } src = src.replace(e.from, e.to); }
    writeFileSync(p, src);
  }
  const r = planted ? runTests(dir) : null;
  const caught = planted && baselineOk && r.exit !== 0;
  out.detail[name] = { planted, ...(r ?? {}), caught };
  rmSync(dir, { recursive: true, force: true });
}
rmSync(base, { recursive: true, force: true });
out.checks.t4a_catches_output_schema_mismatch = out.detail.m1_structured_output_mismatch.caught;
out.checks.t4b_catches_refusal_as_protocol_error = out.detail.m2_refusal_as_protocol_error.caught;
out.checks.t4c_catches_missing_tool = out.detail.m3_tool_missing_from_list.caught;
out.detail.caught = Object.values(out.checks).filter(Boolean).length;
out.detail.baseline_ok = baselineOk;
print(out);
process.exit(0);
