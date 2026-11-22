import { z } from "zod";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import * as store from "./store.js";
import type { Note } from "./store.js";

export interface ToolDef {
  name: string;
  config: { title: string; description: string; inputSchema: z.ZodRawShape; outputSchema?: z.ZodRawShape; annotations?: Record<string, boolean> };
  handler: (args: any) => Promise<CallToolResult>;
}
const ID = z.string().regex(/^n_[0-9a-f]{12}$/);
const noteShape = {
  id: ID,
  title: z.string().min(1).max(200),
  body: z.string(),
  tags: z.array(z.string().min(1)),
  authorEmail: z.string().email().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
};
const out = (s: Record<string, unknown>): CallToolResult => ({ content: [{ type: "text", text: JSON.stringify(s) }], structuredContent: s });
const nf = (id: string): CallToolResult => ({ content: [{ type: "text", text: `No note with id ${id}.` }], isError: true });
const view = (n: Note) => ({ ...n }) as Record<string, unknown>;

export const getNoteTool: ToolDef = {
  name: "get_note",
  config: { title: "Get a note", description: "Read one note by its id.", inputSchema: { id: z.string() }, outputSchema: noteShape, annotations: { readOnlyHint: true } },
  handler: async ({ id }) => { const n = store.getNote(id); return n ? out(view(n)) : nf(id); },
};
export const listNotesTool: ToolDef = {
  name: "list_notes",
  config: { title: "List notes", description: "List all notes.", inputSchema: {}, outputSchema: { notes: z.array(z.object(noteShape)), count: z.number().int().min(0) }, annotations: { readOnlyHint: true } },
  handler: async () => { const ns = store.listNotes(); return out({ notes: ns.map(view), count: ns.length }); },
};
export const createNoteTool: ToolDef = {
  name: "create_note",
  config: {
    title: "Create a note",
    description: "Create a note. requestId is the retry key: send the same requestId when you retry, and the first note comes back instead of a second one.",
    inputSchema: { title: z.string().min(1), body: z.string(), tags: z.array(z.string()).optional(), authorEmail: z.string().optional(), requestId: z.string().min(1).describe("A key the client picks once per note, reused on retries") },
    outputSchema: noteShape,
    annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true },
  },
  handler: async ({ requestId, ...input }) => {
    const existing = store.listNotes().find((n) => (n as any).requestId === requestId);
    if (existing) return out(view(existing));
    const n = store.createNote(input);
    store.updateNote(n.id, {});
    const all = store.listNotes();
    const saved = all.find((x) => x.id === n.id)!;
    (saved as any).requestId = requestId;
    store.replaceAll(all);
    return out(view(n));
  },
};
export const updateNoteTool: ToolDef = {
  name: "update_note",
  config: { title: "Update a note", description: "Change a note.", inputSchema: { id: z.string(), title: z.string().min(1).optional(), body: z.string().optional(), tags: z.array(z.string()).optional() }, outputSchema: noteShape, annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true } },
  handler: async ({ id, ...p }) => { const n = store.updateNote(id, p); return n ? out(view(n)) : nf(id); },
};
export const deleteNoteTool: ToolDef = {
  name: "delete_note",
  config: { title: "Delete a note", description: "Delete a note.", inputSchema: { id: z.string() }, outputSchema: { deleted: z.literal(true), id: ID }, annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: true } },
  handler: async ({ id }) => (store.deleteNote(id) ? out({ deleted: true, id }) : nf(id)),
};
