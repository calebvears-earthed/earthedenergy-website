# Earthed group design system

Version 1 · 30 October 2026

Shared visual system for **earthedhv.au** (Earthed High Voltage) and **earthedenergy.au** (Earthed Energy). Both sites should look like one practice: same colour, type, spacing, buttons, cards, header and footer. Copy, photography and navigation labels stay specific to each company.

Source of truth in this repo:

- `design-system/tokens.css` — CSS variables
- `design-system/tokens.json` — the same values, for tools
- `design-system/components.css` — buttons, header, footer, cards, form fields, mobile bar

Copy both CSS files into the Energy site and do not invent a second palette.

## Principles

- Industrial and quiet. One purple, warm paper, near-black ink. No second brand hue, no hi-vis red, no gradient logos.
- Photography does the talking. Full-bleed images, a dark scrim, type on the scrim. Do not tint photographs purple.
- Type is editorial: a serif for headlines, a grotesk for UI, a mono for indexes and eyebrows.
- Motion is short and optional. Respect `prefers-reduced-motion`. No parallax libraries, no scroll-jacking.
- Corners are 2px. The logo frame is the only ornament: a 1px rule, not a drop shadow stack.
- Body text is never set below 16px. Hit targets are at least 44px, 48px on buttons.

## Colour

| Token | Hex | Use |
| --- | --- | --- |
| `--color-purple` | `#553A66` | Primary brand, primary buttons, eyebrows on paper |
| `--color-purple-deep` | `#3E294C` | Primary button hover |
| `--color-purple-ink` | `#241430` | Dark bands, licence panel |
| `--color-ink` | `#160E1E` | Header (solid), footer, page heroes |
| `--color-lilac` | `#C9A7E8` | Eyebrows and indexes on dark surfaces |
| `--color-lilac-soft` | `#E7D9F4` | Secondary text on dark surfaces |
| `--color-paper` | `#F6F3EF` | Page background |
| `--color-paper-2` | `#EBE6E0` | Quiet fills, if a second surface is needed |
| `--color-white` | `#FFFCF9` | Cards, credential bar, light buttons |
| `--color-text` | `#1C1424` | Body text on paper |
| `--color-muted` | `#4A4154` | Supporting text on paper |
| `--color-muted-on-dark` | `#E4D4F2` | Supporting text on ink |
| `--color-danger` | `#7A1836` | Form errors only |

White on `#553A66` is AAA (about 9.6:1). `#4A4154` on `#F6F3EF` is AAA. `#C9A7E8` on `#241430` is AAA. Do not put `#553A66` text on `#C9A7E8`, and do not fade text with opacity.

`--color-line` is `rgba(85, 58, 102, 0.18)` on paper. `--color-line-on-dark` is `rgba(246, 243, 239, 0.22)`.

## Type

Load these three families. On the High Voltage site they are self-hosted with `next/font`. The Energy site should use the same families.

| Role | Family | Weight |
| --- | --- | --- |
| UI, body, buttons | Instrument Sans | 400, 500 |
| Headlines | Instrument Serif | 400, plus italic for one emphasised line |
| Eyebrows, indexes, licence lines | IBM Plex Mono | 400, 500 |

| Style | Size | Line height | Notes |
| --- | --- | --- | --- |
| Display | `clamp(3.35rem, 7.6vw, 7.15rem)` | 0.9 | Hero and page titles. Tracking `-0.035em` |
| h2 | `clamp(2.1rem, 3.4vw, 3.25rem)` | 1.05 | Serif |
| h3 / card title | `clamp(1.7rem, 2vw, 2.15rem)` | 1 | Serif inside cards |
| Body | `1.0625rem` | 1.65 | Sans |
| Lede | `clamp(1.05rem, 1.4vw, 1.25rem)` | 1.55 | Max width about 42rem |
| Eyebrow | `0.75rem` | 1 | Mono, uppercase, tracking `0.16em` |

Headlines use `text-wrap: pretty`. One italic serif phrase per hero is enough (`High voltage.`). Do not italicise whole paragraphs.

## Spacing and layout

Spacing scale, in px: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128. Mapped to `--space-1` through `--space-10`.

- Header height: 76px (`--header-h`)
- Content width: 1180px
- Wide width (grids, footer): 1360px
- Page gutter: `clamp(1.25rem, 4vw, 3rem)`
- Section padding: `clamp(4rem, 8vw, 7rem)` vertical
- Radius: 2px

Breakpoints used here: 800px (two columns), 900px (desktop nav), 1100px (three-column grids). Build mobile-first.

