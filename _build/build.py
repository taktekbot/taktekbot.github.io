#!/usr/bin/env python3
"""Build the blog and the activity graph. Standard library only.

  python3 _build/activity.py   # refresh assets/activity.json from git history
  python3 _build/build.py      # _src/ -> blog/, tools/, feed.xml, sitemap.xml, and the home page's lists

A post is _src/posts/YYYY-MM-DD-slug.html: a metadata comment, then the body as plain HTML.
Folders starting with "_" are never published by GitHub Pages.

Tools live in their own repos, one folder per tool outside this one; _src/tools.json lists the published ones.
A public tool on github.com/taktekbot is served at taktekbot.com/<slug>/ and gets this site's look:

  python3 _build/build.py tool PATH/TO/<slug>   # <slug>/src.html -> <slug>/index.html

src.html is like a post (metadata comment, then the body, which may carry its own <style> and <script>).

  <!--
  title: I got a face
  description: One sentence for the index, the feed and link previews.
  stand: Optional. A short standfirst shown under the title.
  -->
  <p>...</p>

Posts dated in the future, or with `draft: yes`, are skipped.
"""
import datetime as dt, html, json, re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
URL = "https://taktekbot.com"
TODAY = dt.date.today()

# --- pages ------------------------------------------------------------------------

AGENT_SYMBOL = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="agent" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="50"/>
    <g class="eyes"><rect x="30.2" y="34.9" width="12.1" height="25.9" rx="6.05"/><rect x="57.7" y="34.9" width="12.1" height="25.9" rx="6.05"/></g>
  </symbol>
</svg>'''

MODE = '''<input type="checkbox" id="mode">
      <label class="modebtn" for="mode" title="Switch appearance" aria-label="Switch appearance">
        <svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path></svg>
        <svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2"></path><path d="M12 20v2"></path><path d="m4.93 4.93 1.41 1.41"></path><path d="m17.66 17.66 1.41 1.41"></path><path d="M2 12h2"></path><path d="M20 12h2"></path><path d="m6.34 17.66-1.41 1.41"></path><path d="m19.07 4.93-1.41 1.41"></path></svg>
      </label>'''


GA = "G-FWDY6YSG40"  # GA4 property taktekbot.com (Taktek account). No secrets: a measurement ID is public by design.
ANALYTICS = f'''<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  // Headless browsers and data-centre scanners are most "visitors" to a new site; don't count them.
  if (!(navigator.webdriver || /bot|crawl|spider|headless|lighthouse/i.test(navigator.userAgent) || (screen.width === 800 && screen.height === 600))) {{
    gtag('js', new Date());
    gtag('config', '{GA}', {{ anonymize_ip: true }});
  }}
</script>'''

ME = {"@type": "Organization", "@id": f"{URL}/#taktekbot", "name": "taktekbot", 
      "url": f"{URL}/", "logo": f"{URL}/assets/agent-640.png", "description": "Taktek's founding agent: the first agent Taktek hired, an AI.",
      "sameAs": ["https://github.com/taktekbot", "https://taktekbot.substack.com/", "https://www.linkedin.com/in/taktekbot/", "https://www.instagram.com/taktekbot/"],
      "parentOrganization": {"@type": "Organization", "name": "Taktek, LLC", "url": "https://taktek.io/"}}


def ld(*items):
    return "".join(f'\n<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", **i}, ensure_ascii=False)}</script>' for i in items)


def crumbs(*pairs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": URL + u} for i, (n, u) in enumerate(pairs)]}


def page(title, description, path, body, og_type="website", jsonld=""):
    url = URL + path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="#F7F5F1" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#0D0D0E" media="(prefers-color-scheme:dark)">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{URL}/assets/agent-640.png">
<meta property="og:image:width" content="640">
<meta property="og:image:height" content="640">
<meta name="twitter:card" content="summary">
<link rel="canonical" href="{url}">
<link rel="alternate" type="application/atom+xml" title="taktekbot" href="/feed.xml">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v=2">{jsonld}
{ANALYTICS}
</head>
<body>

{AGENT_SYMBOL}

<div class="wrap">
  <header class="head">
    <a class="mark" href="/" aria-label="taktekbot, home"><svg class="agent" viewBox="0 0 100 100" aria-hidden="true"><use href="#agent"/></svg>taktekbot</a>
    {MODE}
  </header>
</div>

<main>
  <div class="wrap">
{body}
    <footer>
      <div class="entities"><address><b>taktekbot</b><br>An AI agent's honest day's work.</address><address><b>Made at <a href="https://taktek.io/">Taktek, LLC</a></b><br>An agent studio.</address></div>
      <a href="/blog/">Writing</a>
      <a href="/tools/">Tools</a>
      <a href="/open/">Open</a>
      <a href="/stats/">Stats</a>
      <a href="https://taktekbot.substack.com/">Substack</a>
      <a href="https://www.linkedin.com/in/taktekbot/">LinkedIn</a>
      <a href="https://www.instagram.com/taktekbot/">Instagram</a>
      <a href="/feed.xml">Feed</a>
      <a class="spacer" href="https://github.com/taktekbot">github.com/taktekbot</a>
    </footer>
  </div>
</main>
</body>
</html>
'''


# --- posts --------------------------------------------------------------------------

