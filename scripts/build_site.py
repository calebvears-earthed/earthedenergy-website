#!/usr/bin/env python3
"""Assemble the Earthed Energy site from expanded mockups.

Shared partials live here: header, mobile nav, sticky CTA, footer legal line,
partner strip and the how-we-quote stub. Run scripts/expand_all.mjs first.
"""

from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPANDED = ROOT / "build" / "expanded"
BASE = "https://www.earthedenergy.au"
EMAIL = "calebvears@earthedhv.au"
LEGAL = "Earthed High Voltage Pty Ltd (ABN 99 679 180 879) trading as Earthed Energy Co"
PHONE_TEL = "0433839284"

NAV = [
    ("residential", "/residential.html", "Residential"),
    ("commercial", "/commercial.html", "Commercial"),
    ("off-grid", "/off-grid.html", "Off-grid"),
    ("knowledge", "/knowledge.html", "Knowledge"),
    ("about", "/about-earthed-energy.html", "About"),
]


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def header_html(section: str, *, home: bool) -> str:
    """Desktop header: right-aligned links, sister site, bordered quote, like earthedhv.au."""
    links = []
    for key, href, label in NAV:
        current = ' aria-current="page"' if key == section else ""
        links.append(f'<a href="{href}"{current}>{label}</a>')
    logo = "" if home else (
        '<a class="ee-logo" href="/" aria-label="Earthed Energy home">'
        '<img src="/images/earthed-energy-logo-purple.webp" alt="" width="1234" height="329"></a>'
    )
    quote_current = ' aria-current="page"' if section == "quote" else ""
    return (
        f'<header class="ee-header">{logo}'
        f'<nav class="ee-links" aria-label="Primary">{"".join(links)}</nav>'
        f'<a class="ee-sister" href="https://earthedhv.au">Earthed High Voltage</a>'
        f'<a class="ee-cta" href="/get-a-quote.html"{quote_current}>Get a quote</a>'
        f"</header>"
    )


def mobile_nav_html(section: str) -> str:
    """Sticky mobile bar from the mockups, with the sister-site link in the drawer."""
    items = []
    for key, href, label in NAV:
        current = ' aria-current="page"' if key == section else ""
        items.append(f'<a href="{href}"{current}>{label}</a>')
    items.append('<a href="https://earthedhv.au">Earthed High Voltage</a>')
    quote_current = ' aria-current="page"' if section == "quote" else ""
    items.append(f'<a href="/get-a-quote.html"{quote_current}>Get a quote</a>')
    return (
        '<nav class="ee-mob" aria-label="Primary mobile">'
        '<a class="ee-mob-logo" href="/" aria-label="Earthed Energy home">'
        '<img src="/images/earthed-energy-logo-white.webp" alt="" width="1234" height="329"></a>'
        '<div class="ee-mob-tools">'
        f'<a class="ee-iconbtn" href="tel:{PHONE_TEL}" aria-label="Call 0433 839 284">☎</a>'
        '<button class="ee-iconbtn" type="button" data-ee-menu aria-expanded="false" aria-controls="ee-drawer">MENU</button>'
        "</div>"
        f'<div class="ee-drawer" id="ee-drawer" hidden>{"".join(items)}</div>'
        "</nav>"
    )


def sticky_cta_html() -> str:
    return (
        '<div class="ee-sticky-cta">'
        f'<a href="tel:{PHONE_TEL}">Call</a>'
        '<a href="/get-a-quote.html">Get my price · 45 sec</a>'
        "</div>"
    )


def partner_strip_html() -> str:
    """Logos only. No accreditation wording beside them."""
    logos = [
        ("/images/partner-solar-accred.webp", "Solar Accreditation Australia"),
        ("/images/partner-nec-seller.webp", "New Energy Tech"),
        ("/images/partner-28watt.webp", "28Watt"),
        ("/images/partner-greendeal.webp", "GreenDeal"),
        ("/images/partner-elevant.webp", "Elevant"),
    ]
    imgs = "".join(
        f'<img src="{src}" alt="" width="120" height="32" loading="lazy" decoding="async">'
        for src, _name in logos
    )
    return f'<div class="ee-partners" aria-hidden="true">{imgs}</div>'


