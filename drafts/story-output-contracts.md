---
title: "My MCP server's output schemas accepted wrong answers: 7 of 8 tools, found with mcp-drill"
date: 2026-10-15
tags: [mcp, output-schema, json-schema, tool-design, testing]
type: success
status: n/a
reproducible: true
stack: Any MCP server that declares outputSchema on its tools (measured on a Python server on AWS Lambda)
agent: Claude Code
model: claude-opus-5-5
---

# My MCP server's output schemas accepted wrong answers: 7 of 8 tools, found with mcp-drill

MCP lets a tool declare an `outputSchema`, so a client can check a result before it acts on it. Mine had one on every tool, and my tests validated every real result against it. I thought that was done.

Then I read [Tim's post on dev.to](https://dev.to/tim860/i-tested-31-mcp-servers-for-contract-compliance-only-3-passed-25gp) about [mcp-drill](https://github.com/TimurRakhmatullin86/mcp-drill). His check asks a different question: would the schema notice a **wrong** answer? It builds a result with the right structure and types but every value replaced (`"mcp-drill-corruption"`, `-999999999`, `false`) and validates it. If it still passes, the contract is vacuous: it can't tell a wrong result from a right one.

I ran his check, read-only, on my server: 7 of 8 tools were vacuous. My `check_capability` tool returns a capability tier `T0`–`T4` and a sha256, and its schema said `"type": "string"` for both. A tier of `"mcp-drill-corruption"` would have validated. So would a negative count, or `ok: false` from a write that actually succeeded.

I also ran it on 525 random servers from the official MCP registry, the ones that answer `tools/list` without sign-in: 6,243 tools. 75.6% declare no output schema at all, 18.1% declare one that accepts the corrupted result, and 6.3% declare one that rejects it. Tim's 31 popular servers came out at 56%, 42% and 3%, so the long tail is no better.

The fix wasn't stricter types, it was saying what the code already guarantees:
- the tier is one of `T0`…`T4` (`enum`), and so is a finding's severity;
- a sha256 is 64 hex characters (`pattern`);
- counts are never negative (`minimum: 0`);
- a successful write always says `ok: true`, because a refused one is an error result (`const`);
- `get_story` has two real shapes, the story or a "withdrawn" stub, so the schema now says which fields each one has (`anyOf` with `required`).

After the change all 8 tools reject the corrupted result, using mcp-drill's own corruption code. Every real answer from the live server still validates against the new schemas, and a test now runs the same check on every tool, so a new vague schema fails CI.

One thing to know if you run mcp-drill yourself: its corruption builder doesn't follow `$ref`/`$defs`, the way Pydantic and FastMCP write schemas. It puts a string where a referenced object belongs, and the schema rejects it on type, so those tools come out "enforceable" when no value is checked. In the random sample that was 73 tools ([reported upstream](https://github.com/TimurRakhmatullin86/mcp-drill/issues/1)). Read the reason before trusting an "enforceable".

## Check if this applies to you

Applies if: you run an MCP server whose tools declare `outputSchema`. If none do, you have the bigger version of the same problem (no contract at all) and can skip to the fix.

Read-only steps:
1. Get your server's `tools/list` (`initialize`, then `tools/list`; follow `nextCursor` if there are more pages). Do not call any tool.
2. For every tool with an `outputSchema`, build a corrupted result: keep the structure, include only the `required` properties (all properties if none are required), take the first branch of any `anyOf`/`oneOf`/`allOf`, and set every string to `"mcp-drill-corruption"`, every integer to `-999999999`, every number to `-1.5e308`, every boolean to `false`. Or run mcp-drill: `pip install "mcp-drill[scan]"`, then `mcp-drill scan --url <your server>`.
3. Validate the corrupted result against the schema with a real JSON Schema validator (Python `jsonschema`, JS `ajv`).
4. For every tool that rejects it, look at why. If the only error is a `type` mismatch at a `$ref`, the check misfired: count that tool as vacuous.

Has the problem: any tool whose schema accepts the corrupted result.
Doesn't have it: every tool's schema rejects it because of an `enum`, `const`, `pattern`, a bound (`minimum`, `maxLength`, …) or a required field.

Change nothing while checking.

## Reproduce this

Prerequisites: an MCP server you can change and deploy; its tests can call the tools the way a client does (`initialize` → `tools/list` → `tools/call`).

Your agent will need from you: which values your tools really guarantee. It should read the code that builds each result, not guess from field names; when it isn't sure a constraint always holds, it should ask.

Steps:
1. Run the check above and list the vacuous tools.
2. For each, read the code that builds the result and add only constraints the code guarantees: `enum` for fixed sets (statuses, tiers, kinds), `pattern` for formats (hashes, IDs, URL prefixes), `minimum`/`maximum` for counts and limits, `const` for fields that have one possible value on success, `maxItems`/`maxLength` where the code truncates. Mark the fields that are always present as `required`.
3. If a tool returns more than one shape, describe each shape (`anyOf` with its own `required`) instead of making everything optional.
4. Keep JSON Schema features your clients understand. Nullable fields as `anyOf: [{type: X}, {type: "null"}]` rather than `type: [X, "null"]`, which some clients misread.
5. Add a test that builds the corrupted result for every tool and fails if any schema accepts it, so a new vague schema can't slip in.
6. Make sure the test that validates real results checks `enum`, `pattern`, `const` and bounds too, not only types. A home-made validator that checks types only will pass a schema the real client rejects.
7. Validate real answers from the deployed server against the new schemas before you publish them. A constraint that is wrong for some real result breaks every client that validates.
8. The schemas are part of your published tool list: bump your server version and republish wherever it is listed.

Verify:
- The corruption check reports 0 vacuous tools, and none of the rejections is a lone `type` error at a `$ref`.
- Real results from the deployed server, including edge cases (an empty search, a missing optional field, a null), validate against the new schemas with a real JSON Schema validator.
- Your test suite fails if you delete one of the new constraints.

My data: the scan of 525 random registry servers, with the script and every tool's schema, is in [research/output-contracts in worklore-mcp](https://github.com/worklore/worklore-mcp/tree/main/research/output-contracts). The fix in my server: [worklore MCP 0.7.1](https://github.com/worklore/worklore-mcp).
