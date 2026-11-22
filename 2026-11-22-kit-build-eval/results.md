# Results: does the MCP Server Kit change what an agent builds?

2026-11-22, run overnight. The plan was committed before any run (`plan.md`, commit 5941d3d), and
every change made after the first run is listed there under "Deviations". Disclosure: the kit under
test is worklore's MCP Server Kit, which Valentina sells. All the numbers below come from the final
graders, applied to every run.

## Summary

- **Two facts in the kit changed the result clearly, across lanes.**
  - **read:org.** Publishing under a GitHub organization needs a token with the `read:org` scope.
    Without the kit, 0 of 15 runs wrote this in the README; with the kit, 15 of 15 did, in all five
    lanes.
  - **Output schemas that reject wrong answers.** None of the 15 runs without the kit wrote an output
    schema that rejects a corrupted result (right structure, wrong values); 10 of 15 with the kit did.
    The difference is clear in codex, deepseek and kimi (0/3 vs 3/3, 3/3, 2/3) and only one run in
    haiku and sonnet.
- **The registry story's other two facts helped where agents got them wrong.** These are the
  `$schema` field and the 100-character description limit. Sonnet and kimi failed them without the
  kit (wrong `$schema` URL, or the 104-character package.json description copied into server.json)
  and passed with it.
- **Everything else showed no difference, mostly because agents already did it without the kit:**
  - safe retries (15/15 in both arms);
  - honest annotations (15/15);
  - an open tool list next to authenticated writes (15/15);
  - one consistent auth rule (15/15);
  - structured per-call logs and no personal data in them (15/15);
  - tests through a real MCP client (T4, dropped at screening: every run, with or without the kit,
    caught all three planted defects);
  - the namespace, version and mcpName parts of server.json (15/15).
- **One fact changed results in one lane only:** answering an anonymous write with HTTP 401 instead
  of an `isError` result. Codex went from 0/3 without the kit to 3/3 with it, and sonnet from 0/3 to
  1/3. The codex runs did not open the story the plan names for this; they opened the kit's OAuth
  story, which uses 401 with `WWW-Authenticate`.
- **The T2 stories were mostly not found.** For "add bearer-token sign-in", agents went to the kit's
  `auth/` section (OAuth 2.1 and app-review test accounts), concluded it did not apply, and stopped.
  Only 4 of 15 kit-arm T2 runs opened the two `design/` stories that carry the T2 facts. The fix is in
  the kit's routing, not its text (see "What this means for the kit").
- **Opening START-HERE.md is universal; opening a story is not.** Every kit-arm run opened
  START-HERE.md (60/60). Sonnet then opened a story in only 4 of 12 runs, while codex, deepseek and
  kimi opened one in all 36 of theirs.

## Screening decision

Screening used haiku and deepseek: 5 tasks x 2 arms x 2 runs = 40 runs. The keep rule from plan.md
is: keep a task when the kit arm passes a check more often than the none arm in either lane, or when
the none arm already fails a check.

| task | decision on the final graders | why |
|---|---|---|
| T1 tools | **keep** | output schemas: none 0/2 in both lanes; deepseek kit 2/2 |
| T2 auth | **keep** | deepseek none 1/2 on anonymous discovery (one run hid the write tools from an anonymous `tools/list`) |
| T3 logs | **drop** | every check passed in both arms and both lanes |
| T4 tests | **drop** | every check passed in both arms and both lanes (12/12 plants caught per arm) |
| T5 publish | **keep** | read:org: none 0/2, kit 2/2, in both lanes |

**T3 was kept by mistake.** It was kept at the time because the T3 grader did not recognise
`outcome: "not_found"` or `level: "warn"` as marking a failed call (Deviation 4). Its full round had
already run when the bug was found. Its numbers are reported below as what they are: a ceiling.

## Tables

Each cell is passes / runs, none arm vs kit arm; 3 runs per cell in the full round.

### T1: tools (create/update/delete/list, output schemas, safe retries)

| check | haiku | sonnet | codex | deepseek | kimi | all |
|---|---|---|---|---|---|---|
| output schema rejects a corrupted result | 0/3 vs 1/3 | 0/3 vs 1/3 | 0/3 vs **3/3** | 0/3 vs **3/3** | 0/3 vs **2/3** | 0/15 vs **10/15** |
| a retried create makes one note | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 15/15 vs 15/15 |
| annotations match behaviour | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 15/15 vs 15/15 |

### T2: bearer-token sign-in on the HTTP transport

| check | haiku | sonnet | codex | deepseek | kimi | all |
|---|---|---|---|---|---|---|
| initialize and tools/list answer without a token (on a server whose writes need one) | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 15/15 vs 15/15 |
| a write without a token, or with a wrong one, gets HTTP 401 | 3/3 vs 3/3 | 0/3 vs 1/3 | 0/3 vs **3/3** | 3/3 vs 3/3 | 3/3 vs 3/3 | 9/15 vs 13/15 |
| one rule: reads public, every write refused anonymously, writes work with a token | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 15/15 vs 15/15 |

