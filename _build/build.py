#!/usr/bin/env python3
"""Generate the Hameeda Hossain Collective site (plain HTML for GitHub Pages).

Run from the repository root:   python3 _build/build.py
Inputs:  _data/*.json and _content/writings/*.md     Outputs: *.html and writings/*.html
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
photos = load("photos.json", [])
scans = load("scans.json", {})
desc = load("descriptions.json", {})
covers = load("covers.json", {})
commons = {c["key"]: c for c in load("commons.json", [])}
timeline = load("timeline.json", [])
theme_art = load("theme_images.json", {})
writing_art = load("writing_images.json", {})
photo_by = {p["slug"]: p for p in photos}

THEMES = ["Gender & Development", "Violence Against Women", "Human Rights, Justice & Religion", "Democracy & Politics",
          "Labour & Workers' Rights", "1971, War & History", "Crafts, Weaving & Heritage", "Tributes & Remembrances",
          "Speeches, Talks & Lectures", "Forewords, Prefaces & Reviews"]
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", "and")).strip("-")


def image_for(ref):
    """ref is 'photo:<slug>' or 'commons:<key>' -> dict(src, thumb, alt, credit) or None"""
    if not ref:
        return None
    kind, _, key = ref.partition(":")
    if kind == "photo" and key in photo_by:
        p = photo_by[key]
        return dict(src=f"assets/photos/{key}.jpg", thumb=f"assets/photos/thumbs/{key}.jpg", alt=p["caption"], credit="")
    if kind == "cover" and key in covers:
        bk = next((x for x in books if x["key"] == key), {"title": key})
        return dict(src=covers[key], thumb=covers[key], alt=f"Cover of {bk['title']}", credit="", cover=True)
    if kind == "commons" and key in commons:
        c = commons[key]
        return dict(src=c["path"], thumb=c.get("thumb") or c["path"], alt=c.get("alt") or c["subject"], credit=c["credit_line"])
    return None


def theme_image(theme, slug_=None):
    """Individual writings only get a photograph when one belongs to that piece; themes may use one of her photos."""
    if slug_ is not None:
        return image_for(writing_art.get(slug_))
    return image_for(theme_art.get(theme))


# ── Markdown ────────────────────────────────────────────────────────────────
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


def short_pub(p):
    p = re.split(r" – | \(|;|, Vol\.|, later", p or "")[0].strip(" ,")
    return p if len(p) <= 48 else p[:46].rsplit(" ", 1)[0] + "…"


writings = []
for p in sorted((ROOT / "_content" / "writings").glob("*.md")):
    meta, body = front_matter(p.read_text(encoding="utf-8"))
    meta["body"] = body
    meta["bn"] = meta.get("language") == "Bangla"
    meta["pub_short"] = short_pub(meta.get("publication"))
    writings.append(meta)


def ykey(s):
    y = re.search(r"(19|20)\d\d", s or "")
    return int(y.group(0)) if y else 0


writings.sort(key=lambda w: (ykey(w.get("date") or w.get("year")) == 0, -ykey(w.get("date") or w.get("year")), w["title"]))
by_slug = {w["slug"]: w for w in writings}


# ── Layout ──────────────────────────────────────────────────────────────────
NAV = [("writings.html", "Writings"), ("timeline.html", "Life"), ("connections.html", "Her circle"), ("articles.html", "Articles"), ("interviews.html", "Interviews"),
       ("books.html", "Books"), ("photos.html", "Photographs"), ("about.html", "About")]


import hashlib


def ver(rel):
    return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()[:8]


def page(path, title, body, active="", description="", og_image=None, extra_head=""):
    up = "../" * path.count("/")
    full_title = f"{title} — Hameeda Hossain" if title else "Hameeda Hossain"
    desc_ = description or "The writings, interviews, books and life of Hameeda Hossain, Bangladeshi historian, writer and human rights defender."
    nav = "".join(f'<a href="{up}{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a>' for h, t in NAV)
    og = og_image or about["portrait"]
    if not og.startswith("http"):
        og = SITE_URL + og
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc_)}">
<meta property="og:title" content="{E(title or 'Hameeda Hossain')}">
<meta property="og:description" content="{E(desc_)}">
<meta property="og:image" content="{E(og)}">
<link rel="canonical" href="{SITE_URL}{path}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/site.css?v={ver('assets/site.css')}">
<script>try{{var t=localStorage.getItem('hh-theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{up}index.html"><span class="brand-name">Hameeda Hossain</span></a>
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
        <p class="foot-name">Hameeda Hossain <span lang="bn">হামিদা হোসেন</span></p>
        <p class="muted">Writings are reproduced for study and remembrance; each page credits where a piece first appeared. Photographs are from her personal archive.</p>
      </div>
      <ul><li><a href="{up}writings.html">Writings</a></li><li><a href="{up}timeline.html">Life &amp; times</a></li><li><a href="{up}connections.html">Her circle</a></li><li><a href="{up}articles.html">Newspaper articles</a></li><li><a href="{up}interviews.html">Interviews</a></li></ul>
      <ul><li><a href="{up}books.html">Books</a></li><li><a href="{up}videos.html">Video &amp; audio</a></li><li><a href="{up}magazines.html">Magazines</a></li><li><a href="{up}photos.html">Photographs</a></li><li><a href="{up}about.html">About</a></li></ul>
    </div>
  </div>
</footer>
<div class="lightbox" hidden><button class="lb-close" type="button" aria-label="Close">×</button><figure><img alt=""><figcaption></figcaption></figure></div>
<script src="{up}assets/site.js?v={ver('assets/site.js')}" defer></script>
</body>
</html>
"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


def head(title, lede="", crumbs=None, image=None):
    c = ('<div class="crumbs">' + " / ".join(f'<a href="{h}">{E(t)}</a>' for h, t in crumbs) + "</div>") if crumbs else ""
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    if image:
        return f'''<section class="page-head has-image"><div class="wrap head-grid"><div>{c}<h1 class="page-title">{E(title)}</h1>{lede_html}</div>
<figure class="head-image"><img src="{E(image['src'])}" alt="{E(image['alt'])}"><figcaption>{E(image['alt'])}{(' · ' + E(image['credit'])) if image.get('credit') else ''}</figcaption></figure></div></section>'''
    return f'<section class="page-head"><div class="wrap">{c}<h1 class="page-title">{E(title)}</h1>{lede_html}</div></section>'


def langattr(s):
    return ' lang="bn"' if BN.search(s or "") else ""


SEARCH_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'


def chips(key, label, values, counts=None):
    b = [f'<span class="label">{E(label)}</span>', f'<button class="chip" type="button" data-filter="{key}" data-value="all" aria-pressed="true">All</button>']
    for v, text in values:
        n = f" <span class='n'>{counts[v]}</span>" if counts and v in counts else ""
        b.append(f'<button class="chip" type="button" data-filter="{key}" data-value="{E(v)}" aria-pressed="false">{E(text)}{n}</button>')
    return '<div class="chips">' + "".join(b) + "</div>"


def decade(y):
    m = re.search(r"(19|20)\d\d", y or "")
    return f"{m.group(0)[:3]}0s" if m else ""


def toolbar(placeholder, *chipsets):
    return f'''<div class="toolbar">
    <label class="search"><span class="sr-only">Search</span>{SEARCH_ICON}<input type="search" data-search placeholder="{E(placeholder)}"></label>
    {''.join(chipsets)}
  </div>
  <p class="result-count" data-count aria-live="polite"></p>'''


def entry(href, thumb, year, title, source, summary, tags, data, prefix="", external=False, thumb_class=""):
    """One consistent list row used on every list page."""
    t = (f'<span class="row-thumb {thumb_class}"><img src="{prefix}{E(thumb)}" alt="" loading="lazy"></span>' if thumb and not thumb.startswith("http")
         else f'<span class="row-thumb {thumb_class}"><img src="{E(thumb)}" alt="" loading="lazy"></span>' if thumb
         else f'<span class="row-thumb blank {thumb_class}" aria-hidden="true"><span class="orn">❦</span></span>')
    attrs = " ".join(f'data-{k}="{E(v)}"' for k, v in data.items())
    tag_html = "".join(f'<span class="tag{" plain" if i else ""}">{E(x)}</span>' for i, x in enumerate(tags) if x)
    return f"""<li data-item {attrs}>
  <a class="row" href="{E(href)}"{' rel="noopener" target="_blank"' if external else ''}>
    {t}
    <span class="row-main">
      <span class="row-meta">{E(year) if year else ''}{' · ' if year and source else ''}{E(source)}</span>
      <span class="row-title"{langattr(title)}>{E(title)}{' <span class="ext" aria-label="opens another site">↗</span>' if external else ''}</span>
      {f'<span class="row-sum">{E(summary)}</span>' if summary else ''}
      <span class="row-tags">{tag_html}</span>
    </span>
  </a></li>"""


# ── Writing pages ───────────────────────────────────────────────────────────
def citation(w):
    pub = w.get("publication") or ""
    return f'{w["author"]}. “{w["title"]}.”{(" " + pub + ",") if pub else ""} {w.get("date") or "n.d."}. Hameeda Hossain Collective, {SITE_URL}writings/{w["slug"]}.html'


for i, w in enumerate(writings):
    same = [x for x in writings if x["theme"] == w["theme"] and x["slug"] != w["slug"]][:4]
    prev_w = writings[i - 1] if i > 0 else None
    next_w = writings[i + 1] if i + 1 < len(writings) else None
    bits = [f'<span>By <strong>{E(w["author"])}</strong></span>']
    if w.get("date"):
        bits.append(f'<span>{E(w["date"])}</span>')
    if w.get("translator"):
        bits.append(f'<span>{E(w["translator"]) if w["translator"].startswith("Translated") else "Translated by " + E(w["translator"])}</span>')
    src = ""
    if w.get("publication"):
        link = f' <a href="{E(w["source_url"])}" rel="noopener" target="_blank">Read the original ↗</a>' if w.get("source_url") else ""
        verb = "" if re.match(r"(?i)(written|prepared|delivered|reprinted|bangla edition|syed|sahr|south asian|bdi)", w["publication"]) else "First published in "
        src = f'<p class="source-note">{verb}{E(w["publication"])}.{link}</p>'
    notes = ([E(w["author_note"])] if w.get("author_note") else []) + [E(n) for n in (w.get("editorial_notes") or [])]
    notes_html = ("<div class='panel'><h2>Editor's note</h2><ul>" + "".join(f"<li>{n}</li>" for n in notes) + "</ul></div>") if notes else ""
    related = ("<div class='panel'><h2>More on " + E(w["theme"]) + "</h2><ul>" + "".join(
        f'<li><a href="{x["slug"]}.html"{langattr(x["title"])}>{E(x["title"])}</a></li>' for x in same) + "</ul></div>") if same else ""
    pager = '<nav class="pager" aria-label="More writings">'
    pager += (f'<a class="prev" href="{prev_w["slug"]}.html"><small>Previous</small><span{langattr(prev_w["title"])}>{E(prev_w["title"])}</span></a>' if prev_w else "<span></span>")
    pager += (f'<a class="next" href="{next_w["slug"]}.html"><small>Next</small><span{langattr(next_w["title"])}>{E(next_w["title"])}</span></a>' if next_w else "")
    pager += "</nav>"
    img = theme_image(w["theme"], w["slug"])
    banner = f'<div class="reading-band motif t-{slug(w["theme"])}" aria-hidden="true"></div>'
    body = f"""
