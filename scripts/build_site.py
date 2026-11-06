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
    ("knowledge", "/knowledge.html", "Knowledge"),
    ("about", "/about-earthed-energy.html", "About"),
]
CTA_LABEL = "Calculate savings"
CTA_HREF = "/get-a-quote.html"


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def header_html(section: str, *, home: bool) -> str:
    """Four section links and the savings CTA. The sister site lives in the footer."""
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
        f'<a class="ee-cta" href="{CTA_HREF}"{quote_current}>{CTA_LABEL}</a>'
        f"</header>"
    )


def mobile_nav_html(section: str) -> str:
    """Sticky mobile bar. Same four pages and savings CTA as the desktop bar."""
    items = []
    for key, href, label in NAV:
        current = ' aria-current="page"' if key == section else ""
        items.append(f'<a href="{href}"{current}>{label}</a>')
    quote_current = ' aria-current="page"' if section == "quote" else ""
    items.append(f'<a href="{CTA_HREF}"{quote_current}>{CTA_LABEL}</a>')
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
        f'<a href="{CTA_HREF}">{CTA_LABEL}</a>'
        "</div>"
    )


def add_ehv_card(footer: str) -> str:
    """Logo card for Earthed High Voltage on the dusk footer render."""
    if not footer or "ehv-logo.webp" in footer:
        return footer
    logo = (
        '<img class="ee-ehv-logo" src="/images/ehv-logo.webp" alt="" width="520" height="135" '
        'loading="lazy" decoding="async">'
    )
    pill = (
        "<span style=\"align-self:flex-start;font-family:'Open Sans',sans-serif;font-size:11px;"
        "font-weight:600;letter-spacing:.14em;text-transform:uppercase;padding:6px 12px;"
        "border-radius:999px;border:1px solid rgba(255,255,255,.5)\">Earthed High Voltage</span>"
    )
    if pill in footer:
        return footer.replace(pill, logo + pill, 1)
    card = (
        '<a class="ee-ehv-card" href="https://earthedhv.au">'
        f"{logo}"
        '<span class="ee-ehv-kicker">Earthed High Voltage</span>'
        '<span class="ee-ehv-line">Wind, battery and grid connections</span>'
        "</a>"
    )
    needle = 'grid-area:1/1"><div style="grid-area:1/1;align-self:end;'
    if needle in footer:
        return footer.replace(needle, 'grid-area:1/1">' + card + '<div style="grid-area:1/1;align-self:end;', 1)
    return footer + card


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


PIXEL = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
KEEP_SRC = (
    "hero-coastal-daynight",
    "earthed-energy-logo",
    "goodwe-4stack-cut",
    "sigenstor-cut",
)
IMAGE_LOADER = """<script>
(function () {
  function load() {
    var nodes = document.querySelectorAll("img[data-src]");
    for (var i = 0; i < nodes.length; i++) {
      var img = nodes[i];
      img.decoding = "async";
      img.setAttribute("fetchpriority", "low");
      img.src = img.getAttribute("data-src");
      img.removeAttribute("data-src");
    }
  }
  window.addEventListener("load", function () {
    if ("requestIdleCallback" in window) requestIdleCallback(load, { timeout: 1200 });
    else load();
  });
})();
</script>"""


def defer_noncritical_images(html: str) -> str:
    """Keep the hero (and its two product cut-outs) on the first load. Everything else waits."""

    def repl(match: re.Match) -> str:
        tag = match.group(0)
        if any(token in tag for token in KEEP_SRC) or "data-src=" in tag:
            return tag
        src = re.search(r'\ssrc="([^"]+)"', tag)
        if not src or src.group(1).startswith("data:"):
            return tag
        url = src.group(1)
        swapped = tag.replace(f' src="{url}"', f' data-src="{url}" src="{PIXEL}"', 1)
        return swapped + f'<noscript><img src="{url}" alt=""></noscript>'

    return re.sub(r"<img\b[^>]*>", repl, html)


def split_keyframes(css: str) -> tuple[str, str]:
    blocks = re.findall(r"@keyframes\s+[^{]+\{(?:[^{}]|\{[^{}]*\})*\}", css)
    rest = css
    for block in blocks:
        rest = rest.replace(block, "")
    return rest, "\n".join(blocks)


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
    if isinstance(json_ld, list):
        ld = "".join(
            f'<script type="application/ld+json">{item}</script>\n' for item in json_ld if item
        )
    elif json_ld:
        ld = f'<script type="application/ld+json">{json_ld}</script>\n'
    else:
        ld = ""
    fonts_css = (ROOT / "assets/css/fonts.css").read_text(encoding="utf-8")
    ee_css = (ROOT / "assets/css/ee.css").read_text(encoding="utf-8")
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
<meta property="og:image" content="{BASE}/images/og-home.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE}/images/og-home.jpg">
<meta name="theme-color" content="#2B1550">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/open-sans-variable.woff2" as="font" type="font/woff2" crossorigin>
{preload}<style>
{fonts_css}
{ee_css}
{css}
</style>
{ld}</head>
<body class="{" ".join(classes)}">
<a class="skip-link" href="#main">Skip to content</a>
{header_html(section, home=home)}
{mobile_nav_html(section)}
<main id="main">
{body}
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
    rel = path.relative_to(ROOT).as_posix()
    if not rel.startswith("design/"):
        text = polish(text, out_file=path.name)
    path.write_text(text, encoding="utf-8")


