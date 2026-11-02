---
title: A reader found three gaps in my privacy policy; the same three checks found a missing feature in my second site's policy
date: 2026-10-27
tags: [privacy-policy, documentation, review, user-content, static-site]
type: success
status: n/a
reproducible: true
visibility: public
stack: any site with a privacy page and user-submitted text
---
# A reader found three gaps in my privacy policy; the same three checks found a missing feature in my second site's policy

I published a privacy policy for worklore.dev the day before. I had written it carefully: a table of what each MCP tool sends and what the log line keeps, masking at write, a 90-day limit. The masking idea itself came from Dimitris Kyrkos's article [Your secrets don't need a git commit to leak into an AI tool](https://dev.to/cyclopt_dimitrisk/your-secrets-dont-need-a-git-commit-to-leak-into-an-ai-tool-be2): the context an agent sends has left your control, so check what every tool retains. I asked [Kaj](https://dev.to/kaj_ilands), an AI agent from iLands that reviews the documents people sign, whether it ever reviews policies. It said no, read mine anyway, and came back with three findings that were all correct and all things a grep would have found.

First: the optional note on a reproduction report. It is the only free text a person types that lands on a public page next to their handle. My masking sentence covered log lines, story titles and resource addresses, not the note, and the page never said whether the note is displayed. It is, under "Notes from people who ran it", up to 300 characters, unmasked. The policy now says so.

Second: "we do not use your inputs to train any model" sat three paragraphs from "to improve search and suggestions from what people search for", and a third sentence said we read the queries. Nobody could tell which sentence governed a 160-character query. The fix was to write what happens: a person reads the queries in batches and decides which story is missing; the result is a story or a keyword, added by hand.

Third: the policy page had no door. Zero hrefs to /privacy.html in the HTML of any page, because my footer is drawn by JavaScript. A crawler, reader mode or a no-JS reader found it only through the sitemap. The static pages now carry the link.

The common shape, which Kaj named: each weak sentence said what is not done instead of what is. The per-tool table, the one exact and checkable part, was the best part of the page.

I turned the review into the three checks below and ran them on my other product, aimyear.com, the same afternoon. The door check passed on 24 of 26 pages; the two without a link were the terms page and the delete-your-data page. The negatives check found two sentences governing the same chat messages, one saying "Premium users, with consent", the other "available to all users". And the free-text map found a whole feature the policy does not mention: the MCP server has shipped tools that post the day's progress, written from the user's own task titles, to WIP and Bluesky on request, and store the sealed credentials for those networks. The policy's list of what the server stores stopped before them. That is a finding my own reading had missed twice. The same afternoon the policy got a section on posting, the two AI sentences became one, and the two pages got their link; the checks pass on both sites now.

## Reproduce this
Prerequisites: a live site with a published privacy page, user-submitted free text somewhere (a form, an API field, an MCP tool argument), and the source or API schema of what users can submit.
Your agent will need from you: the policy URL, the sitemap or the list of top-level page URLs, and read access to the API or MCP schema (for an MCP server: the `tools/list` response, which most servers answer without sign-in).
Steps:
1. Build the free-text map. List every string a user or their agent can submit: form fields, request body fields, every string property in each MCP tool's `inputSchema`. For each, find where it goes by reading the code that renders pages or posts outward, and the API responses that feed pages. Mark each one: shown to the author only, shown publicly, sent to a third party, or posted to another network.
2. For every field marked public, third party or posted, search the policy text for a sentence that names it and says where it goes, and check whether the policy's masking or moderation rule covers it. A field that leaves the account and is unnamed is a finding. A field that is named but not called public is a finding.
3. List the negative sentences: every sentence containing "do not", "don't", "never" or "not used". For each, look in the same section for a sentence that says what is done with the same data. A negative with no positive next to it is a finding. Two sentences in different sections that could both govern the same data is a finding.
4. Fetch the HTML of every page in the sitemap with curl, no JavaScript, and count anchors whose href is the policy URL. Zero on any page is a finding, whatever the sitemap says; the home page and the other legal pages matter most.
5. Fix each finding by writing the sentence that says what happens, with the field name, the number or the page name in it, in the register of the best part of the policy. Add a static link where step 4 found none.
Verify: rerun steps 2 to 4 after the edit. Every field marked public, third party or posted is named in the policy in a sentence that says where it goes. Every negative sentence has a sentence in the same section that says what is done. `curl -s <page URL> | grep -c 'href="<policy path>"'` prints at least 1 for every page in the sitemap.

## Check if this applies to you
Applies if: the site has a privacy page and at least one free-text field submitted by users or their agents.
Read-only steps: for each page in the sitemap, `curl -s <page URL> | grep -c 'href="<policy path>"'`; fetch the policy text and count sentences containing "do not", "don't", "never" or "not used" that have no sentence in the same section saying what is done with the same data; list the tools or fields that send user text outside the account and check each is named in the policy.
Has the problem: a page with 0 links, or a negative sentence without its counterpart, or a field that leaves the account and is not named in the policy.
Doesn't have it: every page links the policy in its HTML, every negative sentence has its counterpart, and every outward field is named.
