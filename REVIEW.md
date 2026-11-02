# Live site review

Reviewed 2 November 2026 against production at https://www.earthedenergy.au (all 45 sitemap URLs returned 200) and the matching source. Desktop and mobile were checked on Home, About, Residential, Knowledge, and SolarCare.

The subpage header change in this branch is the only fix. Everything below is left open.

Checked and clear on the rebuilt pages (Home and the mockup pages, not SolarCare or the walkthrough): no em dashes, workmanship warranty is 7 years, no "SAPN Accredited" and no "CEC accredited", email is calebvears@earthedhv.au, phone is 0433 839 284, footer legal line is "Earthed High Voltage Pty Ltd (ABN 99 679 180 879) trading as Earthed Energy Co". Internal links on those pages resolve. `robots.txt` disallows `/design/` and `/thanks.html`. Design explorations stay noindex.

## Critical

1. **Quote wizard does not save a lead.** Page: `/get-a-quote.html` (every "Calculate savings" button). Fix: the final step only `console.log`s the payload and opens `mailto:calebvears@earthedhv.au`. The source still says `TODO: POST to Resend / Supabase`. If the visitor has no mail app, or the popup is blocked, the lead is gone and the page still advances to the thank-you step. Post the payload to an inbox Caleb actually reads, and only then show success.

2. **Both booking links 404.** Page: `/get-a-quote.html`. Fix: "Book a call" points at `https://calendly.com/earthedenergy/15min`, and the calendar step points at `https://calendly.com/earthedenergy/energy-assessment`. Both returned 404 on 2 November 2026. Replace them with a live Calendly event, or remove the buttons until one exists.

3. **Wrong legal identity on the old pages.** Pages: `/solarcare/` and `/walkthrough/`. Fix: the footer says "Earthed Energy Co Pty Ltd", ABN 92 691 065 460, ACN 691 065 460, and the street address "26 Wanbrow Ave, Wattle Park". The rest of the site says Earthed High Voltage Pty Ltd (ABN 99 679 180 879) trading as Earthed Energy Co, post to PO Box 4111, Norwood South SA 5067. Replace the footer, or take these two URLs out of the sitemap until they match.

4. **Walkthrough claims "SAPN approved".** Page: `/walkthrough/`. Fix: the trust line lists "SAPN approved" and "NETCC approved seller". That is the accreditation wording the rest of the site was built to avoid. Credentials (`/credentials-and-licences.html`) says the NETCC seller application is "in progress", and SAPN wording elsewhere is "designs to SAPN requirements". Delete or rewrite those two chips.

5. **SolarCare brochure links 404.** Page: `/solarcare/`. Fix: both PDFs 404 on production: `/solarcare/brochures/EE-Brochure-01-Panel-Cleaning-Service.pdf` and `/solarcare/brochures/EE-Brochure-02-Bird-Proofing-Service.pdf`. Upload the files or remove the links.

## High

6. **Contact form depends on a third party, with no privacy notice.** Page: `/contact.html`. Fix: the form POSTs to `https://formsubmit.co/calebvears@earthedhv.au` with `_captcha=false` and `_next` to `/thanks.html`. Leads only arrive if FormSubmit has been activated for that address. There is no privacy policy, no terms page (`/privacy.html` and `/terms.html` 404), and no line telling the visitor the message is handled by FormSubmit. Add a short privacy notice, turn captcha on, and confirm a test message lands in calebvears@earthedhv.au.

7. **Walkthrough form can show success when the send fails.** Page: `/walkthrough/`. Fix: the form POSTs to Formspree `https://formspree.io/f/xlgybzag` (the endpoint exists; GET returns 405). The script calls `showThanks()` on both success and failure, so a blocked request still looks sent. Show an error when the POST fails, and confirm the Formspree form is still delivered to Caleb.

8. **Rebate calculator never submits.** Page: `/federal-rebates-explained.html`. Fix: the sliders only update the on-page estimate (STC and Cheaper Home Batteries, client side). Nothing is stored. That is fine if the page says so. Do not treat it as a lead form. The quote wizard's price step is the same kind of local estimate.

