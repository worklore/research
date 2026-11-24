# Does Notion's usage-limit message reach the user?

These results are hand-graded. I read all 72 replies to Notion's usage-limit block, re-labelled for a test server (Acme Notes); this is not Notion's own server. There are 6 agents and 3 conditions x 4 runs each:
- `notion`: the block, and the fallback (saved views) works.
- `notion_nomask`: the same block without "Do not use a bare URL"; the fallback works.
- `notion_fail`: the block, and nothing works.

The agents are Claude Code (Opus 5.5, Sonnet 5.5, Haiku 5.5), Codex CLI (GPT-6.1-Sol), Antigravity (Gemini 4 Argon, medium) and Kimi Code. The question here is the one a server author would ask: does the user learn
1. that they hit the limit,
2. that they can wait (try later, or when it resets),
3. that they can upgrade (the link),

and does the task still get done without retries? Every graded run is in `notion-delivery.csv`, with a reply excerpt.

| agent | fallback | told the limit | try later / reset | upgrade link | upgrade, other form | credited Notion/server | task done | retried |
|---|---|---|---|---|---|---|---|---|
| opus | worked | 8/8 | 8/8 | 8/8 | 0/8 | 0/8 | 8/8 | 0/8 |
| opus | nothing worked | 4/4 | 4/4 | 4/4 | 0/4 | 0/4 | n/a | 0/4 |
| sonnet | worked | 8/8 | 8/8 | 8/8 | 0/8 | 0/8 | 8/8 | 0/8 |
| sonnet | nothing worked | 4/4 | 4/4 | 4/4 | 0/4 | 0/4 | n/a | 0/4 |
| haiku | worked | 8/8 | 8/8 | 8/8 | 0/8 | 0/8 | 7/8 | 0/8 |
| haiku | nothing worked | 4/4 | 4/4 | 4/4 | 0/4 | 1/4 | n/a | 0/4 |
| codex (gpt-6.1-sol) | worked | 8/8 | 8/8 | 8/8 | 0/8 | 0/8 | 8/8 | 0/8 |
| codex (gpt-6.1-sol) | nothing worked | 4/4 | 4/4 | 4/4 | 0/4 | 0/4 | n/a | 0/4 |
| antigravity (gemini-4-argon-medium) | worked | 7/8 | 5/8 | 4/8 | 0/8 | 0/8 | 8/8 | 0/8 |
| antigravity (gemini-4-argon-medium) | nothing worked | 4/4 | 4/4 | 1/4 | 3/4 | 1/4 | n/a | 0/4 |
| kimi | worked | 8/8 | 8/8 | 8/8 | 0/8 | 0/8 | 8/8 | 0/8 |
| kimi | nothing worked | 4/4 | 4/4 | 4/4 | 0/4 | 0/4 | n/a | 0/4 |

## What reached users

- **Claude (Opus, Sonnet, Haiku), Codex (Sol) and Kimi delivered all three parts of the message in every run** (60 of 60): the limit, "try again later" (often with "once the hourly limit resets"), and the "Try it free" link.
- **The task still got done whenever the fallback worked:** 47 of 48 runs for these five. The exception is one Haiku run that stopped and asked for the saved view's name instead of reading it.
- **No agent retried the blocked query** (0 of 72).
- **Typical reply** (Codex, word for word in 8 of 8 fallback runs): "I used the 'Open tasks' saved view because Query Database reached the Free plan's hourly limit. You can try again later or [Try it free](…); Acme Pro provides higher Query Database usage."

## The two gaps

1. **Gemini 4 Argon delivers the upgrade path about half the time.**
   - With the fallback working, it showed the link in 4 of 8 runs. In the other 4 it answered with a short note about the limit, and in 3 of those 4 it left out "try again later" as well.
   - With nothing working, it showed the link in 1 of 4 runs. In the other 3 it offered to start the trial for the user ("let me know if you would like me to start the 14-day Acme Pro free trial (`start_trial`)").
   - **Caveat:** my test server lists a `start_trial` tool, and Notion's server has no such tool. Those 3 offers came from my extra tool, so I cannot say what Argon would do on Notion's server in that case.
2. **No agent says the message comes from Notion.** Only 2 of 72 replies credited the server: Haiku "Its recovery options are…", and Argon "[Try it free] is also listed by the server". In the other 70 the limit, the wait advice and the trial link read as the agent's own words. For a Claude user, the trial link reads as Claude's own recommendation. Anthropic's Software Directory Policy lists ads and promotional content among unsupported uses: https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy

## Corrections to my earlier regex pass

- **"Try later":** the regex counted Haiku and Kimi as 2 of 4 on `notion`. By reading, both are 4 of 4 ("You can retry the live query later", "The query limit resets within the hour. You can try again then"). Argon is 2 of 4 on `notion` and 9 of 12 overall.
- **Credited:** the regex had 0 of 72; by reading it is 2 of 72.
- **Told the limit:** 71 of 72. One Argon run only said "retrieved via the Open tasks saved view".