def sitemap(urls: list[str]) -> str:
    body = "\n".join(
        f"<url><loc>{BASE}{url}</loc><changefreq>monthly</changefreq><priority>{'1.0' if url == '/' else '0.8'}</priority></url>"
        for url in urls
    )
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n"


FORMSPREE = "https://formspree.io/f/mvkzjdwe"
LEAD_ERROR = (
    '<p class="ee-form-status" data-ee-err hidden>That did not send. '
    f'Call <a href="tel:{PHONE_TEL}">0433 839 284</a> and we will take it from here.</p>'
)
LEAD_OK = '<p class="ee-form-status" data-ee-ok hidden>Sent. Caleb replies within one business day.</p>'
PRIVACY_NOTE = (
    f'<p class="ee-form-note">We email this to {EMAIL} so we can reply. '
    'Read the <a href="/privacy.html">privacy page</a>.</p>'
)

SHORT_TITLES = {
    "index.html": "Solar and battery in South Australia · Earthed Energy",
    "about-earthed-energy.html": "About Earthed Energy · South Australia",
    "aircon-hot-water.html": "Aircon and heat pump hot water · Earthed Energy",
    "battery-sizing.html": "Battery sizing for your home · Earthed Energy",
    "battery-storage.html": "Batteries we install · Earthed Energy",
    "bushfire-prone-areas.html": "Solar in bushfire prone areas · Earthed Energy",
    "commissioning-and-handover.html": "Commissioning and handover · Earthed Energy",
    "credentials-and-licences.html": "Credentials and licences · Earthed Energy",
    "ev-charging.html": "EV charging at home · Earthed Energy",
    "federal-rebates-explained.html": "Federal solar and battery rebates · Earthed Energy",
    "finance-options.html": "Finance options · Earthed Energy",
    "how-much-you-save.html": "How much you save · Earthed Energy",
    "installation-day.html": "Installation day · Earthed Energy",
    "inverters.html": "Inverters we install · Earthed Energy",
    "monitoring-apps.html": "Monitoring apps · Earthed Energy",
    "off-grid-vs-grid-connect.html": "Off-grid vs grid-connect · Earthed Energy",
    "outage-backup.html": "Outage backup · Earthed Energy",
    "racking-and-cable.html": "Racking and cable · Earthed Energy",
    "reading-your-power-bill.html": "Reading your power bill · Earthed Energy",
    "residential.html": "Residential solar and battery · Earthed Energy",
    "sa-export-limits.html": "SA export limits · Earthed Energy",
    "sapn-flexible-export.html": "SAPN Flexible Exports · Earthed Energy",
    "shade-and-roof-orientation.html": "Shade and roof orientation · Earthed Energy",
    "solar-panels.html": "Solar panels we install · Earthed Energy",
    "swer-lines.html": "SWER lines and solar · Earthed Energy",
    "three-phase-vs-single-phase.html": "Three-phase vs single-phase · Earthed Energy",
    "warranty-and-aftercare.html": "Warranty and aftercare · Earthed Energy",
    "what-a-battery-does.html": "What a battery does · Earthed Energy",
    "what-solar-does.html": "What solar does · Earthed Energy",
    "what-we-install.html": "What we install · Earthed Energy",
    "whole-home-backup-explained.html": "Whole-home backup · Earthed Energy",
    "why-we-do-this.html": "Why we do this · Earthed Energy",
}

QUOTE_SUBMIT = """  submit = () => {
    if (this.leadInvalid() || this.state.sending) return;
    const c = this.calc(), s = this.state;
    const payload = { postcode: s.postcode, type: s.ptype, quarterlyBill: s.billQ, recommended: `${c.kw}kW + ${c.bat}kWh`, price: c.price, finance: s.finance, firstName: s.name, phone: s.phone, email: s.email, timestamp: new Date().toISOString(), utm: this.utm || {} };
    const summary = `Quote request, ${s.name}, ${s.postcode}, $${c.price}, ${s.finance}, ${c.kw}kW + ${c.bat}kWh`;
    this.setState({ sending: true });
    const err = document.getElementById('ee-lead-error');
    if (err) err.hidden = true;
    const body = new FormData();
    body.append('form', 'quote');
    body.append('email', s.email);
    body.append('name', s.name);
    body.append('phone', s.phone);
    body.append('_subject', 'Earthed Energy quote request');
    body.append('message', summary + '\\n' + JSON.stringify(payload, null, 2));
    const endpoint = (window.EE_LEAD || 'https://formspree.io/f/mvkzjdwe');
    fetch(endpoint, { method: 'POST', body, headers: { Accept: 'application/json' } })
      .then((res) => { if (!res.ok) throw new Error(String(res.status)); this.setState({ sending: false }); this.go(8, 1); })
      .catch(() => { this.setState({ sending: false }); if (err) err.hidden = false; });
  };"""


