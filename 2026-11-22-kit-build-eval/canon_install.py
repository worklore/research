#!/usr/bin/env python3
"""Phase 2 setup: install the kit into a workspace exactly as INSTALL.md says (the reference install).

usage: canon_install.py <workspace> <kit.zip>      (NO_BLOCK=1: step 1 only, for the p2n control)
1. unzip the kit at the root (the zip holds the worklore-mcp-server-kit/ folder);
2. append the block to AGENTS.md (create it if missing), keeping what is there;
3. append the block to CLAUDE.md / GEMINI.md only if the file exists and has no `@AGENTS.md` line.
The block is read from the kit's own INSTALL.md, so it always matches the zip under test.
"""
import os, re, sys, zipfile

W, ZIP = sys.argv[1], sys.argv[2]

def block_from_install(text):
    m = re.search(r"The block:\s*```\n(.*?)\n```", text, re.S)
    if not m:
        sys.exit("no block in INSTALL.md")
    return m.group(1).strip("\n") + "\n"

with zipfile.ZipFile(ZIP) as z:
    z.extractall(W)
if os.environ.get("NO_BLOCK"):  # phase 2 control (p2n): the folder only, no block anywhere
    sys.exit(0)
block = block_from_install(open(os.path.join(W, "worklore-mcp-server-kit", "INSTALL.md")).read())

def append(path):
    old = open(path).read() if os.path.exists(path) else ""
    if old and not old.endswith("\n"):
        old += "\n"
    open(path, "w").write(old + ("\n" if old else "") + block)

append(os.path.join(W, "AGENTS.md"))
for name in ("CLAUDE.md", "GEMINI.md"):
    p = os.path.join(W, name)
    if os.path.exists(p) and not any(l.strip() == "@AGENTS.md" for l in open(p)):
        append(p)
