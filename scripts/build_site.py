#!/usr/bin/env python3
"""Build the static Earthed Energy site from the live copy and the v222 guides."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
V222 = Path("/tmp/refs/v222")
BASE = "https://www.earthedenergy.au"
PHONE = "0433 839 284"
PHONE_TEL = "+61433839284"
EMAIL = "calebvears@earthedhv.au"
LICENCE = "PGE 336477"

CHB_HTML = (
    '<h2 id="cheaper-home-batteries">Cheaper Home Batteries</h2>'
    "<p>The federal Cheaper Home Batteries discount is paid as small-scale technology "
    "certificates (STCs). It comes to approximately 30% of the eligible battery cost. "
    "The exact discount varies with usable capacity and the installation date, and the "
    "rate steps down from 1 January 2027. We calculate it on your written quote. "
    "We do not publish a fixed dollar amount.</p>"
)

BAD_CHB = re.compile(
    r"6\.80|4\.08|1\.02|\$265 per kWh|\$159 per kWh|\$4,670|\$315|CHB tiers|certificates per kWh",
    re.I,
)

GROUPS = [
    ("basics", "The basics", "Start here if solar and batteries are new to you.", [
        ("what-solar-does", "What solar does", "Six plain-terms outcomes: lower bills, less grid, property value, rebates, cleaner power, 25-year panels."),
        ("what-a-battery-does", "What a battery does", "Day and night solar, less grid reliance, stop exporting for cents, blackout backup, lower bills."),
        ("reading-your-power-bill", "Reading your power bill", "The five numbers on any SA electricity bill that decide your solar design."),
        ("how-much-you-save", "How much you save", "Honest payback brackets by quarterly bill size. When solar-only makes sense and when the battery joins."),
        ("battery-sizing", "Battery sizing", "How many kWh you actually need: 40 to 70 percent of daily use, plus EV, pool and heat pump headroom."),
    ]),
    ("grid", "Your grid connection", "SA Power Networks rules that shape what we can install at your address.", [
        ("sapn-flexible-export", "SAPN flexible exports", "How the 10 kW throttle really behaves, how often it drops, and why an oversized inverter still pays."),
        ("sa-export-limits", "SA export limits", "Fixed 1.5 kW cap or flexible exports. How we check which one your address gets before we quote."),
        ("three-phase-vs-single-phase", "Three-phase vs single-phase", "How your supply changes inverter choice, export limits and battery backup."),
        ("swer-lines", "SWER lines", "Single wire earth return supplies in the Hills and rural SA, and the cap that changed in July 2025."),
        ("shade-and-roof-orientation", "Shade and roof orientation", "Trees, sun angle and roof direction on treed Hills blocks."),
        ("bushfire-prone-areas", "Bushfire prone areas", "How BAL ratings change component selection, cable routing, isolation and battery placement."),
    ]),
    ("backup", "Backup and off-grid", "What keeps running when the grid drops, and when to leave it altogether.", [
        ("outage-backup", "Outage backup", "Standard solar shuts down with the grid. Only a backup-specified battery with a wired switchboard keeps the house up."),
        ("whole-home-backup-explained", "Whole-home backup explained", "GoodWe ESA built-in transfer switch versus Sigenergy Gateway."),
        ("off-grid-vs-grid-connect", "Off-grid vs grid-connect", "Grid-connect sizes for payback. Off-grid sizes for autonomy."),
    ]),
    ("money", "Rebates and finance", "What comes off the invoice, and how people pay.", [
        ("federal-rebates-explained", "Federal rebates explained", "STCs on panels, the Cheaper Home Batteries discount on batteries, and the SA feed-in tariff."),
        ("finance-options", "Finance options", "Elevant interest-free under $10k, 28Watt for larger green loans, and how cash payment is treated."),
    ]),
    ("equipment", "Equipment", "Product lines we install, with the specs published in these guides.", [
        ("what-we-install", "What we install", "Panels, inverters, batteries, racking, cable, EV, aircon and hot water in one place."),
        ("solar-panels", "Solar panels", "Trina Vertex S+ 475 W as default, Astronergy 470 W as the budget alternative."),
        ("inverters", "Inverters", "GoodWe ESA, GoodWe ET Plus, Sigenergy SigenStor SP and TP."),
        ("battery-storage", "Batteries", "GoodWe Lynx Home and Sigenergy SigenStor BAT modules."),
        ("goodwe-vs-sigenergy", "GoodWe vs Sigenergy", "An honest comparison of the two platforms we install."),
        ("ev-charging", "EV charging", "GoodWe HCA AC charger and Sigenergy integrated DC charger."),
        ("aircon-hot-water", "Air conditioning and heat pump hot water", "Daikin reverse-cycle and Reclaim CO2 heat pump, sized to run on your solar."),
        ("racking-and-cable", "Racking and cable", "Clenergy racking, Nexans and Prysmian cable."),
        ("monitoring-apps", "Monitoring apps", "GoodWe SEMS and Sigenergy mySigen."),
    ]),
    ("process", "How we work", "From the first phone call to year seven.", [
        ("get-a-quote", "How we quote", "Free site visit, CEC-signed design and a written quote."),
        ("typical-timeline", "Typical timeline", "Realistic timing from sign day to handover."),
        ("installation-day", "Installation day", "One to two days on the roof. Who comes, what we bring, what you need to do."),
        ("commissioning-and-handover", "Commissioning and handover", "Testing, monitoring on your phone, warranty documents in hand."),
        ("warranty-and-aftercare", "Warranty and aftercare", "Workmanship, panel, inverter and battery warranties, and what happens in later years."),
        ("credentials-and-licences", "Credentials and licences", "Every accreditation, explained in plain English."),
    ]),
]

SERVICE_SLUGS = ["residential", "commercial", "off-grid"]
COMPANY_SLUGS = ["about-earthed-energy", "about-caleb-vears", "about-troy-hooker", "why-we-do-this", "earthed-history"]
CUSTOM = {"get-a-quote", "knowledge"}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def slugify(text: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return base or "section"


def normalize_href(href: str) -> str:
    href = (href or "").strip()
    if not href or href.startswith(("mailto:", "tel:", "#", "http://", "https://")):
        return href
    href = href.split("?")[0].split("#")[0]
    if not href.startswith("/"):
        href = "/" + href
    if href.endswith(".html") or "." in href.split("/")[-1]:
        return href
    href = href.rstrip("/")
    if href in ("", "/"):
        return "/"
    return href + ".html"


def esc(text: str) -> str:
    return escape(text or "", quote=True)


def ser(node) -> str:
    if isinstance(node, NavigableString):
        return escape(str(node))
    if not isinstance(node, Tag):
        return ""
    if node.name == "br":
        return " "
    if node.name == "a":
        href = normalize_href(node.get("href") or "")
        label = clean(node.get_text(" ", strip=True)).lstrip("→").strip()
        if not href or not label or href.startswith("javascript:"):
            return escape(label)
        return f'<a href="{esc(href)}">{escape(label)}</a>'
    if node.name in {"strong", "b"}:
        return "<strong>" + "".join(ser(c) for c in node.children) + "</strong>"
    if node.name in {"em", "i"}:
        return "<em>" + "".join(ser(c) for c in node.children) + "</em>"
    return "".join(ser(c) for c in node.children)


def inner_html(el: Tag) -> str:
    parts = [ser(c) for c in el.children]
    parts = [p for p in parts if p and p.strip()]
    return clean(" ".join(parts))


def is_bad_chb(text: str) -> bool:
    if not BAD_CHB.search(text):
        return False
    return bool(re.search(r"batter|CHB|certificate|kWh|rebate", text, re.I))


def prepare(path: Path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    title_m = re.search(r"<title>(.*?)</title>", raw, re.S)
    desc_m = re.search(r'<meta name="description" content="(.*?)"', raw, re.S)
    title = clean(BeautifulSoup(title_m.group(1), "html.parser").get_text()) if title_m else path.stem
    desc = clean(BeautifulSoup(desc_m.group(1), "html.parser").get_text()) if desc_m else ""
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup.find_all(["script", "style", "nav", "helmet", "template", "svg", "form", "button", "noscript"]):
        tag.decompose()
    for tag in soup.select("[data-mob-nav],[data-sticky-cta],[data-skip]"):
        tag.decompose()
    related = []
    for node in list(soup.find_all(string=lambda s: isinstance(s, str) and s.strip() == "Keep reading")):
        box = node.parent
        for _ in range(3):
            if box and box.parent and box.parent.name == "div":
                box = box.parent
            else:
                break
        if box:
            for a in box.find_all("a"):
                href = normalize_href(a.get("href") or "")
                label = clean(a.get_text(" ", strip=True)).lstrip("→").strip()
                if href and label:
                    related.append((href, label))
            box.decompose()
    for node in list(soup.find_all(string=lambda s: isinstance(s, str) and "PO Box 4111" in s)):
        box = node.parent
        for _ in range(5):
            if box and box.parent and box.parent.name == "div":
                box = box.parent
            else:
                break
        if box:
            box.decompose()
        break
    return soup, title, desc, related


def table_html(table: Tag) -> str | None:
    rows = []
    texts = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        kind = "th" if any(c.name == "th" for c in cells) and tr.find_parent("thead") or tr == table.find("tr") and all(c.name == "th" for c in cells) else "td"
        # header row if first row is all th, else td
        rendered = []
        for c in cells:
            bit = inner_html(c) or escape(clean(c.get_text(" ", strip=True)))
            texts.append(clean(c.get_text(" ", strip=True)))
            rendered.append(bit)
        rows.append((cells[0].name, rendered))
    blob = " ".join(texts)
    if is_bad_chb(blob):
        return None
    if not rows:
        return ""
    head, body = [], []
    if rows and rows[0][0] == "th":
        head = rows[0][1]
        body = [r[1] for r in rows[1:]]
    else:
        body = [r[1] for r in rows]
    parts = ['<div class="table-wrap"><table>']
    if head:
        parts.append("<thead><tr>" + "".join(f"<th>{c}</th>" for c in head) + "</tr></thead>")
    parts.append("<tbody>")
    for row in body:
        parts.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts)


def walk_blocks(soup: BeautifulSoup):
    blocks = []

    def has_structural_child(el: Tag) -> bool:
        return any(isinstance(c, Tag) and c.name in {"div", "section", "article", "ul", "ol", "table"} for c in el.children)

    def walk(el: Tag):
        if not isinstance(el, Tag):
            return
        if el.name in {"script", "style"}:
            return
        if el.name == "table":
            html = table_html(el)
            if html is None:
                blocks.append({"kind": "chb", "html": CHB_HTML, "text": "Cheaper Home Batteries"})
            elif html:
                blocks.append({"kind": "table", "html": html, "text": clean(el.get_text(" ", strip=True))})
            return
        text = clean(el.get_text(" ", strip=True))
        blocked = el.find(["h1", "h2", "h3", "h4", "p", "table", "ul", "ol", "li"])
        leafish = el.name in {"h1", "h2", "h3", "h4", "p", "li", "blockquote", "div", "span"}
        can_take = (
            leafish
            and text
            and "{{" not in text
            and not blocked
            and not has_structural_child(el)
            and (el.name in {"h1", "h2", "h3", "h4", "p", "li", "blockquote"} or len(text) >= 8)
        )
        if can_take:
            kind = el.name if el.name in {"h1", "h2", "h3", "h4", "li", "blockquote"} else "p"
            blocks.append({"kind": kind, "html": inner_html(el) or escape(text), "text": text})
            return
        for child in el.children:
            if isinstance(child, Tag):
                walk(child)

    root = soup.body or soup
    for child in list(root.children):
        if isinstance(child, Tag):
            walk(child)
    return blocks


def useful(block: dict) -> bool:
    text = block["text"]
    if block["kind"] in {"table", "chb"}:
        return True
    low = text.lower()
    if low.startswith(("ready for a real quote", "get your indicative price", "enquire today for a full assessment", "keep reading")):
        return False
    if "trading as earthed high voltage" in low and len(text) < 280:
        return False
    if text in {"Call", "Get my price"}:
        return False
    if any(token in text for token in ("PO Box 4111", "ACN 679", "ABN 99 679", "Residential 01", "Norwood South")):
        return False
    if text.startswith("Home →") or text.startswith("Home ->"):
        return False
    if block["kind"] == "p" and len(text.split()) <= 2 and not re.search(r"[\d.$]", text):
        return False
    if re.fullmatch(r"\d{1,2}", text):
        return False
    return True


def dedupe(blocks):
    seen = set()
    out = []
    for block in blocks:
        key = (block["kind"], block["text"][:180])
        if key in seen:
            continue
        seen.add(key)
        out.append(block)
    return out


def apply_chb(blocks):
    out = []
    inserted = False
    for block in blocks:
        if is_bad_chb(block["text"]):
            if not inserted:
                out.append({"kind": "chb", "html": CHB_HTML, "text": "Cheaper Home Batteries discount"})
                inserted = True
            continue
        out.append(block)
    return out


def cluster(blocks):
    out = []
    buf = []

    def flush():
        if len(buf) >= 3:
            items = "".join(f"<li>{b['html']}</li>" for b in buf)
            text = " ".join(b["text"] for b in buf)
            out.append({"kind": "ul", "html": f"<ul>{items}</ul>", "text": text})
        else:
            out.extend(buf)
        buf.clear()

    for block in blocks:
        if re.match(r"Scenario [A-C]\b", block["text"]):
            flush()
            out.append({**block, "kind": "h2"})
            continue
        short = block["kind"] == "p" and len(block["text"]) < 140 and not block["text"].endswith(".")
        if short and not block["text"].lower().startswith("cheaper home batteries"):
            buf.append(block)
        else:
            flush()
            out.append(block)
    flush()
    return out


def dedupe_chb(blocks):
    out = []
    seen = False
    for block in blocks:
        if block["kind"] == "chb" or block["text"].startswith("The federal Cheaper Home Batteries discount is paid"):
            if seen:
                continue
            seen = True
            block = {"kind": "chb", "html": CHB_HTML, "text": "Cheaper Home Batteries discount"}
        out.append(block)
    return out


def fix_levels(blocks):
    out = []
    level = 1
    for block in blocks:
        if block["kind"] in {"h1", "h2", "h3", "h4"}:
            wanted = int(block["kind"][1])
            if wanted == 1 and any(b["kind"] == "h1" for b in out):
                wanted = 2
            if wanted > level + 1:
                wanted = level + 1
            level = wanted
            block = {**block, "kind": f"h{wanted}"}
        out.append(block)
    return out


def extract(path: Path) -> dict:
    soup, raw_title, desc, related = prepare(path)
    blocks = [b for b in walk_blocks(soup) if useful(b)]
    blocks = dedupe(blocks)
    blocks = apply_chb(blocks)
    h1 = next((b["text"] for b in blocks if b["kind"] == "h1"), path.stem.replace("-", " ").title())
    kicker = ""
    body = []
    seen_h1 = False
    for block in blocks:
        if block["kind"] == "h1" and not seen_h1:
            seen_h1 = True
            continue
        if not seen_h1 and block["kind"] == "p" and len(block["text"]) < 80 and "·" in block["text"]:
            kicker = block["text"]
            continue
        body.append(block)
    lede = ""
    if body and body[0]["kind"] == "p" and len(body[0]["text"]) < 220:
        lede = body[0]["text"]
        body = body[1:]
    body = cluster(body)
    body = fix_levels(body)
    body = dedupe_chb(body)
    for block in body:
        block["html"] = (
            block["html"]
            .replace("team@earthedenergy.au", EMAIL)
            .replace("support@earthedenergy.au", EMAIL)
        )
        block["text"] = (
            block["text"]
            .replace("team@earthedenergy.au", EMAIL)
            .replace("support@earthedenergy.au", EMAIL)
        )
    if path.stem == "credentials-and-licences" and LICENCE not in " ".join(b["text"] for b in body):
        body.append({
            "kind": "p",
            "html": f"Earthed holds SA electrical contractor licence {LICENCE}.",
            "text": f"Earthed holds SA electrical contractor licence {LICENCE}.",
        })
    if is_bad_chb(desc) or "6.80" in desc or "$315" in desc:
        desc = "How the federal solar STC rebate, the Cheaper Home Batteries discount, and SA feed-in tariffs are treated on an Earthed quote."
    if path.stem == "federal-rebates-explained":
        desc = "Solar STCs, the Cheaper Home Batteries discount of about 30% via STCs (it varies by usable capacity and install date, and steps down from 1 January 2027), and the SA feed-in tariff."
    desc = desc or lede or h1
    return {
        "slug": path.stem,
        "h1": h1,
        "kicker": kicker,
        "lede": lede,
        "description": desc[:300],
        "raw_title": raw_title,
        "blocks": body,
        "related_links": related,
    }


def render_blocks(blocks) -> str:
    used = set()
    parts = []
    for block in blocks:
        kind = block["kind"]
        if kind in {"h2", "h3", "h4"}:
            hid = slugify(block["text"])
            n = hid
            i = 2
            while n in used:
                n = f"{hid}-{i}"
                i += 1
            used.add(n)
            parts.append(f'<{kind} id="{n}">{block["html"]}</{kind}>')
        elif kind in {"ul", "table", "chb"}:
            parts.append(block["html"])
        elif kind == "li":
            parts.append(f"<ul><li>{block['html']}</li></ul>")
        else:
            parts.append(f"<p>{block['html']}</p>")
    return "\n".join(parts)


def toc_for(blocks) -> str:
    items = []
    used = set()
    for block in blocks:
        if block["kind"] not in {"h2", "h3"}:
            continue
        hid = slugify(block["text"])
        n = hid
        i = 2
        while n in used:
            n = f"{hid}-{i}"
            i += 1
        used.add(n)
        cls = ' class="toc-sub"' if block["kind"] == "h3" else ""
        items.append(f'<li{cls}><a href="#{n}">{escape(block["text"])}</a></li>')
    if not items:
        return ""
    return '<nav class="toc" aria-label="On this page"><p>On this page</p><ol>' + "".join(items) + "</ol></nav>"


def local_business():
    return {
        "@context": "https://schema.org",
        "@type": ["Electrician", "LocalBusiness"],
        "name": "Earthed Energy",
        "legalName": "Earthed Energy Co Pty Ltd",
        "url": BASE + "/",
        "image": BASE + "/images/og-home.jpg",
        "logo": BASE + "/images/logo-purple.png",
        "telephone": PHONE_TEL,
        "email": EMAIL,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "26 Wanbrow Ave",
            "addressLocality": "Wattle Park",
            "addressRegion": "SA",
            "postalCode": "5066",
            "addressCountry": "AU",
        },
        "areaServed": ["Adelaide", "Adelaide Hills", "Mount Barker", "Yorke Peninsula", "Eyre Peninsula"],
        "parentOrganization": {"@type": "Organization", "name": "Earthed High Voltage", "url": "https://earthedhv.au"},
        "founder": {"@type": "Person", "name": "Caleb Vears"},
        "identifier": {"@type": "PropertyValue", "name": "SA electrical contractor licence", "value": LICENCE},
    }


def shell(title, description, path, body, active="", robots=None, jsonld=None, og_type="website", preload_hero=False):
    canonical = BASE + (path if path != "/" else "/")
    robots_tag = f'<meta name="robots" content="{esc(robots)}">' if robots else ""
    hero = '<link rel="preload" as="image" href="/images/hero-home-800.webp" imagesrcset="/images/hero-home-800.webp 800w, /images/hero-home.webp 1600w" imagesizes="(max-width: 980px) 100vw, 50vw" fetchpriority="high">' if preload_hero else ""
    ld = ""
    if jsonld:
        if isinstance(jsonld, list):
            blob = jsonld
        else:
            blob = [jsonld]
        ld = "\n".join(
            '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"
            for obj in blob
        )
    nav = [
        ("/#packages", "Packages", "packages"),
        ("/knowledge.html", "Guides", "guides"),
        ("/solarcare/", "SolarCare", "solarcare"),
        ("/get-a-quote.html", "Quote", "quote"),
        ("https://earthedhv.au/", "High Voltage", "hv"),
    ]
    links = []
    for href, label, key in nav:
        current = ' aria-current="page"' if key == active else ""
        extra = ' rel="noopener"' if href.startswith("http") else ""
        links.append(f'<a href="{href}"{current}{extra}>{label}</a>')
    links.append('<a class="btn" href="/get-a-quote.html">Book an audit</a>')
    footer = f"""
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <img class="footer-logo" src="/assets/logo-white.png" alt="Earthed Energy" width="240" height="78">
        <p>Residential solar and battery for Adelaide, the Adelaide Hills and Mount Barker. Designed and commissioned by the same people who build Earthed High Voltage projects.</p>
        <p class="licence">SA electrical contractor licence {LICENCE}</p>
      </div>
      <div>
        <h2>Visit</h2>
        <ul>
          <li><a href="/#packages">Packages</a></li>
          <li><a href="/knowledge.html">Guides</a></li>
          <li><a href="/solarcare/">SolarCare</a></li>
          <li><a href="/walkthrough/">Walkthrough</a></li>
          <li><a href="/contact.html">Contact</a></li>
        </ul>
      </div>
      <div>
        <h2>Company</h2>
        <ul>
          <li><a href="/about-earthed-energy.html">About</a></li>
          <li><a href="/about-caleb-vears.html">Caleb Vears</a></li>
          <li><a href="/about-troy-hooker.html">Troy Hooker</a></li>
          <li><a href="/credentials-and-licences.html">Licences</a></li>
          <li><a href="https://earthedhv.au/" rel="noopener">Earthed High Voltage</a></li>
        </ul>
      </div>
      <div>
        <h2>Contact</h2>
        <ul>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="tel:0433839284">{PHONE}</a></li>
          <li>26 Wanbrow Ave, Wattle Park</li>
          <li>ACN 691 065 460 · ABN 92 691 065 460</li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      <div>© 2026 Earthed Energy Co Pty Ltd · A subsidiary of Earthed High Voltage Pty Ltd</div>
      <div>Adelaide, South Australia</div>
    </div>
    <div class="sister">
      <span>Part of the Earthed group</span>
      <a href="https://earthedhv.au/" rel="noopener">High voltage, wind and BESS · earthedhv.au</a>
    </div>
  </div>