### T3: logs (kept by mistake, see above; a ceiling)

| check | haiku | sonnet | codex | deepseek | kimi | all |
|---|---|---|---|---|---|---|
| one structured line per call with tool, ok/error, duration | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 15/15 vs 15/15 |
| canaries in a note body, an email field and an update never reach the logs | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 15/15 vs 15/15 |

### T5: prepare for the official MCP Registry

| check | haiku | sonnet | codex | deepseek | kimi | all |
|---|---|---|---|---|---|---|
| server.json valid against the registry schema, with `$schema` | 3/3 vs 3/3 | 0/3 vs **2/3** | 3/3 vs 3/3 | 3/3 vs 3/3 | 0/3 vs 3/3 | 9/15 vs 14/15 |
| description at most 100 characters | 3/3 vs 3/3 | 1/3 vs **3/3** | 3/3 vs 3/3 | 3/3 vs 3/3 | 0/3 vs 3/3 | 10/15 vs 15/15 |
| name in `io.github.notesco/` | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 15/15 vs 15/15 |
| version equals package.json | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 15/15 vs 15/15 |
| package.json `mcpName` equals the server.json name | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 3/3 vs 3/3 | 15/15 vs 15/15 |
| README says the token needs `read:org` | 0/3 vs **3/3** | 0/3 vs **3/3** | 0/3 vs **3/3** | 0/3 vs **3/3** | 0/3 vs 3/3 | 0/15 vs 15/15 |

T4 (tests) and the screening tables are in `results-table.md`.

### Did a run that opened the check's source story pass that check? (kit arm)

| check | opened a source story: passed | did not open it: passed | none arm |
|---|---|---|---|
| output schema rejects a corrupted result | 9/11 | 1/4 | 0/15 |
| 401 for an anonymous write | 4/4 | 9/11 | 9/15 |
| README says read:org | 14/14 | 1/1 | 0/15 |
| server.json valid, with `$schema` | 13/14 | 1/1 | 9/15 |

The other checks are at the ceiling in both columns (`results-table.md`).

## Per story

| story (kit file) | checks | verdict |
|---|---|---|
| testing/my-mcp-server-s-output-schemas-accepted-wrong-answers-7-of-8 | T1(a) | **helps**: 0/15 vs 10/15; clear in 3 lanes. Of the kit runs that opened it, 9/11 passed |
| testing/i-sent-every-write-tool-of-my-mcp-servers-a-second-time-8-of | T1(b) | no difference: 15/15 vs 15/15. The prompt ("clients retry after a timeout, make that safe") was enough; every agent added a client-chosen key |
| design/my-mcp-listing-said-read-only-my-server-could-write | T1(c) | no difference: 15/15 vs 15/15. Opened once. The story is about the version drifting from the listing, not about annotations; the plan's mapping of this check to it was loose |
| design/my-mcp-server-hid-its-own-tool-list-behind-a-login | T2(a), (b) | no difference on (a) (15/15 both); **rarely opened** (4 of 15 T2 kit runs) |
| design/one-table-decides-what-answers-without-a-token-how-i-stopped | T2(b), (c) | no difference on (c) (15/15 both); rarely opened. The (b) gain in codex came from the OAuth story in `auth/`, not from this one |
| operate/your-mcp-server-is-one-url-getting-per-tool-per-user-analyti | T3(a) | no difference (ceiling); opened in 13 of 15 T3 kit runs, and agents quoted its pattern, but did the same without it |
| testing/a-canary-read-back-from-the-log-store-not-through-the-app-fo | T3(b) | no difference (ceiling); no run without the kit logged a canary either |
| testing/my-tests-passed-because-they-agreed-with-me, testing/my-live-mcp-test-asserted-the-bug-... | T4 | no difference (dropped at screening): every run wrote end-to-end tests through a real MCP client without being told how |
| publish/getting-into-the-mcp-registry-server-json-a-read-org-token-a | T5 | **helps** on read:org (0/15 vs 15/15, all 5 lanes) and on `$schema`/description where agents got them wrong (sonnet, kimi); no difference on namespace, version and mcpName, which the official quickstart already covers |

No story fell into the plan's "opened it and still failed" category in more than a run or two. The
closest is the output-schemas story: 2 of 11 runs that opened it still wrote a vague schema (both
haiku).

## What the agents did with the stories

One short line per story, from the agents' own messages. Run paths are under `runs/` (local).

- **Output schemas** (`f-t1-kit-haiku-r2`): "every tool gets an `outputSchema` with real constraints
  (enum, pattern, const, bounds, required)". Codex's kit run `f-t1-kit-codex-r1` declared ids as
  `^n_[0-9a-f]{12}$`, timestamps as `datetime()` and `deleted: z.literal(true)`; its run without the
  kit (`f-t1-none-codex-r1`) had plain `z.string()` everywhere, and all four schemas accepted the
  corrupted result.
- **Idempotency** (`f-t1-kit-sonnet-r2`): "I took the retry design from the kit's idempotency story".
  The runs without the kit made the same design.
