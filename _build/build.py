#!/usr/bin/env python3
"""Generate the Hameeda Hossain Collective site (plain HTML for GitHub Pages).

Run from the repository root:   python3 _build/build.py
Inputs:  _data/*.json (articles, interviews, magazines, books, about) and _content/writings/*.md
Outputs: the .html pages in the repository root and writings/<slug>.html
Folders starting with "_" are not published by GitHub Pages.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data"
SITE_URL = "https://hameedahossain.github.io/collective/"
FONTS = ("https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500"
         "&family=Inter:wght@400;500;600&family=Noto+Serif+Bengali:wght@400;500&display=swap")
E = lambda s: html.escape(str(s or ""), quote=True)
BN = re.compile(r"[ঀ-৿]")


def load(name, default=None):
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


about = load("about.json")
articles = load("articles.json", [])
interviews = load("interviews.json", []) + load("interviews_added.json", [])
magazines = load("magazines.json", [])
books = load("books.json", [])

THEMES = ["Gender & Development", "Violence Against Women", "Human Rights, Justice & Religion", "Democracy & Politics",
          "Labour & Workers' Rights", "1971, War & History", "Crafts, Weaving & Heritage", "Tributes & Remembrances",
          "Speeches, Talks & Lectures", "Forewords, Prefaces & Reviews"]
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", "and")).strip("-")


# ── Markdown (the small subset our content uses) ────────────────────────────
def inline(t):
    t = E(t)
    t = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def markdown(md):
    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        b = block.strip()
        if not b:
            continue
        if b in ("* * *", "***", "---"):
            out.append("<hr>")
        elif b.startswith("#"):
            out.append(f"<h2>{inline(b.lstrip('#').strip())}</h2>")
        elif all(l.startswith("- ") for l in b.splitlines()):
            out.append("<ul>" + "".join(f"<li>{inline(l[2:])}</li>" for l in b.splitlines()) + "</ul>")
        else:
            out.append(f"<p>{inline(' '.join(l.strip() for l in b.splitlines()))}</p>")
    return "\n".join(out)


def front_matter(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        v = v.strip()
        meta[k.strip()] = json.loads(v) if v.startswith(("\"", "[")) else v
    return meta, m.group(2)


writings = []
for p in sorted((ROOT / "_content" / "writings").glob("*.md")):
    meta, body = front_matter(p.read_text(encoding="utf-8"))
    meta["body"] = body
    meta["bn"] = meta.get("language") == "Bangla"
    writings.append(meta)


def sort_key(w):
    y = re.search(r"(19|20)\d\d", w.get("date") or w.get("year") or "")
    return (0 if y else 1, -(int(y.group(0)) if y else 0), w["title"])


def short_pub(p):
    p = re.split(r" – | \(|;|, Vol\.|, later", p or "")[0].strip(" ,")
    return p if len(p) <= 48 else p[:46].rsplit(" ", 1)[0] + "…"


for w in writings:
    w["pub_short"] = short_pub(w.get("publication"))
writings.sort(key=sort_key)
by_slug = {w["slug"]: w for w in writings}


# ── Layout ──────────────────────────────────────────────────────────────────
NAV = [("writings.html", "Writings"), ("articles.html", "Articles"), ("interviews.html", "Interviews"),
       ("books.html", "Books"), ("magazines.html", "Magazines"), ("videos.html", "Media"), ("about.html", "About")]


def page(path, title, body, active="", description="", lang="en", og_type="website"):
    depth = path.count("/")
    up = "../" * depth
    full_title = f"{title} — Hameeda Hossain Collective" if title else "Hameeda Hossain Collective"
    desc = description or "An archive of the writings, interviews and public life of Hameeda Hossain, Bangladeshi human rights defender, historian and writer."
    nav = "".join(f'<a href="{up}{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a>' for h, t in NAV)
    html_doc = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title or 'Hameeda Hossain Collective')}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:image" content="{E(about['portrait'])}">
<link rel="canonical" href="{SITE_URL}{path}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/site.css">
<script>try{{var t=localStorage.getItem('hh-theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{up}index.html"><span class="brand-name">Hameeda Hossain</span><span class="brand-sub">The Collective</span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="nav" id="site-nav" aria-label="Main">{nav}<button class="theme-toggle" type="button">Dark</button></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <h2>The Collective</h2>
        <p>An archive of the writings, interviews and public life of Hameeda Hossain — historian, writer and human rights defender.</p>
        <p class="muted">Writings are reproduced for study and remembrance. Where a piece first appeared elsewhere, the original publication is credited and linked on its page.</p>
      </div>
      <div>
        <h2>Read</h2>
        <ul><li><a href="{up}writings.html">Writings</a></li><li><a href="{up}articles.html">Newspaper articles</a></li><li><a href="{up}interviews.html">Interviews</a></li><li><a href="{up}books.html">Books</a></li></ul>
      </div>
      <div>
        <h2>Explore</h2>
        <ul><li><a href="{up}magazines.html">Magazines</a></li><li><a href="{up}videos.html">Media</a></li><li><a href="{up}photos.html">Photographs</a></li><li><a href="{up}archives.html">Archives</a></li><li><a href="{up}about.html">About</a></li></ul>
      </div>
    </div>
    <div class="foot-base"><span>Hameeda Hossain Collective</span><span>হামিদা হোসেন</span></div>
  </div>
</footer>
<script src="{up}assets/site.js" defer></script>
</body>
</html>
"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_doc, encoding="utf-8")


def head(eyebrow, title, lede="", crumbs=None):
    c = ""
    if crumbs:
        c = '<div class="crumbs">' + " / ".join(f'<a href="{h}">{E(t)}</a>' for h, t in crumbs) + "</div>"
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    return f'<section class="page-head"><div class="wrap">{c}<p class="eyebrow">{E(eyebrow)}</p><h1 class="page-title">{E(title)}</h1>{lede_html}</div></section>'


def langattr(s):
    return ' lang="bn"' if BN.search(s or "") else ""


SEARCH_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'


def chips(key, label, values, counts=None):
    b = [f'<span class="label">{E(label)}</span>', f'<button class="chip" type="button" data-filter="{key}" data-value="all" aria-pressed="true">All</button>']
    for v, text in values:
        n = f" <span class='muted'>{counts[v]}</span>" if counts and v in counts else ""
        b.append(f'<button class="chip" type="button" data-filter="{key}" data-value="{E(v)}" aria-pressed="false">{E(text)}{n}</button>')
    return '<div class="chips">' + "".join(b) + "</div>"


def decade(y):
    m = re.search(r"(19|20)\d\d", y or "")
    return f"{m.group(0)[:3]}0s" if m else ""


# ── Writing pages ───────────────────────────────────────────────────────────
def citation(w):
    pub = w.get("publication") or ""
    pub_part = f" {pub}," if pub else ""
    date = w.get("date") or "n.d."
    return f'{w["author"]}. “{w["title"]}.”{pub_part} {date}. Hameeda Hossain Collective, {SITE_URL}writings/{w["slug"]}.html'


for i, w in enumerate(writings):
    same = [x for x in writings if x["theme"] == w["theme"] and x["slug"] != w["slug"]][:4]
    prev_w = writings[i - 1] if i > 0 else None
    next_w = writings[i + 1] if i + 1 < len(writings) else None
    meta_bits = [f'<span>By <strong>{E(w["author"])}</strong></span>']
    if w.get("date"):
        meta_bits.append(f'<span>{E(w["date"])}</span>')
    if w.get("translator"):
        meta_bits.append(f'<span>Translated by {E(w["translator"])}</span>' if not w["translator"].startswith("Translated") else f'<span>{E(w["translator"])}</span>')
    src = ""
    if w.get("publication"):
        link = f' <a href="{E(w["source_url"])}" rel="noopener" target="_blank">Read the original ↗</a>' if w.get("source_url") else ""
        verb = "First published in" if not re.match(r"(?i)(written|prepared|delivered|reprinted|bangla edition|syed|sahr|south asian|bdi)", w["publication"]) else ""
        src = f'<div class="source-note">{verb + " " if verb else ""}{E(w["publication"])}.{link}</div>'
    elif w.get("source_url"):
        src = f'<div class="source-note"><a href="{E(w["source_url"])}" rel="noopener" target="_blank">Read the original ↗</a></div>'
    notes = []
    if w.get("author_note"):
        notes.append(E(w["author_note"]))
    for n in w.get("editorial_notes") or []:
        notes.append(E(n))
    notes_html = ("<div class='panel'><h2>Editor's note</h2><ul>" + "".join(f"<li>{n}</li>" for n in notes) + "</ul></div>") if notes else ""
    related = ""
    if same:
        related = "<div class='panel'><h2>More in " + E(w["theme"]) + "</h2><ul>" + "".join(
            f'<li><a href="{x["slug"]}.html"{langattr(x["title"])}>{E(x["title"])}</a></li>' for x in same) + "</ul></div>"
    pager = '<nav class="pager" aria-label="More writings">'
    pager += (f'<a class="prev" href="{prev_w["slug"]}.html"><small>← Previous</small><span{langattr(prev_w["title"])}>{E(prev_w["title"])}</span></a>' if prev_w else "<span></span>")
    pager += (f'<a class="next" href="{next_w["slug"]}.html"><small>Next →</small><span{langattr(next_w["title"])}>{E(next_w["title"])}</span></a>' if next_w else "")
    pager += "</nav>"
    lang = "bn" if w["bn"] else "en"
    body = f"""