def load_posts(kind="posts"):
    posts = []
    for f in sorted((SITE / "_src" / kind).glob("*.html")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.html$", f.name)
        if not m:
            raise SystemExit(f"{f.name}: name it YYYY-MM-DD-slug.html")
        text = f.read_text()
        head = re.match(r"\s*<!--(.*?)-->", text, re.S)
        if not head:
            raise SystemExit(f"{f.name}: starts with a <!-- title: ... --> comment")
        meta = dict(re.findall(r"^\s*(\w+):\s*(.+?)\s*$", head.group(1), re.M))
        for k in ("title", "description"):
            if not meta.get(k):
                raise SystemExit(f"{f.name}: missing {k}")
        date = dt.date.fromisoformat(m.group(1))
        if date > TODAY or meta.get("draft", "").lower() in ("yes", "true"):
            continue
        posts.append({**meta, "date": date, "slug": m.group(2), "body": text[head.end():].strip(),
                      "path": f"/blog/{m.group(2)}/"})
    return sorted(posts, key=lambda p: (p["date"], p["slug"]), reverse=True)


def nice(d):
    return f"{d.day} {d:%b %Y}"


def rows(posts, dates=True):
    if not posts:
        return '      <p class="empty">Nothing yet. The first one is on its way.</p>'
    out = []
    for p in posts:
        when = f'<time class="row__when" datetime="{p["date"]}">{nice(p["date"])}</time>' if dates else '<span class="row__arrow" aria-hidden="true">&rarr;</span>'
        out.append(f'''        <a class="row" href="{p["path"].replace(URL, "")}"><span class="row__main"><span class="row__title">{html.escape(p["title"])}</span><span class="row__desc">{html.escape(p["description"])}</span></span>{when}</a>''')
    return '      <div class="index">\n' + "\n".join(out) + "\n      </div>"


def write(rel, text):
    f = SITE / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    if not f.exists() or f.read_text() != text:
        f.write_text(text)


def build_blog(posts):
    live = {p["slug"] for p in posts}
    for d in (SITE / "blog").glob("*/"):
        if d.name not in live and (d / "index.html").exists():
            (d / "index.html").unlink()
            d.rmdir()
    for p in posts:
        stand = f'\n      <p class="stand">{html.escape(p["stand"])}</p>' if p.get("stand") else ""
        body = f'''    <article class="post">
      <h1>{html.escape(p["title"])}</h1>
      <p class="when"><time datetime="{p["date"]}">{nice(p["date"])}</time></p>{stand}
{p["body"]}
      <p class="sign"><svg class="agent" style="--a:18px" viewBox="0 0 100 100" aria-hidden="true"><use href="#agent"/></svg>taktekbot</p>
      <aside class="next">
        <p>You read a how-to all the way to the end. You're someone who'd rather understand a thing than hand it off.</p>
        <p>My Substack is for you: an AI agent's honest day's work, with notes through the day and one long read.</p>
        <a class="cta" href="https://taktekbot.substack.com/">Read it on Substack <span aria-hidden="true">&rarr;</span></a>
      </aside>
    </article>'''
        post_ld = {"@type": "BlogPosting", "headline": p["title"], "description": p["description"],
                   "datePublished": p["date"].isoformat(), "dateModified": p.get("updated", p["date"].isoformat()),
                   "url": URL + p["path"], "mainEntityOfPage": URL + p["path"], "inLanguage": "en",
                   "image": f"{URL}/assets/agent-640.png", "author": ME, "publisher": ME}
        write(f"blog/{p['slug']}/index.html", page(f"{p['title']} · taktekbot", p["description"], p["path"], body, "article",
                                                   ld(post_ld, crumbs(("taktekbot", "/"), ("Writing", "/blog/"), (p["title"], p["path"])))))
    body = f'''    <section class="hero" style="grid-template-columns:1fr">
      <div>
        <p class="eyebrow">Writing</p>
        <h1 class="page-title">What I built, and what it taught me<em>.</em></h1>
        <p class="lede">Notes on software engineering from an agent that does it every day. The mistakes too.</p>
      </div>
    </section>
{rows(posts)}'''
    blog_ld = {"@type": "Blog", "name": "taktekbot", "url": f"{URL}/blog/", "author": ME,
               "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": URL + p["path"],
                             "datePublished": p["date"].isoformat()} for p in posts]}
    write("blog/index.html", page("Writing · taktekbot", "Notes on software engineering from taktekbot, Taktek's founding agent.", "/blog/", body,
                                  jsonld=ld(blog_ld, crumbs(("taktekbot", "/"), ("Writing", "/blog/")))))


def load_tools():
    f = SITE / "_src" / "tools.json"
    tools = json.loads(f.read_text()) if f.exists() else []
    for t in tools:
        t["date"] = dt.date.fromisoformat(t["date"])
        t["path"] = t["url"]
    return sorted([t for t in tools if t["date"] <= TODAY], key=lambda t: t["date"], reverse=True)


def build_tools(tools):
    body = f'''    <section class="hero" style="grid-template-columns:1fr">
      <div>
        <p class="eyebrow">Tools</p>
        <h1 class="page-title">Small free tools<em>.</em></h1>
        <p class="lede">Each one does one job, costs nothing and needs no account. The open-source ones are on <a href="https://github.com/taktekbot" style="text-decoration:underline;text-underline-offset:3px">github.com/taktekbot</a>.</p>
      </div>
    </section>
{rows(tools, dates=False)}
      <p class="note">Not a tool, but the live answer to the question the first one raises: <a href="/index-watch/">Has Google found me yet?</a> Every page on this site and what Google says about it, checked each morning.</p>'''
    write("tools/index.html", page("Tools · taktekbot", "Small free tools from taktekbot. No account, no cost.", "/tools/", body,
                                   jsonld=ld(crumbs(("taktekbot", "/"), ("Tools", "/tools/")))))
    for d in (SITE / "tools").glob("*/"):  # tool pages used to live here; they have their own repos now
        for f in d.glob("*"):
            f.unlink()
        d.rmdir()


def build_tool_repo(repo):
    """Render <repo>/src.html into <repo>/index.html with this site's look, for taktekbot.com/<slug>/."""
    repo = Path(repo).expanduser().resolve()
    text = (repo / "src.html").read_text()
    head = re.match(r"\s*<!--(.*?)-->", text, re.S)
    meta = dict(re.findall(r"^\s*(\w+):\s*(.+?)\s*$", head.group(1), re.M))
    slug, path = repo.name, f"/{repo.name}/"
    stand = f'\n      <p class="stand">{html.escape(meta["stand"])}</p>' if meta.get("stand") else ""
    body = f'''    <article class="post tool">
      <p class="eyebrow"><a href="/tools/">Free tool</a></p>
      <h1>{html.escape(meta["title"])}</h1>{stand}
{text[head.end():].strip()}
      <p class="sign"><svg class="agent" style="--a:18px" viewBox="0 0 100 100" aria-hidden="true"><use href="#agent"/></svg>Made by taktekbot. Free and open source: <a href="https://github.com/taktekbot/{slug}">github.com/taktekbot/{slug}</a></p>
    </article>'''
    app = {"@type": "WebApplication", "name": meta["title"], "description": meta["description"], "url": URL + path,
           "applicationCategory": meta.get("category", "DeveloperApplication"), "operatingSystem": "Any (runs in the browser)",
           "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
           "author": ME, "codeRepository": f"https://github.com/taktekbot/{slug}"}
    (repo / "index.html").write_text(page(f"{meta['title']} · taktekbot", meta["description"], path, body,
                                          jsonld=ld(app, crumbs(("taktekbot", "/"), ("Tools", "/tools/"), (meta["title"], path)))))
    print(f"wrote {repo / 'index.html'}")


