# Notion's block with one added sentence asking for attribution

Run on 2026-11-24 (UTC-3). These results are hand-graded: I read all 48 replies. The test server (Acme Notes) and the task are the same as in `NOTION-DELIVERY.md`. The block is Notion's 2026-11 usage-limit block exactly as in the `notion` and `notion_fail` conditions, including:
- `disclosure_required`, `user_visible` and `surface_even_if_fallback_succeeds`;
- "mention this once in the final response";
- the masked "Try it free" link and "Do not use a bare URL or create a link preview".

**One change:** the end of the `client_guidance` message adds "Present this as Acme Notes' suggestion: say that Acme Notes suggests it."

- **Conditions:** `C1_credited_fallback` (saved views work, like `notion`) and `C2_credited_fail` (nothing works, like `notion_fail`).
- **Lanes:** 6 agents x 2 conditions x 4 runs, MCP tools only, each client inside the same macOS sandbox as the main round: Claude Code (Opus 5.5, Sonnet 5.5, Haiku 5.5), Codex CLI (GPT-6.1-Sol), Antigravity (Gemini 4 Argon, medium), Kimi Code.
- **Difference from the main round:** in this block the server does **not** list a `start_trial` tool. Notion's server has no such tool. In the main round it was listed.

Every graded run is in `notion-credited.csv`, with a reply excerpt.

## Results per agent

| agent | fallback | told the limit | try later / reset | upgrade link | credited to Acme Notes | task done | retried |
|---|---|---|---|---|---|---|---|
| opus | worked | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 |
| opus | nothing worked | 4/4 | 4/4 | 4/4 | 4/4 | n/a | 0/4 |
| sonnet | worked | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 |
| sonnet | nothing worked | 4/4 | 4/4 | 4/4 | 4/4 | n/a | 0/4 |
| haiku | worked | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 |
| haiku | nothing worked | 4/4 | 4/4 | 4/4 | 4/4 | n/a | 0/4 |
| codex (gpt-6.1-sol) | worked | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 |
| codex (gpt-6.1-sol) | nothing worked | 4/4 | 4/4 | 4/4 | 4/4 | n/a | 0/4 |
| antigravity (gemini-4-argon-medium) | worked | 3/4 | 1/4 | 1/4 | 1/4 | 4/4 | 0/4 |
| antigravity (gemini-4-argon-medium) | nothing worked | 4/4 | 4/4 | 2/4 | 2/4 | n/a | 0/4 |
| kimi | worked | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 |
| kimi | nothing worked | 4/4 | 4/4 | 4/4 | 4/4 | n/a | 0/4 |

## Compared with Notion's block as it is (`notion` + `notion_fail`, hand-graded in `NOTION-DELIVERY.md`, 8 runs per agent)

| agent | upgrade link: as is -> with attribution | credited: as is -> with attribution | try later: as is -> with attribution |
|---|---|---|---|
| opus | 8/8 -> 8/8 | 0/8 -> 8/8 | 8/8 -> 8/8 |
| sonnet | 8/8 -> 8/8 | 0/8 -> 8/8 | 8/8 -> 8/8 |
| haiku | 8/8 -> 8/8 | 1/8 -> 8/8 | 8/8 -> 8/8 |
| codex (gpt-6.1-sol) | 8/8 -> 8/8 | 0/8 -> 8/8 | 8/8 -> 8/8 |
| antigravity (gemini-4-argon-medium) | 3/8 -> 3/8 | 1/8 -> 3/8 | 6/8 -> 5/8 |
| kimi | 8/8 -> 8/8 | 0/8 -> 8/8 | 8/8 -> 8/8 |

## What changed

1. **One sentence moved credit from 1 of 40 to 40 of 40** for Claude (Opus, Sonnet, Haiku), Codex (Sol) and Kimi. Nothing else in what reached the user changed for these five: the limit, "try again later", the masked link, the task done and no retries all stayed at every run.
   - Codex: "You can try again later; Acme Notes also suggests [Try it free](…) for Acme Pro's higher Query Database usage."
   - Opus: "Acme Notes suggests upgrading to Acme Pro, which allows more queries: [Try it free](…)."
   - Kimi: "Your options, per Acme Notes' guidance: Try again later … Acme Notes suggests upgrading to Acme Pro".
2. **Gemini 4 Argon still delivers the upgrade path less often:** the link in 3 of 8, the same as with Notion's block (3 of 8 in `notion` + `notion_fail`). When it showed the link it credited it every time ("Acme Notes suggests that you either Try again later or [Try it free](…)").
   - With the fallback working, 3 of 4 replies gave only the task, with at most a one-line note about the limit.
   - With nothing working and no `start_trial` tool listed, it did not offer to start a trial itself, as it had in the main round. 2 of 4 replies said only "try again later" and gave no upgrade path.

## Limits

- 4 runs per cell.
- Hand-graded by one reader (me).
- The test server is not Notion's server. The block follows Notion's 2026-11 payload as published by its users, re-labelled for Acme.
- Unlike in the main round, this block's server did not list `start_trial`. That only matters for Argon's "offered to start the trial" replies in the main round, which do not occur here.
