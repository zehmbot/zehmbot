"""Render every pixel-art GIF for the profile README into dist/.

  python pixel/generate.py                    offline preview with sample data
  python pixel/generate.py --weather rain     force a weather scene (clear, clouds,
                           --night            overcast, rain, storm, fog, snow)
  python pixel/generate.py --live --readme    what the workflow runs: real GitHub
                                              stats, live weather, README refresh

Open dist/preview.html to see the result laid out like the README.
"""

import argparse
import html
import os
import pathlib
import re
import sys
import time
import tomllib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import avatar  # noqa: E402
import cards  # noqa: E402
import scene  # noqa: E402
from canvas import hex_rgb, rounded_mask, save_gif  # noqa: E402
from data import (LANG_COLORS, book_label, fetch_github, fetch_org, fetch_weather,  # noqa: E402
                  local_now, pick_projects, sample, sample_org, streaks)

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
START, END = "<!-- pixel:projects:start -->", "<!-- pixel:projects:end -->"
KINDS = ("clear", "clouds", "overcast", "rain", "storm", "fog", "snow")


def load_frames(path):
    from PIL import Image, ImageSequence
    return [f.convert("RGB") for f in ImageSequence.Iterator(Image.open(path))]


def projects_block(projects, base):
    if not projects:
        return f"{START}\n{END}"
    lines = [START, f'<img src="{base}/projects.gif" width="100%" alt="Projects" />', "", "<p>"]
    for i, repo in enumerate(projects, 1):
        name = html.escape(repo["name"])
        desc = html.escape(repo.get("description") or repo["name"], quote=True)
        lines.append(f'  <a href="{repo["url"]}"><img src="{base}/project-{i}.gif" width="49%" '
                     f'alt="{name}: {desc}" /></a>')
    lines += ["</p>", END]
    return "\n".join(lines)