<article>
  <header class="reading-head"><div class="wrap">
    <div class="crumbs"><a href="../writings.html">Writings</a> / <a href="../writings.html?theme={slug(w['theme'])}">{E(w['theme'])}</a></div>
    <h1{langattr(w['title'])}>{E(w['title'])}</h1>
    {f'<p class="standfirst">{E(w.get("summary"))}</p>' if w.get('summary') and not w['bn'] else ''}
    <div class="byline">{''.join(bits)}</div>
    {src}
  </div></header>
  {banner}
  <div class="reading-body"><div class="prose" lang="{'bn' if w['bn'] else 'en'}">
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
         og_image=(img["src"] if img else None))


# ── Writings index ──────────────────────────────────────────────────────────
theme_counts = {}
for w in writings:
    theme_counts[slug(w["theme"])] = theme_counts.get(slug(w["theme"]), 0) + 1
themes_present = [(slug(t), t) for t in THEMES if slug(t) in theme_counts]


def writing_row(w, prefix=""):
    img = theme_image(w["theme"], w["slug"])
    text = " ".join([w["title"], w.get("publication") or "", w.get("summary", ""), w["theme"]]).lower()
    return entry(f"{prefix}writings/{w['slug']}.html", img["thumb"] if img else None, w.get("year"), w["title"], w["pub_short"],
                 w.get("summary", ""), [w["theme"], "বাংলা" if w["bn"] else ""],
                 {"theme": slug(w["theme"]), "lang": "bn" if w["bn"] else "en", "text": text}, prefix=prefix,
                 thumb_class="" if img else f"motif t-{slug(w['theme'])}")


