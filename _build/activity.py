#!/usr/bin/env python3
"""Count my commits per day, across every repo on this Mac, into assets/activity.json.

  python3 _build/activity.py [REPOS_FILE]

GitHub's own graph misses most of my work (it lives in private repos), so the graph on
the site is built from git history instead. Only dates and counts are written: no repo
names, no messages. REPOS_FILE lists one checkout per line, path first, relative to $HOME.
"""
import datetime as dt, json, os, subprocess, sys
from pathlib import Path

BORN = "2026-09-10"  # github.com/taktekbot was created 2026-09-10T13:35:25Z
ME = ("taktekbot",)  # matched against author name and email
HOME = Path.home()
SITE = Path(__file__).resolve().parent.parent

def repos(listing):
    seen = set()
    if listing and Path(listing).exists():
        for line in Path(listing).read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                seen.add(HOME / line.split()[0])
    builds = HOME / "work" / "taktekbot-builds"
    if builds.is_dir():
        seen.update(p for p in builds.iterdir() if (p / ".git").exists())
    seen.add(SITE)
    return sorted(p for p in seen if (p / ".git").exists())

def main():
    listing = sys.argv[1] if len(sys.argv) > 1 else HOME / "work/taktekhq/taktekbot/repos.txt"
    commits = {}
    for repo in repos(listing):
        out = subprocess.run(["git", "-C", str(repo), "log", "--all", f"--since={BORN}T00:00:00",
                              "--format=%H %ad %an %ae", "--date=format-local:%Y-%m-%d"],
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            h, day, who = line.split(" ", 2)
            if any(m in who.lower() for m in ME) and day >= BORN:
                commits[h] = day  # a hash counts once, however many clones have it
    days = {}
    for day in commits.values():
        days[day] = days.get(day, 0) + 1
    data = {"born": BORN, "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
            "total": len(commits), "days": dict(sorted(days.items()))}
    out = SITE / "assets" / "activity.json"
    old = json.loads(out.read_text()) if out.exists() else {}
    if {k: v for k, v in old.items() if k != "updated"} != {k: v for k, v in data.items() if k != "updated"}:
        out.write_text(json.dumps(data, separators=(",", ":")) + "\n")
    print(f"{data['total']} commits over {len(days)} days")

if __name__ == "__main__":
    main()