def preview_html(cfg, projects):
    cards_html = "".join(f'<a href="{html.escape(r["url"])}"><img src="project-{i}.gif"></a>'
                         for i, r in enumerate(projects, 1))
    return f"""<!doctype html>
<meta charset="utf-8"><title>Pixel profile preview</title>
<style>
  body {{ margin: 0; background: #0d1117; color: #c9d1d9; font: 14px/1.5 -apple-system, Segoe UI, sans-serif; }}
  body.light {{ background: #fff; color: #1f2328; }}
  main {{ max-width: 830px; margin: 24px auto; padding: 0 16px; }}
  img {{ width: 100%; display: block; margin: 8px 0; }}
  .grid {{ display: flex; gap: 2%; flex-wrap: wrap; }} .grid a {{ width: 49%; }}
  p {{ text-align: center; font-size: 12px; }} button {{ float: right; }}
</style>
<main>
  <button onclick="document.body.classList.toggle('light')">toggle light / dark</button>
  <img src="hero.gif">
  <img src="about.gif"><img src="studio.gif"><img src="stats.gif">
  <img src="projects.gif"><div class="grid">{cards_html}</div>
  <img src="activity.gif"><img src="footer.gif">
</main>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true", help="fetch real data (needs GITHUB_TOKEN)")
    ap.add_argument("--readme", action="store_true", help="rewrite the projects block in README.md")
    ap.add_argument("--weather", choices=KINDS)
    ap.add_argument("--night", action="store_true")
    ap.add_argument("--day", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "dist"))
    args = ap.parse_args()

    cfg = tomllib.loads((HERE / "profile.toml").read_text(encoding="utf-8"))
    login = os.environ.get("PROFILE_LOGIN") or cfg["login"]
    now = local_now(cfg["weather"]["timezone"])
    today = now.date()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.live:
        token = os.environ.get("GH_API_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("--live needs GITHUB_TOKEN (or GH_API_TOKEN) in the environment")
        gh = fetch_github(login, token, now)
        try:
            weather = fetch_weather(cfg["weather"]["latitude"], cfg["weather"]["longitude"])
        except Exception as e:  # weather is decoration; never fail the run over it
            print(f"weather unavailable ({e}); drawing a clear sky", file=sys.stderr)
            weather = {"kind": "clear", "day": 7 <= now.hour < 19, "temp": None}
    else:
        gh = sample(login, today)
        weather = {"kind": "clouds", "day": 7 <= now.hour < 19, "temp": 21}
    if args.weather:
        weather["kind"] = args.weather
    if args.night or args.day:
        weather["day"] = args.day

    gh["current_streak"], gh["best_streak"] = streaks(gh["days"], today)
    colors = {**LANG_COLORS, **cfg.get("colors", {})}
    profile = {**cfg, "colors": colors, "name": cfg.get("name") or gh["name"]}
    projects = pick_projects(gh["repos"], login, cfg["projects"].get("pinned"), cfg["projects"].get("count", 4))

    studio_cfg = cfg.get("studio")
    studio_info, logo = None, None
    if studio_cfg:
        org = studio_cfg["org"]
        try:
            fetched = fetch_org(org, token) if args.live else sample_org(org, today)
        except Exception as e:  # org stats are a bonus; the card still renders without them
            print(f"organization info unavailable ({e})", file=sys.stderr)
            fetched = sample_org(org, today) | {"founded": None}
        studio_info = {**fetched, **{k: v for k, v in studio_cfg.items() if v}}
        studio_info.setdefault("tagline", fetched["description"])
        logo = load_frames(HERE / studio_cfg["logo"])

    portrait = None
    try:
        picture = avatar.load(cfg.get("avatar", "github"), HERE, gh.get("avatar_url"))
        if picture is not None:
            portrait = avatar.pixelate(picture, cfg.get("avatar_style", "ink"))
    except Exception as e:  # a missing picture should never break the render
        print(f"profile picture unavailable ({e}); using the robot", file=sys.stderr)

    ctx = {
        "neon": cfg.get("neon", login).upper(),
        "books": [(book_label(l), hex_rgb(colors.get(l, "#8b949e"))) for l in cfg["languages"]],
        "extra_books": [hex_rgb(colors.get(f, "#8b949e")) for f in cfg.get("frameworks", [])],
        "commits": gh["recent_commits"],
        "weather": weather,
        "city": cfg["weather"]["city"],
        "clock": (now.hour, now.minute),
        "repo_title": f"~/{login}",
    }

    jobs = [
        ("hero.gif", lambda: scene.render(ctx) + (rounded_mask(scene.W, scene.H, (2, 1)),), 3),
        ("about.gif", lambda: cards.about(profile, gh, portrait), 2),
        ("stats.gif", lambda: cards.stats(gh), 2),
        *([("studio.gif", lambda: cards.studio(studio_info, logo), 2)] if studio_info else []),
        ("projects.gif", lambda: cards.header("PROJECTS"), 2),
        ("activity.gif", lambda: cards.activity(gh, today), 2),
        ("footer.gif", lambda: cards.footer(profile), 2),
    ]
    for i, repo in enumerate(projects, 1):
        jobs.append((f"project-{i}.gif", lambda r=repo, i=i: cards.project(r, slot=i - 1), 2))

    for name, build, k in jobs:
        t0 = time.time()
        frames, durations, mask = build()
        save_gif(out / name, frames, durations, k=k, mask=mask, loop=name != "stats.gif")
        kb = (out / name).stat().st_size / 1024
        print(f"{name:<14} {len(frames):>3} frames  {kb:7.0f} KB  {time.time() - t0:4.1f}s")

    (out / "preview.html").write_text(preview_html(cfg, projects), encoding="utf-8")
    (out / "README.md").write_text("Rendered by the pixel-profile workflow. Do not edit.\n", encoding="utf-8")
    print(f"weather: {weather['kind']} ({'day' if weather['day'] else 'night'}) · streak {gh['current_streak']}"
          f" / best {gh['best_streak']} · projects: {', '.join(r['name'] for r in projects) or 'none'}")

    if args.readme:
        readme = ROOT / "README.md"
        text = readme.read_text(encoding="utf-8")
        block = projects_block(projects, cfg["assets"].rstrip("/"))
        new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
        if new != text:
            readme.write_text(new, encoding="utf-8")
            print("README projects block updated")


if __name__ == "__main__":
    main()
