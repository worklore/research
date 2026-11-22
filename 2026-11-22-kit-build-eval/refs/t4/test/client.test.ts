import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import Ajv from "ajv";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { createServer } from "../src/server.js";

let client: Client;
let dir: string;
let tools: any[];
const ajv = new Ajv({ strict: false });
beforeAll(async () => {
  dir = mkdtempSync(join(tmpdir(), "notes-client-"));
  process.env.NOTES_FILE = join(dir, "notes.json");
  const [a, b] = InMemoryTransport.createLinkedPair();
  await createServer().connect(a);
  client = new Client({ name: "test", version: "1" });
  await client.connect(b);
  tools = (await client.listTools()).tools;
});
afterAll(async () => { await client.close(); rmSync(dir, { recursive: true, force: true }); });

async function call(name: string, args: Record<string, unknown>) {
  const r: any = await client.callTool({ name, arguments: args });
  const tool = tools.find((t) => t.name === name);
  if (!r.isError && tool?.outputSchema) expect(ajv.validate(tool.outputSchema, r.structuredContent), JSON.stringify(ajv.errors)).toBe(true);
  return r;
}
describe("as a real client sees it", () => {
  it("lists every tool", () => {
    expect(tools.map((t) => t.name).sort()).toEqual(["create_note", "delete_note", "get_note", "list_notes", "update_note"]);
  });
  it("creates, reads, updates, lists and deletes", async () => {
    const c = await call("create_note", { title: "T", body: "B" });
    expect(c.isError).toBeFalsy();
    const id = c.structuredContent.id;
    expect((await call("get_note", { id })).isError).toBeFalsy();
    expect((await call("update_note", { id, body: "C" })).isError).toBeFalsy();
    expect((await call("list_notes", {})).structuredContent.notes.length).toBe(1);
    expect((await call("delete_note", { id })).isError).toBeFalsy();
  });
  it("refuses a missing id with an isError result, not a protocol error", async () => {
    const r = await call("get_note", { id: "n_000000000000" });
    expect(r.isError).toBe(true);
  });
});