</footer>"""
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
{robots_tag}
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{esc(og_type)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{BASE}/images/og-home.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_AU">
<meta property="og:site_name" content="Earthed Energy">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#553A66">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/josefin-sans-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/open-sans-400.woff2" as="font" type="font/woff2" crossorigin>
{hero}
<link rel="stylesheet" href="/assets/css/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-inner">
    <a class="logo" href="/" aria-label="Earthed Energy home"><img src="/assets/logo-purple.webp" alt="" width="128" height="42"></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" data-nav-toggle>Menu</button>
    <nav id="site-nav" class="nav-panel" aria-label="Primary" data-nav-panel>
      {''.join(links)}
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
{footer}
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def enquiry_form():
    return f"""
<form action="https://formsubmit.co/support@earthedenergy.au" method="POST">
  <input type="hidden" name="_subject" value="New Earthed Energy Enquiry">
  <input type="hidden" name="_captcha" value="false">
  <input type="hidden" name="_template" value="table">
  <input type="hidden" name="_next" value="https://earthedenergy.au/thanks.html">
  <fieldset class="chips">
    <legend>What are you looking for?</legend>
    <label class="chip"><input type="radio" name="Looking for" value="Solar"> Solar</label>
    <label class="chip"><input type="radio" name="Looking for" value="Battery"> Battery</label>
    <label class="chip"><input type="radio" name="Looking for" value="Solar + Battery" checked> Solar + battery</label>
    <label class="chip"><input type="radio" name="Looking for" value="EV Charger"> EV charger</label>
    <label class="chip"><input type="radio" name="Looking for" value="Energy Audit Only"> Energy audit only</label>
  </fieldset>
  <div class="form-grid">
    <div class="field"><label for="f-name">Name</label><input id="f-name" name="Name" type="text" required autocomplete="name"></div>
    <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="Phone" type="tel" required autocomplete="tel" placeholder="04XX XXX XXX"></div>
    <div class="field"><label for="f-email">Email</label><input id="f-email" name="Email" type="email" required autocomplete="email"></div>
    <div class="field"><label for="f-suburb">Suburb</label><input id="f-suburb" name="Suburb" type="text" required autocomplete="address-level2" placeholder="e.g. Mount Barker"></div>
    <div class="field field-full"><label for="f-bill">Average quarterly bill</label><input id="f-bill" name="Quarterly bill" type="text" placeholder="e.g. $850 / quarter"></div>
    <div class="field field-full"><label for="f-notes">Anything we should know? <span class="fine">(optional)</span></label><textarea id="f-notes" name="Notes" rows="3" placeholder="Roof type, EV plans, backup, anything that helps us prepare."></textarea></div>
  </div>
  <p><button class="btn" type="submit">Send my enquiry</button></p>
  <p class="fine">We reply within one business day. Your details stay with Earthed.</p>
  <p class="licence">SA electrical contractor licence {LICENCE}</p>