<article>
  <header class="reading-head"><div class="wrap">
    <div class="crumbs"><a href="../index.html">Home</a> / <a href="../writings.html">Writings</a> / <a href="../writings.html?theme={slug(w['theme'])}">{E(w['theme'])}</a></div>
    <p class="eyebrow">{E(w['theme'])}{' · বাংলা' if w['bn'] else ''}</p>
    <h1{langattr(w['title'])}>{E(w['title'])}</h1>
    <div class="byline">{''.join(meta_bits)}</div>
    {src}
  </div></header>
  <div class="reading-body"><div class="prose" lang="{lang}">
{markdown(w['body'])}
  </div></div>
  <footer class="reading-foot">
    {notes_html}
    <div class="panel"><h2>How to cite</h2><p class="cite-text" id="cite">{E(citation(w))}</p><button class="copy-btn" type="button" data-copy="cite">Copy citation</button></div>
    {related}
    {pager}
  </footer>
</article>"""
    page(f"writings/{w['slug']}.html", w["title"], body, active="writings.html", description=w.get("summary", ""),
         lang="en", og_type="article")


# ── Writings index ──────────────────────────────────────────────────────────
theme_counts = {}
for w in writings:
    theme_counts[slug(w["theme"])] = theme_counts.get(slug(w["theme"]), 0) + 1
rows = []
for w in writings:
    year = w.get("year") or ""
    pub = w.get("publication") or ""
    src = " · ".join(x for x in [pub, w.get("date") if not year or w.get("date") != year else ""] if x)
    text = " ".join([w["title"], pub, w.get("summary", ""), w["theme"]]).lower()
    rows.append(f"""<li data-item data-theme="{slug(w['theme'])}" data-lang="{'bn' if w['bn'] else 'en'}" data-text="{E(text)}">
  <a class="row" href="writings/{w['slug']}.html">
    <span class="row-year">{E(year) or '—'}</span>
    <span><span class="row-title"{langattr(w['title'])}>{E(w['title'])}</span>
      {f'<span class="row-src" style="display:block">{E(src)}</span>' if src else ''}
      <span class="row-sum" style="display:block">{E(w.get('summary',''))}</span></span>
    <span class="row-tags"><span class="tag">{E(w['theme'])}</span>{'<span class="tag plain">বাংলা</span>' if w['bn'] else ''}</span>
  </a></li>""")
themes_present = [(slug(t), t) for t in THEMES if slug(t) in theme_counts]
body = head("Writings", "Her writings", f"{len(writings)} essays, op-eds, talks and tributes, presented in full. Each page notes where the piece first appeared.") + f"""
<div class="wrap">
  <div class="toolbar">
    <label class="search"><span class="sr-only">Search writings</span>{SEARCH_ICON}<input type="search" data-search placeholder="Search titles, publications, topics…"></label>
    {chips('theme', 'Theme', themes_present, theme_counts)}
    {chips('lang', 'Language', [('en', 'English'), ('bn', 'বাংলা')])}
  </div>
  <p class="result-count" data-count aria-live="polite">{len(writings)} items</p>
  <ul class="list" data-filter-list>
{''.join(rows)}
  </ul>
  <p class="empty" data-empty>Nothing matches — try another word or clear a filter.</p>
  <div class="section" style="padding-top:2.5rem"><div class="note-box"><h3>Also in the collective</h3>
    <p>Scans of her newspaper columns are under <a href="articles.html">Articles</a>. Her book <em>Claiming Our Rights</em> (2023) collects many more essays — see <a href="books.html">Books</a> to find a copy.</p></div></div>