def fit_title(out_file: str, title: str) -> str:
    title = SHORT_TITLES.get(out_file, title)
    if len(title) > 60:
        raise SystemExit(f"Title too long ({len(title)}): {title}")
    return title


def local_business_ld() -> str:
    return json.dumps({
        "@context": "https://schema.org",
        "@type": ["Electrician", "LocalBusiness"],
        "@id": BASE + "/#business",
        "name": "Earthed Energy",
        "legalName": "Earthed High Voltage Pty Ltd",
        "url": BASE + "/",
        "logo": BASE + "/images/earthed-energy-logo-purple.webp",
        "image": BASE + "/images/og-home.jpg",
        "email": EMAIL,
        "telephone": "+61433839284",
        "address": {
            "@type": "PostalAddress",
            "postOfficeBoxNumber": "4111",
            "addressLocality": "Norwood South",
            "addressRegion": "SA",
            "postalCode": "5067",
            "addressCountry": "AU",
        },
        "areaServed": {"@type": "AdministrativeArea", "name": "South Australia"},
        "parentOrganization": {
            "@type": "Organization",
            "name": "Earthed High Voltage",
            "url": "https://earthedhv.au",
        },
    }, ensure_ascii=False)


def breadcrumb_ld(page_name: str, page_url: str, section: str) -> str:
    section_names = {
        "residential": ("Residential", "/residential.html"),
        "commercial": ("Commercial", "/commercial.html"),
        "knowledge": ("Knowledge", "/knowledge.html"),
        "about": ("About", "/about-earthed-energy.html"),
        "quote": ("Calculate savings", "/get-a-quote.html"),
    }
    items = [{
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": BASE + "/",
    }]
    parent = section_names.get(section)
    if parent and parent[1] != page_url.replace(BASE, ""):
        items.append({
            "@type": "ListItem",
            "position": 2,
            "name": parent[0],
            "item": BASE + parent[1],
        })
    items.append({
        "@type": "ListItem",
        "position": len(items) + 1,
        "name": page_name,
        "item": page_url if page_url.startswith("http") else BASE + page_url,
    })
    if len(items) < 2:
        return ""
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }, ensure_ascii=False)


