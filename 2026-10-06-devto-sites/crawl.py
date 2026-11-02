#!/usr/bin/env python3
"""What do developers show on their own sites? 100 dev.to authors with a personal site.

Sources: the public dev.to API (profile + article count) and ONE GET of each author's
own homepage. No LinkedIn scraping (LinkedIn's terms forbid it, and job-search status
is personal): we only note whether the site links to LinkedIn, and what the author
says about work in their own bio/site. Aggregates are the point; per-row data stays
in this research folder.
"""
import concurrent.futures as cf, html, json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (compatible; worklore-research/0.1; +https://worklore.dev)"
TAGS = ["webdev", "programming", "career", "ai", "javascript", "python", "devops", "beginners", "react", "opensource"]
NOT_PERSONAL = ("github.com", "gitlab.com", "linkedin.com", "twitter.com", "x.com", "dev.to", "medium.com",
                "hashnode", "youtube.com", "instagram.com", "facebook.com", "linktr.ee", "bento.me",
                "substack.com", "t.me", "discord", "notion.site", "about.me", "polywork", "behance", "dribbble",
                "stackoverflow.com", "npmjs.com", "kaggle.com", "huggingface.co", "bsky.app", "threads.net")

def get(url, timeout=20, limit=1_500_000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.geturl(), r.read(limit).decode("utf-8", "replace")

def api(path):
    for i in range(4):
        try:
            return json.loads(get("https://dev.to/api/" + path, timeout=60, limit=200_000_000)[1])
        except Exception:
            time.sleep(2 + 3 * i)
    return None

def personal(url, user):
    if not url:
        return False
    host = urllib.parse.urlparse(url if "://" in url else "https://" + url).netloc.lower()
    if not host or any(h in host for h in NOT_PERSONAL):
        return False
    # org sites: a heuristic — keep hosts that look like a person's (name/username in host, or
    # common personal patterns); everything else is judged after fetching (see classify: 'org_like')
    return True

def candidates(n):
    seen, out = set(), []
    for page in range(1, 6):
        for tag in TAGS:
            arts = api(f"articles?tag={tag}&per_page=100&page={page}&top=365") or []
            for a in arts:
                u = (a.get("user") or {}).get("username")
                if not u or u in seen or a.get("organization"):
                    continue
                seen.add(u)
                p = api(f"users/by_username?url={urllib.parse.quote(u)}")
                if not p or not personal(p.get("website_url"), u):
                    continue
                out.append(p)
                print(f"\r{len(out)} candidates ({len(seen)} authors seen)", end="", file=sys.stderr)
                if len(out) >= n:
                    return out
            time.sleep(0.5)
    return out

KEYS = {
    "repos/projects": r"github\.com/[\w.-]+/[\w.-]+|\bprojects?\b|\bportfolio\b|\bopen[- ]source\b",
    "articles/blog": r"\bblog\b|\barticles?\b|\bposts?\b|\bwriting\b|\bnewsletter\b",
    "talks/videos": r"\btalks?\b|\bspeaking\b|\bpodcast\b|\bvideos?\b|youtube\.com",
    "resume/cv": r"\bresume\b|\brésumé\b|\bcv\b|curriculum",
    "uses/now/til": r"/uses\b|/now\b|\btil\b|today i learned",
    "products/apps": r"\bapp store\b|play\.google|\bmy (product|app|saas)\b|\bproducts?\b",
    "services/hire": r"\bhire me\b|\bwork with me\b|\bservices\b|\bconsult(ing|ant)\b|\bfreelanc",
    "case studies": r"case stud(y|ies)",
}
WORK = {
    "open_to_work": r"open to (work|new opportunit|opportunit)|available for (hire|work|new)|looking for (a )?(new )?(job|role|position|opportunit)|seeking (a )?(new )?(role|position|opportunit)",
    "freelance": r"\bfreelanc|\bindependent (developer|consultant)|\bavailable for (contract|projects)",
    "employed": r"\b(currently|now) (at|working at|working for|@)|\b(senior|staff|lead|principal)?\s*(software |frontend |backend |full[- ]?stack )?(engineer|developer) (at|@)\s+[A-Z]",
    "founder": r"\b(founder|co-?founder|building)\b",
    "student": r"\bstudent\b|\bbootcamp\b|\blearning to code\b",
}

def text_of(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    return html.unescape(re.sub(r"(?s)<[^>]+>", " ", h))

def classify(p):
    u, site = p["username"], p.get("website_url") or ""
    row = {"username": u, "devto": f"https://dev.to/{u}", "site": site, "github": p.get("github_username") or "",
           "joined": p.get("joined_at"), "bio": (p.get("summary") or "")[:200]}
    arts, page = 0, 1
    while page <= 10:
        a = api(f"articles?username={urllib.parse.quote(u)}&per_page=1000&page={page}") or []
        arts += len(a)
        if len(a) < 1000:
            break
        page += 1
    row["devto_articles"] = arts
    try:
        final, h = get(site if "://" in site else "https://" + site)
        row["site_ok"] = True
        row["site_final"] = final
    except Exception as e:
        row["site_ok"] = False
        row["site_error"] = type(e).__name__
        h = ""
    low = h.lower()
    t = text_of(h)
    row["shows"] = sorted(k for k, rx in KEYS.items() if re.search(rx, low, re.I))
    row["github_repo_links"] = len(set(re.findall(r"github\.com/[\w.-]+/[\w.-]+", low)))
    row["links_linkedin"] = "linkedin.com/in/" in low
    row["links_devto"] = "dev.to/" in low
    row["links_github_profile"] = bool(re.search(r"github\.com/[\w-]+/?[\"' ]", low))
    said = (row["bio"] + " " + t[:20000])
    row["work_signals"] = sorted(k for k, rx in WORK.items() if re.search(rx, said, re.I))
    title = re.search(r"(?is)<title[^>]*>(.*?)</title>", h)
    row["site_title"] = html.unescape(title.group(1)).strip()[:120] if title else ""
    return row

def main(n=100):
    cands = candidates(int(n * 1.3))  # extra, since some sites are down or turn out to be org sites
    print(file=sys.stderr)
    with cf.ThreadPoolExecutor(6) as ex:
        rows = list(ex.map(classify, cands))
    ok = [r for r in rows if r["site_ok"]][:n]
    json.dump(ok, open(os.path.join(HERE, "profiles.json"), "w"), indent=1, ensure_ascii=False)
    json.dump([r for r in rows if not r["site_ok"]], open(os.path.join(HERE, "unreachable.json"), "w"), indent=1)
    print(f"profiles with a reachable personal site: {len(ok)} (of {len(rows)} candidates)")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