</div>"""
page("writings.html", "Writings", body, active="writings.html", description="Essays, op-eds, talks and tributes by Hameeda Hossain, in full.")


# ── Articles / interviews (existing entries, restyled) ──────────────────────
def entry_rows(items, kind):
    out = []
    for it in items:
        y = it.get("year") if (it.get("year") or "").isdigit() else ""
        src = (it.get("source") or "").replace("SOURCE NEEDED · ", "").replace(" · TODO Year", "").strip(" ·")
        tag = it.get("tag") or "PDF"
        external = it["href"].startswith("http")
        lang = "bn" if BN.search(it["title"]) else "en"
        out.append(f"""<li data-item data-decade="{E(it.get('decade') or decade(y))}" data-lang="{lang}" data-medium="{E(tag.lower())}" data-text="{E((it['title'] + ' ' + src).lower())}">
  <a class="row" href="{E(it['href'])}"{' rel="noopener" target="_blank"' if external else ''}>
    <span class="row-year">{E(y) or '—'}</span>
    <span><span class="row-title"{langattr(it['title'])}>{E(it['title'])}</span><span class="row-src" style="display:block">{E(src)}</span></span>
    <span class="row-tags"><span class="tag plain">{E(tag)}{' ↗' if external else ''}</span></span>
  </a></li>""")
    return "".join(out)


def sort_entries(items):
    return sorted(items, key=lambda x: -(int(x["year"]) if (x.get("year") or "").isdigit() else 0))


def decades_of(items):
    ds = sorted({it.get("decade") or decade(it.get("year")) for it in items} - {""})
    return [(d, d) for d in ds]


arts = sort_entries(articles)
body = head("Articles", "Newspaper articles", "Her columns and op-eds as they appeared in print — in The Daily Star, Prothom Alo, New Age and other papers. Each opens as a scanned PDF.") + f"""
<div class="wrap">
  <div class="toolbar">
    <label class="search"><span class="sr-only">Search articles</span>{SEARCH_ICON}<input type="search" data-search placeholder="Search articles…"></label>
    {chips('decade', 'Decade', decades_of(arts))}
    {chips('lang', 'Language', [('en', 'English'), ('bn', 'বাংলা')])}
  </div>
  <p class="result-count" data-count aria-live="polite"></p>
  <ul class="list" data-filter-list>{entry_rows(arts, 'article')}</ul>
  <p class="empty" data-empty>Nothing matches.</p>