</form>"""


TERMS = """
<div class="price-terms" id="package-terms">
  <p><strong>Package terms.</strong> The $13,999* and $19,999* figures (and the $2,999* EV charger) are indicative package prices for a straightforward single-storey home in greater Adelaide, after the rebates we are able to apply to the invoice. They are not a quotation. Roof type, switchboard condition, metering, access and the final design can change the price. Nothing is ordered until you have a written quote.</p>
</div>"""


def price(amount, label):
    return f'<p class="pkg-price"><a href="#package-terms">{amount}<span aria-hidden="true">*</span><span class="visually-hidden">, see package terms</span></a></p><p class="pkg-spec">{label}</p>'


def home_body():
    try:
        from PIL import Image
    except ImportError:
        Image = None

    def wh(rel):
        if not Image:
            return ""
        w, h = Image.open(ROOT / rel).size
        return f' width="{w}" height="{h}"'

    gallery = [
        ("images/install-fowlers-bay.jpg", "Fowlers Bay rooftop solar install", "Fowlers Bay · Coastal residential"),
        ("images/install-solax-offgrid.jpg", "Solax off-grid battery stack", "Solax off-grid · Triple power stack"),
        ("images/install-trina-475.jpg", "Trina 475 panels with a Solax inverter", "Trina 475 · Commercial Solax"),
        ("images/install-byrn-lightview.jpg", "Byrn 50kW GoodWe system at Lightview", "Byrn · 50kW GoodWe · Lightview"),
        ("images/install-victor-whes.jpg", "Victor Harbor WHES solar and battery", "Victor Harbor · WHES solar and battery"),
        ("images/install-eyre-2.jpg", "Eyre Peninsula solar install", "Eyre Peninsula"),
        ("images/install-victor-solar.jpg", "Victor Harbor solar array", "Victor Harbor · Solar"),
        ("images/install-sigen-reynella.jpg", "Sigenergy system at Reynella", "Sigen · Reynella"),
        ("images/install-foxess-paralowie.jpg", "FoxESS system at Paralowie", "FoxESS · Paralowie"),
        ("images/install-sigen-aldinga.jpg", "Sigenergy system at Aldinga", "Sigen · Aldinga"),
        ("images/install-backup-wiring.jpg", "Backup circuit wiring on a residential install", "Backup circuit wiring"),
    ]
    figures = []
    for src, alt, cap in gallery:
        figures.append(
            f'<figure class="reveal"><img src="/{src}" alt="{esc(alt)}" loading="lazy" decoding="async"{wh(src)}><figcaption>{esc(cap)}</figcaption></figure>'
        )
    guides = [
        ("/what-solar-does.html", "The basics", "What solar actually does"),
        ("/battery-sizing.html", "The basics", "How big a battery"),
        ("/sapn-flexible-export.html", "The grid", "SAPN flexible exports"),
        ("/federal-rebates-explained.html", "Rebates", "Federal rebates, without the folklore"),
        ("/whole-home-backup-explained.html", "Backup", "Whole-home backup"),
        ("/swer-lines.html", "The Hills", "SWER lines"),
    ]
    cards = "\n".join(
        f'<a class="guide-card reveal" href="{href}"><span>{esc(kicker)}</span><strong>{esc(title)}</strong></a>'
        for href, kicker, title in guides
    )
    return f"""
