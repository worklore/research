import json, re, statistics, collections
rows = json.load(open("people.json"))
SELF = re.compile(r"\b(self[- ]?employed|freelanc\w*|independent|indie|solo|consultant|contractor|founder|co-?founder|ceo|cto|owner|maker|bootstrapp\w*|building @?\w+|my own)\b", re.I)
LOOK = re.compile(r"open to (work|opportunit|new)|looking for (a )?(new )?(job|role|work|opportunit)|seeking (a )?(new )?(role|job|opportunit)|available for hire|#opentowork|job ?hunting|unemployed", re.I)
STUD = re.compile(r"\b(student|undergrad|university|bootcamp|learning to code|aspiring)\b", re.I)
NOCO = re.compile(r"^(n/?a|none|-|freelance\w*|self[- ]?employed|independent|myself|me|home|unemployed|open to work|looking.*)$", re.I)
def status(r):
    txt = f"{r['bio']} {r['company']}"
    if LOOK.search(txt): return "looking"
    if STUD.search(txt) and not r["company"]: return "student"
    if SELF.search(txt): return "own work (founder / indie / freelance)"
    co = r["company"].strip()
    if co and not NOCO.match(co): return "employed"
    if re.search(r"\b(engineer|developer|dev|sre|architect)\s+(at|@)\s*\S", r["bio"], re.I): return "employed"
    return "not stated"
def links(r):
    s = set(p.lower() for p in r["socials"])
    urls = " ".join(r["social_urls"] + [r["blog"]]).lower()
    out = set()
    if r["blog"]: out.add("personal site / blog")
    if "linkedin" in s or "linkedin.com" in urls: out.add("LinkedIn")
    if r["twitter"] or "twitter" in s or "x.com/" in urls: out.add("X/Twitter")
    if "youtube" in s or "youtube.com" in urls: out.add("YouTube")
    if "bluesky" in s or "bsky" in urls: out.add("Bluesky")
    if "mastodon" in s: out.add("Mastodon")
    if "dev.to" in urls or "medium.com" in urls or "hashnode" in urls or "substack" in urls: out.add("blog platform (dev.to/Medium/Hashnode/Substack)")
    if "instagram" in s or "instagram.com" in urls: out.add("Instagram")
    return out
for r in rows:
    r["status"] = status(r); r["links"] = sorted(links(r))
def med(xs): return statistics.median(xs) if xs else 0
L = []
for g in ("writers", "builders"):
    G = [r for r in rows if r["group"] == g]; n = len(G)
    L.append(f"\n## {g} (n={n})")
    L.append(f"followers median {med([r['followers'] for r in G])} | mean {round(sum(r['followers'] for r in G)/n)} | stars median {med([r['stars'] for r in G])} | public repos median {med([r['public_repos'] for r in G])}")
    L.append(f"hireable (GitHub 'Available for hire'): {sum(r['hireable'] for r in G)} ({round(100*sum(r['hireable'] for r in G)/n)}%)")
    sc = collections.Counter(r["status"] for r in G)
    L.append("status: " + " · ".join(f"{k} {v} ({round(100*v/n)}%)" for k, v in sc.most_common()))
    lc = collections.Counter(l for r in G for l in r["links"])
    L.append("links: " + " · ".join(f"{k} {round(100*v/n)}%" for k, v in lc.most_common()))
    L.append(f"no links at all: {sum(1 for r in G if not r['links'])} ({round(100*sum(1 for r in G if not r['links'])/n)}%)")
    L.append("followers median by status: " + " · ".join(f"{k}: {med([r['followers'] for r in G if r['status']==k])} (n={v})" for k, v in sc.most_common()))
    L.append("hireable by status: " + " · ".join(f"{k}: {sum(r['hireable'] for r in G if r['status']==k)}/{v}" for k, v in sc.most_common()))
ALL = rows
w_site = [r["followers"] for r in ALL if "personal site / blog" in r["links"]]; wo = [r["followers"] for r in ALL if "personal site / blog" not in r["links"]]
L.append(f"\n## both groups: followers median with a personal site/blog {med(w_site)} (n={len(w_site)}) vs without {med(wo)} (n={len(wo)})")
k = collections.Counter(len(r["links"]) for r in ALL)
L.append("followers median by number of links: " + " · ".join(f"{i} links: {med([r['followers'] for r in ALL if len(r['links'])==i])} (n={k[i]})" for i in sorted(k)))
print("\n".join(L))
json.dump(rows, open("people.json", "w"), indent=1, ensure_ascii=False)