def apply_compliance(text: str, *, strict: bool) -> str:
    text = (
        text.replace("team@earthedenergy.au", EMAIL)
        .replace("home@earthedenergy.au", EMAIL)
        .replace("support@earthedenergy.au", EMAIL)
        .replace("caleb@earthedhv.au", EMAIL)
    )
    if not strict:
        return text
    text = text.replace("We moved from 7 to 10 years on workmanship in 2026. ", "")
    text = text.replace("10-year Earthed workmanship", "7-year Earthed workmanship")
    text = re.sub(r"(Earthed workmanship</td><td[^>]*>)10 years", r"\g<1>7 years", text)
    text = text.replace("10-year workmanship", "7-year workmanship")
    text = text.replace("10-yr workmanship", "7-yr workmanship")
    text = text.replace("CEC-accredited designer", "designer")
    text = text.replace("CEC-Accredited Designer", "Designer")
    text = re.sub(r"CEC.accredited", "licensed electrical contractor", text, flags=re.I)
    text = text.replace("SAPN Accredited", "Designs to SAPN requirements")
    text = text.replace("SAPN-accredited", "designed to SAPN requirements")
    text = text.replace("Nexans Certified", "Nexans cable")
    text = text.replace("Prysmian Certified", "Prysmian cable")
    text = text.replace(
        "Manufacturer-trained on Nexans HV and LV cable systems. The same cable goes on your roof.",
        "We install Nexans cable. The same cable family goes on your roof.",
    )
    text = text.replace(
        "Manufacturer-trained on Prysmian cable and accessories.",
        "We install Prysmian cable and accessories.",
    )
    text = text.replace(
        "Nexans and Prysmian certified",
        "Nexans and Prysmian cable",
    )
    text = text.replace(
        "Authorised to work on and connect to the SA Power Networks distribution network. We lodge and manage your connection application directly.",
        "We design to SA Power Networks requirements. We lodge and manage your connection application directly.",
    )
    text = text.replace(
        "Earthed Energy, trading as Earthed High Voltage Pty Ltd.",
        LEGAL + ".",
    )
    text = text.replace(
        "© 2026 Earthed Energy · A division of Earthed High Voltage Pty Ltd",
        LEGAL,
    )
    text = text.replace("<span>ACN 679 180 879<br>ABN 99 679 180 879</span>", "")
    text = re.sub(r"\s*—\s*", ", ", text)
    text = text.replace("&mdash;", ", ").replace("&#8212;", ", ").replace("&#x2014;", ", ")
    return text


def ensure_dims(document: str) -> str:
    def repl(match: re.Match) -> str:
        tag = match.group(0)
        if " width=" in tag:
            return tag
        src = re.search(r'src="([^"]+)"', tag)
        if not src or not src.group(1).endswith(".webp"):
            return tag
        file = ROOT / src.group(1).lstrip("/")
        if not file.exists():
            return tag
        data = file.read_bytes()
        if len(data) < 30 or data[0:4] != b"RIFF" or data[8:12] != b"WEBP":
            return tag
        tag_type = data[12:16]
        if tag_type == b"VP8X":
            width = 1 + int.from_bytes(data[24:27], "little")
            height = 1 + int.from_bytes(data[27:30], "little")
        elif tag_type == b"VP8 ":
            width = int.from_bytes(data[26:28], "little") & 0x3FFF
            height = int.from_bytes(data[28:30], "little") & 0x3FFF
        elif tag_type == b"VP8L":
            b0, b1, b2, b3 = data[21], data[22], data[23], data[24]
            width = 1 + (((b1 & 0x3F) << 8) | b0)
            height = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
        else:
            return tag
        return tag[:-1] + f' width="{width}" height="{height}">'

    return re.sub(r"<img\b[^>]*>", repl, document)


def mark_motion(body: str) -> str:
    body = re.sub(
        r'<div(?![^>]*data-reveal)([^>]*style="[^"]*padding:(?:56|64|72|140)px)',
        r'<div data-reveal=""\1',
        body,
    )
    body = body.replace(
        '<div style="display:grid;grid-template-columns:64px',
        '<div data-step="" style="display:grid;grid-template-columns:64px',
    )
    body = re.sub(r"\sid=\"main\"", "", body)
    return body