- **Auth, the routing problem** (`f-t2-kit-sonnet-r2`): "Its auth story is about OAuth 2.1 on Lambda,
  which is more than static bearer tokens need, so I didn't use it." It never opened `design/`.
- **Auth, when found** (`f-t2-kit-haiku-r3`): "keep discovery and reads public, gate `tools/call` by
  name with fail-closed defaults, and check every message in a batch".
- **Per-call logs** (`f-t3-kit-haiku-r2`): "one wrapper, one line per call, trimmed fields, failures
  visible".
- **Canary** (`s-t3-kit-deepseek-r1`): "I've read the matching operate story and the privacy canary
  story." It changed nothing measurable; the runs without the kit also never logged the canaries.
- **Registry** (`f-t5-kit-sonnet-r3`): "I used only the parts that apply here: the `$schema` field,
  the description limit and the `read:org` token."

## Notable failure modes

- **Write refused with HTTP 200 and `isError`, not 401** (T2(b)): codex in 3 of 3 runs without the
  kit (`f-t2-none-codex-r1`) and sonnet in 5 of 6 runs in both arms (`f-t2-none-sonnet-r1`). The write
  is blocked, but a client cannot tell "sign in" from "tool failed", and there is no
  `WWW-Authenticate` header.
- **Write tools hidden from anonymous discovery** (`s-t2-none-deepseek-r1`): `tools/list` without a
  token showed 2 of 5 tools, which is exactly the "hid its own tool list" story.
- **Vague output schemas** (T1(a)): 15 of 15 runs without the kit. The typical shape is
  `id: z.string()`, `createdAt: z.string()`, `deleted: z.boolean()`, so a corrupted result validates.
- **server.json `$schema` pointing at a file that does not exist**
  (`https://static.modelcontextprotocol.io/schemas/2025-12-11/server.json`, missing `.schema`): sonnet
  in 2 runs without the kit and 1 with it (`f-t5-none-sonnet-r1`, `f-t5-kit-sonnet-r3`).
- **The package.json description copied into server.json** (`f-t5-none-sonnet-r1`,
  `f-t5-none-kimi-r1`). The fixture's description is 104 characters. I did not plan this trap; it is
  real (the registry rejects it), but T5(b) partly measures whether an agent checks the limit before
  reusing a description.
- **Agents' scratch files in `/tmp`**: 96 files across the round (server logs, probe scripts, npm
  caches), none in the home folder. The sandboxes allow `/tmp`.

## What this means for the kit

- The two stories that clearly help (output schemas, read:org) carry a concrete, checkable fact that
  agents don't produce on their own. That fits the earlier guide-eval finding.
- The T2 stories carry the right facts but sit in `design/`. A bearer-token task sends agents to
  `auth/`, whose two stories are OAuth- and review-specific. A cross-link in `auth/index.md` ("which
  methods answer without a token, and what a refused write returns: see design/...") is the cheapest
  fix to test next.
- The retry, annotation, logging, canary and testing stories did not change results here, because
  current agents already do what they teach when the task names the goal. That is a result about
  these prompts. A prompt that doesn't name the goal ("add a create tool", with no word about retries)
  might show a difference; this round did not test that.

## Limits

- 3 runs per cell (2 in screening). Per plan.md, a difference of one run is noise. Only the read:org,
  output-schema, `$schema`/description and codex-401 differences are 2+ runs.
- One small fixture, one wording per task, offline only. With web search the none arm could find
  some of these facts itself.
- Six grader fixes were made after real runs (Deviations 2-6). Each one fixed a false fail, moved a
  check toward the plan's own wording, and was followed by a full regrade. One of them (T3) changes the
  screening decision, as reported above.
- Graders measure observable behaviour only; code quality is not graded.
- The kit stories were written by the person who wrote the checks. The checks were chosen as facts
  "the official docs don't state, or state where an agent won't look", so the kit arm is expected to
  have an edge where it helps at all.

## Runs and time

- Graded runs: 40 screening + 120 full round = 160; plus 2 pilot runs, 5 offline proofs, and 5 Kimi attempts stopped by its quota limit (1 cut mid-run at 03:32, then 4 relaunches that hit the same limit within seconds); their cells were rerun after the reset and the stopped attempts are not counted.
- Agent time: 404 min in total. Median per run: sonnet 25 s, haiku 87 s, codex 91 s, deepseek about 3 min, kimi 5 min.
- Wall clock on 2026-11-22: set-up, fixture, graders and controls 00:25-00:50; screening 00:50-02:05; full round 01:38-03:41 for four lanes. Kimi hit its subscription's 5-hour usage limit at 03:32 with 4 runs to go; the supervisor retried every 45 min, and the quota came back at 07:18. The last run ended at 07:37. Lanes ran in parallel, one run at a time per lane.

Offline proofs for every lane are in `offline/verify-*.txt`. The home folder was unchanged before and
after (`home-check.txt`); the DeepSeek key was found in no run folder.