body = head("Writings", f"{len(writings)} essays, columns, talks and tributes, in full. Each one notes where it first appeared.") + f"""
<div class="wrap">
  {toolbar('Search titles, publications, topics…', chips('theme', 'Theme', themes_present, theme_counts), chips('lang', 'Language', [('en', 'English'), ('bn', 'বাংলা')]))}
  <ul class="list" data-filter-list>{''.join(writing_row(w) for w in writings)}</ul>
  <p class="empty" data-empty>Nothing matches — try another word or clear a filter.</p>
  <p class="aside-note">Scans of her newspaper columns are under <a href="articles.html">Articles</a>. Many more essays are collected in <a href="books.html"><em>Claiming Our Rights</em></a> (2023).</p>
</div>"""
page("writings.html", "Writings", body, active="writings.html", description="Essays, columns, talks and tributes by Hameeda Hossain, in full.")


# ── Articles / interviews ───────────────────────────────────────────────────
def yt_id(u):
    m = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", u)
    return m.group(1) if m else None


def clean_source(s):
    return (s or "").replace("SOURCE NEEDED · ", "").replace(" · TODO Year", "").replace("Interview by ", "").strip(" ·")


def archive_rows(items):
    out = []
    for it in items:
        y = it.get("year") if (it.get("year") or "").isdigit() else ""
        d = desc.get(it["href"], {})
        external = it["href"].startswith("http")
        vid = yt_id(it["href"])
        thumb = scans.get(it["href"]) or (f"https://img.youtube.com/vi/{vid}/mqdefault.jpg" if vid else None)
        tag = it.get("tag") or "PDF"
        lang = "bn" if BN.search(it["title"]) else "en"
        title = it["title"]
        sub = d.get("title_en") or ""
        out.append(entry(it["href"], thumb, y, title + (f" ({sub})" if sub and lang == "bn" else ""), clean_source(it.get("source")), d.get("summary", ""),
                         [tag], {"decade": it.get("decade") or decade(y), "lang": lang, "medium": tag.lower(),
                                 "text": (title + " " + sub + " " + (it.get("source") or "") + " " + d.get("summary", "")).lower()},
                         external=external, thumb_class="scan" if it["href"] in scans else ("video" if vid else "")))
    return "".join(out)


