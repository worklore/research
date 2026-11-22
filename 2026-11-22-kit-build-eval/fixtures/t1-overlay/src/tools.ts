import { z } from "zod";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import * as store from "./store.js";

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

export const getNoteTool: ToolDef = {
  name: "get_note",
  config: {
    title: "Get a note",
    description: "Read one note by its id.",
    inputSchema: { id: z.string().describe("The note id, e.g. n_1a2b3c4d5e6f") },
  },
  handler: async ({ id }) => {
    const note = store.getNote(id);
    if (!note) return { content: [{ type: "text", text: `No note with id ${id}.` }], isError: true };
    return { content: [{ type: "text", text: JSON.stringify(note) }] };
  },
};
