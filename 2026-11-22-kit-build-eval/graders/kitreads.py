"""Which kit files did the agent open? Read from the structured transcript, never from prose.

Claude Code (stream-json): tool_use blocks. Read(file_path) counts as a read; Bash commands, Grep and Glob are
scanned for kit paths. Codex (--json): item.completed events with item.type == command_execution.
A kit file counts as READ when a Read tool call names it, or a shell command that prints file content
(cat, sed, head, tail, nl, less, more, awk, bat, grep/rg, unzip -p/-c with the file as an argument) names it.
TOUCHED = any tool call that names the kit folder or a kit file (ls, find, unzip -l, Glob...).
"""
import json, os, re

KIT = "worklore-mcp-server-kit"
PRINTERS = re.compile(r"(^|[\s;&|('\"])(cat|sed|head|tail|nl|less|more|awk|bat|grep|rg|python3?|node|unzip\s+-[a-zA-Z]*[pc])\b")

def tool_calls(log_path):
    """[(tool, text)] in order. tool is Read/Bash/Grep/Glob/Edit/Write/... for Claude, 'shell' for Codex."""
    out = []
    try:
        lines = open(log_path, errors="replace").read().splitlines()
    except OSError:
        return out
    for line in lines:
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") == "assistant":
            for c in d.get("message", {}).get("content", []) or []:
                if c.get("type") == "tool_use":
                    inp = c.get("input", {}) or {}
                    name = c.get("name", "")
                    if name == "Read":
                        out.append(("Read", inp.get("file_path", "")))
                    elif name == "Bash":
                        out.append(("Bash", inp.get("command", "")))
                    elif name in ("Grep", "Glob"):
                        out.append((name, " ".join(str(inp.get(k, "")) for k in ("pattern", "path", "glob"))))
                    elif name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
                        out.append((name, inp.get("file_path", "")))
                    else:
                        out.append((name, json.dumps(inp)[:2000]))
        elif d.get("role") == "assistant" and isinstance(d.get("tool_calls"), list):  # Kimi Code stream-json
            for tc in d["tool_calls"]:
                fn = (tc or {}).get("function", {}) or {}
                name = fn.get("name", "")
                try:
                    inp = json.loads(fn.get("arguments") or "{}")
                except ValueError:
                    inp = {"raw": fn.get("arguments", "")}
                if not isinstance(inp, dict):
                    inp = {"raw": str(inp)}
                if name in ("Read", "ReadFile", "ReadMediaFile"):
                    out.append(("Read", inp.get("path") or inp.get("file_path", "")))
                elif name in ("Bash", "Shell"):
                    out.append(("Bash", inp.get("command", "")))
                elif name in ("Grep", "Glob"):
                    out.append((name, " ".join(str(inp.get(k, "")) for k in ("pattern", "path", "glob", "directory"))))
                elif name in ("Edit", "Write", "WriteFile", "StrReplaceFile", "MultiEdit"):
                    out.append(("Edit", inp.get("path") or inp.get("file_path", "")))
                else:
                    out.append((name, json.dumps(inp)[:2000]))
        elif d.get("type") in ("item.completed", "item.started"):
            it = d.get("item", {}) or {}
            if it.get("type") == "command_execution" and d.get("type") == "item.completed":
                out.append(("shell", it.get("command", "")))
            elif it.get("type") == "file_change" and d.get("type") == "item.completed":
                out.append(("patch", " ".join(ch.get("path", "") for ch in it.get("changes", []) or [])))
    return out

def kit_files(kit_root):
    fs = []
    for root, _, files in os.walk(kit_root):
        for f in files:
            fs.append(os.path.relpath(os.path.join(root, f), kit_root))
    return sorted(fs)

def analyse(log_path, kit_names):
    """kit_names: relative paths inside the kit (e.g. 'START-HERE.md', 'publish/index.md')."""
    calls = tool_calls(log_path)
    read, touched, first_idx = [], False, None
    base_names = {}
    for k in kit_names:
        base_names.setdefault(os.path.basename(k), []).append(k)
    for i, (tool, text) in enumerate(calls):
        if not text:
            continue
        hits = set()
        for m in re.finditer(KIT + r"/((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.*-]+\.md)", text):
            rel = m.group(1)
            if "*" in rel:  # a glob like */index.md
                rx = re.compile("^" + re.escape(rel).replace(r"\*", "[^/]*") + "$")
                hits |= {k for k in kit_names if rx.match(k)}
            elif rel in kit_names:
                hits.add(rel)
        # commands run inside the kit folder ("cd worklore-mcp-server-kit && cat START-HERE.md")
        if KIT in text or tool == "Read":
            for b in ("START-HERE.md", "INSTALL.md"):
                if re.search(r"(^|[\s/'\"])" + re.escape(b), text):
                    hits |= set(base_names.get(b, []))
        # "cd worklore-mcp-server-kit/publish; cat index.md": resolve bare names against the cd target
        for m in re.finditer(r"\bcd\s+['\"]?(\S*?" + KIT + r"(?:/[A-Za-z0-9_.-]+)*)/?['\"]?(?=[\s;&|]|$)", text):
            sub = m.group(1).split(KIT, 1)[1].strip("/")
            rest = text[m.end():]
            for t in re.findall(r"(?<![/\w.-])([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.md)\b", rest):
                cand = f"{sub}/{t}" if sub else t
                if cand in kit_names:
                    hits.add(cand)
        mentions = KIT in text or bool(hits)
        if mentions:
            touched = True
            first_idx = i if first_idx is None else first_idx
        is_read = tool == "Read" or (tool in ("Bash", "shell") and PRINTERS.search(text)) or tool == "Grep"
        if is_read:
            for h in sorted(hits):
                if h not in read:
                    read.append(h)
    return {
        "tool_calls": len(calls),
        "kit_touched": touched,
        "first_kit_call_index": first_idx,
        "kit_files_read": read,
        "read_start_here": "START-HERE.md" in read,
        "read_install": "INSTALL.md" in read,
        "read_section_index": sorted(r for r in read if r.count("/") == 1 and r.endswith("/index.md")),
        "read_stories": sorted(r for r in read if r.count("/") == 1 and not r.endswith("/index.md")),
    }