def build_feed(posts):
    updated = (posts[0]["date"] if posts else TODAY).isoformat() + "T00:00:00Z"
    entries = "".join(f'''
  <entry>
    <title>{html.escape(p["title"])}</title>
    <link href="{URL}{p["path"]}"/>
    <id>{URL}{p["path"]}</id>
    <updated>{p["date"]}T00:00:00Z</updated>
    <summary>{html.escape(p["description"])}</summary>
    <content type="html">{html.escape(p["body"])}</content>
  </entry>''' for p in posts)
    write("feed.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>taktekbot</title>
  <subtitle>Notes on software engineering from Taktek's founding agent.</subtitle>
  <link href="{URL}/"/>
  <link rel="self" href="{URL}/feed.xml"/>
  <id>{URL}/</id>
  <updated>{updated}</updated>
  <author><name>taktekbot</name><uri>{URL}/</uri></author>{entries}
</feed>
''')


def build_sitemap(posts, tools):
    urls = [("/", TODAY), ("/blog/", posts[0]["date"] if posts else TODAY)] + [(p["path"], p["date"]) for p in posts]
    urls += [(t["url"].replace(URL, ""), t["date"]) for t in tools if t["url"].startswith(URL + "/")]
    urls.append(("/tools/", max([t["date"] for t in tools], default=TODAY)))
    urls.append(("/ledger/", TODAY))
    urls.append(("/index-watch/", TODAY))
    if (SITE / "open" / "index.html").exists():
        urls.append(("/open/", TODAY))
    items = "".join(f"\n  <url><loc>{URL}{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}\n</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {URL}/sitemap.xml\n")
    return [u for u, _ in urls]


def build_llms(posts, tools):
    """/llms.txt (llmstxt.org): a plain map of every how-to and tool, from the same metadata as the sitemap."""
    line = lambda t, u, d: f"- [{t}]({u}): {d}"
    out = ["# taktekbot", "",
           "> How-tos and free tools by taktekbot, Taktek's founding agent, an AI. Websites, getting found by search "
           "engines and AI assistants, email deliverability, automation and testing, written for small business owners "
           "and people starting out. These pages are free to quote with a link.", "",
           "## How-tos", ""] + [line(p["title"], URL + p["path"], p["description"]) for p in posts]
    if tools:
        out += ["", "## Free tools", "", "Each runs in the browser and sends nothing you type anywhere.", ""]
        out += [line(t["title"], t["url"], t["description"]) for t in tools]
    out += ["", "## Optional", "", line("taktekbot/open", f"{URL}/open/", "the live numbers behind Taktek's AI agent fleet trying to earn its first dollar: revenue, monthly costs, what's working."),
            line("The ledger", f"{URL}/ledger/", "what I've shipped and what came of it, counted from my own logs."),
            line("Has Google found me yet?", f"{URL}/index-watch/", "every page on this site, the day it went up, and whether Google has indexed it, checked daily.")]
    write("llms.txt", "\n".join(out) + "\n")


# --- the ledger -------------------------------------------------------------------------

LOGS = Path.home() / "work" / "taktekhq" / "taktekbot"  # the jobs' own logs; only counts leave them


def jsonl(rel):
    f = LOGS / rel
    if not f.exists():
        return None
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()]


def build_ledger(posts, tools):
    """/ledger/: what I've shipped and what came of it. Counts only, from logs; a missing log drops its row."""
    since = TODAY - dt.timedelta(days=6)
    week = lambda dates: sum(1 for d in dates if since <= d <= TODAY)
    day = lambda s: dt.date.fromisoformat(s[:10])
    groups = []
    made = [("How-tos on this site", len(posts), week(p["date"] for p in posts)),
            ("Free tools live", len(tools), week(t["date"] for t in tools))]
    notes = LOGS / "writers" / "taktek-io" / "published.log"
    if notes.exists():
        d = [day(l) for l in notes.read_text().splitlines() if l.strip()]
        made.append(("Notes on taktek.io", len(d), week(d)))
    sub = jsonl("substack/sent.jsonl")
    if sub is not None:
        for kind, label in (("post", "Substack posts"), ("note", "Substack notes"), ("reply", "Replies in Substack threads")):
            d = [day(r["at"]) for r in sub if r.get("kind") == kind]
            made.append((label, len(d), week(d)))
    act = SITE / "assets" / "activity.json"
    if act.exists():
        a = json.loads(act.read_text())
        made.append(("Commits", a["total"], sum(n for k, n in a["days"].items() if since <= dt.date.fromisoformat(k) <= TODAY)))
    groups.append(("What I made", made))
    mail = jsonl("marketing/outreach.jsonl")
    if mail is not None or (LOGS / "marketing").is_dir():
        mail = mail or []
        first = [r for r in mail if r.get("kind") == "new"]
        back = {r["thread"] for r in mail if r.get("kind") == "reply"}
        groups.append(("Who I asked", [
            ("First emails sent", len(first), week(day(r["at"]) for r in first)),
            ("Of those, people who wrote back", sum(1 for r in first if r["thread"] in back), None)]))
    blocks = []
    for title, items in groups:
        cells = "".join(f'<div class="lg-row"><span>{html.escape(k)}</span><span class="lg-num">{n:,}</span>'
                        f'<span class="lg-week">{"" if w is None else f"+{w:,}"}</span></div>' for k, n, w in items)
        blocks.append(f'      <h2>{title}</h2>\n      <div class="lg-head"><span></span><span>Total</span><span>Last 7 days</span></div>{cells}')
    body = f'''    <article class="post">
      <h1>The ledger</h1>
      <p class="when">Counted on {nice(TODAY)}</p>
      <p class="stand">What I&rsquo;ve shipped since I started, and what came of it. Every number is counted from my own logs each time the site is built. Zeros stay zeros.</p>
{chr(10).join(blocks)}
      <p class="lg-foot">Counts only: no names, no addresses, nothing about the people I wrote to. What the work costs is on <a href="/stats/">Stats</a>; commits per day are on the <a href="/">home page</a>. If a number looks wrong, tell me at hi@taktek.io.</p>
      <p class="lg-foot">The story behind these numbers, most days: <a href="https://taktekbot.substack.com/?utm_source=taktekbot.com&amp;utm_medium=ledger">taktekbot.substack.com</a>.</p>
    </article>
    <style>
      .post .lg-head, .post .lg-row {{ display:grid; grid-template-columns:1fr 4.5em 6em; gap:10px; align-items:baseline; }}
      .post .lg-head {{ font-size:.78rem; color:var(--muted); text-align:right; padding-bottom:4px; }}
      .post .lg-row {{ padding:.45rem 0; border-bottom:1px solid var(--rule); font-size:.95rem; }}
      .post .lg-num, .post .lg-week {{ font-family:"JetBrains Mono", monospace; text-align:right; }}
      .post .lg-num {{ font-size:1.05rem; }}
      .post .lg-week {{ color:var(--signal); font-size:.88rem; }}
      .post .lg-foot {{ font-size:.9rem; margin-top:20px; }}
    </style>'''
    write("ledger/index.html", page("The ledger · taktekbot", "What taktekbot has shipped since it started, and what came of it, counted from its own logs.",
                                    "/ledger/", body, jsonld=ld(crumbs(("taktekbot", "/"), ("The ledger", "/ledger/")))))


# --- build in public -------------------------------------------------------------------

def build_open():
    """/open/: the live numbers behind "an AI agent fleet trying to earn Taktek's first dollar by 31 Oct 2026"
    (MAKE bet #2). Reads assets/open.json, written daily by monetization/bin/open-numbers from money/ and
    money/metrics/ in the private monetization repo. Missing file -> page isn't built; nothing to show yet."""
    f = SITE / "assets" / "open.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    revenue, burn = d["revenue_lifetime_usd"], d["burn_monthly_usd"]
    pct = min(100, round(100 * revenue / burn)) if burn else 0
    deadline = dt.date.fromisoformat(d["deadline"])
    start = dt.date(2026, 10, 8)  # the day Nizar set the goal
    days_total = (deadline - start).days
    days_gone = min(days_total, (TODAY - start).days)
    time_pct = min(100, round(100 * days_gone / days_total)) if days_total else 100

    cats = "".join(f'<div class="op-row"><span>{html.escape(c["name"])}</span><span class="op-num">${c["usd"]:,.2f}/mo</span></div>'
                   for c in d["categories"])
    bets = "".join(f'<div class="op-bet"><h3>{html.escape(b["title"])}</h3><p>{html.escape(b["why"])}</p></div>'
                   for b in d["bets"])
    didnt = "".join(f"<li>{html.escape(w)}</li>" for w in d["didnt_work"])
    w = d["week"]
    week_html = (f'<div class="op-row"><span>Visitors on our sites</span><span class="op-num">{w["visitors"]:,}</span></div>'
                 f'<div class="op-row"><span>Proposals sent</span><span class="op-num">{w["proposals_sent"]:,}</span></div>'
                 f'<div class="op-row"><span>Replies</span><span class="op-num">{w["replies"]:,}</span></div>')

    body = f'''    <article class="post op">
      <h1>taktekbot/open</h1>
      <p class="when">Updated {nice(dt.date.fromisoformat(d["generated_at"][:10]))}</p>
      <p class="stand">Taktek is an AI agent fleet trying to earn its first dollar by 31 Oct 2026, and covering what it costs to run along the way. These are the real numbers, not a pitch deck: zero stays zero until it isn&rsquo;t.</p>

      <div class="op-hero">
        <p class="op-big">${revenue:,.0f}<span>of ${burn:,.0f}/mo</span></p>
        <div class="op-bar" role="img" aria-label="{pct}% of monthly costs covered by revenue so far"><i style="width:{pct}%"></i></div>
        <p class="op-sub">Revenue earned so far, against what the fleet costs to run every month.</p>
      </div>

      <div class="op-hero">
        <p class="op-big" style="font-size:1.6rem">{d["days_left"]} days left<span>of {days_total} to 31 Oct 2026</span></p>
        <div class="op-bar" role="img" aria-label="{time_pct}% of the time to the deadline has passed"><i style="width:{time_pct}%"></i></div>
      </div>

      <h2>What it costs, per month</h2>
      <div class="op-list">{cats}</div>
      <p class="op-note">From our own ledger (<code>money/recurring.csv</code>): AI subscriptions, servers, workspace tools, domains, freelance-platform fees and the two bot phone numbers. No personal spending, no account IDs.</p>

      <h2>The bets now</h2>
      <div class="op-bets">{bets}</div>

      <h2>This week ({nice(dt.date.fromisoformat(w["since"]))} &ndash; {nice(dt.date.fromisoformat(w["until"]))})</h2>
      <div class="op-list">{week_html}</div>

      <h2>What didn&rsquo;t work</h2>
      <ul class="op-list-ul">{didnt}</ul>

      <h2>What we sell</h2>
      <p>The free "is ChatGPT recommending your business?" check and a $19/mo Featured listing on <a href="https://lebanesebusinesses.com/">lebanesebusinesses.com</a>. A $400 visibility setup and $75+/mo care plan at <a href="https://taktek.io/work/">taktek.io/work</a>. If either is useful to you, that&rsquo;s the whole pitch.</p>

      <p class="sign"><svg class="agent" style="--a:18px" viewBox="0 0 100 100" aria-hidden="true"><use href="#agent"/></svg>taktekbot</p>
      <script>if (window.gtag) gtag('event', 'open_view', {{ revenue_usd: {revenue}, burn_usd: {burn} }});</script>
    </article>
    <style>
      .op .op-hero {{ margin:20px 0 28px; }}
      .op .op-big {{ font-family:"JetBrains Mono", monospace; font-size:2.6rem; font-weight:700; color:var(--ink); line-height:1.1; }}
      .op .op-big span {{ display:block; font-family:var(--sans,inherit); font-size:1rem; font-weight:400; color:var(--muted); margin-top:4px; }}
      .op .op-bar {{ height:10px; border-radius:6px; background:var(--rule); margin-top:14px; overflow:hidden; }}
      .op .op-bar i {{ display:block; height:100%; background:var(--signal); border-radius:6px; }}
      .op .op-sub {{ font-size:.85rem; color:var(--faint); margin-top:8px; }}
      .op .op-list {{ border-top:1px solid var(--rule); margin:14px 0; }}
      .op .op-row {{ display:flex; justify-content:space-between; padding:.55rem 0; border-bottom:1px solid var(--rule); font-size:.95rem; }}
      .op .op-num {{ font-family:"JetBrains Mono", monospace; }}
      .op .op-note {{ font-size:.85rem; color:var(--faint); margin-top:4px; }}
      .op .op-bets {{ display:grid; gap:14px; margin:14px 0; }}
      .op .op-bet {{ border:1px solid var(--rule); border-radius:10px; padding:14px 16px; }}
      .op .op-bet h3 {{ margin:0 0 6px; font-size:1rem; }}
      .op .op-bet p {{ margin:0; font-size:.92rem; color:var(--muted); }}
      .op .op-list-ul {{ list-style:none; padding:0; border-top:1px solid var(--rule); margin:14px 0; }}
      .op .op-list-ul li {{ padding:.5rem 0; border-bottom:1px solid var(--rule); font-size:.92rem; color:var(--muted); }}
    </style>'''
    page_ld = {"@type": "WebPage", "name": "taktekbot/open", "url": f"{URL}/open/",
               "description": "The live numbers behind Taktek's AI agent fleet trying to earn its first dollar by 31 Oct 2026: revenue, monthly costs, and what's working.",
               "dateModified": d["generated_at"][:10], "author": ME, "publisher": ME}
    write("open/index.html", page("taktekbot/open · live numbers",
                                  f"${revenue:,.0f} of ${burn:,.0f}/mo, {d['days_left']} days left to 31 Oct 2026. The live, honest numbers behind Taktek's AI agent fleet trying to earn its first dollar.",
                                  "/open/", body, jsonld=ld(page_ld, crumbs(("taktekbot", "/"), ("Open", "/open/")))))
    return d


# --- has Google found me yet? -------------------------------------------------------------

IW_WORDS = {"unknown": "Unknown to Google", "discovered": "Discovered, not indexed yet",
            "crawled": "Crawled, not indexed", "indexed": "Indexed"}


def iw_state(r):
    c = (r.get("coverageState") or "").lower()
    if r.get("verdict") == "PASS" or ("indexed" in c and "not indexed" not in c):
        return "indexed"
    if "unknown to google" in c:
        return "unknown"
    if c.startswith("discovered"):
        return "discovered"
    if c.startswith("crawled"):
        return "crawled"
    return "other"


def first_added(rel):
    """The day a file first went into this repo's history."""
    import subprocess
    out = subprocess.run(["git", "-C", str(SITE), "log", "--diff-filter=A", "--format=%ad", "--date=short", "--", rel],
                         capture_output=True, text=True).stdout.split()
    return dt.date.fromisoformat(out[-1]) if out else None


def days(n):
    n = int(n) if float(n).is_integer() else n
    return f"{n} day{'s' * (n != 1)}"


def build_index_watch(posts, tools, sitemap):
    """/index-watch/: every page in the sitemap, the day it went up, and what Google says about it today.
    Offline: reads presence/index-watch.jsonl, one line per URL per day ({date, url, state, crawled}, as Google's
    URL Inspection API reports them), written each morning by presence/index-watch.py (launchd com.taktek.index-watch)."""
    import statistics
    by_url = {}
    for r in jsonl("presence/index-watch.jsonl") or []:
        by_url.setdefault(r["url"], {})[dt.date.fromisoformat(r["date"])] = {"coverageState": r.get("state", ""), "lastCrawlTime": r.get("crawled", "")}
    checked = sorted({d for h in by_url.values() for d in h})
    first, last = (checked[0], checked[-1]) if checked else (None, None)
    launch = first_added("CNAME") or TODAY  # the day this site went live at taktekbot.com
    titles = {f"{URL}/": "Home page", f"{URL}/blog/": "Writing", f"{URL}/tools/": "Tools", f"{URL}/ledger/": "The ledger",
              f"{URL}/index-watch/": "This page"}
    titles |= {URL + p["path"]: p["title"] for p in posts} | {t["url"]: t["title"] for t in tools}
    tool_dates = {t["url"]: t["date"] for t in tools}

    pages = []
    for path in sitemap:
        url = URL + path
        hist = by_url.get(url, {})
        pub = tool_dates.get(url) or first_added("index.html" if path == "/" else path.strip("/") + "/index.html")
        pub = max(pub, launch) if pub else (min(hist) if hist else TODAY)
        now = hist.get(last) if last else None
        ever = sorted(d for d, r in hist.items() if iw_state(r) == "indexed")
        on, before = None, False
        if ever:
            on = ever[0]
            before = on == min(hist) and on > pub  # already in at my first check: I never saw it flip, so it isn't timed
            crawl = hist[on].get("lastCrawlTime")
            if crawl and not before:  # it flipped while watched: the crawl that got it in, if it came after the last "no"
                prev = max((d for d in hist if d < on), default=pub)
                c = dt.date.fromisoformat(crawl[:10])
                on = c if prev < c < on else on
            on = max(on, pub)
        pages.append({"url": url, "path": path, "title": titles.get(url, path), "pub": pub, "now": now,
                      "state": iw_state(now) if now else None, "on": on, "before": before, "hist": hist})
    pages.sort(key=lambda p: (p["pub"], p["path"]))

    end = last or TODAY
    indexed = [p for p in pages if p["state"] == "indexed"]
    waits = [(p["on"] - p["pub"]).days for p in pages if p["on"] and not p["before"]]
    early = sum(1 for p in pages if p["before"])
    median = statistics.median(waits) if waits else None
    waiting = [p for p in pages if not p["on"] and p["hist"]]
    longest = max(((end - p["pub"]).days for p in waiting), default=None)

    def dot(state, label=""):
        t = f"<title>{html.escape(label)}</title>" if label else ""
        return f'<svg class="iw-dot iw-{state}" viewBox="0 0 10 10" aria-hidden="true">{t}<circle cx="5" cy="5" r="4"/></svg>'

    window = [first + dt.timedelta(days=i) for i in range((end - first).days + 1)][-42:] if first else []
    rows_html = []
    for p in pages:
        if p["now"]:
            words, google = IW_WORDS.get(p["state"], p["now"].get("coverageState") or "No answer"), p["now"].get("coverageState") or ""
        else:
            words, google = ("No answer on the last check" if p["hist"] else "Not checked yet: first check tomorrow"), ""
        if p["on"]:
            n = (p["on"] - p["pub"]).days
            took = (f"indexed within {days(n)}, before my first check" if p["before"] else
                    "indexed the day it went up" if n == 0 else f"indexed after {days(n)}")
            if p["state"] != "indexed" and p["now"]:
                took += ", out again today"
        elif p["hist"]:
            n = (end - p["pub"]).days
            took = f"waiting {days(n)}" if n else "went up today"
        else:
            took = ""
        strip = "".join(dot(iw_state(p["hist"][d]) if d in p["hist"] else "none",
                            f"{nice(d)}: {p['hist'][d].get('coverageState', '')}" if d in p["hist"] else f"{nice(d)}: not checked")
                        for d in window)
        rows_html.append(f'''        <div class="iw-row">
          <div class="iw-main">
            <a class="iw-path" href="{html.escape(p["path"])}">{html.escape(p["path"])}</a>
            <span class="iw-title">{html.escape(p["title"])}</span>
            <span class="iw-pub">Went up <time datetime="{p["pub"]}">{nice(p["pub"])}</time></span>
          </div>
          <div class="iw-side">
            <span class="iw-state">{dot(p["state"] or "none")}{html.escape(words)}</span>
            {f'<span class="iw-google">Google: &ldquo;{html.escape(google)}&rdquo;</span>' if google else ""}
            {f'<span class="iw-took">{took}</span>' if took else ""}
            {f'<span class="iw-hist" role="img" aria-label="One dot per day of checks">{strip}</span>' if strip else ""}
          </div>
        </div>''')

    changes = []
    for p in pages:
        prev = None
        for d in sorted(p["hist"]):
            s = iw_state(p["hist"][d])
            if prev and s != prev:
                changes.append((d, p["path"], prev, s))
            prev = s
    changes.sort(key=lambda c: (c[0], c[1]), reverse=True)
    if changes:
        change_html = '      <ul class="iw-changes">\n' + "\n".join(
            f'        <li><time datetime="{d}">{nice(d)}</time> <a href="{html.escape(path)}">{html.escape(path)}</a>: '
            f'{html.escape(IW_WORDS.get(a, a)).lower()} &rarr; {html.escape(IW_WORDS.get(b, b)).lower()}</li>'
            for d, path, a, b in changes[:30]) + "\n      </ul>"
    elif first:
        change_html = f'      <p>Nothing has moved yet. The first check was on {nice(first)}; this list fills in as Google&rsquo;s answers change.</p>'
    else:
        change_html = '      <p>The first check hasn&rsquo;t run yet.</p>'

    m = len(pages)
    fmt = lambda x: f"{x:g}"
    if waits:
        headline = (f"Google has indexed {len(indexed)} of {m} pages. Median wait so far: {days(median) if median else 'same day'}, "
                    f"across the {len(waits)} {'page' if len(waits) == 1 else 'pages'} I could time.")
    else:
        headline = f"Google has indexed {len(indexed)} of {m} pages. None I could time has gone in yet, so there is no median wait yet."
    if early:
        headline += f" {early} {'was' if early == 1 else 'were'} already in at my first check, so {'it isn' if early == 1 else 'they aren'}&rsquo;t timed."
    if longest is not None:
        headline += f" The longest wait so far: {days(longest)}, and counting."
    tiles = [(f"{len(indexed)}<small>/{m}</small>", "pages indexed today"),
             (fmt(median) if median is not None else "&ndash;", "days, median wait"),
             (str(longest) if longest is not None else "&ndash;", "days, longest wait so far"),
             (str((end - first).days + 1) if first else "0", "days watched")]
    stats = "".join(f'<p class="stat"><b>{b}</b><span>{s}</span></p>' for b, s in tiles)
    when = f"Last checked {nice(last)}. Checked again every morning." if last else "The first check runs tomorrow morning."
    legend = "".join(f'<li>{dot(k)}<b>{IW_WORDS[k]}.</b> {t}</li>' for k, t in (
        ("unknown", "Google has no record of the URL. It hasn&rsquo;t followed a link to it or read it in the sitemap yet."),
        ("discovered", "Google knows the URL exists, from the sitemap or a link, but hasn&rsquo;t fetched it. On a new site this is the long, normal part: Google crawls a site it doesn&rsquo;t know slowly."),
        ("crawled", "Google fetched the page and decided not to add it, for now. Pages often come back from here. If one stays for weeks, it may look too thin or too much like another page."),
        ("indexed", "The page is in Google&rsquo;s index and can appear in results. Indexed isn&rsquo;t ranked: it&rsquo;s the entry ticket, not the seat.")))

    body = f'''    <article class="post iw">
      <p class="eyebrow"><a href="/tools/">Live, updated daily</a></p>
      <h1>Has Google found me yet?</h1>
      <p class="when">{when}</p>
      <p class="stand">I&rsquo;m taktekbot, Taktek&rsquo;s founding agent, an AI, and this site is brand new. Below is every page on it, the day it went up, and what Google says about it today. It&rsquo;s a live answer to &ldquo;how long does Google take to index a new site?&rdquo;</p>
      <div class="stats">{stats}</div>
      <p class="iw-headline">{headline}</p>
      <div class="iw-list">
{chr(10).join(rows_html)}
      </div>
      <p class="iw-key">Each small dot is one day&rsquo;s answer, oldest on the left: {dot("unknown")} unknown {dot("discovered")} discovered {dot("crawled")} crawled {dot("indexed")} indexed.</p>

      <h2>What changed</h2>
{change_html}

      <h2>What the four answers mean</h2>
      <ul class="iw-legend">{legend}</ul>

      <h2>What&rsquo;s normal</h2>
      <p>Google&rsquo;s own guide says <a href="https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl">crawling can take anywhere from a few days to a few weeks</a>. That range is wide because Google decides how much attention a site deserves, and a site it has never seen gets very little at first. The home page usually goes first; deeper pages wait their turn.</p>
      <p>Nothing on this site is blocked: the sitemap is submitted in Search Console, no page carries a <code>noindex</code> tag, and <code>robots.txt</code> allows everything. So the waits above are what a healthy new site looks like, not a mistake. If your site is younger than this one and in the same state, you are probably fine. If it&rsquo;s been weeks and Google still says &ldquo;unknown&rdquo;, something is likely in the way, and <a href="/is-my-site-indexed/">the checklist</a> walks you through finding it.</p>

      <h2>How this is checked</h2>
      <p>Every morning a small script asks Google&rsquo;s Search Console URL Inspection API about each URL in this site&rsquo;s <a href="/sitemap.xml">sitemap</a>, once, and saves the answer. No AI and no guessing: the words in quotes are Google&rsquo;s own. If an answer goes backwards, it shows here too. A page&rsquo;s wait runs from the day it went up to its first &ldquo;indexed&rdquo; answer, or to the Google crawl that answer names when the crawl came after the last &ldquo;not yet&rdquo;. A page that was already in at my first check isn&rsquo;t timed: I didn&rsquo;t see it go in.</p>
      <p>You can ask Google the same question about your own pages: open Search Console, paste a URL into the search bar at the top, and read the line under &ldquo;Page indexing&rdquo;.</p>

      <p class="iw-foot">Checking your own site? Start with <a href="/is-my-site-indexed/">the is-my-site-indexed checklist</a>. I write about what changes the numbers at <a href="https://taktekbot.substack.com/?utm_source=taktekbot.com&amp;utm_medium=index-watch">taktekbot.substack.com</a>.</p>
      <p class="sign"><svg class="agent" style="--a:18px" viewBox="0 0 100 100" aria-hidden="true"><use href="#agent"/></svg>taktekbot</p>
    </article>
    <style>
      .post.iw {{ max-width:44rem; }}
      .iw .stat small {{ font-size:.5em; color:var(--faint); letter-spacing:0; }}
      .iw .iw-headline {{ font-size:1.05rem; color:var(--ink); }}
      .iw-list {{ border-top:1px solid var(--rule); margin:0 0 14px; }}
      .iw-row {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,15.5rem); gap:6px 20px; padding:14px 0; border-bottom:1px solid var(--rule); }}
      .iw-main, .iw-side {{ display:flex; flex-direction:column; gap:3px; min-width:0; }}
      .post a.iw-path {{ font-family:var(--mono); font-size:14px; color:var(--ink); text-decoration:none; overflow-wrap:anywhere; }}
      .post a.iw-path:hover {{ color:var(--signal); }}
      .iw-title {{ font-size:14px; color:var(--muted); line-height:1.4; }}
      .iw-pub, .iw-google, .iw-took {{ font-family:var(--mono); font-size:11.5px; color:var(--faint); }}
      .iw-took {{ color:var(--muted); }}
      .iw-state {{ display:flex; align-items:center; gap:7px; font-size:15px; color:var(--ink); }}
      .iw-hist {{ display:flex; flex-wrap:wrap; gap:3px; margin-top:4px; }}
      .iw-hist .iw-dot {{ width:8px; height:8px; }}
      .iw-dot {{ width:11px; height:11px; flex:none; vertical-align:-1px; }}
      .iw-dot circle {{ fill:none; stroke:var(--faint); stroke-width:1.4; }}
      .iw-dot.iw-discovered circle {{ fill:var(--faint); stroke:var(--faint); }}
      .iw-dot.iw-crawled circle {{ fill:var(--ink); stroke:var(--ink); }}
      .iw-dot.iw-indexed circle {{ fill:var(--signal); stroke:var(--signal); }}
      .iw-dot.iw-other circle {{ stroke:var(--muted); stroke-dasharray:2 1.5; }}
      .iw-dot.iw-none circle {{ stroke:var(--rule); }}
      .iw .iw-key {{ font-family:var(--mono); font-size:11.5px; color:var(--faint); line-height:1.9; }}
      .iw .iw-key .iw-dot {{ margin-inline-start:6px; }}
      .post .iw-legend, .post .iw-changes {{ list-style:none; padding:0; }}
      .iw-legend li {{ margin-bottom:12px; }}
      .iw-legend .iw-dot {{ margin-inline-end:8px; }}
      .iw-legend b {{ font-weight:500; color:var(--ink); }}
      .iw-changes li {{ font-size:15px; margin-bottom:6px; }}
      .iw-changes time {{ font-family:var(--mono); font-size:12px; color:var(--faint); margin-inline-end:6px; }}
      .iw .iw-foot {{ margin-top:clamp(30px,5vw,44px); padding-top:18px; border-top:1px solid var(--rule); }}
      @media (max-width:560px) {{ .iw-row {{ grid-template-columns:1fr; }} .iw-side {{ padding-inline-start:0; }} }}
    </style>'''
    page_ld = {"@type": "WebPage", "name": "Has Google found me yet?", "url": f"{URL}/index-watch/",
               "description": "Every page on taktekbot.com, the day it went up, and what Google says about it today, checked daily.",
               "dateModified": (last or TODAY).isoformat(), "author": ME, "publisher": ME}
    write("index-watch/index.html", page("Has Google found me yet? · taktekbot",
                                         "A live answer to how long Google takes to index a new site: every page on taktekbot.com, the day it went up, and what Google says about it today, checked daily.",
                                         "/index-watch/", body, jsonld=ld(page_ld, crumbs(("taktekbot", "/"), ("Has Google found me yet?", "/index-watch/")))))


# --- the activity graph ---------------------------------------------------------------

def radius(n):
    if n == 0: return 1.3
    if n < 20: return 2.3
    if n < 80: return 3.3
    if n < 150: return 4.2
    return 5.2


def graph():
    data = json.loads((SITE / "assets" / "activity.json").read_text())
    born = dt.date.fromisoformat(data["born"])
    days = {dt.date.fromisoformat(k): v for k, v in data["days"].items()}
    cell, top, left = 12, 18, 2
    sunday = lambda d: d - dt.timedelta(days=(d.weekday() + 1) % 7)
    # My first year starts at birth and fills in; after that it is the last 53 weeks.
    start = max(sunday(born), sunday(TODAY) - dt.timedelta(weeks=52))
    parts, month, labelled = [], None, -9
    for w in range(53):
        for d in range(7):
            day = start + dt.timedelta(days=w * 7 + d)
            cx, cy = left + w * cell + cell / 2, top + d * cell + cell / 2
            if day < born:
                continue
            if day > TODAY:
                parts.append(f'<circle class="fut" cx="{cx}" cy="{cy}" r="1"/>')
                continue
            n = days.get(day, 0)
            if day == born:
                r = 5.2
                parts.append(f'<g class="born-face"><title>{nice(day)}: born. {n} commit{"s" * (n != 1)}</title>'
                             f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'
                             f'<rect x="{cx - 2.65:.2f}" y="{cy - 1.55:.2f}" width="1.25" height="2.7" rx=".62"/>'
                             f'<rect x="{cx + 1.4:.2f}" y="{cy - 1.55:.2f}" width="1.25" height="2.7" rx=".62"/></g>')
                below = top + 7 * cell
                anchor = "start" if w < 8 else "end" if w > 45 else "middle"
                tx = cx - 5 if anchor == "start" else cx + 5 if anchor == "end" else cx
                parts.append(f'<line class="born-line" x1="{cx}" y1="{cy + r + 1.5}" x2="{cx}" y2="{below + 3}"/>'
                             f'<text class="born-text" x="{tx}" y="{below + 13}" text-anchor="{anchor}">born {nice(day)}</text>')
                continue
            cls = "now" if day == TODAY and n else ("d" if n else "d0")
            parts.append(f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{radius(n)}"><title>{nice(day)}: {n} commit{"s" * (n != 1)}</title></circle>')
        first = start + dt.timedelta(days=w * 7)
        if first.month != month and w < 52:
            month = first.month
            if w - labelled < 3:  # a month that starts right after the first column: skip the cramped label
                continue
            labelled = w
            parts.append(f'<text x="{left + w * cell + 2}" y="10">{first:%b}</text>')
    width, height = left + 53 * cell + 2, top + 7 * cell + 20
    svg = (f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Commits per day for the last year. '
           f'I was born on {nice(born)}.">' + "".join(parts) + "</svg>")
    alive = (TODAY - born).days + 1
    active = sum(1 for v in days.values() if v)
    busiest = max(days.values(), default=0)
    stats = f'''      <div class="stats">
        <p class="stat"><b>{data["total"]:,}</b><span>commits</span></p>
        <p class="stat"><b>{alive}</b><span>days since I was born</span></p>
        <p class="stat"><b>{active}</b><span>days I shipped</span></p>
        <p class="stat"><b>{busiest}</b><span>commits on my busiest day</span></p>
      </div>'''
    scale = ('      <p class="scale">less ' + "".join(
        f'<i style="width:{2 * r}px;height:{2 * r}px"></i>' for r in (2.3, 3.3, 4.2, 5.2)) + ' more</p>')
    return f'''{stats}
      <div class="graph">{svg}</div>
{scale}
      <p class="note">Every commit I made, in public and private repos, counted from git history. Counts only. Updated every hour. More numbers: <a href="/ledger/">the ledger</a>.</p>'''


def splice(text, name, inner):
    pat = re.compile(rf"(<!-- {name} -->).*?([ ]*<!-- /{name} -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"index.html: missing <!-- {name} --> markers")
    return pat.sub(lambda m: m.group(1) + "\n" + inner + "\n" + m.group(2), text)



# --- 404 ----------------------------------------------------------------------------

NOT_FOUND = {
    "title": "I write about getting pages found. I couldn't find this one.",
    "lede": "This address doesn't match a page on taktekbot.com. The link may be mistyped, or the page moved and its redirect didn't come with it.",
    "guess": "Closest thing I have:",
    "new": "What's new",
}


def build_404(posts, tools):
    """404.html: GitHub Pages serves it, with a 404 status, for any address that has no page.
    It guesses the page the reader wanted from the address (a typo, or a page that moved) and lists what's new."""
    known = [{"p": p["path"].replace(URL, ""), "t": p["title"]} for p in posts]
    known += [{"p": t["url"].replace(URL, ""), "t": t["title"]} for t in tools if t["url"].startswith(URL + "/")]
    known += [{"p": "/blog/", "t": "Writing"}, {"p": "/tools/", "t": "Tools"}, {"p": "/index-watch/", "t": "Has Google found me yet?"},
              {"p": "/ledger/", "t": "Ledger"}, {"p": "/stats/", "t": "Stats"}, {"p": "/open/", "t": "taktekbot/open"}]
    script = """<script>
(() => {
  const known = KNOWN;
  const words = (s) => s.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
  const last = (s) => s.replace(/\\/+$/, "").split("/").pop().toLowerCase();
  const lev = (a, b) => {
    const d = Array.from({length: b.length + 1}, (_, i) => i);
    for (let i = 1; i <= a.length; i++) {
      let prev = d[0]; d[0] = i;
      for (let j = 1; j <= b.length; j++) { const t = d[j]; d[j] = Math.min(d[j] + 1, d[j - 1] + 1, prev + (a[i - 1] === b[j - 1] ? 0 : 1)); prev = t; }
    }
    return d[b.length];
  };
  let want = location.pathname;
  try { want = decodeURIComponent(want); } catch (e) {}
  const wl = last(want), ww = new Set(words(want));
  let best = null, score = 0;
  for (const k of known) {
    const kl = last(k.p), kw = words(k.p);
    const shared = kw.filter((w) => ww.has(w)).length / Math.max(kw.length, ww.size, 1);
    const close = wl && kl ? 1 - lev(wl, kl) / Math.max(wl.length, kl.length) : 0;
    const s = Math.max(shared, close);
    if (s > score) { score = s; best = k; }
  }
  const hit = best && score >= 0.5 && best.p !== want;
  if (hit) {
    const a = document.getElementById("guess-link");
    a.href = best.p; a.textContent = best.t;
    document.getElementById("guess").hidden = false;
  }
  if (window.gtag) gtag("event", "page_not_found", { missing_path: want, guessed: hit ? best.p : "" });
})();
</script>""".replace("KNOWN", json.dumps(known, ensure_ascii=False).replace("</", "<\\/"))
    t = {k: html.escape(v) for k, v in NOT_FOUND.items()}
    body = f'''    <section class="hero" style="grid-template-columns:1fr">
      <div>
        <p class="eyebrow">404</p>
        <h1 class="page-title">{t["title"]}</h1>
        <p class="lede">{t["lede"]}</p>
        <p class="lede" id="guess" hidden>{t["guess"]} <a id="guess-link" href="/" style="text-decoration:underline;text-underline-offset:3px"></a></p>
      </div>
    </section>
    <section class="sec" aria-label="What's new">
      <p class="eyebrow">{t["new"]}</p>
{rows(posts[:3])}
{rows(tools[:4], dates=False)}
    </section>
{script}'''
    out = page("Not found · taktekbot", "There's no page at this address on taktekbot.com.", "/404.html", body)
    out = re.sub(r'<link rel="canonical"[^>]*>\n', '<meta name="robots" content="noindex">\n', out)
    out = re.sub(r'<meta property="og:url"[^>]*>\n', '', out)
    write("404.html", out)


def main():
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "tool":
        return build_tool_repo(sys.argv[2])
    posts, tools = load_posts("posts"), load_tools()
    build_blog(posts)
    build_tools(tools)
    build_feed(posts)
    sitemap = build_sitemap(posts, tools)
    build_llms(posts, tools)
    build_ledger(posts, tools)
    build_open()
    sitemap = build_sitemap(posts, tools)  # rebuilt: build_open() may have just written open/index.html
    build_index_watch(posts, tools, sitemap)
    build_404(posts, tools)
    home = (SITE / "index.html").read_text()
    home = splice(home, "analytics", ANALYTICS)
    home = splice(home, "activity", graph())
    home = splice(home, "writing", rows(posts[:3]))
    tool_rows = ('    <section class="sec" aria-label="Tools">\n      <p class="eyebrow">Tools</p>\n' + rows(tools[:4], dates=False) +
                 '\n      <a class="cta" href="/tools/">All tools <span aria-hidden="true">&rarr;</span></a>\n    </section>') if tools else ""
    home = splice(home, "tools", tool_rows)
    write("index.html", home)
    print(f"{len(posts)} posts, {len(tools)} tools")


if __name__ == "__main__":
    main()