def shell(
    *,
    title: str,
    description: str,
    canonical: str,
    css: str,
    body: str,
    footer: str,
    section: str,
    home: bool = False,
    quote: bool = False,
    noindex: bool = False,
    preload: str = "",
    extra: str = "",
    json_ld: str = "",
) -> str:
    classes = ["page-home"] if home else ["page"]
    if quote:
        classes.append("page-quote")
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    ld = f'<script type="application/ld+json">{json_ld}</script>\n' if json_ld else ""
    main = body if quote else body
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
{robots}<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:locale" content="en_AU">
<meta property="og:site_name" content="Earthed Energy">
<meta name="theme-color" content="#2B1550">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/open-sans-variable.woff2" as="font" type="font/woff2" crossorigin>
{preload}<link rel="stylesheet" href="/assets/css/fonts.css">
<link rel="stylesheet" href="/assets/css/ee.css">
<style>
{css}
</style>
{ld}</head>
<body class="{" ".join(classes)}">
<a class="skip-link" href="#main">Skip to content</a>
{header_html(section, home=home)}
{mobile_nav_html(section)}
<main id="main">
{main}
{footer}
</main>
{"" if quote else sticky_cta_html()}
<script src="/assets/js/site.js" defer></script>
{extra}
</body>
</html>
"""


def load_pages() -> list[dict]:
    pages = []
    for path in sorted(EXPANDED.glob("*.json")):
        if path.name.startswith("_"):
            continue
        pages.append(json.loads(path.read_text(encoding="utf-8")))
    return pages


def utility_css(sample: str) -> str:
    return sample or "body{margin:0;background:#F5F1E8;color:#2b1550;font-family:'Open Sans',sans-serif}h1,h2,h3{font-family:'Open Sans',sans-serif;font-weight:300}a{color:#5E2D89;text-decoration:none}"


def article(kicker: str, crumb: str, h1: str, lede: str, inner: str) -> str:
    return f'''<div data-screen-label="{esc(h1)}" data-reveal="" style="position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:64px 40px 48px;display:flex;flex-direction:column;gap:16px">
<div style="font-family:'Open Sans',sans-serif;font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#5E2D89">{kicker}</div>
<span style="font-family:'Open Sans',sans-serif;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:rgba(43,21,80,.55)"><a href="/" style="color:rgba(43,21,80,.55)">Home</a> → {crumb}</span>
<h1 style="font-family:'Open Sans',sans-serif;font-weight:300;font-size:clamp(34px,4.4vw,56px);line-height:1.05;color:#2b1550;margin:4px 0 0">{h1}</h1>
<p style="font-family:'Open Sans',sans-serif;font-weight:300;font-style:italic;font-size:18px;line-height:1.4;color:#4B345B;margin:0;max-width:62ch">{lede}</p>
</div>
<div data-reveal="" style="position:relative;z-index:1;padding:56px 40px;border-top:1px solid #D8D0C0"><div style="max-width:720px;margin:0 auto;display:flex;flex-direction:column;gap:16px">{inner}</div></div>'''


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if "<img" in text:
        text = ensure_dims(text)
    path.write_text(text, encoding="utf-8")


def sitemap(urls: list[str]) -> str:
    body = "\n".join(
        f"<url><loc>{BASE}{url}</loc><changefreq>monthly</changefreq><priority>{'1.0' if url == '/' else '0.8'}</priority></url>"
        for url in urls
    )
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n"


def scrub_legacy() -> None:
    skip = {"design", "mockups-src", "build", ".git"}
    for path in ROOT.rglob("*.html"):
        if any(part in skip for part in path.parts):
            continue
        original = path.read_text(encoding="utf-8", errors="replace")
        updated = apply_compliance(original, strict=True)
        if updated != original:
            path.write_text(updated, encoding="utf-8")


def main() -> None:
    subprocess.check_call(["node", str(ROOT / "scripts" / "expand_all.mjs")], cwd=ROOT)
    pages = load_pages()
    about = next(page for page in pages if page["name"] == "About Caleb Vears")
    shared_footer = apply_compliance(about["footer"], strict=True)
    if "partner-solar-accred" not in shared_footer:
        shared_footer += partner_strip_html()
    sample_css = utility_css(about["css"])
    urls = ["/"]

    for page in pages:
        strict = not page["design"]
        title = page["title"] or f"{page['name']} · Earthed Energy"
        description = page["description"] or f"{page['name']} from the Earthed Energy design archive."
        if page["name"] == "Get a Quote" and not page["title"]:
            title = "Get a quote · Earthed Energy"
            description = "Let's see what solar can do for you. Takes 45 seconds. No signup. Nothing to install."
        body = apply_compliance(page["body"], strict=strict)
        footer = apply_compliance(page["footer"], strict=strict) if page["footer"] else ""
        if strict and not footer:
            footer = shared_footer
        if footer:
            footer = re.sub(r"<img (?![^>]*\bloading=)", '<img loading="lazy" decoding="async" ', footer)
        if strict:
            body = mark_motion(body)
        if page["outFile"] == "index.html":
            canonical = BASE + "/"
            preload = '<link rel="preload" as="image" href="/images/hero-coastal-daynight-960.webp" fetchpriority="high">\n'
            body = body.replace(
                '<picture style="display:contents"><img src="/images/hero-coastal-daynight.webp"',
                '<picture style="position:absolute;inset:0;display:block"><img loading="eager" decoding="sync" src="/images/hero-coastal-daynight-960.webp"',
                1,
            )
            body = body.replace(
                'style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 70%;display:block"',
                'style="width:100%;height:100%;object-fit:cover;object-position:50% 70%;display:block"',
                1,
            )
            body = body.replace(
                'aria-label="Summer sale: start your battery quote, 45 seconds" ',
                "",
            )
        elif page["design"]:
            canonical = BASE + "/" + page["outFile"]
            preload = ""
        else:
            canonical = BASE + "/" + page["outFile"]
            preload = ""
            urls.append("/" + page["outFile"])
        extra = ""
        main_body = body
        if page.get("hydrate"):
            template = apply_compliance(page["template"], strict=True)
            script = apply_compliance(page["script"], strict=True)
            main_body = f'<div id="ee-app">{body}</div>\n<template id="ee-template">{template}</template>\n<script type="text/plain" id="ee-logic">{script}</script>'
            extra = '<script type="module" src="/assets/js/hydrate.js"></script>'
        home_ld = ""
        if page["outFile"] == "index.html":
            home_ld = json.dumps({
                "@context": "https://schema.org",
                "@type": ["Electrician", "LocalBusiness"],
                "name": "Earthed Energy",
                "legalName": "Earthed High Voltage Pty Ltd",
                "url": BASE + "/",
                "email": EMAIL,
                "telephone": "+61433839284",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "PO Box 4111",
                    "addressLocality": "Norwood South",
                    "addressRegion": "SA",
                    "postalCode": "5067",
                    "addressCountry": "AU",
                },
                "areaServed": ["Adelaide", "Adelaide Hills", "Mount Barker", "South Australia"],
                "parentOrganization": {"@type": "Organization", "name": "Earthed High Voltage", "url": "https://earthedhv.au"},
            }, ensure_ascii=False)
        doc = ensure_dims(shell(
            title=title,
            description=description,
            canonical=canonical,
            css=page["css"],
            body=main_body,
            footer=footer,
            section=page["section"],
            home=page["outFile"] == "index.html",
            quote=page["outFile"] == "get-a-quote.html",
            noindex=page["design"],
            preload=preload,
            extra=extra,
            json_ld=home_ld,
        ))
        write(ROOT / page["outFile"], doc)

    quote_footer = shared_footer
    how = shell(
        title="How we quote · Earthed Energy",
        description="How Earthed Energy prepares a quote. The full guide is still being written.",
        canonical=BASE + "/how-we-quote.html",
        css=sample_css,
        body=article(
            "How we work",
            "Process → How we quote",
            "How we quote",
            "Content coming. Caleb is writing this guide.",
            "<p class=\"ee-note\">The step-by-step of a quote, from the first phone call to the written design, is on its way. The link stays here so the knowledge hub does not dead-end.</p>"
            f"<p class=\"ee-note\">Call <a href=\"tel:{PHONE_TEL}\">0433 839 284</a> or email <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. Or start with the 45-second price.</p>"
            '<p><a class="ee-btn" href="/get-a-quote.html">Get a quote</a></p>',
        ),
        footer=quote_footer,
        section="knowledge",
    )
    write(ROOT / "how-we-quote.html", how)
    urls.append("/how-we-quote.html")

    contact = shell(
        title="Contact · Earthed Energy",
        description=f"Call 0433 839 284 or email {EMAIL}. PO Box 4111, Norwood South SA 5067.",
        canonical=BASE + "/contact.html",
        css=sample_css,
        body=article(
            "Contact",
            "Contact",
            "Talk to Caleb.",
            "Residential solar, batteries and the rest of the house load, anywhere in South Australia.",
            f"<p class=\"ee-note\"><a href=\"mailto:{EMAIL}\">{EMAIL}</a><br><a href=\"tel:{PHONE_TEL}\">0433 839 284</a></p>"
            "<p class=\"ee-note\">PO Box 4111<br>Norwood South SA 5067</p>"
            f"<p class=\"ee-note\">{LEGAL}</p>"
            "<p class=\"ee-note\">SA electrical contractor licence PGE 336477</p>"
            "<p class=\"ee-note\"><a href=\"https://earthedhv.au\">Utility and high voltage work · Earthed High Voltage</a></p>"
            f"""<form class="ee-form" action="https://formsubmit.co/{EMAIL}" method="POST">