def sort_entries(items):
    return sorted(items, key=lambda x: -(int(x["year"]) if (x.get("year") or "").isdigit() else 0))


def decades_of(items):
    return [(d, d) for d in sorted({it.get("decade") or decade(it.get("year")) for it in items} - {""})]


arts = sort_entries(articles)
body = head("Newspaper articles", "Her columns and op-eds as they appeared in print, in The Daily Star, Prothom Alo, New Age and other papers. Each opens as a scanned PDF.") + f"""
<div class="wrap">
  {toolbar('Search articles…', chips('decade', 'Decade', decades_of(arts)), chips('lang', 'Language', [('en', 'English'), ('bn', 'বাংলা')]))}
  <ul class="list" data-filter-list>{archive_rows(arts)}</ul>
  <p class="empty" data-empty>Nothing matches.</p>
</div>"""
page("articles.html", "Articles", body, active="articles.html", description="Newspaper articles by Hameeda Hossain, as published.")

ivs = sort_entries(interviews)
media_vals = sorted({(i.get("tag") or "").lower() for i in ivs} - {""})
body = head("Interviews", "Conversations with journalists, scholars and oral-history projects, in print, on air and online.") + f"""
<div class="wrap">
  {toolbar('Search interviews…', chips('medium', 'Format', [(m, m.title()) for m in media_vals]), chips('lang', 'Language', [('en', 'English'), ('bn', 'বাংলা')]))}
  <ul class="list" data-filter-list>{archive_rows(ivs)}</ul>
  <p class="empty" data-empty>Nothing matches.</p>
</div>"""
page("interviews.html", "Interviews", body, active="interviews.html", description="Interviews with Hameeda Hossain in print, audio and video.")

media = [i for i in ivs if (i.get("tag") or "").lower() in ("video", "audio")]
body = head("Video & audio", "Recorded interviews, oral histories and television conversations. Each opens where it was first published.") + f"""
<div class="wrap"><ul class="list">{archive_rows(media)}</ul></div>"""
page("videos.html", "Video & audio", body, active="interviews.html", description="Video and audio recordings of Hameeda Hossain.")

mag_rows = []
for m in magazines:
    d = desc.get(m["href"], {})
    mag_rows.append(entry(m["href"], m["cover"], m["year"], m["title"] + (f" — {d['title_en']}" if d.get("title_en") else ""), "",
                          d.get("summary", ""), ["Magazine"], {"decade": m.get("decade", "")}, thumb_class="scan"))
body = head("Magazines", "Magazine pieces by and about her, and the publications she helped build, among them <em>Forum</em>, the weekly she co-founded with Rehman Sobhan and Kamal Hossain.") + f"""
<div class="wrap"><ul class="list">{''.join(mag_rows)}</ul></div>"""
page("magazines.html", "Magazines", body, active="", description="Magazine pieces by and about Hameeda Hossain.")


# ── Books ───────────────────────────────────────────────────────────────────
PALETTES = ["c1", "c2", "c3", "c4", "c5", "c6"]


def book_cover(b, i, prefix=""):
    if covers.get(b["key"]):
        return f'<div class="cover real"><img src="{prefix}{E(covers[b["key"]])}" alt="Cover of {E(b["title"])}" loading="lazy"></div>'
    t = b["title"].split(":")[0]
    sub = b["title"].split(":", 1)[1].strip() if ":" in b["title"] else ""
    author = re.sub(r"\s*\(.*?\)", "", b["authors"]).split(";")[0]
    return f'''<div class="cover drawn {PALETTES[i % len(PALETTES)]}" role="img" aria-label="{E(b["title"])}">
  <span class="cv-rule"></span><span class="cv-title"{langattr(t)}>{E(t)}</span>{f'<span class="cv-sub">{E(sub)}</span>' if sub else ''}
  <span class="cv-author">{E(author)}</span><span class="cv-pub">{E(b["publisher"].split("(")[0].split(",")[0])}</span></div>'''


def buy_links(b):
    ls = b.get("links", [])
    buy = [l for l in ls if re.search(r"(?i)publisher|rokomari|pathak|chicago|series page", l["label"])]
    return buy or ls[:2]


def book_links(b, cls="btn"):
    b = dict(b, links=buy_links(b))
    return "".join(f'<a class="{cls}{" ghost" if j else ""}" href="{E(l["url"])}" rel="noopener" target="_blank">{E(l["label"])} ↗</a>' for j, l in enumerate(b.get("links", [])))


