#!/usr/bin/env python3
"""Who shows what, and does it pay? Public GitHub profile data only (no LinkedIn).

Group A "writers": dev.to authors from research/2026-10-06-devto-sites with a GitHub username.
Group B "builders": owners (type User) of repos with >=10 stars pushed in the last 7 days.
Per person: company, hireable (GitHub's own 'Available for hire'), bio, blog, social accounts,
followers, public repos, total stars on own non-fork repos (top 100 by stars).
"""
import json, os, subprocess, datetime, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))

def gh(path):
    r = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github+json", path], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None

def profile(login, group):
    u = gh(f"users/{login}")
    if not u or u.get("type") != "User":
        return None
    socials = gh(f"users/{login}/social_accounts") or []
    repos = gh(f"users/{login}/repos?per_page=100&sort=pushed&type=owner") or []
    own = [r for r in repos if not r.get("fork")]
    return {"group": group, "login": login, "name": u.get("name"), "company": u.get("company") or "",
            "hireable": bool(u.get("hireable")), "bio": (u.get("bio") or "")[:300], "blog": u.get("blog") or "",
            "twitter": u.get("twitter_username") or "", "socials": [s.get("provider") for s in socials],
            "social_urls": [s.get("url") for s in socials], "followers": u.get("followers", 0),
            "following": u.get("following", 0), "public_repos": u.get("public_repos", 0),
            "stars": sum(r.get("stargazers_count", 0) for r in own), "created": u.get("created_at", "")[:10],
            "pushed_recently": sum(1 for r in own if r.get("pushed_at", "") >= (datetime.date.today() - datetime.timedelta(days=30)).isoformat())}

def writers():
    rows = json.load(open(os.path.join(HERE, "..", "2026-10-06-devto-sites", "profiles.json")))
    return [(r["github"], "writers") for r in rows if r.get("github")]

def builders(n=100):
    since = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    seen, out, page = set(), [], 1
    while len(out) < n * 2 and page <= 10:
        res = gh(f"search/repositories?q=pushed:>={since}+stars:10..5000+fork:false&sort=updated&order=desc&per_page=100&page={page}")
        for r in (res or {}).get("items", []):
            o = r["owner"]
            if o["type"] == "User" and o["login"] not in seen:
                seen.add(o["login"]); out.append((o["login"], "builders"))
        page += 1
    return out

if __name__ == "__main__":
    w = writers(); b = builders()
    wl = {l for l, _ in w}
    b = [x for x in b if x[0] not in wl]
    with cf.ThreadPoolExecutor(6) as ex:
        rows = [r for r in ex.map(lambda x: profile(*x), w + b) if r]
    bw = [r for r in rows if r["group"] == "builders"][:100]
    rows = [r for r in rows if r["group"] == "writers"] + bw
    json.dump(rows, open(os.path.join(HERE, "people.json"), "w"), indent=1, ensure_ascii=False)
    print({g: sum(1 for r in rows if r["group"] == g) for g in ("writers", "builders")})
