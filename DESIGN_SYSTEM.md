# Earthed design system

Shared visual language for **earthedenergy.au** (residential solar and battery) and **earthedhv.au** (high voltage, wind and BESS). The high-voltage site did not have a `DESIGN_SYSTEM.md` on `main` or `feat/mobile-plus-forms` when this file was written. This is the token set both sites should follow. The live high-voltage page currently uses a darker purple (`#3B2660` / `#5E2D89`) and the same type families; new work should move to the tokens below.

## Colour

| Token | Value | Use |
| --- | --- | --- |
| `--purple` | `#553A66` | Primary. Buttons, header accents, footer, links |
| `--purple-deep` | `#3E284C` | Button hover, photo fallback |
| `--paper` | `#F6F3EE` | Page background |
| `--paper-2` | `#EFEAE3` | Quiet bands |
| `--white` | `#FFFCF8` | Cards |
| `--ink` | `#24182F` | Body text |
| `--ink-soft` | `#3E3348` | Secondary text. Stays above WCAG AA on `--paper` |
| `--lilac` | `#E7D6F4` | Text and eyebrows on purple. Do not use `#C9A7E8` for small text on `#553A66` |
| `--line` | `rgba(85, 58, 102, 0.2)` | Hairline borders |

White on `#553A66` is about 9.6:1. `#553A66` on `#F6F3EE` is about 8.8:1.

## Type

| Role | Family | Notes |
| --- | --- | --- |
| Display | Josefin Sans | 400. Headings. `letter-spacing: -0.02em` |
| Body | Open Sans | 400 body, 600 emphasis. 17px / 1.65 |
| Meta | JetBrains Mono | 500. Eyebrows, buttons, captions. 11px, tracking `0.16em–0.18em`, uppercase |

Self-host the latin woff2 files. `font-display: swap`. Do not load a font from a third-party stylesheet.

### Scale

| Token | Size |
| --- | --- |
| `--step-1` | 0.6875rem |
| `--step-2` | 0.875rem |
| `--step-3` | 1.0625rem |
| `--step-4` | 1.25rem |
| `--step-5` | 1.5rem |
| `--step-6` | clamp(1.75rem, 2.4vw, 2.25rem) |
| `--step-7` | clamp(2.15rem, 3.6vw, 3.15rem) |
| `--step-8` | clamp(2.6rem, 5.4vw, 4.5rem) |

## Space

4, 8, 12, 16, 24, 32, 48, 64, 96 px, as `--space-1` through `--space-9` in rem. Page padding is 96px desktop, 64px under 720px. Content width `--content: 1120px`. Reading measure `--measure: 68ch`. Header height `--header-h: 76px`.

## Components

**Buttons.** Filled `#553A66`, white mono label, 2px radius, min-height 48px, padding `0.75rem 1.25rem`. Hover `#3E284C`. Ghost is transparent with a purple border. On a purple band, invert to white fill and purple text.

**Cards.** `--white` background, 1px `--line` border, 2px radius, padding 24px. Hover only changes the border colour. No drop shadow.

**Header.** Fixed, paper at 92% opacity, 16px blur, bottom hairline. Logo left, mono links, one button. Under 720px the links collapse behind a Menu button with `aria-expanded`.

**Footer.** Full-bleed `#553A66`, white text, four columns (brand, visit, company, contact), then a legal line and a sister-site strip. Energy links to `https://earthedhv.au/`. High voltage links to `https://www.earthedenergy.au/`.

**Forms.** Mono labels above the field. Inputs are underline only (`1.5px` at 45% purple), 16px type, no grey placeholder as the only label. Focus ring is a 2px purple outline. Choice chips are 44px tall.

**Motion.** Opacity and 12px translate, 560ms, only after a `.js` class, only when `prefers-reduced-motion` is off. No looping pulses.

## Cross-link

Energy footer line: “Part of the Earthed group” and “High voltage, wind and BESS · earthedhv.au”.

High voltage should mirror it: “Residential solar and battery · earthedenergy.au”.