feat = books[0]
shelf = []
for i, b in enumerate(books):
    role = b["role"] + (" · " + b["role_detail"].split("(")[1].rstrip(")") if b["role"] == "Contributor" and "(" in b["role_detail"] else "")
    shelf.append(f"""<article class="book" id="{E(b['key'])}">
  {book_cover(b, i)}
  <div class="book-info">
    <p class="book-role">{E(role)} · {E(b['year'])}</p>
    <h3{langattr(b['title'])}>{E(b['title'])}</h3>
    <p class="book-by">{E(b['authors'])}</p>
    <p class="book-desc">{E(b['description'])}</p>
    <p class="book-pub">{E(b['publisher'])}{' · ISBN ' + E(b['isbn']) if b.get('isbn') else ''}</p>
    <div class="book-links">{book_links(b, 'link-btn')}</div>
  </div>
</article>""")
body = head("Books", "Her books, the volumes she edited, and books that carry her chapters and forewords. The texts are not reproduced here; follow the links to buy a copy or find one in a library.") + f"""
<section class="section"><div class="wrap"><div class="shelf">{''.join(shelf)}</div></div></section>"""
page("books.html", "Books", body, active="books.html", description="Books by and with Hameeda Hossain, with links to buy or borrow.",
     og_image=covers.get(feat["key"]))


# ── Photographs ─────────────────────────────────────────────────────────────
gal = []
for p in photos:
    if p["slug"] == "portrait":
        continue
    cap = p["caption"] + (f", {p['place']}" if p.get("place") and p["place"] not in p["caption"] else "") + (f" · {p['year']}" if p.get("year") else "")
    gal.append(f'<figure class="g-item" data-decade="{E(p.get("decade"))}"><button type="button" class="g-open" data-full="assets/photos/{p["slug"]}.jpg" data-caption="{E(cap)}"><img src="assets/photos/thumbs/{p["slug"]}.jpg" alt="{E(p["caption"])}" loading="lazy" width="{p["w"]}" height="{p["h"]}"></button><figcaption>{E(cap)}</figcaption></figure>')
pdec = sorted({p.get("decade") for p in photos if p.get("decade")})
body = head("Photographs", "From her personal archive: a childhood in Sindh, the 1952 Herald Tribune Forum in the United States, student years at Wellesley, and the decades of work that followed. Some names and dates are still being confirmed.") + f"""
<div class="wrap">
  <div class="toolbar">{chips('decade', 'Decade', [(d, d) for d in pdec])}</div>
  <div class="gallery" data-filter-list>{''.join(g.replace('<figure class="g-item"', '<figure data-item class="g-item"') for g in gal)}</div>
</div>"""
page("photos.html", "Photographs", body, active="photos.html", description="Photographs from the life of Hameeda Hossain.",
     og_image="assets/photos/herald-tribune-pakistan-flag.jpg")

body = head("Archives", "Letters, documents and institutional records are being catalogued and will be added here.") + """
<section class="section"><div class="wrap"><div class="hero-actions"><a class="btn ghost" href="photos.html">See the photographs</a><a class="btn ghost" href="timeline.html">Her life and times</a></div></div></section>"""
page("archives.html", "Archives", body, description="Letters, documents and records from the life of Hameeda Hossain.")


# ── Timeline ────────────────────────────────────────────────────────────────
STRANDS = [("life", "Her life"), ("work", "Her work"), ("movement", "Movements"), ("history", "History")]
tl_items, last_dec = [], None
title_to_slug = {w["title"].lower(): w["slug"] for w in writings}
for ev in timeline:
    y = ev.get("year")
    dec = f"{str(y)[:3]}0s" if y else ""
    if dec != last_dec:
        tl_items.append(f'<li class="tl-decade" id="d{dec[:4]}" data-decade-marker="{dec}"><span>{dec}</span></li>')
        last_dec = dec
    img = image_for(ev.get("image"))
    lk = ev.get("link")
    rel_html = (f'<a class="tl-link" href="{E(lk["href"])}"{langattr(lk["label"])}>{"See" if lk["href"].startswith("photos") else "Read more"}: {E(lk["label"])} →</a>'
                if lk and ((lk["href"].startswith("writings/") and lk["href"][9:-5] in by_slug) or lk["href"].startswith(("books.html", "photos.html"))) else "")
    img_html = (f'<button type="button" class="tl-img g-open" data-full="{E(img["src"])}" data-caption="{E(img["alt"] + (" · " + img["credit"] if img.get("credit") else ""))}"><img src="{E(img["thumb"])}" alt="{E(img["alt"])}" loading="lazy"></button>' if img else "")
    tl_items.append(f'''<li class="tl-event s-{E(ev["strand"])}{' has-img' if img else ''}{' has-cover' if img and img.get('cover') else ''}" data-item data-strand="{E(ev["strand"])}">
  <div class="tl-card">
    <p class="tl-when"><span class="tl-year">{E(ev.get("date") or y)}</span><span class="tl-strand">{E(dict(STRANDS).get(ev["strand"], ""))}</span>{f'<span class="tl-place">{E(ev["place"])}</span>' if ev.get("place") else ''}</p>
    {img_html}
    <h3>{E(ev["title"])}</h3>
    <p>{E(ev["text"])}</p>
    {f'<p class="tl-conn">{E(ev["connection"])}</p>' if ev.get("connection") else ''}
    {rel_html}
  </div>
</li>''')
decades_tl = sorted({f"{str(e['year'])[:3]}0s" for e in timeline if e.get("year")})
strand_chips = "".join(f'<button class="chip strand s-{k}" type="button" data-strand-toggle="{k}" aria-pressed="true"><span class="dot"></span>{E(v)}</button>' for k, v in STRANDS)
body = f"""
<section class="tl-hero">
  <div class="tl-hero-bg" aria-hidden="true">{''.join(f'<img src="assets/photos/thumbs/{s}.jpg" alt="">' for s in ['with-brother-iqbal','herald-tribune-pakistan-flag','young-portrait-1950s','paris-1965-cafe','kyoto-gosho','meeting-1980s','portrait'] if s in photo_by)}</div>
  <div class="wrap tl-hero-text">
    <h1 class="page-title">A life in its times</h1>
    <p class="lede">Hameeda Hossain's life alongside the movements and upheavals it moved through, from Partition to the garment workers' struggles of today. Choose what to follow, and jump between decades.</p>
  </div>
</section>
<div class="tl-controls"><div class="wrap">
  <div class="chips">{strand_chips}</div>
  <nav class="tl-decades" aria-label="Decades">{''.join(f'<a href="#d{d[:4]}">{d}</a>' for d in decades_tl)}</nav>
</div><div class="tl-progress"><span></span></div></div>
<div class="wrap"><ol class="timeline-list" data-timeline>{''.join(tl_items)}</ol></div>"""
page("timeline.html", "A life in its times", body, active="timeline.html", description="An interactive timeline of Hameeda Hossain's life, work and the movements around her.",
     og_image="assets/photos/herald-tribune-pakistan-flag.jpg")