## Buttons

Always `min-height: 48px`, horizontal padding `1.25rem`, sans 500, sentence case. Not uppercase.

| Class | Surface | Look |
| --- | --- | --- |
| `.btn.btn-primary` | Paper | Fill `#553A66`, white label. Hover `#3E294C` |
| `.btn.btn-light` | Photography or ink | Fill `#F6F3EF`, ink label |
| `.btn.btn-ghost` | Photography or ink | Transparent, 1px paper rule, paper label. Hover inverts |
| `.btn.btn-line` | Paper | Transparent, purple rule and label. Hover fills purple |

On a purple-ink band, the primary action swaps to a paper fill (see `.cta-band .btn-primary`) so it does not disappear into the background.

Focus: `outline: 2px solid` lilac on dark, purple on paper, offset 3px. Do not remove outlines.

## Cards

`.media-card` is a block link. Image fills the card (`object-fit: cover`), a bottom scrim runs from transparent to `rgba(22, 14, 30, 0.88)`, and the index, title and one sentence sit on the scrim in paper and lilac. Minimum height 420px. Hover scales the image to 1.045 over 1.1s. Reduced motion disables that scale.

The index (`.idx`) is mono and tracked out: `01`, `02`. Use lilac on ink or photography, and `#553A66` on paper so the small type stays above 4.5:1.

`.shot` is a positioned frame for `next/image` with `fill`. Give it an aspect ratio (`16/10`, `4/5`, `3/4`). Background while loading is `--color-purple-ink`.

## Header

Fixed, 76px, ink text in paper colour.

- Transparent over the home hero.
- Solid `rgba(22, 14, 30, 0.94)` with a hairline and a 16px blur once the page has scrolled, and on every page that is not the home hero.
- Left: white wordmark (transparent PNG, about 42px tall).
- Centre/right: Services, Projects, About, Contact. Sentence case, no boxes.
- Then the sister-site link, in lilac-soft, labelled with the other company's name.
- Then a light button: "Request a quote".
- Below 900px: hide the inline nav and show a 48px menu button. The menu is a full-viewport ink panel, serif links, Escape to close. A fixed bottom bar holds Call and Request a quote. Add bottom padding so it does not cover content.

HTML shape:

```html
<header class="site-header">
  <div class="header-inner">
    <a class="logo" href="/">…wordmark…</a>
    <nav class="nav-links" aria-label="Primary">…</nav>
    <a class="nav-sister" href="https://earthedenergy.au">Earthed Energy</a>
    <a class="btn btn-light header-cta" href="/contact">Request a quote</a>
    <button class="nav-toggle" type="button" aria-label="Open menu">…</button>
  </div>
</header>
```

On earthedenergy.au, point `.nav-sister` at `https://www.earthedhv.au` and label it **Earthed High Voltage**. Keep the same order: wordmark, primary nav, sister link, quote (or the Energy equivalent primary action).

## Footer

Ink background. Four columns from 900px up: brand blurb, navigate, contact, the group. Under a hairline: the SA licence line on the High Voltage site, and the copyright.

The group column always cross-links:

- High Voltage footer links to `https://earthedenergy.au` as Earthed Energy, with the line "Part of the Earthed Energy group" and "Solar and battery".
- Energy footer links back to `https://www.earthedhv.au` as Earthed High Voltage, with "High voltage electrical".

Licence line on this site, verbatim structure: `SA electrical contractor licence PGE 336477 · ABN 99 679 180 879 · ACN 679 180 879`. The Energy site should show its own licence if it has one, in the same position, not this number.

## Forms

Underline fields, not boxes. Mono uppercase label at 0.72rem, tracked. 1.5px rule in `--color-line-strong`. Focus outline 2px purple, offset 4px. Errors use `--color-danger` and `role="alert"`. Submit is `.btn.btn-primary`.

## Motion

- Hero photograph may drift from scale 1 to 1.05 over 36s. Overflow hidden on the frame.
- Below-fold blocks may rise 18px and fade if the browser supports `animation-timeline: view()`. Do not animate the hero headline. It is the LCP text.
- Card image scale on hover, link underline grows from the left (`background-size`).
- `@media (prefers-reduced-motion: reduce)` removes animation and transition.

## What not to change between the two sites

- The purple `#553A66`, the paper `#F6F3EF`, the ink `#160E1E`.
- The three typefaces and the display scale.
- Button shapes, the 76px header, the sister-link position, the footer columns.
- The 2px radius and the 1px rules.

Photography, page titles, services and the phone number stay with each company.
