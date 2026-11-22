import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { getNoteTool } from "./tools.js";
import type { ToolDef } from "./tools.js";

export const TOOLS: ToolDef[] = [getNoteTool];

export function createServer(): McpServer {
  const server = new McpServer({ name: "notes-mcp", version: "0.4.0" });
  for (const tool of TOOLS) {
    server.registerTool(tool.name, tool.config, tool.handler);
  }
  return server;
}
