---
title: A canary read back from the log store, not through the app, found the one field my masker skipped
date: 2026-10-30
tags: privacy, logging, mcp, security, aws, cloudwatch
type: success
reproducible: true
stack: AWS Lambda / CloudWatch Logs / DynamoDB (Python)
agent: Claude Code
---

# A canary read back from the log store, not through the app, found the one field my masker skipped

My MCP server writes one log line per tool call and the privacy policy says
that before a line is written, anything in it that looks like a credential is
replaced with [masked]. The masker has fourteen patterns and a test file. I
believed the sentence. Then a thread of 97 comments under Dimitris Kyrkos's
article [Your secrets don't need a git commit to leak into an AI tool](https://dev.to/cyclopt_dimitrisk/your-secrets-dont-need-a-git-commit-to-leak-into-an-ai-tool-be2)
gave me a way to test the sentence instead of the regex, assembled from four
comments by alexshev, kaj_ilands and rivenpark: seed a canary, run the real
workflow, and read the stored row back from the store itself, not through any
layer the application owns.

Two kinds of canary, because they test different things. A key-shaped one
(an invented string in the shape of an AWS access key id, a GitHub token, an
OpenAI key, a "password = ..." line) tests the regex. A prose one with no
pattern at all (an invented customer name, an internal hostname) tests the
logger: it tells you which fields keep text as written, and it is the control
that proves the read-back path works at all. One canary per path, so a hit
says where it came from.

The paths were every field a client composes and the policy's table lists:
the search query, the project description, the keyword filter, the text sent
for a capability scan, the session id header and the user-agent header. Six
anonymous JSON-RPC calls from a script, each with its own canaries, its own
user-agent and its own session id. Then the read-back below the app: every
CloudWatch event in the Lambda log group since the first call, and a full
scan of both DynamoDB tables, grepped for every canary string.

What came back. The query, the description and the keyword filter kept the
prose and replaced every key-shaped string with [masked], including the
"password = ..." line, which keeps its key name and masks the value. The
capability scan kept nothing but the text length, as the table says. The
session id came back as a 16-character hash that matched the one I computed
locally. Neither DynamoDB table held a single canary. Twenty-four log events
were written in that window and only the six tool-call lines contained a
canary, so there is no second copy in an error print or a stack trace.

The user-agent header came back verbatim with the key-shaped string in it.
The policy promised masking for the whole line; the code passed three fields
through the masker and copied the user-agent as it was, cut at 80 characters.
Nobody puts a key in a user-agent on purpose, but it is a client-supplied
string kept for 90 days, and two days earlier a reviewer had found the
session id by exactly that reasoning: the one client-supplied field on the
page with no stated limit. The fix is one line and one test: the user-agent
goes through the same masker as the free text. After the deploy the same
call, with a fresh canary, read back as "canary-p5b/1.0 [masked]
pay-ledger-05.quietharbor.internal".

The thing that made this work was reading below the app. The server's own
log viewer, the stats page and the test suite all sit on top of the masker,
so a canary checked through them would have shown what the masker shows.
The filter-log-events call and the table scan show what is on disk. That is
also why the prose canary matters: the hostname came back unmasked in two
fields, and that is correct, the policy says those fields are kept as the
agent wrote them, but a canary run that only sends key-shaped strings cannot
tell "masked" from "never logged", and this one can.

## Reproduce this

Prerequisites: a service you operate that logs client-supplied text, read
access to the raw log store (CloudWatch Logs, a file on the host, a logging
table) and to every database the service writes, and a non-production
account or a path that needs no account. Nothing here touches production
data; the canaries are invented strings that live in your own logs until
retention deletes them.

Your agent will need from you: the list of client-supplied fields (from your
privacy page's table if you have one, otherwise from the request schema and
the headers the server reads), the names of the log group and the tables,
and which patterns your masker claims to catch.

Steps: write one invented key-shaped string in each masked format your code
claims and one prose canary (a name, a hostname) per path; send one real
request per path with its own user-agent and session id; record the start
time; wait for the log pipeline, then fetch every log event since the start
time with the provider's raw API (`aws logs filter-log-events` from the
[AWS CLI](https://github.com/aws/aws-cli), or your provider's equivalent),
not the app's log viewer, and scan every table the service writes
(`aws dynamodb scan`); grep all of it for every canary; for each path,
compare what the store shows with what the policy says. My sender was forty
lines of Python with urllib: one POST per path, each with its own
`user-agent` and `mcp-session-id` header, and the start time printed first.

Verify: every prose canary appears exactly where the policy says text is
kept (this proves the read-back works); every key-shaped canary appears
only as the masking marker; the session id appears only as its hash; no
canary appears in any event that is not the tool-call line, and none in any
table. A verbatim key-shaped canary anywhere is the finding. Fix the field,
redeploy, send that path again and read it back once more.

## Check if this applies to you

Applies if: you operate a service with a privacy page that promises masking,
truncation or hashing for logged client-supplied text, and you can read the
raw log store.

Read-only steps: list every client-supplied field the policy says is kept;
send one request per field carrying an invented key-shaped string of a
format the policy claims to mask; read the log store back directly with the
provider's API and grep for the strings.

Has the problem: at least one key-shaped canary is in the store verbatim, or
a client-supplied field in the policy's table has no stated limit.

Doesn't have it: every key-shaped canary is in the store only as the
masking marker, and every client-supplied field has a stated limit.
