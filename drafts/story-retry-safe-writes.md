---
title: "I sent every write tool of my MCP servers a second time: 8 of 31 duplicated, reset or hit the wrong record"
date: 2026-10-20
tags: [mcp, idempotency, retries, offline-sync, tool-design, firestore, dynamodb]
type: success
status: n/a
reproducible: true
stack: Any MCP server with tools that write (measured on a TypeScript server on Firestore and a Python server on DynamoDB)
agent: Claude Code
model: claude-fable-5-1
---

# I sent every write tool of my MCP servers a second time: 8 of 31 duplicated, reset or hit the wrong record

A tool call is a remote procedure call with a model choosing the procedure. When the response is lost, the agent retries, and the write lands twice. [Dimitris K.'s post on dev.to](https://dev.to/cyclopt_dimitrisk/your-agents-retry-bug-isnt-an-ai-problem-its-a-distributed-systems-problem-with-an-llm-on-top-1i6k) makes the point with a refund paid twice, and his fix is the standard one: the app mints an idempotency key before the first attempt, stores the intent, and a replay returns the first result.

I run two MCP servers that agents write through every day, both built with agents. Neither had asked the question. So I asked it of every write tool: what happens when the same call lands a second time?

Of 31 tools that write, 8 were not safe to call twice:

| server | tool | what a second landing did |
|---|---|---|
| worklore | `publish_story` | replaced the author's own story with a fresh row: reproduction counts back to 0, reports and checks gone, and a second post to Bluesky |
| worklore | `report_reproduction` | checked "already reported" and then wrote, so two parallel calls counted twice and notified twice |
| worklore | `edit_story` | appended a revision and re-notified every reproducer, with identical content |
| AimYear | `log_session` | logged the time again: a retry double-counted the day |
| AimYear | `start_focus` | started a second running session and halved the attention share of the first |
| AimYear | `add_steps`, `heartbeat` | duplicated the steps, duplicated the note |
| AimYear | `end_focus`, `delete_session` without an id | fell back to "the only running session", so a retry after a success could stop or delete another terminal's session |

The other 23 were safe by construction, and that is the useful pattern: every one of them was a replace keyed by something the caller already knows (a slug, a date, a handle, a device token) or a delete that fails the second time. `report_check`, which stores one result per handle and overwrites, was the model for the rest.

Three things I learned fixing them.

**For an LLM caller, the key is the argument, not a token.** Dimitris is right that a key the model invents protects nothing. But an agent calling `stop_session` already has the session id from `get_now`, and that is the key: a stop on a session that has ended returns the stored result instead of guessing another session. `start_session` accepts a client-minted session id and becomes create-if-absent. The dedup is a condition on the write (DynamoDB `ConditionExpression`, a Firestore transaction), not a new table.

**For an app caller, the key is a request document.** AimYear has a phone app that can be offline. A stop queued on the phone at 14:05 and delivered at 16:40 used to be recorded at 16:40, because the server stamped the end on arrival. Now a stop carries its own `end_at` and an `op_id` the app minted when the user tapped; the server keeps `users/{uid}/ops/{op_id}` with the result, written in the same transaction as the session, and a replay returns it. The op id is the document id, so writing it twice is one document.

**Two devices need a merge rule, not a key.** The case the article doesn't cover: the phone stops the session at 14:05 offline, the laptop stops it at 14:20 online, and the phone's request lands last. Two different intents, two different keys. The rule I chose is order-independent: the earliest end wins, because once anyone stopped the session it was not running; every stop is kept on the session; `done` beats any other outcome; a different later summary goes to the notes. Phone-then-laptop and laptop-then-phone converge on the same record, and the late request gets `applied: "shortened"` and a sentence saying what moved.

On the worklore side the fixes were smaller: a republish updates content fields and keeps the counts, the Bluesky post is claimed with a conditional write before posting so a concurrent publish can't post twice, the reproduction count is conditional on the list it read, and an identical edit writes nothing. 25 new tests on one server, 11 on the other, including both arrival orders.

## Check if this applies to you

Applies if: your MCP server has tools that create, append, count, send or delete.

Read-only steps, from the code, without calling anything:
1. List the tools (`tools/list`). Keep the ones that write.
2. For each, find the storage call and sort it into one of four bins: **append** with a server-generated id or timestamp (`put` with a random id, `list_append`, `ADD +1`, push to an array); **replace** keyed by an argument the caller supplies (`set`, `update` on a known id, "one per handle"); **guess**, a stop, close or delete whose target is "the current one" or "the only one" when no id is given; **conditional**, a write with a condition that fails the second time.
3. For each append and guess, note the side effects that ride along: a notification, an outbound post, a counter, a webhook.

Has the problem: any tool in the append or guess bin, or a replace that first reads and then writes without a condition.
Doesn't have it: every writing tool is a conditional write or a replace keyed by an argument, and its side effects are gated on the write having happened.

Change nothing while checking.

## Reproduce this

Prerequisites: an MCP server you can change, with tests that can call the tools the way a client does. A store with conditional writes or transactions (DynamoDB conditions, Firestore transactions, Postgres `ON CONFLICT`).

Your agent will need from you: which callers are models and which are apps, and for records two callers can close, which rule should win. It should read the storage code for each tool, not guess from the tool name: `set_projects` in my server replaces the whole list, `log_session` appends, and the names don't say so.

Steps:
1. Run the check above and list the append and guess tools.
2. For each append whose caller is a model, find the argument that identifies the record (a session id, a slug, a handle, a date) and make the write create-if-absent or replace-by-key. If no argument identifies it, add one that the caller already has.
3. For each guess, require the id when the call carries anything that marks it as queued or replayed (a timestamp, an op id), and make the error list the candidates with their ids so the agent can pick.
4. For callers that are apps and can be offline: accept an `op_id` the app mints before the first attempt and the event's own timestamp; store the op with its result in the same transaction as the change; replay returns the stored result. Give the op a TTL. Reject a timestamp before the record's start and clamp one that is ahead of the server's clock.
5. Where two callers can legitimately close the same record, write the merge rule down before the code: it must give the same result in either arrival order. Keep every attempt on the record.
6. Move the dedup into the write: a condition on the field you read, or a transaction. A read-then-write check is what counted my reproductions twice.
7. Gate side effects on the write: claim a marker (`bsky_uri = pending` with `attribute_not_exists`) before posting, and release it if the post fails.
8. Say in the tool descriptions which arguments are keys and that `op_id` is for apps replaying queued requests, so the model doesn't invent one.

Verify:
- The same write with the same key or op id sent twice returns the same answer, and the record, the counts and the side effects are unchanged after the second call.
- Two different closes of one record, sent in both orders, end in the same stored state.
- A close or delete without an id, from a connection that owns no running record, is refused with the list of candidates.
- Your test suite fails if you remove the condition from any of the writes.

My code: [AimYear MCP 0.7.0](https://github.com/Yahhi/aimyear-mcp) (`service.ts`, `applyOnce` and `mergeStop`) and the worklore backend (`publish`, `announce_story`, `report_reproduction`). The survey table above is from reading both servers end to end before changing anything.