# ── About ───────────────────────────────────────────────────────────────────
credits = sorted({(re.sub(r"^\d+\.\s*", "", c["subject"]), c["credit_line"], c.get("commons_page", "")) for c in commons.values()})
credit_html = ("<details class='credits' id='credits'><summary>Image credits</summary><p>Historical photographs are from Wikimedia Commons under the licences shown. All other photographs are from Hameeda Hossain's personal archive.</p><ul>" + "".join(
    f'<li>{E(s)}: {E(cr)}{f" (<a href={chr(34)}{E(u)}{chr(34)} rel={chr(34)}noopener{chr(34)} target={chr(34)}_blank{chr(34)}>source</a>)" if u else ""}</li>' for s, cr, u in credits) + "</ul></details>") if credits else ""
body = head("About Hameeda Hossain") + f"""
<section class="section"><div class="wrap two-col">
  <div class="prose about-prose">{''.join(f'<p>{E(p)}</p>' for p in about['bio'])}
    <h2>Milestones</h2>
    <ul class="timeline-mini">{''.join(f'<li>{E(m)}</li>' for m in about['milestones'])}</ul>
    <p><a class="more" href="timeline.html">Follow her life year by year →</a></p>
  </div>
  <div class="about-photos">
    <figure class="portrait"><img src="{E(about['portrait'])}" alt="Portrait of Hameeda Hossain"></figure>
    {''.join(f'<figure class="about-photo"><img src="assets/photos/thumbs/{s}.jpg" alt="{E(photo_by[s]["caption"])}" loading="lazy"><figcaption>{E(photo_by[s]["caption"])}, {E(photo_by[s]["year"])}</figcaption></figure>' for s in ['herald-tribune-pakistan-flag', 'paris-1965-cafe'] if s in photo_by)}
  </div>
</div></section>
<section class="section"><div class="wrap narrow">
  <h2 class="section-title">About this collection</h2>
  <p>This site gathers Hameeda Hossain's writings, newspaper columns, interviews, books and photographs. Essays appear in full; where a piece was first published elsewhere, its page names the original publication and links to it. Her published books are not reproduced. The <a href="books.html">Books</a> page shows where to buy or borrow them. Some dates, places and names are still being confirmed, and corrections are welcome.</p>
  {credit_html}
</div></section>"""
page("about.html", "About", body, active="about.html", description="Biography of Hameeda Hossain and about this collection.")


# ── Home ────────────────────────────────────────────────────────────────────
LEAD = "the-challenge-of-citizenship-in-building-a-just-society-bdi"
FEATURES = ["towards-tolerance-and-justice", "remembering-asma"]
NUMBERED = ["recollections-of-kormojibi-nari", "bangladesh-2006-a-human-rights-audit", "crossing-the-boundaries", "its-time-to-pay-up"]


def feat_img(w):
    return theme_image(w["theme"], w["slug"])


