"""Everything the pixel art needs to know, fetched live or faked for previews.

Live mode uses the GitHub GraphQL API (the Actions GITHUB_TOKEN is enough)
and Open-Meteo for the weather (free, no key). Offline mode returns a sample
profile so the art can be previewed without any network access.
"""

import datetime as dt
import json
import random
import urllib.request

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

# GitHub linguist colours for the usual suspects.
LANG_COLORS = {
    "PHP": "#4F5D95", "Java": "#b07219", "Python": "#3572A5", "Go": "#00ADD8",
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Kotlin": "#A97BFF", "Rust": "#dea584",
    "C": "#555555", "C++": "#f34b7d", "C#": "#178600", "Ruby": "#701516", "Swift": "#F05138",
    "Dart": "#00B4AB", "Shell": "#89e051", "HTML": "#e34c26", "CSS": "#663399", "Vue": "#41b883",
    "Blade": "#f7523f", "Scala": "#c22d40", "Elixir": "#6e4a7e", "Lua": "#000080",
    "Dockerfile": "#384d54", "Jupyter Notebook": "#DA5B0B",
}

# Short spine labels for the bookshelf (max 4 letters fit).
BOOK_LABELS = {
    "Python": "PY", "JavaScript": "JS", "TypeScript": "TS", "Kotlin": "KT", "Rust": "RS",
    "Ruby": "RB", "Swift": "SWFT", "Shell": "SH", "Scala": "SCLA", "Elixir": "EX",
    "Jupyter Notebook": "IPYN", "Dockerfile": "DOCK",
}


def book_label(lang):
    return BOOK_LABELS.get(lang, lang.upper()[:4])


# --- weather ------------------------------------------------------------------
def weather_kind(code):
    """Map a WMO weather code to one of the scenes the window can draw."""
    if code in (0, 1):
        return "clear"
    if code == 2:
        return "clouds"
    if code == 3:
        return "overcast"
    if code in (45, 48):
        return "fog"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "storm"
    if 51 <= code <= 67 or 80 <= code <= 82:
        return "rain"
    return "clouds"


def fetch_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,is_day&timezone=auto"
    )
    with urllib.request.urlopen(url, timeout=20) as r:
        cur = json.load(r)["current"]
    return {"kind": weather_kind(int(cur["weather_code"])), "day": bool(cur["is_day"]),
            "temp": cur.get("temperature_2m")}


def local_now(tz_name):
    try:
        return dt.datetime.now(ZoneInfo(tz_name))
    except Exception:
        return dt.datetime.now(dt.timezone(dt.timedelta(hours=1)))


# --- github -------------------------------------------------------------------
Q_PROFILE = """
query($login: String!) {
  user(login: $login) {
    name
    login
    createdAt
    avatarUrl(size: 240)
    followers { totalCount }
    pullRequests { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100,
                 orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      nodes {
        name description url stargazerCount isArchived pushedAt
        primaryLanguage { name color }
      }
    }
    recent: repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 6,
                         orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 10) {
                nodes { oid messageHeadline committedDate author { user { login } } }
              }
            }
          }
        }
      }
    }
  }
}
"""


