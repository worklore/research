# notes-mcp

An MCP server for a small team's notes, kept in a JSON file. Maintained by the
[Notesco](https://github.com/notesco) organization on GitHub.

Tools: `list_notes`, `get_note`, `create_note`, `update_note`, `delete_note`.

```bash
npm run build
npm start            # stdio
npm run start:http   # Streamable HTTP on http://localhost:3000/mcp (PORT to change)
npm test
```

Notes are stored in `data/notes.json`; set `NOTES_FILE` to use another file.