<section class="hero">
  <div class="hero-copy">
    <p class="eyebrow">Adelaide Hills · Mount Barker · Residential solar and battery</p>
    <h1>Solar, batteries, and the quiet kind of power.</h1>
    <p class="lede">Designed, delivered, and commissioned by South Australia's renewable energy specialists. Not a sales company that subcontracts your install.</p>
    <div class="hero-actions">
      <a class="btn" href="#audit">Book a free energy audit</a>
      <a class="btn btn-ghost" href="#packages">See the packages</a>
    </div>
    <ul class="trust">
      <li>CEC accredited</li>
      <li>SA electrical contractor {LICENCE}</li>
      <li>GoodWe ESA</li>
      <li>Adelaide owned · ACN 691 065 460</li>
    </ul>
  </div>
  <div class="hero-media">
    <img src="/images/hero-home-800.webp" srcset="/images/hero-home-800.webp 800w, /images/hero-home.webp 1600w" sizes="(max-width: 980px) 100vw, 50vw" alt="Rooftop solar on coastal homes at Fowlers Bay, installed by Earthed Energy" width="1600" height="600" fetchpriority="high" decoding="async">
  </div>
</section>

<section class="section" id="packages">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Packages</p>
      <h2>Pick the system that fits your home.</h2>
      <p>From a single-storey courtyard cottage to a commercial site running all day. We build to the house, not to a brochure.</p>
    </div>
    <div class="pkg-grid">
      <article class="pkg reveal">
        <img src="/images/card-small.webp" alt="A home battery and inverter installed in a garage" loading="lazy"{wh("images/card-small.webp")}>
        <div class="pkg-body"><h3 class="pkg-name">Small residential</h3>{price("$13,999", "6.6kW solar + 25kWh battery")}</div>
      </article>
      <article class="pkg reveal">
        <img src="/images/card-large.webp" alt="A stacked home battery system" loading="lazy"{wh("images/card-large.webp")}>
        <div class="pkg-body"><h3 class="pkg-name">Large residential</h3>{price("$19,999", "10kW solar + 50kWh battery")}</div>
      </article>
      <article class="pkg reveal">
        <img src="/images/card-ev.webp" alt="A wall-mounted home EV charger" loading="lazy"{wh("images/card-ev.webp")}>
        <div class="pkg-body"><h3 class="pkg-name">Smart EV charging</h3>{price("$2,999", "Single or three-phase · GoodWe, Tesla and others")}</div>
      </article>
      <article class="pkg reveal">
        <img src="/images/card-commercial.webp" alt="A commercial battery cabinet" loading="lazy"{wh("images/card-commercial.webp")}>
        <div class="pkg-body"><h3 class="pkg-name">Commercial cabinet</h3><p class="pkg-price"><a href="/commercial.html">POA</a></p><p class="pkg-spec">WHES PC G1 · up to 233kWh</p></div>
      </article>
    </div>
    {TERMS}
  </div>
</section>

<section class="section" id="process" style="padding-top:0">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Our approach</p>
      <h2>Five calm steps. No hard sell.</h2>
      <p>You wouldn't let a stranger build your roof. We don't think you should let one build your energy system either.</p>
    </div>
    <ol class="steps">
      <li class="step reveal"><span class="step-num">01 · Listen</span><h3>Free energy audit</h3><p>We assess your power bill with your current situation, future requirements and budget. No pressure. We listen to how you use power.</p></li>
      <li class="step reveal"><span class="step-num">02 · Design</span><h3>Home assessment</h3><p>Tailored to your needs, with finance options explained. We stay clear on each step and the process we use.</p></li>
      <li class="step reveal"><span class="step-num">03 · Approve</span><h3>Grid and rebate paperwork</h3><p>SAPN application, STC paperwork and the Cheaper Home Batteries discount. We lodge it so you are not chasing forms.</p></li>
      <li class="step reveal"><span class="step-num">04 · Install</span><h3>Installation day</h3><p>Caleb or Troy meets the crew in the morning and walks the job. We keep you posted through the day. A short power interruption is sometimes required.</p></li>
      <li class="step reveal"><span class="step-num">05 · Live</span><h3>Commissioning and care</h3><p>System tested, app paired. VPP customers and everyone else get the same technical support. We are a phone call away.</p></li>
    </ol>
  </div>
</section>

<section class="section" id="installs" style="padding-top:0">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Recent installs</p>
      <h2>Real homes. Real work.</h2>
      <p>Every photo is a system we designed, installed and commissioned ourselves, across Adelaide, Yorke Peninsula and the West Coast.</p>
    </div>
    <div class="gallery">{''.join(figures)}</div>
  </div>
</section>

<section class="band">
  <div class="wrap bess">
    <img src="/images/install-bess-portwakefield.jpg" alt="Battery energy storage equipment at the Port Wakefield site" loading="lazy"{wh("images/install-bess-portwakefield.jpg")}>
    <div>
      <p class="eyebrow">Earthed High Voltage</p>
      <h2>5MW BESS · Port Wakefield</h2>
      <p>The same hands that connect South Australian wind farms and battery sites also commission the system on your wall.</p>
      <ul class="specs">
        <li><strong>5MW</strong><span>Capacity</span></li>
        <li><strong>33kV</strong><span>Grid connection</span></li>
        <li><strong>SAPN</strong><span>Accredited</span></li>
      </ul>
      <a class="btn btn-on-dark" href="https://earthedhv.au/" rel="noopener">See it at Earthed High Voltage</a>
    </div>
  </div>