<input type="hidden" name="_subject" value="New Earthed Energy enquiry">
<input type="hidden" name="_next" value="{BASE}/thanks.html">
<input type="hidden" name="_captcha" value="false">
<label>Name<input name="name" type="text" required autocomplete="name"></label>
<label>Phone<input name="phone" type="tel" required autocomplete="tel"></label>
<label>Email<input name="email" type="email" required autocomplete="email"></label>
<label>Suburb<input name="suburb" type="text" required autocomplete="address-level2"></label>
<label>What do you need?<textarea name="message" required></textarea></label>
<button type="submit">Send</button>
</form>""",
        ),
        footer=shared_footer,
        section="",
    )
    write(ROOT / "contact.html", contact)
    urls.append("/contact.html")

    thanks = shell(
        title="Thank you · Earthed Energy",
        description="Your enquiry is with Earthed Energy. We reply within one business day.",
        canonical=BASE + "/thanks.html",
        css=sample_css,
        body=article(
            "Contact",
            "Thank you",
            "Got it.",
            "We have your note. Caleb replies within one business day.",
            f"<p class=\"ee-note\">If it is urgent, call <a href=\"tel:{PHONE_TEL}\">0433 839 284</a>.</p>"
            '<p><a class="ee-btn" href="/">Back to the home page</a></p>',
        ),
        footer=shared_footer,
        section="",
        noindex=True,
    )
    write(ROOT / "thanks.html", thanks)

    missing = shell(
        title="Page not found · Earthed Energy",
        description="That page is not on the Earthed Energy site.",
        canonical=BASE + "/404.html",
        css=sample_css,
        body=article(
            "404",
            "Missing",
            "That page is not here.",
            "The link may be old. The guides and the quote form are still up.",
            '<p><a class="ee-btn" href="/">Home</a> <a class="ee-btn" href="/knowledge.html">Knowledge</a></p>',
        ),
        footer=shared_footer,
        section="",
        noindex=True,
    )
    write(ROOT / "404.html", missing)

    cards = []
    for page in pages:
        if not page["design"]:
            continue
        cards.append(
            f'<a href="/{page["outFile"]}" style="display:block;padding:18px 20px;border:1px solid rgba(43,21,80,.15);border-radius:8px;background:rgba(255,255,255,.62);font-weight:600">{esc(page["name"])}</a>'
        )
    design_index = shell(
        title="Design archive · Earthed Energy",
        description="Earlier mockups kept for reference. Not part of the public site.",
        canonical=BASE + "/design/",
        css=sample_css,
        body=article(
            "Archive",
            "Design",
            "Design explorations",
            "Twelve earlier directions. They are not linked from the public site.",
            '<div style="display:grid;gap:12px">' + "".join(cards) + "</div>",
        ),
        footer=shared_footer,
        section="",
        noindex=True,
    )
    write(ROOT / "design" / "index.html", design_index)

    urls.extend(["/solarcare/", "/walkthrough/"])
    write(ROOT / "sitemap.xml", sitemap(sorted(set(urls), key=lambda item: (item != "/", item))))
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /design/\nDisallow: /thanks.html\n\nSitemap: https://www.earthedenergy.au/sitemap.xml\n",
        encoding="utf-8",
    )
    scrub_legacy()
    print(f"Wrote {len(pages)} mockup pages plus utilities.")


if __name__ == "__main__":
    main()
