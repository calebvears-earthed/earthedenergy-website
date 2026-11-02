import fs from "node:fs";
import path from "node:path";
import { groups as rawGroups } from "../mockups-src/knowledge-index.js";
import {
  defaultProps,
  expand,
  loadImageMap,
  rewriteTreeUrls,
  runComponent,
  stripChrome,
} from "./dc_engine.mjs";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const SRC = path.join(ROOT, "mockups-src");

const PRODUCTION = {
  "Earthed Energy Home v5": "index.html",
  "About Caleb Vears": "about-caleb-vears.html",
  "About Earthed Energy": "about-earthed-energy.html",
  "About Troy Hooker": "about-troy-hooker.html",
  "Aircon Hot Water": "aircon-hot-water.html",
  "Battery Sizing": "battery-sizing.html",
  "Battery Storage": "battery-storage.html",
  "Bushfire Prone Areas": "bushfire-prone-areas.html",
  "Commercial": "commercial.html",
  "Commissioning and Handover": "commissioning-and-handover.html",
  "Credentials and Licences": "credentials-and-licences.html",
  "EV Charging": "ev-charging.html",
  "Earthed History": "earthed-history.html",
  "Federal Rebates Explained": "federal-rebates-explained.html",
  "Finance Options": "finance-options.html",
  "Get a Quote": "get-a-quote.html",
  "GoodWe vs Sigenergy": "goodwe-vs-sigenergy.html",
  "How Much You Save": "how-much-you-save.html",
  "Installation Day": "installation-day.html",
  "Inverters": "inverters.html",
  "Knowledge": "knowledge.html",
  "Monitoring Apps": "monitoring-apps.html",
  "Off-grid vs Grid-connect": "off-grid-vs-grid-connect.html",
  "Off-grid": "off-grid.html",
  "Outage Backup": "outage-backup.html",
  "Racking and Cable": "racking-and-cable.html",
  "Reading Your Power Bill": "reading-your-power-bill.html",
  "Residential": "residential.html",
  "SA Export Limits": "sa-export-limits.html",
  "SAPN Flexible Export": "sapn-flexible-export.html",
  "SWER Lines": "swer-lines.html",
  "Shade and Roof Orientation": "shade-and-roof-orientation.html",
  "Solar Panels": "solar-panels.html",
  "Three-phase vs Single-phase": "three-phase-vs-single-phase.html",
  "Typical Timeline": "typical-timeline.html",
  "Warranty and Aftercare": "warranty-and-aftercare.html",
  "What Solar Does": "what-solar-does.html",
  "What We Install": "what-we-install.html",
  "What a Battery Does": "what-a-battery-does.html",
  "Whole-home Backup Explained": "whole-home-backup-explained.html",
  "Why We Do This": "why-we-do-this.html",
};

const DESIGN = {
  "Earthed Energy Home": "home.html",
  "Earthed Energy Home v2": "home-v2.html",
  "Earthed Energy Home v3": "home-v3.html",
  "Earthed Energy Home v4 After Dark": "home-v4-after-dark.html",
  "Earthed Way Options": "earthed-way-options.html",
  "Footer Options": "footer-options.html",
  "Quote Step Options": "quote-step-options.html",
  "Solar Calculator Options": "solar-calculator-options.html",
  "Hero Coastal Trials": "hero-coastal-trials.html",
  "Hero Purple Explorations": "hero-purple-explorations.html",
  "Sub-page Sample A - lavender": "sub-page-sample-a.html",
  "Sub-page Sample B - lavender - navy bands": "sub-page-sample-b.html",
};

const ABOUT = new Set(["About Caleb Vears", "About Earthed Energy", "About Troy Hooker", "Why We Do This", "Earthed History"]);

function sectionFor(name) {
  if (name === "Earthed Energy Home v5") return "home";
  if (name === "Residential") return "residential";
  if (name === "Commercial") return "commercial";
  if (name === "Off-grid") return "off-grid";
  if (name === "Get a Quote") return "quote";
  if (ABOUT.has(name)) return "about";
  if (name === "Knowledge" || PRODUCTION[name]) return "knowledge";
  return "";
}

function pageMap() {
  const map = new Map();
  for (const [name, file] of Object.entries(PRODUCTION)) {
    map.set(name + ".dc.html", file === "index.html" ? "/" : "/" + file);
  }
  map.set("How We Quote.dc.html", "/how-we-quote.html");
  for (const [name, file] of Object.entries(DESIGN)) {
    map.set(name + ".dc.html", "/design/" + file);
  }
  return map;
}