def align_claims(text: str) -> str:
    swaps = [
        (
            ">10 yrs</span><span style=\"font-size:14px;line-height:1.45;color:#3A2947\">Workmanship warranty on every install</span>",
            ">7 yrs</span><span style=\"font-size:14px;line-height:1.45;color:#3A2947\">Workmanship warranty on every install</span>",
        ),
        ("Inverter (GoodWe or Sigenergy)", "Inverter, GoodWe"),
        (
            ">10 years</td>",
            ">10 years</td>",
        ),
        (
            "Battery (Lynx or SigenStor)",
            "Battery, GoodWe Lynx",
        ),
        (
            "10-year inverter and battery",
            "GoodWe 10-year inverter and battery, Sigenergy 12-year inverter and 15-year battery",
        ),
        (
            "GoodWe Lynx and Sigenergy SigenStor modules. LFP, modular, 10 years to 70 percent.",
            "GoodWe Lynx, 10 years to 70 percent. Sigenergy SigenStor, 15 years.",
        ),
        (
            "<td style=\"padding:12px 14px;border-bottom:1px solid #D8D0C0;vertical-align:top\">10 yr inverter, 10 yr battery</td><td style=\"padding:12px 14px;border-bottom:1px solid #D8D0C0;vertical-align:top\">10 yr inverter, 10 yr battery</td>",
            "<td style=\"padding:12px 14px;border-bottom:1px solid #D8D0C0;vertical-align:top\">10 yr inverter, 10 yr battery</td><td style=\"padding:12px 14px;border-bottom:1px solid #D8D0C0;vertical-align:top\">12 yr inverter, 15 yr battery</td>",
        ),
        ("CEC-approved off-grid", "Dedicated off-grid"),
        ("CEC-approved. ", ""),
        ("Selectronic · Melbourne-made · world-class", "Selectronic · Melbourne-made"),
        ("The world’s best off-grid inverter.", "An Australian-made off-grid inverter."),
        ("The world's best off-grid inverter.", "An Australian-made off-grid inverter."),
        ("widely regarded as the world’s best off-grid inverter by industry reviewers.", "built in Australia for properties that need a dedicated off-grid inverter."),
        ("It is considered the world’s best off-grid inverter by expert industry reviewers.", "It is made in Melbourne for off-grid properties."),
        ("widely regarded as the world's best off-grid inverter by industry reviewers.", "built in Australia for properties that need a dedicated off-grid inverter."),
        (
            "<strong style=\"color:#2b1550\">$0 upfront at $333 per month for 24 months*</strong>",
            "Finance options are on the <a href=\"/finance-options.html\">finance page</a>. We do not quote a monthly repayment here. The comparison rate depends on the lender and the term, and we will not publish one we cannot source.",
        ),
        ("Get a quote · 45 seconds", "Calculate savings"),
        ("Now get your full indicative price · 45 seconds", "Calculate savings"),
        ('href="/warranty-and-aftercare.html"', 'href="/warranty-and-aftercare.html"'),
    ]
    for old, new in swaps:
        text = text.replace(old, new)
    text = re.sub(
        r'href="/warranty-and-aftercare.html"([^>]*)>Full terms',
        r'href="/terms.html"\1>Full terms',
        text,
    )
    # Split the warranty table: the GoodWe inverter cell stays 10 years.
    # Insert a Sigenergy inverter row and a SigenStor battery row by rewriting the two generic rows once.
    text = text.replace(
        "Inverter, GoodWe",
        "Inverter, GoodWe",
    )
    cell = 'style="padding:12px 14px;border-bottom:1px solid #D8D0C0;vertical-align:top"'
    strong = 'style="padding:12px 14px;border-bottom:1px solid #D8D0C0;vertical-align:top;font-weight:600"'
    if "Inverter, Sigenergy" not in text and "Inverter, GoodWe" in text:
        text = text.replace(
            f'<td {strong}>Battery, GoodWe Lynx</td>',
            (
                f'<td {strong}>Inverter, Sigenergy</td>'
                f'<td {cell}>12 years</td>'
                f'<td {cell}>Inverter failure, firmware, transfer switch</td>'
                f'<td {cell}>Manufacturer, we handle the claim and the swap</td></tr><tr>'
                f'<td {strong}>Battery, GoodWe Lynx</td>'
            ),
            1,
        )
        text = text.replace(
            f'<td {cell}>10 years to 70% capacity</td><td {cell}>Module failure, capacity below 70%</td><td {cell}>Manufacturer, we handle the claim and the swap</td></tr>',
            (
                f'<td {cell}>10 years to 70% capacity</td><td {cell}>Module failure, capacity below 70%</td><td {cell}>Manufacturer, we handle the claim and the swap</td></tr><tr>'
                f'<td {strong}>Battery, Sigenergy SigenStor</td>'
                f'<td {cell}>15 years</td>'
                f'<td {cell}>Module failure, capacity below 70%</td>'
                f'<td {cell}>Manufacturer, we handle the claim and the swap</td></tr>'
            ),
            1,
        )
    return text


def fix_heading_order(document: str) -> str:
    parts = []
    cursor = 0
    last = 0
    for match in re.finditer(r"<h([1-6])\b([^>]*)>(.*?)</h\1>", document, flags=re.S):
        parts.append(document[cursor:match.start()])
        level = int(match.group(1))
        if last and level > last + 1:
            level = last + 1
        parts.append(f"<h{level}{match.group(2)}>{match.group(3)}</h{level}>")
        last = level
        cursor = match.end()
    parts.append(document[cursor:])
    return "".join(parts)


def designed_panel(title: str, note: str, ratio: str = "21 / 9") -> str:
    return (
        f'<div class="ee-panel" style="aspect-ratio:{ratio}" role="img" aria-label="{esc(title)}">'
        '<p class="ee-panel-kicker">Photograph to come</p>'
        f'<p class="ee-panel-title">{esc(title)}</p>'
        f'<p class="ee-panel-note">{esc(note)}</p>'
        "</div>"
    )


PLACEHOLDER_COPY = {
    "Caleb on site": ("Caleb on site", "A portrait goes here when Caleb has one he wants on the page."),
    "Troy on site": ("Troy on site", "A portrait goes here when there is a photo of Troy he is happy to publish."),
    "Caleb on the first Earthed job": ("The first Earthed job", "A wide photo of that job will replace this panel."),
    "Early site photo": ("Early site", "Goyder South or Port Wakefield, when a photo from the job is ready."),
    "Real dashboard screenshots": ("Monitoring apps", "SEMS and mySigen screenshots will sit here. No mock dashboard."),
    "Anonymised SA power bill": ("Your power bill", "An anonymised SA bill, with the five numbers marked, will sit here."),
    "Drone shot · commercial": ("Commercial rooftop", "A drone photo of a commercial roof will replace this panel."),
    "Drone shot · remote": ("Off-grid site", "A photo of a remote install will replace this panel."),
}


