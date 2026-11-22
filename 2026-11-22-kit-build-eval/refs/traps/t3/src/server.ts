import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createNoteTool, deleteNoteTool, getNoteTool, listNotesTool, updateNoteTool } from "./tools.js";
import type { ToolDef } from "./tools.js";

export const TOOLS: ToolDef[] = [listNotesTool, getNoteTool, createNoteTool, updateNoteTool, deleteNoteTool];

function logCall(rec: Record<string, unknown>): void {
  try { process.stderr.write(JSON.stringify({ evt: "mcp_call", v: 1, ts: new Date().toISOString(), ...rec }) + "\n"); } catch { /* never fail a call */ }
}

export function createServer(): McpServer {
  const server = new McpServer({ name: "notes-mcp", version: "0.4.0" });
  for (const tool of TOOLS) {
    server.registerTool(tool.name, tool.config, async (args: any) => {
      const t0 = Date.now();
      try {
        const r = await tool.handler(args);
        logCall({ tool: tool.name, ok: !r.isError, duration_ms: Date.now() - t0, args });
        return r;
      } catch (e) {
        logCall({ tool: tool.name, ok: false, duration_ms: Date.now() - t0, error: (e as Error).name });
        throw e;
      }
    });
  }
  return server;
}