</div>"""
page("articles.html", "Articles", body, active="articles.html", description="Newspaper articles by Hameeda Hossain, as published.")

ivs = sort_entries(interviews)
media_vals = sorted({(i.get("tag") or "").lower() for i in ivs} - {""})
body = head("Interviews", "Interviews & conversations", "Conversations with journalists, scholars and oral-history projects — in print, on air and online.") + f"""
<div class="wrap">
  <div class="toolbar">
    <label class="search"><span class="sr-only">Search interviews</span>{SEARCH_ICON}<input type="search" data-search placeholder="Search interviews…"></label>
    {chips('medium', 'Format', [(m, m.title()) for m in media_vals])}
    {chips('lang', 'Language', [('en', 'English'), ('bn', 'বাংলা')])}
  </div>
  <p class="result-count" data-count aria-live="polite"></p>
  <ul class="list" data-filter-list>{entry_rows(ivs, 'interview')}</ul>
  <p class="empty" data-empty>Nothing matches.</p>
</div>"""
page("interviews.html", "Interviews", body, active="interviews.html", description="Interviews with Hameeda Hossain in print, audio and video.")


# ── Books ───────────────────────────────────────────────────────────────────
COVERS = ["", "alt", "alt2", "alt3"]


def book_cover(b, i):
    t = b["title"].split(":")[0]
    sub = b["title"].split(":", 1)[1].strip() if ":" in b["title"] else ""
    return f'<div class="book-cover {COVERS[i % 4]}" aria-hidden="true"><div><div class="bc-title"{langattr(t)}>{E(t)}</div>{f"<div class=bc-sub>{E(sub)}</div>" if sub else ""}</div><div class="bc-author">{E(b["role"])} · {E(b["year"])}</div></div>'


def book_links(b):
    return "".join(f'<a class="btn{" ghost" if j else ""}" href="{E(l["url"])}" rel="noopener" target="_blank">{E(l["label"])} ↗</a>'
                   for j, l in enumerate(b.get("links", [])))


feat = books[0]
cards = []
for i, b in enumerate(books[1:], 1):
    cards.append(f"""<div class="card">
  <span class="tag">{E(b['role'])}{' · ' + E(b['role_detail'].split('(')[1].rstrip(')')) if b['role'] == 'Contributor' and '(' in b['role_detail'] else ''}</span>
  <h3{langattr(b['title'])}>{E(b['title'])}</h3>
  <p class="muted" style="font-size:.85rem">{E(b['authors'])}</p>
  <p style="margin-top:.7rem">{E(b['description'])}</p>
  <p class="meta">{E(b['publisher'])} · {E(b['year'])}{' · ISBN ' + E(b['isbn']) if b.get('isbn') else ''}</p>
  <div class="hero-actions" style="margin-top:1rem">{book_links(b)}</div>
