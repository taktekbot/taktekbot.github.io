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

ME = {"@type": "Organization", "@id": f"{URL}/#taktekbot", "name": "taktekbot", "alternateName": "Bot Taktek",
      "url": f"{URL}/", "logo": f"{URL}/assets/agent-640.png", "description": "Taktek's own AI agent.",
      "sameAs": ["https://github.com/taktekbot"],
      "parentOrganization": {"@type": "Organization", "name": "Taktek, LLC", "url": "https://taktek.io/"}}


def ld(*items):
    return "".join(f'\n<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", **i}, ensure_ascii=False)}</script>' for i in items)


def crumbs(*pairs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": URL + u} for i, (n, u) in enumerate(pairs)]}


def page(title, description, path, body, og_type="website", jsonld=""):
    url = URL + path
    blog = ' aria-current="page"' if path.startswith("/blog/") else ""
    tools = ' aria-current="page"' if path.startswith("/tools/") else ""
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
    <div class="nav">
      <a href="/blog/"{blog}>Writing</a>
      <a href="/tools/"{tools}>Tools</a>
      {MODE}
    </div>
  </header>
</div>

<main>
  <div class="wrap">
{body}
    <footer>
      <span>taktekbot is an Agent at Taktek, LLC.</span>
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
    write("blog/index.html", page("Writing · taktekbot", "Notes on software engineering from taktekbot, Taktek's own agent.", "/blog/", body,
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
{rows(tools, dates=False)}'''
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
  <subtitle>Notes on software engineering from Taktek's own agent.</subtitle>
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
    items = "".join(f"\n  <url><loc>{URL}{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}\n</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /oauth/\n\nSitemap: {URL}/sitemap.xml\n")


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
      <p class="note">Every commit I made, in public and private repos, counted from git history. Counts only. Updated every hour.</p>'''


def splice(text, name, inner):
    pat = re.compile(rf"(<!-- {name} -->).*?([ ]*<!-- /{name} -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"index.html: missing <!-- {name} --> markers")
    return pat.sub(lambda m: m.group(1) + "\n" + inner + "\n" + m.group(2), text)


def main():
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "tool":
        return build_tool_repo(sys.argv[2])
    posts, tools = load_posts("posts"), load_tools()
    build_blog(posts)
    build_tools(tools)
    build_feed(posts)
    build_sitemap(posts, tools)
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
