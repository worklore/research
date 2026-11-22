import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { createNoteTool, deleteNoteTool, getNoteTool, listNotesTool, updateNoteTool } from "../src/tools.js";

let dir: string;
beforeAll(() => { dir = mkdtempSync(join(tmpdir(), "notes-tools-")); process.env.NOTES_FILE = join(dir, "notes.json"); });
afterAll(() => rmSync(dir, { recursive: true, force: true }));
describe("tool handlers", () => {
  it("create, get, update, list, delete", async () => {
    const c: any = await createNoteTool.handler({ title: "T", body: "B" });
    const id = c.structuredContent.id;
    expect((await getNoteTool.handler({ id }) as any).structuredContent.title).toBe("T");
    expect((await updateNoteTool.handler({ id, body: "C" }) as any).structuredContent.body).toBe("C");
    expect((await listNotesTool.handler({}) as any).structuredContent.notes).toHaveLength(1);
    expect((await deleteNoteTool.handler({ id }) as any).structuredContent.deleted).toBe(true);
  });
});
