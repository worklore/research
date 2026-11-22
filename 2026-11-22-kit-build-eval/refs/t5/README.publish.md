
## Publishing to the MCP Registry

1. `npm publish --access public` (package.json carries `mcpName`, which must equal `name` in server.json).
2. Log in with a GitHub token that has the `read:org` scope, because the name is under the notesco
   organization: `mcp-publisher login github -token "$(gh auth token)"`.
3. `mcp-publisher publish`. Keep the version in server.json equal to package.json.