def gql(query, variables, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "pixel-profile"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def fetch_github(login, token, now):
    user = gql(Q_PROFILE, {"login": login}, token)

    # one contributionsCollection per calendar year since the account was created
    start = int(user["createdAt"][:4])
    stamp = now.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    parts = []
    for y in range(start, now.year + 1):
        to = f"{y}-12-31T23:59:59Z" if y < now.year else stamp
        parts.append(
            f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{to}") '
            "{ totalCommitContributions contributionCalendar { weeks { contributionDays "
            "{ date contributionCount } } } }"
        )
    years = gql("query($login: String!) { user(login: $login) { " + " ".join(parts) + " } }",
                {"login": login}, token)

    days, commits_total = {}, 0
    for coll in years.values():
        commits_total += coll["totalCommitContributions"]
        for week in coll["contributionCalendar"]["weeks"]:
            for d in week["contributionDays"]:
                days[dt.date.fromisoformat(d["date"])] = d["contributionCount"]

    repos = [r for r in user["repositories"]["nodes"]]
    stars = sum(r["stargazerCount"] for r in repos)

    recent = []
    for repo in user["recent"]["nodes"]:
        target = (repo.get("defaultBranchRef") or {}).get("target") or {}
        for c in (target.get("history") or {}).get("nodes", []):
            author = ((c.get("author") or {}).get("user") or {}).get("login", "")
            recent.append((c["committedDate"], c["oid"], c["messageHeadline"], author.lower() == login.lower()))
    recent.sort(reverse=True)
    mine = [r for r in recent if r[3]] or recent
    commits = [(oid, msg) for _, oid, msg, _ in mine[:8]]

    return {
        "name": user["name"] or user["login"],
        "avatar_url": user["avatarUrl"],
        "followers": user["followers"]["totalCount"],
        "repo_count": user["repositories"]["totalCount"],
        "since": start,
        "stars": stars,
        "prs": user["pullRequests"]["totalCount"],
        "commits": commits_total,
        "days": days,
        "repos": repos,
        "recent_commits": commits,
    }


# --- derived numbers -------------------------------------------------------------
def streaks(days, today):
    if not days:
        return 0, 0
    if today not in days:
        today = max(d for d in days if d <= today) if any(d <= today for d in days) else max(days)
    cur, d = 0, today
    if days.get(d, 0) == 0:  # today isn't over yet; yesterday keeps the streak alive
        d -= dt.timedelta(days=1)
    while days.get(d, 0) > 0:
        cur += 1
        d -= dt.timedelta(days=1)
    best = run = 0
    prev = None
    for d in sorted(days):
        if days[d] > 0:
            run = run + 1 if prev is not None and (d - prev).days == 1 else 1
            prev = d
            best = max(best, run)
        else:
            prev = None
            run = 0
    return cur, max(best, cur)


def pick_projects(repos, login, pinned, count):
    by_name = {r["name"].lower(): r for r in repos}
    if pinned:
        chosen = [by_name[p.lower()] for p in pinned if p.lower() in by_name]
    else:
        pool = [r for r in repos if not r.get("isArchived") and r["name"].lower() != login.lower()]
        pool.sort(key=lambda r: (r["stargazerCount"], r.get("pushedAt") or ""), reverse=True)
        chosen = pool
    return chosen[:count]


# --- offline sample ------------------------------------------------------------------
def sample(login, today):
    rng = random.Random(42)
    days = {}
    for i in range(400):
        d = today - dt.timedelta(days=i)
        busy = 0.72 if d.weekday() < 5 else 0.35
        days[d] = rng.choice((1, 2, 3, 4, 6, 9, 12)) if rng.random() < busy else 0
    for i in range(5):
        days[today - dt.timedelta(days=i)] = max(1, days[today - dt.timedelta(days=i)])
    return {
        "name": login,
        "avatar_url": f"https://github.com/{login}.png?size=240",
        "followers": 42,
        "repo_count": 18,
        "since": 2019,
        "stars": 156,
        "prs": 87,
        "commits": 1240,
        "days": days,
        "repos": [
            {"name": "laravel-api-kit", "description": "Opinionated Laravel starter for clean, versioned REST APIs with auth, rate limiting and docs.",
             "url": "https://github.com", "stargazerCount": 64, "primaryLanguage": {"name": "PHP", "color": "#4F5D95"}},
            {"name": "spring-orders", "description": "Order management microservice built with Spring Boot, Kafka and PostgreSQL.",
             "url": "https://github.com", "stargazerCount": 41, "primaryLanguage": {"name": "Java", "color": "#b07219"}},
            {"name": "go-ratelimit", "description": "Tiny token-bucket rate limiter middleware for net/http.",
             "url": "https://github.com", "stargazerCount": 29, "primaryLanguage": {"name": "Go", "color": "#00ADD8"}},
            {"name": "souk-scraper", "description": "Python scraper that tracks prices across Moroccan marketplaces.",
             "url": "https://github.com", "stargazerCount": 22, "primaryLanguage": {"name": "Python", "color": "#3572A5"}},
        ],
        "recent_commits": [
            ("a1b2c3d", "feat: add jwt auth middleware"), ("9f8e7d6", "fix(api): handle null cursor"),
            ("1234abc", "refactor: extract order service"), ("c0ffee1", "test: cover payment webhooks"),
            ("7a7a7a7", "chore: bump spring boot to 3.5"), ("5b5b5b5", "perf: cache user lookups"),
            ("e1e1e1e", "feat(go): token bucket limiter"), ("deadbee", "docs: update readme"),
        ],
    }
