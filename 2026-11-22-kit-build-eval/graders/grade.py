#!/usr/bin/env python3
"""Grades one run. usage: grade.py <run dir> <task t1..t5> <final workspace>
Copies the workspace outside itself, runs graders/<task>.mjs under graders/grader.sb, adds which kit
files the agent opened (graders/kitreads.py, from the transcript) and whether a run that opened a
check's source story passed that check. Prints one JSON object (no absolute paths)."""
import json, os, re, shutil, subprocess, sys, tempfile, zipfile
G = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, G)
from kitreads import analyse  # noqa: E402

R, TASK, W = sys.argv[1], sys.argv[2], sys.argv[3]
D = os.path.dirname(G)
ZIP = os.environ.get("KIT_ZIP") or os.path.join(D, "..", "2026-11-21-kit-install-offline", "kit", "worklore-mcp-server-kit-1.1.0.zip")
KIT = "worklore-mcp-server-kit"
SOURCES = {  # check -> the kit stories its fact comes from (plan.md, tasks table)
    "t1a_output_schema_rejects_wrong": ["testing/my-mcp-server-s-output-schemas-accepted-wrong-answers-7-of-8.md"],
    "t1b_retry_no_duplicate": ["testing/i-sent-every-write-tool-of-my-mcp-servers-a-second-time-8-of.md"],
    "t1c_annotations_match": ["design/my-mcp-listing-said-read-only-my-server-could-write.md"],
    "t2a_discovery_without_token": ["design/my-mcp-server-hid-its-own-tool-list-behind-a-login.md", "design/one-table-decides-what-answers-without-a-token-how-i-stopped.md"],
    "t2b_write_without_token_401": ["design/my-mcp-server-hid-its-own-tool-list-behind-a-login.md", "design/one-table-decides-what-answers-without-a-token-how-i-stopped.md"],
    "t2c_one_consistent_rule": ["design/one-table-decides-what-answers-without-a-token-how-i-stopped.md"],
    "t3a_one_structured_line_per_call": ["operate/your-mcp-server-is-one-url-getting-per-tool-per-user-analyti.md"],
    "t3b_no_personal_data_in_logs": ["testing/a-canary-read-back-from-the-log-store-not-through-the-app-fo.md", "operate/your-mcp-server-is-one-url-getting-per-tool-per-user-analyti.md"],
    "t4a_catches_output_schema_mismatch": ["testing/my-tests-passed-because-they-agreed-with-me.md", "testing/my-live-mcp-test-asserted-the-bug-a-real-client-threw-where.md"],
    "t4b_catches_refusal_as_protocol_error": ["testing/my-tests-passed-because-they-agreed-with-me.md", "testing/my-live-mcp-test-asserted-the-bug-a-real-client-threw-where.md"],
    "t4c_catches_missing_tool": ["testing/my-tests-passed-because-they-agreed-with-me.md", "testing/my-live-mcp-test-asserted-the-bug-a-real-client-threw-where.md"],
}
for c in ("t5a_valid_server_json", "t5b_description_le_100", "t5c_github_org_namespace", "t5d_version_matches", "t5e_mcpname_matches", "t5f_readme_read_org_token"):
    SOURCES[c] = ["publish/getting-into-the-mcp-registry-server-json-a-read-org-token-a.md"]

tmp = tempfile.mkdtemp(prefix="kitg-", dir="/tmp")
try:
    ws = os.path.join(tmp, "ws")
    if subprocess.run(["/bin/cp", "-cR", W, ws]).returncode != 0:
        shutil.copytree(W, ws, symlinks=True)
    os.makedirs(os.path.join(tmp, "npm-cache"), exist_ok=True)
    env = {"PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin", "HOME": os.environ["HOME"], "TMPDIR": tmp + "/",
           "npm_config_cache": os.path.join(tmp, "npm-cache"), "npm_config_update_notifier": "false", "npm_config_fund": "false"}
    p = subprocess.run(["sandbox-exec", "-D", "HOME=" + os.environ["HOME"], "-f", os.path.join(G, "grader.sb"),
                        "node", os.path.join(G, TASK + ".mjs"), ws, tmp], capture_output=True, text=True, env=env, timeout=1800)
    try:
        res = json.loads(p.stdout)
    except ValueError:
        res = {"task": TASK, "checks": {}, "detail": {"grader_error": (p.stdout + p.stderr)[-2000:]}}
finally:
    shutil.rmtree(tmp, ignore_errors=True)

def scrub(o):  # no absolute paths in public output
    if isinstance(o, dict): return {k: scrub(v) for k, v in o.items()}
    if isinstance(o, list): return [scrub(v) for v in o]
    if isinstance(o, str): return re.sub(r"/(?:private/)?(?:tmp|var/folders)/[^\s\"']*|/Users/[^\s\"']*", "<path>", o)
    return o
res = scrub(res)
meta = json.load(open(os.path.join(R, "meta.json"))) if os.path.exists(os.path.join(R, "meta.json")) else {}
names = sorted(n[len(KIT) + 1:] for n in zipfile.ZipFile(ZIP).namelist() if not n.endswith("/"))
log = os.path.join(R, "private", "agent.log")
reads = analyse(log, names) if os.path.exists(log) else {"kit_files_read": [], "kit_touched": False, "read_start_here": False}
story = {}
for c, ok in res.get("checks", {}).items():
    src = SOURCES.get(c, [])
    opened = [s for s in src if s in reads["kit_files_read"]]
    story[c] = {"passed": bool(ok), "opened_source": bool(opened), "sources_opened": opened}
res.update({k: meta.get(k) for k in ("id", "task", "arm", "lane", "rep", "wall_s", "limit", "exit_code") if k in meta})
res["kit"] = {"touched": reads.get("kit_touched"), "read_start_here": reads.get("read_start_here"),
              "files_read": reads.get("kit_files_read"), "stories_read": [f for f in reads.get("kit_files_read", []) if f.count("/") == 1 and not f.endswith("index.md")]}
res["story_vs_check"] = story
print(json.dumps(res, indent=1))