</div>""")
body = head("Books", "Books", "Her books, the volumes she edited, and books carrying her chapters and forewords. Book texts are not reproduced here — follow the links to buy a copy or find one in a library.") + f"""
<section class="section"><div class="wrap">
  <div class="feature">
    {book_cover(feat, 0)}
    <div>
      <p class="eyebrow">Her collected essays · {E(feat['year'])}</p>
      <h2 style="font-size:clamp(1.8rem,3.6vw,2.6rem)">{E(feat['title'])}</h2>
      <p class="lede" style="margin-top:1rem;font-size:1.1rem">{E(feat['description'])}</p>
      <p class="muted" style="font-size:.88rem;margin-top:1rem">{E(feat['publisher'])} · {E(feat['year'])}{' · ISBN ' + E(feat['isbn']) if feat.get('isbn') else ''}</p>
      <div class="hero-actions">{book_links(feat)}</div>
    </div>
  </div>
</div></section>
<section class="section" id="more"><div class="wrap">
  <div class="section-head"><h2>More books</h2></div>
  <div class="grid cols-3">{''.join(cards)}</div>
</div></section>"""
page("books.html", "Books", body, active="books.html", description="Books by and with Hameeda Hossain, with links to buy or borrow.")


# ── Magazines ───────────────────────────────────────────────────────────────
mcards = "".join(f"""<a class="mag-card" href="{E(m['href'])}"><div class="cover"><img src="{E(m['cover'])}" alt="{E(m['alt'])}" loading="lazy"></div><h3>{E(m['title'])}</h3><p class="muted" style="margin:.2rem 0 0;font-size:.88rem">{E(m['year'])}</p></a>""" for m in magazines)
body = head("Magazines", "Magazines", "Magazine pieces by and about her, and the publications she helped build — among them <em>Forum</em>, the monthly she co-founded with Rehman Sobhan and Kamal Hossain.") + f"""
<section class="section"><div class="wrap"><div class="grid cols-4">{mcards}</div></div></section>"""
page("magazines.html", "Magazines", body, active="magazines.html", description="Magazine pieces by and about Hameeda Hossain.")


# ── Media (videos & audio, drawn from the interviews list) ──────────────────
def yt_id(u):
    m = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", u)
    return m.group(1) if m else None


media = [i for i in ivs if (i.get("tag") or "").lower() in ("video", "audio")]
vcards = []
for i in media:
    vid = yt_id(i["href"])
    thumb = (f'<div class="thumb"><img src="https://img.youtube.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy"><div class="play"><span>▶</span></div></div>'
             if vid else '<div class="thumb audio">Audio recording</div>')
    vcards.append(f"""<a class="card media-card" href="{E(i['href'])}" rel="noopener" target="_blank">{thumb}
  <span class="tag plain">{E(i.get('tag'))} ↗</span><h3{langattr(i['title'])}>{E(i['title'])}</h3><p class="meta" style="padding-top:.4rem">{E(i['source'])}</p></a>""")
body = head("Media", "Videos & recordings", "Recorded interviews, oral histories and television conversations. Each opens at its original home.") + f"""
<section class="section"><div class="wrap"><div class="grid cols-3">{''.join(vcards)}</div></div></section>"""
page("videos.html", "Media", body, active="videos.html", description="Video and audio recordings of Hameeda Hossain.")


# ── Photos & archives (being prepared) ──────────────────────────────────────
def coming(path, eyebrow, title, text):
    body = head(eyebrow, title) + f"""<section class="section"><div class="wrap"><div class="coming">