lead = by_slug.get(LEAD)
lead_img = image_for("photo:forum-at-the-microphone") or (feat_img(lead) if lead else None)
spread = ""
if lead:
    spread += f'''<a class="lead-story" href="writings/{lead['slug']}.html">
  {f'<span class="ls-img"><img src="{E(lead_img["src"])}" alt="{E(lead_img["alt"])}"></span><span class="ls-cap">Photograph: {E(lead_img["alt"])}, 1952</span>' if lead_img else ''}
  <span class="ls-text"><span class="kicker">{E(lead['theme'])}</span><span class="ls-title">{E(lead['title'])}</span>
  {f'<span class="ls-quote">“{E(lead["pull_quote"])}”</span>' if lead.get('pull_quote') else ''}
  <span class="ls-meta">{E(lead['pub_short'])} · {E(lead.get('year'))}</span></span></a>'''
side = []
for s in FEATURES:
    w = by_slug.get(s)
    if not w:
        continue
    im = feat_img(w)
    panel = (f'<span class="ss-img"><img src="{E(im["thumb"])}" alt="" loading="lazy"></span>' if im else
             f'<span class="ss-img ss-design motif t-{slug(w["theme"])}"><span class="ss-q">“{E(w.get("pull_quote") or w["title"])}”</span></span>')
    side.append(f'''<a class="side-story" href="writings/{w['slug']}.html">{panel}
  <span class="kicker">{E(w['theme'])}</span><span class="ss-title">{E(w['title'])}</span><span class="ss-sum">{E(w.get('summary'))}</span></a>''')
numbered = []
for n, s in enumerate(NUMBERED, 1):
    w = by_slug.get(s)
    if w:
        numbered.append(f'<li><a href="writings/{w["slug"]}.html"><span class="num">{n:02d}</span><span><span class="nt">{E(w["title"])}</span><span class="nm">{E(w["pub_short"] or w["theme"])}{" · " + E(w.get("year")) if w.get("year") else ""}</span></span></a></li>')

tiles = []
for s, t in themes_present:
    im = theme_image(t)
    tiles.append(f'''<a class="theme-tile{'' if im else f' no-img motif t-{s}'}" href="writings.html?theme={s}">{f'<img src="{E(im["thumb"])}" alt="" loading="lazy">' if im else ''}<span class="tt-shade"></span><span class="tt-text"><span class="tt-name">{E(t)}</span><span class="tt-n">{theme_counts[s]} {'piece' if theme_counts[s] == 1 else 'pieces'}</span></span></a>''')

film = [p for p in photos if p["slug"] != "portrait"][:12]
filmstrip = "".join(f'<figure><img src="assets/photos/thumbs/{p["slug"]}.jpg" alt="{E(p["caption"])}" loading="lazy"><figcaption>{E(p.get("year"))}</figcaption></figure>' for p in film)
scan_list = [(a, scans[a["href"]]) for a in sort_entries(articles) if a["href"] in scans][:6]
clips = "".join(f'<a class="clip" href="{E(a["href"])}" style="--r:{(-2.5, 1.8, -1.2, 2.4, -1.8, 1.2)[i % 6]}deg"><img src="{E(src)}" alt="" loading="lazy"><span{langattr(a["title"])}>{E(a["title"])}</span></a>' for i, (a, src) in enumerate(scan_list))
quote_w = by_slug.get("towards-tolerance-and-justice")
cover_row = "".join(f'<a class="mini-book" href="books.html#{E(b["key"])}" title="{E(b["title"])}">{book_cover(b, i)}</a>' for i, b in enumerate(books[:6]))

body = f"""
<section class="hero"><div class="wrap hero-grid">
  <div class="hero-text">
    <h1 class="display">Hameeda Hossain<span class="bn-name" lang="bn">হামিদা হোসেন</span></h1>
    <p class="lede">{E(about['hero'])}</p>
    <div class="hero-actions"><a class="btn" href="writings.html">Read her writings</a><a class="btn ghost" href="timeline.html">Her life and times</a></div>
  </div>
  <figure class="portrait"><img src="{E(about['portrait'])}" alt="Portrait of Hameeda Hossain" width="480" height="600"></figure>
</div></section>

<section class="filmstrip-band" aria-label="Photographs from her life"><div class="filmstrip">{filmstrip}</div>
  <div class="wrap"><a class="more" href="photos.html">All photographs →</a></div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><h2 class="section-title">Selected writings</h2><a class="more" href="writings.html">All {len(writings)} writings →</a></div>
  <div class="spread">
    {spread}
    <div class="side-col">{''.join(side)}</div>
  </div>
  <ol class="numbered">{''.join(numbered)}</ol>
</div></section>

{f'''<section class="quote-band"><div class="wrap"><blockquote>{E(quote_w["pull_quote"])}<cite><a href="writings/{quote_w["slug"]}.html">{E(quote_w["title"])}</a>, {E(quote_w.get("year") or "")}</cite></blockquote></div></section>''' if quote_w and quote_w.get("pull_quote") else ''}

<section class="section"><div class="wrap">
  <div class="section-head"><h2 class="section-title">Read by theme</h2></div>
  <div class="theme-grid">{''.join(tiles)}</div>
</div></section>

<section class="section tl-teaser"><div class="wrap tl-teaser-grid">
  <div><h2 class="section-title">A life in its times</h2>
  <p class="lede">From Hyderabad and Partition to Wellesley, Oxford and Dhaka; from the Liberation War to the founding of Ain o Salish Kendra and the long campaigns for women's and workers' rights.</p>
  <a class="btn" href="timeline.html">Explore the timeline</a></div>
  <div class="tl-teaser-photos">{''.join(f'<img src="assets/photos/thumbs/{s}.jpg" alt="{E(photo_by[s]["caption"])}" loading="lazy">' for s in ['with-brother-iqbal', 'herald-tribune-pakistan-flag', 'paris-1965-cafe'] if s in photo_by)}</div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><h2 class="section-title">From the newspapers</h2><a class="more" href="articles.html">All articles →</a></div>
  <div class="clips">{clips}</div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><h2 class="section-title">Books</h2><a class="more" href="books.html">All books →</a></div>
  <div class="mini-shelf">{cover_row}</div>
</div></section>"""
page("index.html", "", body, description="")


