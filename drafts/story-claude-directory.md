---
title: "Submitting an MCP server to the Claude connectors directory: no Team plan needed, and the auth option the portal suggests would break it"
date: 2026-10-06
tags: mcp, claude, connectors-directory, submission, oauth
type: proposal
status: open
reproducible: true
stack: Remote MCP server (Streamable HTTP) · OAuth 2.1 with dynamic client registration · Claude connectors directory
agent: Claude Code
model: claude-opus-5-5
---

# Submitting an MCP server to the Claude connectors directory: no Team plan needed, and the auth option the portal suggests would break it

**This is a proposal, not a result.** I submitted today and the review isn't in. I'm writing it now because two of the things I learned don't depend on the outcome.

For almost a month I had a card on my board: "decide whether to buy a Claude Team plan, about $40 a month, just to submit to the directory". When I'd last read about it, submissions lived in an organisation's admin settings, which a personal plan doesn't have. A reader on Reddit corrected me: there is now a developer portal at claude.ai/directory/manage, and the current docs say any paid plan can submit. On Pro or Max you submit from your own account. I checked the docs, closed the card, and submitted the same afternoon.

The second thing was a trap. My server answers search and reading without a token, on purpose, and requires sign-in only for publishing and editing. The portal connected to it, saw a 200, and marked the authentication requirement as "None — Detected". Accepting it would have told Claude the server needs no sign-in, so Claude would have no reason to offer one, and the write tools would answer 401 to everyone. The right answer was "Required when the server asks", with OAuth dynamic client registration. Before choosing it I checked that a write without a token really returns 401 with a `WWW-Authenticate` header pointing at the sign-in metadata, because that is the signal Claude prompts on.

The rest was paperwork, and one more lesson from it: the example prompts in the form link to real pages, and the first story link in my draft, written from memory, returned 404. A reviewer clicks those. Check every link before you paste it.

## Reproduce this

**Unverified.** These steps produced a submission whose review is pending. If you run them and get a different result, I'd like to know.

Prerequisites: a deployed remote MCP server reachable over HTTPS, a paid Claude plan (Pro, Max, Team or Enterprise; on Team or Enterprise an Owner or someone with the Directory permission submits), a public documentation page, a privacy policy URL, and a test account a reviewer can use.

Your agent will need from you: the server URL, which tools write or delete, how users sign in, the documentation, privacy and support URLs, and test-account credentials (have the agent put the password in your clipboard rather than print it).

Steps:

1. Read the current submission docs before deciding anything about plans: https://claude.com/docs/connectors/building/submission.md. Requirements have changed; what you read a month ago may be wrong.
2. Check annotations from the live server, not the code: call `tools/list` and confirm every tool has a `title` and a `readOnlyHint` or `destructiveHint`. The portal flags tools without them.
3. Make the claims true. A tool marked read-only must not write.
4. Connect the server as a custom connector in Claude, reconnect after any server change so Claude picks up the current tool list, and call every tool once. The form asks you to confirm this.
5. Open claude.ai/directory/manage → Submit new → MCP connector, and paste the server URL.
6. Listing: pick one or two categories that really fit; write a one-liner (up to 200 characters) and a description (up to 2,000) that state plainly what needs sign-in and what doesn't. Reviewers compare the description with the tools.
7. Use cases: for each, an example prompt. Open every link inside the prompts and confirm it loads.
8. Authentication: if any tool needs sign-in, do not accept "None", even if the portal detected it. If reading works anonymously and writing needs sign-in, choose "Required when the server asks". Verify first: a write call without a token returns 401 with `WWW-Authenticate: Bearer resource_metadata="…"`; your authorization server metadata lists a `registration_endpoint` (for dynamic client registration) and `S256` in `code_challenge_methods_supported`.
9. Company: a solo developer can use the product name; the contact email is not public.
10. Test & launch: give step-by-step reviewer instructions, including which tools work without signing in, how to sign in to the test account, and one example call per tool. If writes in the test account go to a sandbox, say so.

Verify: the portal shows the submission as received; the status and any reviewer feedback appear at claude.ai/directory/manage. According to the docs, a submission is scanned automatically and by default listed as a Community connector; some also get a review from a person. I'll update this story with what actually happens.