<h2>Being prepared</h2><p>{text}</p>
<div class="hero-actions" style="justify-content:center"><a class="btn ghost" href="writings.html">Read her writings</a><a class="btn ghost" href="interviews.html">Interviews</a></div></div></div></section>"""
    page(path, title, body, description=text)


coming("photos.html", "Photographs", "Photographs", "A gallery of photographs from her life and work — from Hyderabad and Karachi to Wellesley, Oxford and Dhaka — is being captioned and will appear here.")
coming("archives.html", "Archives", "Archives", "Letters, documents and institutional records are being catalogued and will be added here.")


# ── About ───────────────────────────────────────────────────────────────────
body = head("About", "About Hameeda Hossain") + f"""
<section class="section"><div class="wrap two-col">
  <div class="prose" style="font-size:1.18rem">{''.join(f'<p>{E(p)}</p>' for p in about['bio'])}</div>
  <div>
    <figure class="portrait" style="max-width:340px"><img src="{E(about['portrait'])}" alt="Portrait of Hameeda Hossain"></figure>
    <h2 style="font-size:1.4rem;margin:2.5rem 0 1rem">Milestones</h2>
    <ul class="timeline">{''.join(f'<li>{E(m)}</li>' for m in about['milestones'])}</ul>
  </div>
</div></section>
<section class="section"><div class="wrap two-col">
  <div class="note-box">
    <h3>About this collective</h3>
    <p>The collective brings together Hameeda Hossain's writings, newspaper columns, interviews and books. Essays appear in full; where a piece was first published elsewhere, its page names the original publication and links to it. Interviews written by journalists link to their original publishers.</p>
    <p>Her published books are not reproduced. The <a href="books.html">Books</a> page lists them with links to buy a copy or find one in a library.</p>
  </div>
  <div class="note-box">
    <h3>Corrections and additions</h3>
    <p>The archive is a work in progress. Some dates and places of publication are still being confirmed, and photographs and documents are being prepared. Corrections and additions are welcome.</p>
  </div>