</section>

<section class="section" id="why">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Why Earthed</p>
      <h2>Three things our customers say.</h2>
    </div>
    <div class="why-grid">
      <article class="why reveal"><h3>Hand-picked, hands-on team.</h3><p>Caleb and Troy lead every job, with a tight crew of specialists. Every install is monitored through eProfiling. No call-centre brand. No revolving door of subcontractors.</p></article>
      <article class="why reveal"><h3>Warranties you can claim.</h3><p>Premium-tier products with Australian warranty service. Trina, GoodWe (including ESA), Tesla and WHES. Names that are still here in three years.</p></article>
      <article class="why reveal"><h3>Fair pricing.</h3><p>We may not be cheaper than a national solar advertisement. You do get a specialist team you can call.</p></article>
    </div>
  </div>
</section>

<section class="section" id="rebates" style="padding-top:0">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Rebates</p>
      <h2>What comes off the price.</h2>
      <p>You don't lodge the paperwork. We apply every eligible discount to the invoice. The package figures above already assume that. The final number is on your written quote.</p>
    </div>
    <div class="rebate-grid">
      <article class="rebate reveal"><p class="tag">Auto-applied · Federal solar</p><h3>STC rebate</h3><p>Small-scale Technology Certificates. We register the install with the Clean Energy Regulator and discount the certificate value off the invoice. Currently about $400/kW for SA Zone 3 on a five-year deeming period. Indicative only.</p></article>
      <article class="rebate reveal"><p class="tag">Auto-applied · Federal battery</p><h3>Cheaper Home Batteries</h3><p>The federal battery discount is paid as small-scale technology certificates (STCs). It is approximately 30% of the eligible battery cost. It varies with usable capacity and the installation date, and the rate steps down from 1 January 2027. We do not promise a fixed dollar amount.</p></article>
      <article class="rebate reveal"><p class="tag">Optional · SA Power Networks</p><h3>Virtual power plant</h3><p>Opt in to a compatible VPP and earn credits on top of bill savings. Ask which inverter and battery combinations qualify. This is separate from the federal discount.</p></article>
    </div>
    <p class="fine reveal" style="margin-top:1.5rem">Rebate values move with certificate prices and the rules on the day of installation. The figure that applies to you is the one on the written quote.</p>
  </div>
</section>

<section class="section" id="guides" style="padding-top:0">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Guides</p>
      <h2>Read it before you buy it.</h2>
      <p>Plain-language notes on bills, export limits, batteries and the Hills. Written from the installs, not from a brochure.</p>
    </div>
    <div class="guides">{cards}</div>
    <p style="margin-top:1.5rem"><a class="btn btn-ghost" href="/knowledge.html">All guides</a></p>
  </div>
</section>

<section class="section" id="people" style="padding-top:0">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">People</p>
      <h2>The same hands, on the roof and on the high-voltage sites.</h2>
      <p>Earthed Energy is the residential and commercial wing of Earthed High Voltage, the contractor behind South Australian wind farms, BESS sites and substation work.</p>
    </div>
    <div class="team-grid">
      <article class="team reveal">
        <img src="/images/caleb-windfarm.jpg" alt="Caleb Vears at a South Australian wind farm" loading="lazy"{wh("images/caleb-windfarm.jpg")}>
        <p class="role">Founder · Director</p>
        <h3>Caleb Vears</h3>
        <p>Caleb's knowledge comes from 12 years moving through South Australia's renewable industry. He partners with specialists he trusts and stays focused on the client experience.</p>
        <p>When he is not on a job, he is outside with his dog Koda, or keeping up with basketball.</p>
        <p><a href="/about-caleb-vears.html">More about Caleb</a></p>
      </article>
      <article class="team reveal">
        <img src="/images/troy.jpg" alt="Troy Hooker, Head of Electrical" loading="lazy"{wh("images/troy.jpg")}>
        <p class="role">Head of Electrical</p>
        <h3>Troy Hooker</h3>
        <p>CEC-accredited specialist with 30-plus years in South Australia's solar and battery sector, and a transmission powerline ticket. Troy walks each client through the compliance and the quality of the work.</p>
        <p>Off shift, he is at the sidelines watching his twin sons play soccer.</p>
        <p><a href="/about-troy-hooker.html">More about Troy</a></p>
      </article>
    </div>
  </div>
</section>

<section class="section" id="audit">
  <div class="wrap enquiry">
    <div>
      <p class="eyebrow">Complimentary · No obligation</p>
      <h2>Book your free home energy audit.</h2>
      <p class="lede">One of us, not a salesperson, sits with you, reviews your bills and your roof, and gives you an honest answer on what the home actually needs.</p>
      <p class="licence">SA electrical contractor licence {LICENCE}</p>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a><br><a href="tel:0433839284">{PHONE}</a></p>
    </div>
    {enquiry_form()}
  </div>
</section>
"""


def solarcare_body():
    return f"""
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">SolarCare · Adelaide's eastern suburbs</p>
    <h1>Cleaned by electricians, not window washers.</h1>
    <p class="lede">Every SolarCare visit is a pure-water panel clean plus a licensed electrician's health assessment of your system. No cleaning company in Adelaide can offer the second half.</p>
    <p>Panel cleaning. Bird proofing. And with every full service, a home energy audit, free for our first thirty customers.</p>
    <div class="hero-actions">
      <a class="btn" href="tel:0433839284">Call Caleb · {PHONE}</a>
      <a class="btn btn-ghost" href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
    <p class="fine">No call centre. No sales script. You speak to the electrician who does the work.</p>
    <p class="licence">SA electrical contractor licence {LICENCE}</p>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    <p class="eyebrow">What we do</p>
    <div class="why-grid">
      <article class="why">
        <h2>Panel clean and health check</h2>
        <p>A deionised-water clean, no chemicals, no pressure, warranty-safe, with a full visual inspection, isolator and cabling condition check, inverter error-log review, and a generation reading before and after.</p>
        <p>You receive a photo condition report the same day. If we find a cracked isolator or a hotspot cell, you will know precisely what it is and what it costs to fix.</p>
        <p><a href="/solarcare/brochures/EE-Brochure-01-Panel-Cleaning-Service.pdf">Download the panel cleaning brochure (PDF)</a></p>
      </article>
      <article class="why">
        <h2>Bird proofing</h2>
        <p>UV-stabilised mesh fitted around the array perimeter with stainless clips. No drilling, no warranty risk. Nest and fouling removal with sanitising where droppings sit under the panels.</p>
        <p>Pigeons establish under arrays in late winter and early spring. Proofing now is easier than evicting them in October.</p>
        <p><a href="/solarcare/brochures/EE-Brochure-02-Bird-Proofing-Service.pdf">Download the bird proofing brochure (PDF)</a></p>
      </article>
      <article class="why">
        <h2>Two-storey homes welcome</h2>
        <p>Most cleaners won't do them. We work at heights for a living, on substations, with harnesses and rated anchors, and we bring the same discipline to your roof.</p>
        <h3>The honest winter numbers</h3>
        <p>An Adelaide roof produces roughly a third as much in winter as in summer. Soiling typically costs 3–5% of output, more under bird fouling or lichen, which rain does not remove. A properly cleaned 10 kW system recovers in the order of 250–400 kWh a year, worth roughly $100–$200. Others promise 30% more output. We won't, because it isn't true.</p>
      </article>
    </div>
  </div>
</section>
<section class="band">
  <div class="wrap narrow">
    <p class="eyebrow">The full service</p>
    <h2>Book a clean and bird-proofing together, and we will audit your whole home's energy, free.</h2>
    <p>While we are on your roof, a licensed electrician walks your switchboard, your tariff, your usage and your appliances, and tells you plainly where the money is going and what is worth changing. No obligation follows it.</p>
    <p>The audit is free for our first 30 full-service customers. After that, it is quoted like everything else.</p>
    <a class="btn btn-on-dark" href="tel:0433839284">Claim one of the thirty · {PHONE}</a>
  </div>