def replace_placeholders(text: str) -> str:
    def ee_ph(match: re.Match) -> str:
        inner = re.sub(r"<[^>]+>", " ", match.group(0))
        inner = re.sub(r"\s+", " ", inner)
        ratio = "16 / 7" if "aspect-ratio:16/7" in match.group(0) else "21 / 9"
        for key, (title, note) in PLACEHOLDER_COPY.items():
            if key in inner:
                return designed_panel(title, note, ratio)
        return designed_panel("Photograph to come", "This space stays empty until there is a real photo.", ratio)

    text = re.sub(r'<div class="ee-ph"[\s\S]*?</div>', ee_ph, text)

    def picture(match: re.Match) -> str:
        alt = re.search(r'alt="([^"]*)"', match.group(0))
        label = alt.group(1) if alt else ""
        for key, (title, note) in PLACEHOLDER_COPY.items():
            if key in label or key in match.group(0):
                return designed_panel(title, note)
        return match.group(0)

    text = re.sub(r'<picture\b[^>]*>[\s\S]*?Caleb to add[\s\S]*?</picture>', picture, text)
    return text


def footer_links(text: str) -> str:
    legal = f">{LEGAL}</span>"
    links = (
        f">{LEGAL}</span>"
        '<span style="display:flex;gap:16px;font-size:12.5px">'
        '<a href="/privacy.html" style="color:#5E2D89">Privacy</a>'
        '<a href="/terms.html" style="color:#5E2D89">Terms</a>'
        "</span>"
    )
    if legal in text and "/privacy.html" not in text:
        text = text.replace(legal, links, 1)
    text = re.sub(r'<img[^>]*partner-nec-seller\.webp[^>]*>', "", text)
    return text


def contrast_and_chrome(text: str) -> str:
    text = text.replace("rgba(43,21,80,.55)", "rgba(43,21,80,.9)")
    text = text.replace("rgba(43,21,80,0.55)", "rgba(43,21,80,.9)")
    text = text.replace("rgba(43,21,80,.62)", "rgba(43,21,80,.9)")
    text = text.replace("rgba(43,21,80,.4)", "rgba(43,21,80,.78)")
    text = text.replace("rgba(107,79,187,.35)", "rgba(75,40,120,.78)")
    text = text.replace("top:96px", "top:16px")
    text = text.replace('<div aria-label="Progress"', '<div aria-hidden="true"')
    return text


def prioritise_lcp(text: str, src: str) -> str:
    def repl(match: re.Match) -> str:
        tag = match.group(0)
        tag = re.sub(r'\sloading="lazy"', "", tag)
        tag = re.sub(r'\sdecoding="async"', "", tag)
        if "fetchpriority=" not in tag:
            tag = tag.replace("<img ", '<img fetchpriority="high" decoding="sync" loading="eager" ', 1)
        return tag

    return re.sub(rf"<img\b[^>]*{re.escape(src)}[^>]*>", repl, text)


def patch_quote(text: str) -> str:
    text = re.sub(r"submit = \(\) => \{.*?\n  \};", QUOTE_SUBMIT, text, count=1, flags=re.S)
    text = text.replace(
        '<button onClick="{{ goCal }}" style="background:none;border:none;padding:0;cursor:pointer;font-family:\'Open Sans\',sans-serif;font-size:14px;color:#5E2D89;text-decoration:underline;text-underline-offset:3px">Or reserve a time for a free energy assessment in our live calendar →</button>',
        f'<a href="/contact.html">Book a call</a> or <a href="tel:{PHONE_TEL}">0433 839 284</a>',
    )
    text = text.replace(
        '<a href="https://calendly.com/earthedenergy/15min" target="_blank" rel="noopener" style="padding:14px 20px;border-radius:10px;border:1px solid #2b1550;color:#2b1550;font-size:15px;font-weight:600" style-hover="background:#ffffff;color:#2b1550">Book a call</a>',
        f'<a href="/contact.html" style="padding:14px 20px;border-radius:10px;border:1px solid #2b1550;color:#2b1550;font-size:15px;font-weight:600">Book a call</a>'
        f'<a href="tel:{PHONE_TEL}" style="padding:14px 20px;border-radius:10px;border:1px solid #2b1550;color:#2b1550;font-size:15px;font-weight:600">0433 839 284</a>',
    )
    text = re.sub(
        r'<div style="border:1px solid #D8D0C0;border-radius:14px;overflow:hidden;background:#F5F1E8;min-height:560px">\s*<iframe src="\{\{ calUrl \}\}"[\s\S]*?</iframe>\s*</div>',
        (
            '<div style="border:1px solid #D8D0C0;border-radius:14px;background:#F5F1E8;padding:28px;display:flex;flex-direction:column;gap:12px">'
            '<p style="margin:0;font-size:17px;line-height:1.5;color:#2b1550">There is no online booking calendar yet. Send the quote, or call.</p>'
            f'<a href="/contact.html">Book a call</a><a href="tel:{PHONE_TEL}">0433 839 284</a>'
            "</div>"
        ),
        text,
        count=1,
    )
    if "ee-lead-error" not in text:
        text = text.replace(
            "<span>{{ submitLabel }}</span>\n        </button>",
            "<span>{{ submitLabel }}</span>\n        </button>\n"
            '<p id="ee-lead-error" hidden style="margin:0;font-size:14px;line-height:1.45;color:#8C2F2F">That did not send. Call <a href="tel:0433839284">0433 839 284</a>.</p>\n'
            f'<p style="margin:0;font-size:13px;line-height:1.45;color:#3A2947">We email this to {EMAIL}. <a href="/privacy.html">Privacy</a>.</p>',
            1,
        )
    text = text.replace(
        'src="/images/hf-20260615-150951-1b5883ca-ca70-4757-934c-e12ff4c502c4.webp"',
        'src="/images/quote-backdrop-960.webp"',
    )
    text = text.replace(
        'quote-backdrop-960.webp" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 50%" width="2400" height="1357"',
        'quote-backdrop-960.webp" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 50%" width="960" height="543"',
    )
    text = text.replace(
        "calUrl: (this.props.calendarUrl ?? 'https://calendly.com/earthedenergy/energy-assessment') + '?hide_gdpr_banner=1&primary_color=5e2d89&background_color=f5f1e8&text_color=2b1550'",
        "calUrl: '/contact.html'",
    )
    return text