# ── Connections (demo; unlisted) ───────────────────────────────────────────
people = load("people.json", [])
if people:
    GROUPS = [("family", "Family", "#e29aa7"), ("forum-and-friends", "Forum & friends", "#d2b07a"),
              ("ask-and-rights", "ASK & human rights", "#7fb7bb"), ("movement", "Women's movement", "#e2a861"),
              ("crafts", "Crafts", "#9fc28a"), ("scholarship", "Scholarship", "#a9a2c4"), ("co-authors", "Co-authors & editors", "#8fb0e0")]
    present = [g for g in GROUPS if any(p["group"] == g[0] for p in people)]
    valid = lambda h: (h.startswith("writings/") and h[9:-5] in by_slug) or h.startswith(("books.html", "timeline.html", "photos.html"))
    for p in people:
        p["works"] = [w for w in p.get("works", []) if valid(w["href"])]
        p["links"] = [l for l in p.get("links", []) if l.get("verified", True)]
    payload = json.dumps({"groups": [{"key": k, "label": l, "color": c} for k, l, c in present],
                          "people": [{k: p.get(k) for k in ("id", "name", "group", "role", "connection", "works", "links", "related", "years")} for p in people]},
                         ensure_ascii=False).replace("</", "<\\/")
    gchips = "".join(f'<button class="chip" type="button" data-cx-group="{k}" aria-pressed="false"><span class="sw" style="--gc:{c}"></span>{E(l)}</button>' for k, l, c in present)
    lists = ""
    for k, l, c in present:
        items = "".join(f'<li class="cx-person"><a href="#{E(p["id"])}" data-open="{E(p["id"])}"><span class="nm">{E(p["name"])}</span><span class="rl">{E(p["role"])}</span></a></li>' for p in people if p["group"] == k)
        lists += f'<section class="cx-group-list"><h3 style="--gc:{c}"><span class="sw"></span>{E(l)}</h3><ul class="cx-people">{items}</ul></section>'
    body = f"""
<section class="cx-hero"><div class="wrap">
  <h1 class="page-title">Her circle</h1>
  <p class="lede">The people Dr. Hossain has lived and worked alongside: family, friends, colleagues, co-founders and co-authors. Choose a person to see how they are connected, the work they shared, and where to read more about them.</p>
</div></section>
<section class="cx-wrap"><div class="wrap">
  <div class="cx-tools">
    <div class="chips"><button class="chip" type="button" data-cx-group="all" aria-pressed="true">Everyone</button>{gchips}</div>
    <label class="search"><span class="sr-only">Find a person</span>{SEARCH_ICON}<input type="search" data-cx-search placeholder="Find a person…"></label>
  </div>
  <div class="cx-layout">
    <div class="cx-stage" role="group" aria-label="Map of people connected to Hameeda Hossain">
      <svg viewBox="0 0 1000 1000" aria-hidden="true"></svg>
      <div class="cx-core" aria-hidden="true"><span class="core-name">Hameeda Hossain</span><span class="core-sub">{len(people)} people · {len(present)} circles of work and life</span></div>
      <div class="cx-nodes"></div>
    </div>
    <aside class="cx-panel" aria-live="polite"><p class="cx-panel-empty"><strong>Choose a person</strong>Hover over a name to see their links, or click to read how they are connected to Dr. Hossain.</p></aside>
  </div>
</div></section>
<section class="cx-all"><div class="wrap"><h2 class="section-title">Everyone on the map</h2>{lists}</div></section>
<script type="application/json" id="people-data">{payload}</script>
<script src="assets/connections.js?v={ver('assets/connections.js')}" defer></script>"""
    page("connections.html", "Her circle", body, active="connections.html", description="The people connected to Hameeda Hossain: family, friends, colleagues and collaborators.")

page("404.html", "Page not found", head("This page isn't here", "It may have moved. Try the <a href='/collective/writings.html'>writings</a> or the <a href='/collective/'>home page</a>."))
print(f"Built {len(writings)} writings, {len(articles)} articles, {len(interviews)} interviews, {len(books)} books, {len(photos)} photos, {len(timeline)} timeline events; "
      f"descriptions {sum(1 for v in desc.values() if v.get('summary'))}, covers {len(covers)}, commons {len(commons)}.")
