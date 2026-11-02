# Canary read-back of the MCP log, 2026-10-30

Method from the comments under Dimitris Kyrkos's dev.to article "Your secrets don't need a git
commit to leak into an AI tool" (alexshev, kaj_ilands, rivenpark): seed one key-shaped and one
prose canary per client-supplied path, run the real calls, read the store back below the app.

- send.py: the six anonymous tools/call requests (every string invented), one user-agent and
  one session id per path. send.out: their responses and t0.
- Read-back: `aws logs filter-log-events` on /aws/lambda/worklore-api since t0 (24 events, only
  the six tool-call lines carried a canary) and a full `aws dynamodb scan` of worklore-stories
  (355 items) and worklore-mcp-stats (1365 items): no canary in either table.
- log-lines-read-back.json: the canary log lines as stored (the six, plus the resend p5b after
  the fix).

Result: query, project description and keyword filter masked every key-shaped string and kept
the prose; check_capability kept only text_len; session id came back as its 16-char hash. The
user-agent came back verbatim with the key-shaped string: the client field was copied without
the masker. Fixed the same evening (app.py: client through log_mask.mask, test in
tests/test_session_ref.py), redeployed, resent as p5b: "canary-p5b/1.0 [masked] ...".
