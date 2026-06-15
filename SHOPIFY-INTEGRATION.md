# Purple Earth — Shopify Integration Plan
**Built 15 June 2026 · Arc**

The `index.html` is a complete launch page. Now it needs to plug into Shopify so the cart, checkout, products, and loyalty actually work. Two paths.

---

## Path A — Drop into Shopify as a custom theme section (recommended)

**What:** Convert the HTML into Shopify Liquid templates. The site becomes a custom Shopify theme. Customers shop, cart, check out — all native Shopify. Same look exactly.

**Steps next session:**
1. Spin up a Shopify Partner store (free for dev)
2. Create new theme directory: `templates/`, `sections/`, `snippets/`, `layout/`, `assets/`, `config/`
3. Move:
   - `index.html` body → `sections/` split (one section per visual block: hero, thesis, categories, featured, etc.)
   - Embedded CSS → `assets/theme.css`
   - JavaScript → `assets/theme.js`
4. Replace static product cards with Liquid loops:
   ```liquid
   {% for product in collections.featured.products limit: 6 %}
     <a href="{{ product.url }}" class="product-card">
       <div class="product-img">
         <img src="{{ product.featured_image | image_url: width: 800 }}" alt="{{ product.title }}">
       </div>
       <div class="product-cat">{{ product.type }}</div>
       <div class="product-name">{{ product.title }}</div>
       <div class="product-price">{{ product.price | money }}</div>
     </a>
   {% endfor %}
   ```
5. Wire the cart icon to `{{ cart.item_count }}`
6. Newsletter form → connect to Klaviyo or native Shopify customer creation
7. Push to Shopify via `shopify theme push`
8. Deploy on `purpleearth.com.au`

**Pros:** Native Shopify cart + checkout (AppleSamsung/PayPal/cards all work), product inventory from Shopify admin, native variants, native discount codes, native taxes.

**Cons:** ~2 hours of Liquid templating work.

---

## Path B — Headless: Next.js + Shopify Storefront API

**What:** Keep the React/HTML site as-is, connect to Shopify products via GraphQL Storefront API. Checkout still happens on Shopify (their hosted checkout).

**Pros:** Faster page loads, total design freedom, can host on Vercel (same flow as Earthed Energy).

**Cons:** More setup. Requires Node.js + Next.js scaffolding. Worth it long-term if Purple Earth scales.

**Recommendation:** Do Path A for launch (faster to ship). Migrate to Path B in v2 if/when traffic justifies it.

---

## What Caleb owns this week

1. **Create a Shopify store** at shopify.com — Basic plan ($38/mo AU) is enough to start
2. **Buy the domain** `purpleearth.com.au` if not already owned (GoDaddy or Crazy Domains)
3. **Generate the 6 Higgsfield visuals** from `Higgsfield-Brand-Visual-Pack-v1.md`
4. **Drop the visuals** into `_PurpleEarth/site/images/` with these filenames:
   - `hero-1.jpg` — main hero
   - `lifestyle-2.jpg` — interlude section
   - `loyalty-4.jpg` — Earth Points section
   - `divider-5.jpg` — between sections
   - Plus any product flatlay shots → individual product card slots

---

## What Arc owns next session

Once Caleb has the Shopify store + domain + visuals:

1. Convert the HTML to Shopify Liquid theme (~2 hours)
2. Create the 5 collections in Shopify Admin (Grounding / Strength / Hydration / Audio / Sleep)
3. Add 6-10 hero products to the Featured collection
4. Wire Spocket integration for dropship products → Shopify auto-imports
5. Install Smile.io for Earth Points loyalty programme
6. Configure shipping zones (free over $99 AU, flat $9.99 below)
7. Connect Klaviyo for the newsletter
8. Test full checkout flow with a $1 test product
9. Deploy theme → publish → point domain
10. Soft launch — friends + family link

Target: site live at `purpleearth.com.au` within 5 business days of Caleb completing his side.

---

## Tonight's deliverable

The `index.html` you can open right now in any browser to preview the entire experience. Everything is placeholder text + colour-block category tiles — once the Higgsfield visuals drop in, it's launch-ready visually.

To preview now:
```
open "/Users/calebvearsdot/Library/CloudStorage/OneDrive-earthedhv.au/000 claude unearthed/_PurpleEarth/site/index.html"
```

Sleep on it. Tomorrow's the build.