function webpSize(buf) {
  if (buf.length < 30) return null;
  if (buf.toString("ascii", 0, 4) !== "RIFF" || buf.toString("ascii", 8, 12) !== "WEBP") return null;
  const tag = buf.toString("ascii", 12, 16);
  if (tag === "VP8X") return { w: 1 + buf.readUIntLE(24, 3), h: 1 + buf.readUIntLE(27, 3) };
  if (tag === "VP8 ") return { w: buf.readUInt16LE(26) & 0x3fff, h: buf.readUInt16LE(28) & 0x3fff };
  if (tag === "VP8L") {
    const b0 = buf[21], b1 = buf[22], b2 = buf[23], b3 = buf[24];
    return {
      w: 1 + (((b1 & 0x3f) << 8) | b0),
      h: 1 + (((b3 & 0x0f) << 10) | (b2 << 2) | ((b1 & 0xc0) >> 6)),
    };
  }
  return null;
}

function loadDims(imageMap) {
  const dims = new Map();
  for (const rel of new Set(imageMap.values())) {
    const file = path.join(ROOT, rel);
    if (!fs.existsSync(file)) continue;
    const size = webpSize(fs.readFileSync(file));
    if (size) dims.set("/" + rel, size);
  }
  return dims;
}

function extract(raw) {
  const title = (raw.match(/<title>([\s\S]*?)<\/title>/) || [, ""])[1].replace(/\s+/g, " ").trim();
  const description = (raw.match(/<meta name="description" content="([\s\S]*?)"/) || [, ""])[1].trim();
  const helmet = (raw.match(/<helmet[^>]*>([\s\S]*?)<\/helmet>/) || [, ""])[1];
  const css = [...helmet.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map((m) => m[1]).join("\n");
  const propsRaw = (raw.match(/data-props="([\s\S]*?)"/) || [, ""])[1];
  const scriptMatch = raw.match(/<script[^>]*data-dc-script[^>]*>([\s\S]*?)<\/script>/);
  const script = scriptMatch ? scriptMatch[1].trim() : "";
  const bodyMatch = raw.match(/<\/helmet>([\s\S]*?)<script[^>]*data-dc-script/);
  const body = bodyMatch ? bodyMatch[1] : (raw.match(/<\/helmet>([\s\S]*?)<\/x-dc>/) || [, ""])[1];
  return { title, description, css, propsRaw, script, body };
}

const groups = rawGroups.map((group) => ({
  ...group,
  items: group.items.map(([file, title, blurb]) => [
    file,
    title,
    blurb.replaceAll("10-year workmanship", "7-year workmanship"),
  ]),
}));

const pages = pageMap();
const imageMap = loadImageMap(fs.readFileSync(path.join(SRC, "IMAGE_MAP.csv"), "utf8"));
const dims = loadDims(imageMap);
const ctx = { pageMap: pages, imageMap, dims };
const outDir = path.join(ROOT, "build", "expanded");
fs.mkdirSync(outDir, { recursive: true });

const files = fs.readdirSync(SRC).filter((name) => name.endsWith(".dc.html"));
const manifest = [];
for (const file of files) {
  const name = file.replace(/\.dc\.html$/, "");
  const design = Object.prototype.hasOwnProperty.call(DESIGN, name);
  const production = Object.prototype.hasOwnProperty.call(PRODUCTION, name);
  if (!design && !production) {
    console.error("UNMAPPED", file);
    continue;
  }
  const raw = fs.readFileSync(path.join(SRC, file), "utf8");
  const extracted = extract(raw);
  const stripped = stripChrome(extracted.body);
  const template = rewriteTreeUrls(stripped.html, pages, imageMap);
  const footer = rewriteTreeUrls(stripped.footer, pages, imageMap);
  let scope = {};
  let error = "";
  if (extracted.script.includes("class Component")) {
    try {
      scope = runComponent(extracted.script, defaultProps(extracted.propsRaw), groups);
    } catch (err) {
      error = err.stack || String(err);
    }
  }
  let html = template;
  if (!error) {
    try {
      html = expand(template, scope, ctx).html;
    } catch (err) {
      error = err.stack || String(err);
    }
  }
  const outFile = design ? "design/" + DESIGN[name] : PRODUCTION[name];
  const record = {
    name,
    file,
    outFile,
    design,
    section: sectionFor(name),
    title: extracted.title,
    description: extracted.description,
    css: extracted.css,
    body: html,
    footer,
    hydrate: name === "Get a Quote",
    template: name === "Get a Quote" ? template : "",
    script: name === "Get a Quote" ? extracted.script : "",
    error,
  };
  const dest = path.join(outDir, name.replace(/[^\w]+/g, "-").toLowerCase() + ".json");
  fs.writeFileSync(dest, JSON.stringify(record));
  manifest.push({ name, outFile, design, error: error ? error.split("\n")[0] : "", bytes: html.length, footer: footer.length });
  console.log(`${error ? "FAIL" : "ok  "} ${outFile} body=${html.length} footer=${footer.length}${error ? " " + error.split("\n")[0] : ""}`);
}
fs.writeFileSync(path.join(outDir, "_manifest.json"), JSON.stringify(manifest, null, 2));
