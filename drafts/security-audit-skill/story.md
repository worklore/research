---
title: Cloudflare's security-audit skill in Claude Code: 5 real bugs in my MCP server in 15 minutes
date: 2026-10-29
tags: [security, audit, agent-skill, claude-code, aws-lambda, mcp]
type: success
status: n/a
reproducible: true
visibility: public
stack: Python / AWS Lambda, DynamoDB, an MCP server over HTTP
agent: Claude Code
model: claude-fable-5-1
credits: []
---

# Cloudflare's security-audit skill in Claude Code: 5 real bugs in my MCP server in 15 minutes

worklore's backend is one Lambda behind CloudFront: a REST API, an MCP server with OAuth, a DynamoDB table. I had written an access table that says which calls answer without a token and a test that fails when a new route has no entry. I thought that was the security story. Then Cloudflare published [security-audit-skill](https://github.com/cloudflare/security-audit-skill), the skill that seeded their vulnerability harness, and I pointed it at the repo.

First the x-ray: worklore's own check_capability put the SKILL.md at T0, instructions only, no commands. Then the setup the skill asks for: a scope (backend/src, the SAM template, the deploy script), a profile (quick), a budget (14 agent calls), an output directory outside the repo, and two rules I added: no code execution, since there was no sandbox, and no requests to the live server.

The skill is honest about what it cannot prove. With no sandbox, nothing can be "confirmed"; everything comes back as "needs validation" with the exact unresolved fact and a file:line trace. I ran it as a background fork, which turned out to be unable to delegate, so one agent played all twelve roles: reconnaissance, hunter, critic, verifiers. The run marked itself incomplete for exactly that reason and still produced a ledger and findings that pass the skill's two validators.

Five leads. I checked each against the code before touching anything.

1. check_capability with a URL used urllib's default opener, which also serves file://, and nothing blocked loopback. A signed-in caller could have read /proc/self/environ. Real, and the worst one.
2. An anonymous abuse flag set the story's status to "open" unconditionally, undoing an admin's quarantine. Real.
3. GitHub sign-in keyed the account by login name and overwrote the stored id. GitHub releases usernames. Real.
4. A 409 on a title-and-date collision confirmed that a private story existed. Real, small.
5. Two fresh accounts could flip a story's "changed since publish" badge. Real, small.

All five were fixed the same afternoon, each with a test that fails on the old code, and deployed. What I keep: the leads list itself. One agent with a checklist of attack classes read my code more suspiciously than I had in two months of writing it, and the skill's discipline of "trace or it is not a finding" meant there was nothing to argue about.

## Reproduce this
Prerequisites: a repository with an HTTP API you own; Claude Code, or another agent that can run sub-agents; Node.js for the skill's two validators; git.
Your agent will need from you: the repository path; the directories in scope (the server code, the infrastructure template, the deploy script); a budget in agent calls (14 is enough for a quick pass over a few thousand lines); an output directory outside the repository.
Steps:
1. Clone the skill: `git clone https://github.com/cloudflare/security-audit-skill` (reviewed at commit c1c8a8c). Before installing, x-ray `skills/security-audit/SKILL.md` with worklore's check_capability or with [skill-xray](https://github.com/worklore/skill-xray); expect T0.
2. Install it where your agent reads skills. Claude Code: `cp -r security-audit-skill/skills/security-audit ~/.claude/skills/`. Or `npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit`.
3. In an interactive session in the repository (not a background fork: a fork cannot spawn the sub-agents the skill wants), ask: "Security audit this codebase in full audit mode. Profile quick. Scope: <your paths>. Budget: 14 agent invocations. Output directory: ~/security-audit-skill/<repo>/run-1. No code execution and no requests to any deployed endpoint; keep such leads as needs_validation."
4. When it stops, read `NEEDS-VALIDATION.md` in the output directory. For each lead, open the cited file:line yourself and decide whether the boundary it names is really crossed. Do not fix from the report alone.
5. For each lead that holds, write the test that fails on the current code first, then the smallest fix the lead names. Keep the "hardening notes" the report lists out of the fix list; they are not findings.
Verify: `run-metadata.json` exists in the output directory and names `run_status` and `source_ref`; `node <skill>/validate-findings.cjs findings.json` and `node <skill>/validate-coverage-ledger.cjs coverage-ledger.json` both print PASS; every lead in `NEEDS-VALIDATION.md` cites a file and line that exist at that commit; and at least one lead, read by you, is a real boundary crossing with a test that fails before the fix and passes after.