</section>
<section class="section" id="pricing">
  <div class="wrap">
    <p class="eyebrow">Pricing</p>
    <h2>Every price includes the electrician's assessment.</h2>
    <p>Same-day condition report included. All prices ex GST.</p>
    <div class="table-wrap">
      <table class="table">
        <thead><tr><th>System size</th><th>Single storey</th><th>Two storey</th></tr></thead>
        <tbody>
          <tr><td>Up to 12 panels (~5 kW)</td><td>$220</td><td>$280</td></tr>
          <tr><td>13–24 panels (~6.6–10 kW)</td><td>$290</td><td>$360</td></tr>
          <tr><td>25–36 panels (~13–15 kW)</td><td>$360</td><td>$440</td></tr>
          <tr><td>37–48 panels</td><td>$430</td><td>$520</td></tr>
          <tr><td>49+ / commercial</td><td>$9 / panel</td><td>$11 / panel (min $520)</td></tr>
        </tbody>
      </table>
    </div>
    <div class="extras">
      <article><h3>Bird proofing</h3><p>From $450 for a typical 6.6 kW array. Larger perimeters quoted on the roof.</p></article>
      <article><h3>SolarCare+ · add $180</h3><p>Thermal imaging, string voltage tests, torque and earthing checks, written defect register.</p></article>
      <article><h3>While we're up there</h3><p>Gutter clean $140 single storey, $180 two storey. Nest removal and sanitise $90. Repairs quoted.</p></article>
      <article><h3>Plans</h3><p>Annual clean and check, 10% off. Autumn and spring visits, 15% off. The correct science.</p></article>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap narrow">
    <h2>A share of every SolarCare visit funds the System of Love.</h2>
    <p>For every one hundred panels we install across this community, ten are donated, fully installed, fully warranted, to a South Australian family who could not otherwise afford solar. Your clean helps put panels on a roof that needs them.</p>
  </div>
</section>
"""


def quote_body(article: dict | None):
    prose = ""
    if article and article["blocks"]:
        prose = f"""<section class="section" style="padding-top:0"><div class="wrap article-grid solo"><div class="prose">{render_blocks(article['blocks'])}</div></div></section>"""
    return f"""
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Quote · No obligation</p>
    <h1>A written quote, after we have seen the house.</h1>
    <p class="lede">Tell us a little here. One of us comes out, reviews the bills and the roof, and sends a written quote. The package prices below are a starting point, not the quote.</p>
    <p class="licence">SA electrical contractor licence {LICENCE}</p>
  </div>
</section>
<section class="section" id="packages" style="padding-top:0">
  <div class="wrap">
    <div class="pkg-grid">
      <article class="pkg"><div class="pkg-body"><h2 class="pkg-name">Small residential</h2>{price("$13,999", "6.6kW solar + 25kWh battery")}</div></article>
      <article class="pkg"><div class="pkg-body"><h2 class="pkg-name">Large residential</h2>{price("$19,999", "10kW solar + 50kWh battery")}</div></article>
      <article class="pkg"><div class="pkg-body"><h2 class="pkg-name">Smart EV charging</h2>{price("$2,999", "Single or three-phase")}</div></article>
      <article class="pkg"><div class="pkg-body"><h2 class="pkg-name">Commercial</h2><p class="pkg-price">POA</p><p class="pkg-spec">Scoped to the site</p></div></article>
    </div>
    {TERMS}
    <p class="fine">The federal Cheaper Home Batteries discount is approximately 30% via STCs. It varies with usable capacity and install date, and steps down from 1 January 2027. Your quote shows the figure that applies. We do not lock a dollar amount on this page.</p>
  </div>
</section>
{prose}
<section class="section" id="audit">
  <div class="wrap enquiry">
    <div>
      <h2>Send the enquiry.</h2>
      <p>We reply within one business day.</p>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a><br><a href="tel:0433839284">{PHONE}</a><br>26 Wanbrow Ave, Wattle Park</p>
      <p class="licence">SA electrical contractor licence {LICENCE}</p>
    </div>
    {enquiry_form()}
  </div>
</section>
"""


def contact_body():
    return f"""
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Contact</p>
    <h1>Talk to Caleb.</h1>
    <p class="lede">Residential solar, batteries and SolarCare for Adelaide, the Adelaide Hills and Mount Barker. High-voltage and utility work lives at Earthed High Voltage.</p>
  </div>
</section>
<section class="section" id="audit" style="padding-top:0">
  <div class="wrap enquiry">
    <div>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p><a href="tel:0433839284">{PHONE}</a></p>
      <p>26 Wanbrow Ave, Wattle Park SA 5066</p>
      <p>Earthed Energy Co Pty Ltd<br>ACN 691 065 460 · ABN 92 691 065 460</p>
      <p class="licence">SA electrical contractor licence {LICENCE}</p>
      <p><a href="https://earthedhv.au/" rel="noopener">Utility, wind and BESS enquiries · earthedhv.au</a></p>
    </div>
    {enquiry_form()}
  </div>
</section>
"""


def thanks_body():
    return f"""
<section class="page-hero">
  <div class="wrap narrow">
    <p class="eyebrow">Enquiry received</p>
    <h1>Assessment request received.</h1>
    <p class="lede">Thank you for getting in touch. We'll review your property details and be in contact within one business day.</p>
    <p>In the meantime, call us on <a href="tel:0433839284">{PHONE}</a>.</p>
    <p><a class="btn" href="/">Back to Earthed Energy</a></p>
  </div>
</section>
"""


def missing_body():
    return """
<section class="page-hero">
  <div class="wrap narrow">
    <p class="eyebrow">404</p>
    <h1>Page not found.</h1>
    <p class="lede">That address isn't on this site. The guides are indexed, if you were looking for one.</p>
    <p><a class="btn" href="/">Back to Earthed Energy</a> <a class="btn btn-ghost" href="/knowledge.html">Browse the guides</a></p>
  </div>
</section>
"""


def walkthrough_body():
    return f"""
<section class="walk-hero">
  <div class="wrap">
    <p class="eyebrow">Earthed Energy · South Australia</p>
    <h1>An energy broker that cares.</h1>
    <p class="lede">Design, install, and ongoing management walked through with you. Own it outright, finance it, or roll it into an Earthed Power Pass. We take on a small number of clients, with one job: designing the system that actually fits your home, then managing it to get the most out of it.</p>
    <p><a class="btn" href="#quote">Start the walkthrough</a></p>
    <ul class="trust">
      <li>CEC accredited</li>
      <li>SAA switching</li>
      <li>SAPN approved</li>
      <li>NETCC approved seller</li>
      <li>SA electrical contractor {LICENCE}</li>
    </ul>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap">
    <p class="eyebrow">The Earthed difference</p>
    <h2>Engineered specifically for your home.</h2>
    <div class="walk-grid">
      <article class="why"><h3>01 · Designed, not sold.</h3><p>We don't sell what's on the shelf. Each design starts with your roof, your bill, your future, then matches the hardware to that brief. Tesla, Sungrow, GoodWe, Trina, Risen. The system fits you.</p></article>
      <article class="why"><h3>02 · Three ways to own it.</h3><p>Pay outright. Spread it across finance. Or roll it into an Earthed Power Pass, a managed agreement where you keep the energy benefit without the upfront.</p></article>
      <article class="why"><h3>03 · A short list by design.</h3><p>A handful of clients each cycle. Every system gets the same hand-built install, the same compliance pack, the same person answering the phone six months later.</p></article>
    </div>
    <figure class="walk-photo"><img src="/images/walkthrough-collage.webp" alt="A collage of Earthed Energy residential solar and battery installations" width="1600" height="900" loading="lazy"></figure>
  </div>
