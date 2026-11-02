# Hand check of 20 flagged findings (2026-10-27)

Seeded sample (`random.Random(20)`): 8 "negative sentence without a positive counterpart", 7 "conflicting sentence pairs", 5 "typed text goes outward to an unnamed place". Each judged against the policy section text (`sample20.txt`). TP = the finding holds as a reader would see it; weak = holds but minor or arguable; FP = not a finding.

## Negatives without a positive counterpart: 1 of 8 (12%)

| # | host | verdict | why |
|---|---|---|---|
| 1 | aipricinghub.com | FP | "Provider integration is not enabled yet" is a product note, not a data sentence |
| 2 | ofacscreen.com | FP | section says exactly what the public verification page shows; "not listed by search engines" is an extra fact |
| 3 | buywise.fyi | FP | section says when it runs and what is sent; the negative is part of a complete description |
| 4 | countersignatory.com | FP | the positive ("hashed on the way in") is in the same sentence |
| 5 | api.buyerawareapp.com | FP | a disclaimer about verdicts, not data handling |
| 6 | larabench.com | FP | "no telemetry toggle" sits next to what you can do instead (block GA in the browser) |
| 7 | myinsurancecity.com | weak TP | the section lists what the chat never asks for and never says what happens to what you type |
| 8 | vaultvision.tech | FP | an instruction to the user next to a sentence on what the service does |

Verdict: the model flags any negative sentence. The check as Kaj applied it (a negative that leaves the reader unable to tell what happens to a given piece of data) is really the conflict check plus "is the data's fate stated anywhere". Drop this count from the headline; keep the sentence list as raw material only.

## Conflicting sentence pairs: 4 of 7 (57%; 3 of 7 strict)

| # | host | verdict | why |
|---|---|---|---|
| 9 | clippingalpha.com | TP | "never share your tier with anyone" vs tier decides which list Google and Meta see you in |
| 10 | peerpush.com | TP | "content sent to AI providers not used to train" vs "may share with AI companies including to train models"; the reader cannot tell which covers product data |
| 11 | binruleschecker.co.uk | weak TP | analytics "shared with nobody" vs hosting and AI tools that hold the site's data; different data, same register problem |
| 12 | checkmypayrate.com | TP | language "stays on your device, not transmitted" vs Umami records a language-selection event |
| 13 | peerpush.com | FP | "never store raw IP" and "stored as a one-way hash" agree |
| 14 | hedgr.app | FP | the two sentences are adjacent and the second explains the first |
| 15 | music-studio.linxule.com | FP | two different tool sets (player tools vs service tools); consistent |

## Typed text goes outward, unnamed: 4 of 5 (80%; 2 of 5 strict)

| # | host | verdict | why |
|---|---|---|---|
| 16 | api.buyerawareapp.com | FP | the policy names Anthropic's web search as the searcher; the claim asks for a provider that is already named |
| 17 | clippingalpha.com | weak TP | a thorough policy that still says nothing about what happens to the arguments of anonymous MCP calls |
| 18 | chargerdojo.com | TP | "integrations with third-party platforms (e.g., AI APIs, cloud providers) follow their own privacy policies" names no recipient |
| 19 | agentready.market | TP | the store URL is fetched from the store's own site by the scanner; the policy lists the URL as collected, never as sent |
| 20 | cybergenic.im | weak TP | a template policy; nothing about the product's own tools, so "where it goes" is unanswered by omission |

## What this means for the write-up

- Report the door check (exact), the "policy exists" and "tools/list open" counts (exact), the "policy mentions agents/MCP/tool calls at all" count (exact string match, checked by eye on 10: holds), and the conflicts and outward findings only after a hand pass on each row used.
- Do not report the "negatives without positive" count.
- Expected yield for a hand pass: about half of the conflict pairs and most of the outward claims survive, so for 50 policies with conflicts expect roughly 50 real pairs to pick examples from.