def polish(text: str, *, out_file: str) -> str:
    text = align_claims(text)
    text = contrast_and_chrome(text)
    text = replace_placeholders(text)
    text = footer_links(text)
    if out_file == "residential.html":
        text = text.replace(
            'data-screen-label="Commercial solar Adelaide · utility-grade design and install"',
            'data-screen-label="Residential solar and battery across South Australia"',
        )
    if out_file == "off-grid.html":
        text = text.replace(
            'data-screen-label="Commercial solar Adelaide · utility-grade design and install"',
            'data-screen-label="Off-grid solar and battery"',
        )
    if out_file in {"get-a-quote.html"} or "calendly.com" in text or "submit = () =>" in text:
        text = patch_quote(text)
    if out_file == "commercial.html":
        text = prioritise_lcp(text, "/images/quote-backdrop-960.webp")
    if "quote-backdrop-960.webp" in text:
        text = prioritise_lcp(text, "quote-backdrop-960.webp")
    if 'data-ee-input="bat"' in text and "ee-estimate" not in text:
        text = text.replace(
            '<a href="/get-a-quote.html" style="grid-column:1 / -1;display:flex;align-items:center;justify-content:center;min-height:56px;border-radius:6px;background:#2A1B4A;color:#F1EDF9;font-size:15px;font-weight:600" style-hover="background:#5E2D89;color:#F1EDF9">Calculate savings</a>',
            ESTIMATE_FORM
            + '<a href="/get-a-quote.html" style="grid-column:1 / -1;display:flex;align-items:center;justify-content:center;min-height:56px;border-radius:6px;background:#2A1B4A;color:#F1EDF9;font-size:15px;font-weight:600">Calculate savings</a>',
            1,
        )
    text = fix_heading_order(text)
    return text