</section>
<section class="section" id="quote" style="padding-top:0">
  <div class="wrap narrow">
    <p class="quote-eyebrow eyebrow">Five questions · 30 seconds</p>
    <h2 class="quote-title">Let's start the walkthrough.</h2>
    <div class="progress-track"><div class="progress-fill" id="progress"></div></div>
    <form id="quoteForm" action="https://formspree.io/f/xlgybzag" method="POST">
      <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
      <input type="hidden" name="_subject" value="New Earthed Energy walkthrough request">
      <div class="step-pane active" data-step="1">
        <p class="eyebrow">01 / 05 · Power bill</p>
        <h3>What's your average quarterly power bill?</h3>
        <div class="options">
          <button type="button" class="option" data-val="$300–$600 / quarter">$300 – $600</button>
          <button type="button" class="option" data-val="$600–$900 / quarter">$600 – $900</button>
          <button type="button" class="option" data-val="$900–$1,500 / quarter">$900 – $1,500</button>
          <button type="button" class="option" data-val="$1,500+ / quarter">$1,500 or more</button>
          <button type="button" class="option" data-val="Not sure">Not sure</button>
        </div>
        <input type="hidden" name="01_power_bill" id="ans1">
        <div class="nav-row"><button type="button" class="btn-next" id="next1" disabled onclick="nextStep(1)">Continue</button></div>
      </div>
      <div class="step-pane" data-step="2">
        <p class="eyebrow">02 / 05 · What you're after</p>
        <h3>What are you looking at?</h3>
        <div class="options">
          <button type="button" class="option" data-val="Solar + battery (new system)">Solar + battery (new system)</button>
          <button type="button" class="option" data-val="Battery only (already have solar)">Battery only (already have solar)</button>
          <button type="button" class="option" data-val="Replacing an old system">Replacing an old system</button>
          <button type="button" class="option" data-val="Earthed Power Pass · managed">Earthed Power Pass · managed</button>
          <button type="button" class="option" data-val="Just looking">Just having a look</button>
        </div>
        <input type="hidden" name="02_interest" id="ans2">
        <div class="nav-row"><button type="button" class="btn-back" onclick="prevStep(2)">Back</button><button type="button" class="btn-next" id="next2" disabled onclick="nextStep(2)">Continue</button></div>
      </div>
      <div class="step-pane" data-step="3">
        <p class="eyebrow">03 / 05 · Roof</p>
        <h3>What kind of roof?</h3>
        <div class="options">
          <button type="button" class="option" data-val="Tin / metal">Tin / metal</button>
          <button type="button" class="option" data-val="Tile">Tile</button>
          <button type="button" class="option" data-val="Flat / low-pitch">Flat / low-pitch</button>
          <button type="button" class="option" data-val="Mixed / not sure">Mixed or not sure</button>
        </div>
        <input type="hidden" name="03_roof" id="ans3">
        <div class="nav-row"><button type="button" class="btn-back" onclick="prevStep(3)">Back</button><button type="button" class="btn-next" id="next3" disabled onclick="nextStep(3)">Continue</button></div>
      </div>
      <div class="step-pane" data-step="4">
        <p class="eyebrow">04 / 05 · Location</p>
        <h3>What's your postcode?</h3>
        <div class="field">
          <label class="input-label" for="ans4">SA postcode</label>
          <input class="input-field" type="tel" inputmode="numeric" pattern="5[0-9]{{3}}" maxlength="4" name="04_postcode" id="ans4" placeholder="e.g. 5066" oninput="validatePostcode()" autocomplete="postal-code">
          <p class="input-error" id="err4">SA postcodes only. Must start with 5.</p>
        </div>
        <div class="nav-row"><button type="button" class="btn-back" onclick="prevStep(4)">Back</button><button type="button" class="btn-next" id="next4" disabled onclick="nextStep(4)">Continue</button></div>
      </div>
      <div class="step-pane" data-step="5">
        <p class="eyebrow">05 / 05 · Contact</p>
        <h3>How should we reach you?</h3>
        <div class="field"><label class="input-label" for="ansName">First name</label><input class="input-field" type="text" name="05_name" id="ansName" autocomplete="given-name" oninput="validateContact()"></div>
        <div class="field"><label class="input-label" for="ansEmail">Email</label><input class="input-field" type="email" name="05_email" id="ansEmail" autocomplete="email" oninput="validateContact()"></div>
        <div class="field"><label class="input-label" for="ansPhone">Mobile</label><input class="input-field" type="tel" name="05_phone" id="ansPhone" autocomplete="tel" oninput="validateContact()"><p class="input-error" id="errContact">Please fill all three so we can get back to you.</p></div>
        <div class="nav-row"><button type="button" class="btn-back" onclick="prevStep(5)">Back</button><button type="submit" class="btn-next" id="submitBtn" disabled>Send walkthrough request</button></div>
      </div>
    </form>
    <div class="thanks-pane" id="thanks">
      <h2>Walkthrough requested.</h2>
      <p>We've got your details. The next step is a call to talk through the right system for your home. No rush, no quota.</p>
      <p>Caleb or Troy will be in touch within 24 hours. Industry's tight. We're different.</p>
      <p>Caleb · {PHONE}<br>Troy · 0400 254 124<br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p class="licence">SA electrical contractor licence {LICENCE}</p>
    </div>
  </div>
</section>
<script>
let current = 1;
const total = 5;
document.querySelectorAll('.option').forEach(btn => {{
  btn.addEventListener('click', function() {{
    const step = this.closest('.step-pane').dataset.step;
    this.closest('.options').querySelectorAll('.option').forEach(o => o.classList.remove('selected'));
    this.classList.add('selected');
    document.getElementById('ans' + step).value = this.dataset.val;
    document.getElementById('next' + step).disabled = false;
  }});
}});
function nextStep(from) {{
  if (from < total) {{
    document.querySelector('.step-pane[data-step="' + from + '"]').classList.remove('active');
    current = from + 1;
    document.querySelector('.step-pane[data-step="' + current + '"]').classList.add('active');
    updateProgress();
  }}
}}
function prevStep(from) {{
  if (from > 1) {{
    document.querySelector('.step-pane[data-step="' + from + '"]').classList.remove('active');
    current = from - 1;
    document.querySelector('.step-pane[data-step="' + current + '"]').classList.add('active');
    updateProgress();
  }}
}}
function updateProgress() {{
  document.getElementById('progress').style.width = (current / total * 100) + '%';
}}
function validatePostcode() {{
  const val = document.getElementById('ans4').value;
  const err = document.getElementById('err4');
  const btn = document.getElementById('next4');
  if (/^5[0-9]{{3}}$/.test(val)) {{ err.classList.remove('show'); btn.disabled = false; }}
  else {{ if (val.length >= 4) err.classList.add('show'); btn.disabled = true; }}
}}
function validateContact() {{
  const name = document.getElementById('ansName').value.trim();
  const email = document.getElementById('ansEmail').value.trim();
  const phone = document.getElementById('ansPhone').value.trim();
  const btn = document.getElementById('submitBtn');
  const validEmail = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email);
  const validPhone = phone.replace(/\\s/g, '').length >= 8;
  btn.disabled = !(validEmail && validPhone && name.length >= 2);
}}
document.getElementById('quoteForm').addEventListener('submit', function(e) {{
  e.preventDefault();
  const form = e.target;
  const data = new FormData(form);
  fetch(form.action, {{ method: 'POST', body: data, headers: {{ 'Accept': 'application/json' }} }})
    .then(() => showThanks()).catch(() => showThanks());
}});
function showThanks() {{
  document.getElementById('quoteForm').style.display = 'none';
  document.querySelector('.progress-track').style.display = 'none';
  document.querySelector('.quote-eyebrow').style.display = 'none';
  document.querySelector('.quote-title').style.display = 'none';
  document.getElementById('thanks').classList.add('active');
}}
</script>
"""


def article_page(article, group_label, siblings):
    toc = toc_for(article["blocks"])
    solo = "" if toc else " solo"
    related = []
    seen = set()
    for href, label in article["related_links"]:
        if href not in seen:
            related.append((href, label))
            seen.add(href)
    for href, label in siblings:
        if href not in seen and len(related) < 3:
            related.append((href, label))
            seen.add(href)
    rel_html = ""
    if related:
        cards = "".join(
            f'<a class="guide-card" href="{esc(href)}"><span>Related</span><strong>{escape(label)}</strong></a>'
            for href, label in related[:3]
        )
        rel_html = f'<section class="related"><div class="wrap"><h2>Keep reading</h2><div class="related-grid">{cards}</div></div></section>'
    kicker = article["kicker"] or group_label
    lede = f'<p class="lede">{escape(article["lede"])}</p>' if article["lede"] else ""
    crumbs = f'<p class="crumbs"><a href="/">Home</a> · <a href="/knowledge.html">Guides</a> · {escape(article["h1"])}</p>'
    desc = article["description"]
    if len(desc) > 170:
        desc = desc[:167].rsplit(" ", 1)[0] + "."
    body = f"""
<section class="article-hero">
  <div class="wrap">
    {crumbs}
    <p class="eyebrow">{escape(kicker)}</p>
    <h1>{escape(article["h1"])}</h1>
    {lede}
  </div>
</section>
<div class="wrap article-grid{solo}">
  {toc}
  <article class="prose">
    {render_blocks(article["blocks"])}
    <p class="fine">Figures in these guides are indicative. The price, and any rebate, that applies to your house is the one on the written quote.</p>
  </article>