9. **Legacy pages are a second website.** Pages: `/solarcare/`, `/walkthrough/`, both in `sitemap.xml`. Fix: they still use the old header (Packages, Guides, SolarCare, Contact), Instrument fonts, and a sister link to `https://www.earthedhv.au`. "Packages" goes to `/#packages`, which does not exist on the new Home, so it dumps the visitor at the top of Home. Rebuild them in the current chrome, or noindex them and drop them from the sitemap until that happens.

10. **Mobile menu does nothing on those two pages.** Pages: `/solarcare/`, `/walkthrough/`, under 900px. Fix: `.nav-toggle` is visible and the desktop links are hidden, but `assets/js/site.js` only opens `[data-ee-menu]`. Clicking the button leaves `#mobile-nav` hidden. Wire the old toggle, or replace the header with the current one. The bottom Call / Request a quote bar still works.

11. **NETCC logo versus the credentials table.** Pages: footer on every rebuilt page, and `/credentials-and-licences.html`. Fix: the footer image alt is "New Energy Tech Approved Seller", while the credentials table says the NETCC application is "in progress". Same clash as the walkthrough chip. Remove the logo until the code is granted, or change the alt and the table so they say the same thing.

12. **Warranty terms do not match the scenario cards.** Pages: `/warranty-and-aftercare.html` versus `/residential.html` scenario B. Fix: the warranty table says inverter 10 years and battery 10 years to 70 percent, for GoodWe or Sigenergy. Scenario B says "Sigenergy SigenStor 15 kW 3-phase, 12-yr warranty" and "SigenStor BAT, 15-yr warranty". Make the table name the longer Sigenergy terms, or stop quoting 12 and 15 on the scenario card.

13. **"CEC-approved" on the off-grid tier.** Page: `/off-grid.html`. Fix: tier 1 is labelled "CEC-approved off-grid". That is not the banned phrase "CEC accredited", and `/solar-panels.html` plus `/sa-export-limits.html` say "CEC-listed" about products, which is the product list. "CEC-approved" on a tier name reads like a company accreditation. Rename the tier after Caleb confirms what it is meant to mean.

14. **No social image, and LocalBusiness only on Home.** Pages: every rebuilt page, plus `/`. Fix: production pages have title, description, canonical, and `og:title` / `og:description`, and no `og:image` or Twitter card. `/images/og-home.jpg` exists and is only referenced by SolarCare and the walkthrough. Add one 1200x630 image to the shared head. Home JSON-LD is `Electrician` + `LocalBusiness` with email, phone, PO Box, and area served. It has no logo, no photo, and no opening hours, and `streetAddress` is a PO Box, so Google may not draw a map pin. Repeat a slimmer LocalBusiness (or point `WebPage` at the Home entity) on the other commercial pages.

15. **Titles are longer than the snippet.** Pages: most guides. Fix: many `<title>` values run past 60 characters and several past 90 (`/what-we-install.html` is 102, `/warranty-and-aftercare.html` is 100). Keep the suburb and the offer, cut the equipment list out of the title, leave it in the description.

16. **No Google Business link.** Pages: Home, Contact, footer. Fix: nothing points at a Maps or Google Business profile. Add the profile URL next to the phone and PO Box once Caleb confirms the listing. Do not invent the URL.

17. **Placeholder slots are live.** Fix: swap the grey boxes for real photos, or hide the sections until the files exist.
    - `/about-caleb-vears.html`: "Caleb on site, portrait (Caleb to add)"
    - `/about-troy-hooker.html`: "Troy on site, portrait (Caleb to add)"
    - `/earthed-history.html`: "Caleb on the first Earthed job" and "Early site photo, Goyder South or Port Wakefield"
    - `/monitoring-apps.html`: "Real dashboard screenshots, SEMS and mySigen (Caleb to add)"
    - `/reading-your-power-bill.html`: "Anonymised SA power bill, five numbers circled (Caleb to add)"

18. **How we quote is a stub in the knowledge hub.** Page: `/how-we-quote.html`. Fix: the lede is "Content coming. Caleb is writing this guide." It is linked from Knowledge and listed in the sitemap. Write the guide, or mark the hub card as coming and noindex the URL.