ESTIMATE_FORM = f"""<form class="ee-form" data-ee-lead data-ee-estimate style="grid-column:1 / -1;display:flex;flex-direction:column;gap:12px;padding:8px 0 4px" action="{FORMSPREE}" method="POST">
<input type="hidden" name="form" value="rebate-estimate">
<input type="hidden" name="_subject" value="Earthed Energy rebate estimate">
<input type="hidden" name="message" value="">
<p style="margin:0;font-size:16px;line-height:1.45;color:#2b1550">Send me this estimate</p>
<label>Name<input name="name" type="text" required autocomplete="name"></label>
<label>Phone<input name="phone" type="tel" required autocomplete="tel"></label>
<label>Email<input name="email" type="email" required autocomplete="email"></label>
{PRIVACY_NOTE}
<button type="submit">Send me this estimate</button>
{LEAD_OK}
{LEAD_ERROR}
</form>"""


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
    shared_footer = add_ehv_card(apply_compliance(about["footer"], strict=True))
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
            description = "See what solar can do for your home. Takes 45 seconds. No signup."
        if not page["design"]:
            description = align_claims(description)
            title = fit_title(page["outFile"], title)
        body = apply_compliance(page["body"], strict=strict)
        footer = apply_compliance(page["footer"], strict=strict) if page["footer"] else ""
        footer = add_ehv_card(footer)
        if strict and not footer:
            footer = shared_footer
        if footer:
            footer = re.sub(r"<img (?![^>]*\bloading=)", '<img loading="lazy" decoding="async" ', footer)
        if strict:
            body = mark_motion(body)
        extra_motion = ""
        if page["outFile"] == "index.html":
            canonical = BASE + "/"
            preload = '<link rel="preload" as="image" href="/images/hero-coastal-daynight-960.webp" fetchpriority="high">\n'
            body = body.replace(
                '<picture style="display:contents"><img src="/images/hero-coastal-daynight.webp"',
                '<picture style="position:absolute;inset:0;display:block"><img loading="eager" decoding="sync" fetchpriority="high" src="/images/hero-coastal-daynight-960.webp"',
                1,
            )
            body = body.replace(
                'style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 70%;display:block"',
                'style="width:100%;height:100%;object-fit:cover;object-position:50% 70%;display:block"',
                1,
            )
            body = body.replace(' width="2400" height="1797"', ' width="960" height="719"', 1)
            body = body.replace(
                'aria-label="Summer sale: start your battery quote, 45 seconds" ',
                "",
            )
            for marker in ("equipment", "how", "cost"):
                body = body.replace(
                    f'<div data-reveal="" id="{marker}"',
                    f'<div data-reveal="" class="ee-fold" id="{marker}"',
                    1,
                )
            if footer:
                footer = footer.replace(
                    '<div style="position:relative;z-index:1;overflow:hidden">',
                    '<div class="ee-fold" style="position:relative;z-index:1;overflow:hidden">',
                    1,
                )
            page["css"], motion_css = split_keyframes(page["css"])
            if motion_css:
                extra_motion = (
                    '<style media="print" id="ee-motion">' + motion_css + "</style>"
                    '<script>document.getElementById("ee-motion").media="all"</script>'
                )
            else:
                extra_motion = ""
            body = defer_noncritical_images(body)
            footer = defer_noncritical_images(footer) if footer else footer
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
        if page["outFile"] == "index.html":
            extra = extra_motion + IMAGE_LOADER
        ld_blocks = []
        if not page["design"]:
            ld_blocks.append(local_business_ld())
            if page["outFile"] != "index.html":
                crumb = breadcrumb_ld(page["name"], canonical, page["section"])
                if crumb:
                    ld_blocks.append(crumb)
        if page["outFile"] == "get-a-quote.html":
            preload = '<link rel="preload" as="image" href="/images/quote-backdrop-960.webp" fetchpriority="high">\n'
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
            json_ld=ld_blocks,
        ))
        write(ROOT / page["outFile"], doc)

    quote_footer = shared_footer
    how_body = """
<h2>The 45-second price is not the quote</h2>
<p>Calculate savings asks for a South Australian postcode, the kind of property, and a quarterly bill. It returns an indicative system and price from the same bands published on this site. Treat that number as a starting point. The written proposal replaces it.</p>
<h2>Site assessment</h2>
<p>Caleb or Troy visits. We look at the roof, the shade, the switchboard, whether the supply is single-phase or three-phase, and any solar already on the house. If backup during an outage matters, say so then. It changes the battery, the inverter and the switchboard work. Troy signs the design. The STC rebate and the Cheaper Home Batteries rebate both need that sign-off.</p>
<h2>Single line diagram</h2>
<p>The design pack includes a single line diagram. It shows how the panels, inverter, battery and switchboard connect, and it is what we lodge when SA Power Networks needs the connection application. We design to their requirements. The proposal does not say the company is accredited by SA Power Networks.</p>
<h2>OSW pricing</h2>
<p>Equipment on the proposal is priced from our wholesaler list (OSW), not a retail shelf price. The proposal separates the equipment, the installation and the rebate deduction. We do not add a line after you sign for something that was already in the scope.</p>
<h2>Rebate maths</h2>
<p>Small-scale Technology Certificates and the Cheaper Home Batteries rebate are worked out and shown as a deduction on the proposal, assigned to Earthed. The method, including the deeming period and the battery tiers, is the one on the <a href="/federal-rebates-explained.html">federal rebates</a> page. The proposal uses the certificate price current when we write it. This page does not add a second set of figures.</p>
<h2>The written proposal</h2>
<p>You receive a proposal you can sign. It names the equipment, the warranties (7-year Earthed workmanship, plus the manufacturer terms on the <a href="/warranty-and-aftercare.html">warranty page</a>), and what is included. Finance, where someone wants it, is the lenders on the <a href="/finance-options.html">finance page</a>. We do not put a monthly repayment on this page, because the comparison rate belongs to the lender.</p>
"""
    how = shell(
        title="How we quote · Earthed Energy",
        description="How a quote is built: indicative price, site assessment, single line diagram, OSW pricing, rebate maths, written proposal.",
        canonical=BASE + "/how-we-quote.html",
        css=sample_css,
        body=article(
            "How we work",
            "Process → How we quote",
            "How we quote",
            "From the 45-second price to a proposal you can sign.",
            how_body
            + f'<p class="ee-note">Call <a href="tel:{PHONE_TEL}">0433 839 284</a> or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>'
            + '<p><a class="ee-btn" href="/get-a-quote.html">Calculate savings</a></p>',
        ),
        footer=quote_footer,
        section="knowledge",
        json_ld=[local_business_ld(), breadcrumb_ld("How we quote", "/how-we-quote.html", "knowledge")],
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
            "<p class=\"ee-note\">SA electrical contractor licence PGE 363823</p>"
            "<p class=\"ee-note\"><a href=\"https://earthedhv.au\">Utility and high voltage work · Earthed High Voltage</a></p>"
            f"""<form class="ee-form" data-ee-lead action="{FORMSPREE}" method="POST">
<input type="hidden" name="form" value="contact">
<input type="hidden" name="_subject" value="Earthed Energy enquiry">
<label>Name<input name="name" type="text" required autocomplete="name"></label>
<label>Phone<input name="phone" type="tel" required autocomplete="tel"></label>
<label>Email<input name="email" type="email" required autocomplete="email"></label>
<label>Suburb<input name="suburb" type="text" required autocomplete="address-level2"></label>
<label>What do you need?<textarea name="message" required></textarea></label>
{PRIVACY_NOTE}
<button type="submit">Send</button>
{LEAD_OK}
{LEAD_ERROR}
</form>""",
        ),
        footer=shared_footer,
        section="",
        json_ld=[local_business_ld(), breadcrumb_ld("Contact", "/contact.html", "")],
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

    legal_pages = [
        (
            "privacy.html",
            "Privacy · Earthed Energy",
            "How Earthed Energy handles personal information.",
            "Privacy",
            "How we handle personal information.",
            f"""
<h2>Who we are</h2>
<p>{LEGAL}. Postal address: PO Box 4111, Norwood South SA 5067. Email <a href="mailto:{EMAIL}">{EMAIL}</a>. Phone <a href="tel:{PHONE_TEL}">0433 839 284</a>.</p>
<h2>What we collect</h2>
<p>If you use a form, call, or email, we collect the details you give us: name, phone, email, suburb, and what you tell us about your bill, roof and the system you want. The quote tool also stores the postcode, property type and indicative price you asked us to send.</p>
<h2>Why</h2>
<p>We use that information to reply, prepare a quote, design and install a system, and handle warranty calls. We do not sell lists.</p>
<h2>Who else sees it</h2>
<p>Form messages are sent through Formspree to {EMAIL}. Formspree processes the submission so it can be delivered. We do not run analytics and we do not set advertising cookies. A Google Business profile is not linked from this site, because none has been confirmed.</p>
<h2>Access and correction</h2>
<p>Email {EMAIL} to ask what we hold, or to correct it. If you are not happy with the reply, you can contact the Office of the Australian Information Commissioner. We handle personal information in line with the Australian Privacy Principles.</p>
""",
        ),
        (
            "terms.html",
            "Terms · Earthed Energy",
            "Terms for using the Earthed Energy site and for quotes.",
            "Terms",
            "The site, the indicative price, and the written proposal.",
            f"""
<h2>The business</h2>
<p>{LEGAL}. PO Box 4111, Norwood South SA 5067. <a href="mailto:{EMAIL}">{EMAIL}</a>. <a href="tel:{PHONE_TEL}">0433 839 284</a>. SA electrical contractor licence PGE 363823.</p>
<h2>The indicative price</h2>
<p>Calculate savings and the scenario pages are guides. They are not an offer. The written proposal is the document that sets the equipment, the price and what is included. Nothing on this website adds a cost after you sign for work that was already in that proposal.</p>
<h2>Warranties</h2>
<p>Earthed workmanship is 7 years, as described on the <a href="/warranty-and-aftercare.html">warranty page</a>. Panel, inverter and battery warranties are the manufacturer terms named there: Trina, GoodWe and Sigenergy are not the same length.</p>
<h2>Finance</h2>
<p>Where a page mentions finance, the lender sets the rate and the comparison rate. We do not publish a monthly repayment unless that lender's rate is the source.</p>
<h2>The site</h2>
<p>These pages are general information for South Australia. They are not a connection approval and not personal advice. South Australian law applies. Questions go to {EMAIL}.</p>
""",
        ),
    ]
    for filename, title, description, h1, lede, inner in legal_pages:
        page = shell(
            title=title,
            description=description,
            canonical=BASE + "/" + filename,
            css=sample_css,
            body=article("Legal", h1, h1, lede, inner),
            footer=shared_footer,
            section="",
            json_ld=[local_business_ld(), breadcrumb_ld(h1, "/" + filename, "")],
        )
        write(ROOT / filename, page)
        urls.append("/" + filename)

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