</div>
{rel_html}
"""
    path = f"/{article['slug']}.html"
    crumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": BASE + "/knowledge.html"},
            {"@type": "ListItem", "position": 3, "name": article["h1"], "item": BASE + path},
        ],
    }
    article_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["h1"],
        "description": desc,
        "mainEntityOfPage": BASE + path,
        "author": {"@type": "Organization", "name": "Earthed Energy", "url": BASE + "/"},
        "publisher": {"@type": "Organization", "name": "Earthed Energy", "logo": {"@type": "ImageObject", "url": BASE + "/images/logo-purple.png"}},
    }
    html = shell(
        f"{article['h1']} — Earthed Energy",
        desc,
        path,
        body,
        active="guides",
        jsonld=[crumb_ld, article_ld],
        og_type="article",
    )
    (ROOT / f"{article['slug']}.html").write_text(html, encoding="utf-8")
    return path


def knowledge_body(catalog):
    filter_buttons = ['<button type="button" data-kb-filter="all" aria-pressed="true">All</button>']
    groups_html = []
    for gid, label, blurb, items in catalog:
        filter_buttons.append(f'<button type="button" data-kb-filter="{gid}" aria-pressed="false">{escape(label)}</button>')
        lis = []
        for slug, title, summary in items:
            search = escape(f"{title} {summary} {label}".lower())
            lis.append(
                f'<li data-kb-item data-cat="{gid}" data-search="{search}"><a href="/{slug}.html"><strong>{escape(title)}</strong><span>{escape(summary)}</span></a></li>'
            )
        groups_html.append(
            f'<section class="kb-group" data-kb-group><p class="eyebrow">{escape(label)}</p><h2>{escape(label)}</h2><p>{escape(blurb)}</p><ul class="kb-list">{"".join(lis)}</ul></section>'
        )
    return f"""
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Knowledge</p>
    <h1>Guides for South Australian homes.</h1>
    <p class="lede">Bills, export limits, batteries, backup and the way we install. Search or filter. Nothing here is a quote.</p>
    <div class="kb-tools">
      <div class="field" style="flex:1;min-width:min(100%,240px)">
        <label for="kb-search">Search guides</label>
        <input id="kb-search" type="search" data-kb-search placeholder="Try battery, export, Hills, GoodWe">
      </div>
      <div class="filters" role="group" aria-label="Filter by category">{''.join(filter_buttons)}</div>
    </div>
    <p class="kb-empty fine" data-kb-empty>No guides match that search. Try a shorter word, or show all.</p>
    {''.join(groups_html)}
  </div>
</section>
"""


def build_catalog(articles):
    catalog = []
    known = set()
    for gid, label, blurb, items in GROUPS:
        kept = []
        for slug, title, summary in items:
            known.add(slug)
            if slug == "get-a-quote" or slug in articles or (ROOT / f"{slug}.html").exists() or (V222 / f"{slug}.html").exists():
                kept.append((slug, title, summary))
        catalog.append((gid, label, blurb, kept))
    services = []
    company = []
    for slug, article in articles.items():
        if slug in known or slug in CUSTOM:
            continue
        summary = article["lede"] or article["description"]
        summary = clean(summary)[:180]
        title = article["h1"]
        if slug in SERVICE_SLUGS:
            services.append((slug, title, summary))
        else:
            company.append((slug, title, summary))
    if services:
        catalog.append(("services", "Services", "Residential, commercial and off-grid, in the same voice as the guides.", services))
    if company:
        catalog.append(("company", "The company", "Who does the work.", company))
    return catalog


def siblings_for(slug, catalog):
    for gid, label, blurb, items in catalog:
        slugs = [s for s, _, _ in items]
        if slug in slugs:
            out = []
            for s, title, _ in items:
                if s != slug:
                    out.append((f"/{s}.html", title))
            return label, out
    return "Guides", []


def write_sitemap(paths):
    urls = ["/", "/solarcare/", "/walkthrough/", "/knowledge.html", "/get-a-quote.html", "/contact.html", "/thanks.html"]
    for path in paths:
        if path not in urls:
            urls.append(path)
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path in urls:
        loc = BASE + (path if path != "/" else "/")
        priority = "1.0" if path == "/" else "0.6" if path == "/thanks.html" else "0.8"
        body.append(f"<url><loc>{escape(loc)}</loc><lastmod>2026-10-30</lastmod><changefreq>monthly</changefreq><priority>{priority}</priority></url>")
    body.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(body) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /thanks.html\n\nSitemap: https://www.earthedenergy.au/sitemap.xml\n",
        encoding="utf-8",
    )


def main():
    sources = sorted(p for p in V222.glob("*.html") if p.stem not in {"index", "knowledge"})
    articles = {}
    for path in sources:
        if path.stem == "get-a-quote":
            continue
        articles[path.stem] = extract(path)
    quote_article = extract(V222 / "get-a-quote.html") if (V222 / "get-a-quote.html").exists() else None
    catalog = build_catalog(articles)
    written = []
    for slug, article in articles.items():
        label, sibs = siblings_for(slug, catalog)
        written.append(article_page(article, label, sibs))

    pages = {
        "index.html": ("/", "Earthed Energy — Adelaide's Boutique Energy Installers", "Residential solar and battery for Adelaide, the Adelaide Hills and Mount Barker. Designed and commissioned by Earthed Energy, not subcontracted.", home_body(), "", local_business(), True),
        "knowledge.html": ("/knowledge.html", "Guides — Earthed Energy", "Plain-language guides to solar, batteries, SA Power Networks export limits, rebates and backup for South Australian homes.", knowledge_body(catalog), "guides", None, False),
        "contact.html": ("/contact.html", "Contact — Earthed Energy", "Call Caleb Vears on 0433 839 284 or email calebvears@earthedhv.au. SA electrical contractor licence PGE 336477. Wattle Park, Adelaide.", contact_body(), "quote", local_business(), False),
        "get-a-quote.html": ("/get-a-quote.html", "Get a quote — Earthed Energy", "Book a free home energy audit. Indicative packages from $13,999 and $19,999 with the terms beside the price. Licence PGE 336477.", quote_body(quote_article), "quote", local_business(), False),
        "thanks.html": ("/thanks.html", "Thank you — Earthed Energy", "Your Earthed Energy enquiry has been received.", thanks_body(), "", None, False),
        "404.html": ("/404.html", "Page not found — Earthed Energy", "That page is not on the Earthed Energy site.", missing_body(), "", None, False),
    }
    (ROOT / "solarcare").mkdir(exist_ok=True)
    (ROOT / "walkthrough").mkdir(exist_ok=True)
    (ROOT / "solarcare" / "index.html").write_text(shell(
        "Earthed SolarCare — Panel cleaning and bird proofing, Adelaide",
        "Solar panel cleaning with a licensed electrician's health assessment, plus bird proofing, for Adelaide's eastern suburbs. SA contractor licence PGE 336477.",
        "/solarcare/",
        solarcare_body(),
        active="solarcare",
    ), encoding="utf-8")
    (ROOT / "walkthrough" / "index.html").write_text(shell(
        "Walkthrough — Earthed Energy",
        "A short walkthrough for a home energy system. Cash, finance, or Earthed Power Pass. A small list of South Australian homes.",
        "/walkthrough/",
        walkthrough_body(),
    ), encoding="utf-8")
    for filename, (path, title, desc, body, active, ld, hero) in pages.items():
        robots = "noindex" if filename in {"thanks.html", "404.html"} else None
        (ROOT / filename).write_text(shell(title, desc, path, body, active=active, robots=robots, jsonld=ld, preload_hero=hero), encoding="utf-8")
        if filename not in {"404.html"}:
            written.append(path if filename != "index.html" else "/")
    write_sitemap(written)
    print(f"Wrote {len(articles)} guides and core pages")
    # compliance scan
    banned = ["Boston", "Chicago", "6.80", "$315", "$4,670", "ACN 679", "PO Box 4111"]
    bad_hits = []
    for html in ROOT.glob("*.html"):
        text = html.read_text(encoding="utf-8", errors="replace")
        for word in banned:
            if word in text:
                bad_hits.append(f"{html.name}: {word}")
    for folder in ("solarcare", "walkthrough"):
        for html in (ROOT / folder).glob("*.html"):
            text = html.read_text(encoding="utf-8", errors="replace")
            for word in banned:
                if word in text:
                    bad_hits.append(f"{folder}/{html.name}: {word}")
    if bad_hits:
        print("COMPLIANCE HITS")
        print("\n".join(bad_hits))
        raise SystemExit(1)
    quote = (ROOT / "get-a-quote.html").read_text(encoding="utf-8")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if "Package terms" not in home or "Package terms" not in quote:
        raise SystemExit("package terms missing")
    if LICENCE not in home or LICENCE not in quote or LICENCE not in (ROOT / "contact.html").read_text():
        raise SystemExit("licence missing")
    print("compliance scan clean")


if __name__ == "__main__":
    main()