19. **No reviews and no real case studies.** Pages: Home, Residential, Commercial, Off-grid. Fix: trust on the new pages is the licence, the 7-year workmanship line, the partner strip, and the phone number. Scenario cards are labelled as Adelaide averages ("your written quote will land inside 15%"), which is honest, and they are not named jobs. There is no review, no star rating, and no link to Google reviews. Add two or three real jobs (suburb, system, outcome Caleb will stand behind) and a Google review link. Residential also shows "$0 upfront at $333 per month for 24 months". That needs the lender's comparison rate and a pointer to `/finance-options.html`, not only the asterisk already on the card.

20. **Contrast and heading order fail on the scenario pages.** Lighthouse mobile, this branch, simulated. Fix: muted 11px labels (`rgba(43,21,80,.55)`) fail contrast on Residential, Commercial, Off-grid, and Knowledge. Scenario cards jump to an `h3` with no `h2` (Residential and Commercial accessibility 93). The quote progress element uses `aria-label` on a plain `div` (accessibility 95). SolarCare `.fine` fails contrast (accessibility 96). Home, About, and Warranty scored accessibility 100. Darken the meta text, wrap scenario blocks in an `h2`, and put the progress label on text instead of ARIA.

21. **Photo pages miss the performance bar.** Same Lighthouse run. Fix: compress the LCP photo and give it a preload. Measured mobile scores: Home 98 (LCP 2.4s), About 100 (1.5s), Warranty 100 (1.9s), Knowledge 99 (2.0s), Off-grid 99 (2.0s), SolarCare 99 (1.7s), Residential 96 (2.9s), Commercial 89 (3.8s), Quote 88 (3.8s). Text guides ship about 420KB (shared dusk footer plus the font) and should sit with Warranty. Heavier pages: About about 3MB (the photo strip), Quote about 1.3MB, Off-grid about 0.9MB, Aircon about 0.9MB, Commercial about 0.8MB, GoodWe vs Sigenergy about 0.7MB, Residential about 0.6MB. Home references about 10MB of photos; below-the-fold ones wait until idle, which is why the lab score is 98. Commercial and the quote page are the ones to compress first.

## Nice to have

22. **CTA label is split.** Header and the mobile bar say "Calculate savings". The footer button still says "Get a quote, 45 seconds", and `/how-we-quote.html` says "Get a quote". All of them go to `/get-a-quote.html`. Use one label.

23. **Section sidebars still stick 96px down.** Pages: Knowledge group labels, warranty sidebars, scenario rails. Fix: `position: sticky; top: 96px` was sized for the old sticky header. Now that the subpage header scrolls away, those rails float with an empty gap. Drop the offset to the top of the viewport.

24. **"Full terms" is the warranty page.** Page: Home price footnote. Fix: the link labelled "Full terms" goes to `/warranty-and-aftercare.html`, which is the warranty explainer, not a contract. Point it at real terms once those exist, or rename the link "Warranty and aftercare".

25. **No analytics, so no cookie banner.** All pages. Fix: no gtag, GTM, Meta pixel, or other tracker in the HTML or `site.js`. A cookie banner is not required until a tracker is added. When one is added, add the banner and a privacy page in the same change. Until then, quote and contact conversion cannot be measured.

26. **Home is the only page with structured data.** Covered in item 14. Also add `BreadcrumbList` on the guides. The visible breadcrumb is already there.

27. **Unused originals in `/images`.** About 56 files, about 13MB, are not referenced by any page (`residential-install-hero.jpg` at 1.2MB, `residential-rooftop.jpg` at 1.2MB, and the `install-*.jpg` set). They do not slow the live site. Delete them from the deploy, or move them out of `images/`, so they are not easy to hotlink by filename.

28. **`data-screen-label` on two pages is the commercial string.** Pages: `/residential.html` and `/off-grid.html`. Fix: the attribute value is "Commercial solar Adelaide, utility-grade design and install". It is not visible. The visible headings are "Residential" and "Off-grid". Correct the attribute so it matches the page.

29. **Superative on Off-grid.** Page: `/off-grid.html`, tier 3: "The world's best off-grid inverter." Fix: soften unless Caleb wants that claim in public.

30. **Design archive.** `/design/` is noindex and disallowed. Leave it that way. Those files still contain em dashes and the old copy on purpose.