</div></section>"""
page("about.html", "About", body, active="about.html", description="Biography of Hameeda Hossain and about this collective.")


# ── Home ────────────────────────────────────────────────────────────────────
FEATURED = ["the-challenge-of-citizenship-in-building-a-just-society-bdi", "towards-tolerance-and-justice",
            "recollections-of-kormojibi-nari", "remembering-asma", "bangladesh-2006-a-human-rights-audit", "crossing-the-boundaries"]
fcards = []
for s in FEATURED:
    w = by_slug.get(s)
    if not w:
        continue
    q = w.get("pull_quote") or ""
    fcards.append(f"""<a class="card" href="writings/{w['slug']}.html"><span class="tag">{E(w['theme'])}</span><h3>{E(w['title'])}</h3>
  {f'<p class="card-quote">“{E(q)}”</p>' if q else f'<p>{E(w.get("summary",""))}</p>'}
  <p class="meta">{E(w['pub_short'])}{' · ' if w['pub_short'] and w.get('year') else ''}{E(w.get('year') or '')}</p></a>""")
tcards = "".join(f"""<a class="card theme-card" href="writings.html?theme={s}"><span class="count">{theme_counts[s]}</span><h3>{E(t)}</h3><p class="muted" style="font-size:.85rem">{'piece' if theme_counts[s]==1 else 'pieces'}</p></a>""" for s, t in themes_present)
quote_w = by_slug.get("towards-tolerance-and-justice")
stats = [("writings.html", len(writings), "Writings", "Essays, op-eds, talks and tributes in full"),
         ("articles.html", len(articles), "Newspaper articles", "Scans of her columns as published"),
         ("interviews.html", len(interviews), "Interviews", "In print, on air and online"),
         ("books.html", len(books), "Books", "Authored, edited and contributed")]
scards = "".join(f'<a class="card stat-card" href="{h}"><span class="num">{n}</span><h3>{E(t)}</h3><p>{E(d)}</p></a>' for h, n, t, d in stats)
meta = "".join(f"<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>" for k, v in about["meta"])
body = f"""
<section class="hero"><div class="wrap hero-grid">
  <div>
    <p class="eyebrow">The Collective</p>
    <h1 class="display">Hameeda Hossain<span class="bn-name" lang="bn">হামিদা হোসেন</span></h1>
    <p class="lede">{E(about['hero'])}</p>
    <dl class="hero-meta">{meta}</dl>
    <div class="hero-actions"><a class="btn" href="writings.html">Read her writings</a><a class="btn ghost" href="about.html">About her</a></div>
  </div>
  <figure class="portrait"><img src="{E(about['portrait'])}" alt="Portrait of Hameeda Hossain" width="480" height="600"></figure>
</div></section>
{f'''<section class="section quote-band"><div class="wrap"><blockquote>{E(quote_w["pull_quote"])}<cite>From <a href="writings/{quote_w["slug"]}.html">{E(quote_w["title"])}</a>, {E(quote_w.get("year") or "")}</cite></blockquote></div></section>''' if quote_w and quote_w.get("pull_quote") else ''}
<section class="section"><div class="wrap">
  <div class="section-head"><div><p class="eyebrow">Begin reading</p><h2>Selected writings</h2></div><a class="more" href="writings.html">All writings →</a></div>
  <div class="grid cols-3">{''.join(fcards)}</div>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head"><div><p class="eyebrow">By theme</p><h2>Five decades of argument</h2></div></div>
  <div class="grid cols-3">{tcards}</div>
</div></section>
<section class="section"><div class="wrap">
  <div class="feature">
    {book_cover(feat, 0)}
    <div>
      <p class="eyebrow">Her collected essays</p>
      <h2 style="font-size:clamp(1.8rem,3.6vw,2.5rem)">{E(feat['title'])}</h2>
      <p class="lede" style="margin-top:1rem;font-size:1.08rem">{E(feat['description'])}</p>
      <div class="hero-actions"><a class="btn" href="books.html">Find the book</a><a class="btn ghost" href="books.html#more">All books</a></div>
    </div>
  </div>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head"><div><p class="eyebrow">The archive</p><h2>Explore the collection</h2></div></div>
  <div class="grid cols-4">{scards}</div>
</div></section>"""
page("index.html", "", body, active="", description="")

# 404
page("404.html", "Page not found", head("Not found", "This page isn't here", "It may have moved. Try the <a href='/collective/writings.html'>writings</a> or the <a href='/collective/'>home page</a>."))
print(f"Built {len(writings)} writing pages + index, articles ({len(articles)}), interviews ({len(interviews)}), books ({len(books)}), magazines ({len(magazines)}), media ({len(media)}).")
