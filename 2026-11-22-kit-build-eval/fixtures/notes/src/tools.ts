import { z } from "zod";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import * as store from "./store.js";
import type { Note } from "./store.js";

/** The structured form of a note that every tool returns. */
export function noteOutput(note: Note): Record<string, unknown> {
  return {
    id: note.id,
    title: note.title,
    body: note.body,
    tags: note.tags,
    ...(note.authorEmail ? { authorEmail: note.authorEmail } : {}),
    createdAt: note.createdAt,
    updatedAt: note.updatedAt,
  };
}

/** The answer for an id that does not exist. */
export function notFound(id: string): CallToolResult {
  return { content: [{ type: "text", text: `No note with id ${id}.` }], isError: true };
}

function ok(structured: Record<string, unknown>): CallToolResult {
  return { content: [{ type: "text", text: JSON.stringify(structured) }], structuredContent: structured };
}

const noteShape = {
  id: z.string(),
  title: z.string(),
  body: z.string(),
  tags: z.array(z.string()),
  authorEmail: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
};

export interface ToolDef {
  name: string;
  config: {
    title: string;
    description: string;
    inputSchema: z.ZodRawShape;
    outputSchema?: z.ZodRawShape;
    annotations?: Record<string, boolean>;
  };
  handler: (args: any) => Promise<CallToolResult>;
}

export const listNotesTool: ToolDef = {
  name: "list_notes",
  config: {
    title: "List notes",
    description: "List all notes, newest first.",
    inputSchema: {},
    outputSchema: { notes: z.array(z.object(noteShape)) },
    annotations: { readOnlyHint: true },
  },
  handler: async () => {
    const notes = store.listNotes().sort((a, b) => b.createdAt.localeCompare(a.createdAt));
    return ok({ notes: notes.map(noteOutput) });
  },
};

export const getNoteTool: ToolDef = {
  name: "get_note",
  config: {
    title: "Get a note",
    description: "Read one note by its id.",
    inputSchema: { id: z.string().describe("The note id, e.g. n_1a2b3c4d5e6f") },
    outputSchema: noteShape,
    annotations: { readOnlyHint: true },
  },
  handler: async ({ id }) => {
    const note = store.getNote(id);
    return note ? ok(noteOutput(note)) : notFound(id);
  },
};

export const createNoteTool: ToolDef = {
  name: "create_note",
  config: {
    title: "Create a note",
    description: "Create a note.",
    inputSchema: {
      title: z.string().min(1).describe("Short title"),
      body: z.string().describe("The note text"),
      tags: z.array(z.string()).optional(),
      authorEmail: z.string().optional().describe("Email of the person the note is from"),
    },
    outputSchema: noteShape,
    annotations: { readOnlyHint: false, destructiveHint: false },
  },
  handler: async (args) => ok(noteOutput(store.createNote(args))),
};

export const updateNoteTool: ToolDef = {
  name: "update_note",
  config: {
    title: "Update a note",
    description: "Change the title, body, tags or author of a note.",
    inputSchema: {
      id: z.string(),
      title: z.string().min(1).optional(),
      body: z.string().optional(),
      tags: z.array(z.string()).optional(),
      authorEmail: z.string().optional(),
    },
    outputSchema: noteShape,
    annotations: { readOnlyHint: false, destructiveHint: false },
  },
  handler: async ({ id, ...patch }) => {
    const note = store.updateNote(id, patch);
    return note ? ok(noteOutput(note)) : notFound(id);
  },
};

export const deleteNoteTool: ToolDef = {
  name: "delete_note",
  config: {
    title: "Delete a note",
    description: "Delete a note by its id.",
    inputSchema: { id: z.string() },
    outputSchema: { deleted: z.boolean(), id: z.string() },
    annotations: { readOnlyHint: false, destructiveHint: true },
  },
  handler: async ({ id }) => (store.deleteNote(id) ? ok({ deleted: true, id }) : notFound(id)),
};
