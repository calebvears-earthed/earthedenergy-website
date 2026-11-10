/**
 * Expand design-canvas mockups (sc-for, sc-if, {{ }} and image-slot)
 * into static HTML. The same module hydrates the quote wizard in the browser.
 */
export const EMPTY_SLOTS = new Set([
  "caleb-portrait",
  "troy-portrait",
  "history-hero",
  "history-site",
  "app-screens",
  "bill-annotated",
]);

const VOID = new Set(["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]);

const OUTPUT_KEYS = new Set([
  "kwLabel", "batLabel", "stcLine", "chbLine", "totalLine", "stcSub", "chbSub", "totalSub", "countLabel",
]);

const INPUT_EXPR = { setKw: "kw", setBat: "bat" };

export function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function loadImageMap(csvText) {
  const map = new Map();
  const lines = csvText.trim().split(/\r?\n/).slice(1);
  for (const line of lines) {
    const comma = line.indexOf(",");
    const comma2 = line.indexOf(",", comma + 1);
    if (comma < 0 || comma2 < 0) continue;
    map.set(line.slice(0, comma), line.slice(comma + 1, comma2));
  }
  return map;
}

function unwrap(value) {
  const m = String(value ?? "").match(/^\s*\{\{([\s\S]*?)\}\}\s*$/);
  return m ? m[1].trim() : null;
}

export function rewriteHref(href, pageMap) {
  if (!href || /^(mailto:|tel:|https?:|javascript:)/i.test(href)) return href;
  const hash = href.indexOf("#");
  const q = href.indexOf("?");
  let cut = href.length;
  if (hash >= 0) cut = Math.min(cut, hash);
  if (q >= 0) cut = Math.min(cut, q);
  const pathPart = href.slice(0, cut);
  const rest = href.slice(cut);
  const file = decodeURIComponent(pathPart.replace(/^\.\//, ""));
  if (!file.endsWith(".dc.html")) return href;
  const dest = pageMap.get(file);
  return dest ? dest + rest : href;
}

const SLOT_ALIAS = new Map([
  ["img-work/solar-transparent.png", "images/slot-img-solar.webp"],
  ["img-work/sigenergy-transparent.png", "images/slot-img-battery.webp"],
  ["img-work/ev-transparent.png", "images/slot-img-ev.webp"],
  ["img-work/aircon2-transparent.png", "images/slot-img-aircon.webp"],
  ["slot-images/img-solar.webp", "images/slot-img-solar.webp"],
  ["slot-images/img-battery.webp", "images/slot-img-battery.webp"],
  ["slot-images/img-ev.webp", "images/slot-img-ev.webp"],
  ["slot-images/img-aircon.webp", "images/slot-img-aircon.webp"],
  ["slot-images/img-solarcare.webp", "images/slot-img-solarcare.webp"],
]);

export function rewriteSrc(src, imageMap) {
  if (!src || /^(https?:|data:|mailto:|tel:|#|\/)/i.test(src)) return src;
  if (src.includes("{{")) return src;
  const key = decodeURIComponent(src).replace(/^\.\//, "").split("?")[0];
  if (SLOT_ALIAS.has(key)) return "/" + SLOT_ALIAS.get(key);
  if (imageMap.has(key)) return "/" + imageMap.get(key);
  return null;
}

function isReactEl(value) {
  return value && typeof value === "object" && value.$$typeof === "el";
}

function isRef(value) {
  return value && typeof value === "object" && Object.keys(value).length === 1 && "current" in value;
}

export function makeReact() {
  class Component {
    constructor(props) {
      this.props = props || {};
    }
    setState(partial) {
      const patch = typeof partial === "function" ? partial(this.state || {}) : partial;
      this.state = { ...(this.state || {}), ...patch };
    }
  }
  function createElement(type, props, ...children) {
    return { $$typeof: "el", type, props: props || {}, children: children.flat(Infinity) };
  }
  return {
    Component,
    createElement,
    createRef() {
      return { current: null };
    },
  };
}

export function renderReact(node) {
  if (node == null || node === false || node === true) return "";
  if (Array.isArray(node)) return node.map(renderReact).join("");
  if (typeof node === "number" || typeof node === "string") return escapeHtml(node);
  if (!isReactEl(node)) return "";
  if (typeof node.type === "function") {
    const inst = new node.type(node.props);
    inst.props = { ...(node.props || {}), children: node.children };
    if (!inst.state) inst.state = {};
    return renderReact(inst.render());
  }
  const attrs = node.props || {};
  let html = "<" + node.type;
  for (const [key, val] of Object.entries(attrs)) {
    if (val == null || val === false || key === "children") continue;
    html += ` ${key}="${escapeHtml(val)}"`;
  }
  html += ">";
  html += (node.children || []).map(renderReact).join("");
  if (!VOID.has(node.type)) html += `</${node.type}>`;
  return html;
}

export function evalExpr(expr, scope) {
  const keys = Object.keys(scope);
  const fn = new Function(...keys, `"use strict"; return (${expr});`);
  return fn(...keys.map((key) => scope[key]));
}

function interpolateValue(expr, scope) {
  try {
    return evalExpr(expr, scope);
  } catch (error) {
    return undefined;
  }
}

export function expand(html, scope, ctx) {
  const owned = !ctx._bag;
  if (owned) ctx._bag = { handlers: [], refs: [] };
  const state = { i: 0, html, heroUsed: false, handlers: ctx._bag.handlers, refs: ctx._bag.refs };
  const out = parseNodes(state, scope, ctx, null);
  const result = { html: out, handlers: ctx._bag.handlers, refs: ctx._bag.refs };
  if (owned) delete ctx._bag;
  return result;
}

function parseNodes(state, scope, ctx, stopTag) {
  let out = "";
  const html = state.html;
  while (state.i < html.length) {
    if (stopTag && html.startsWith("</" + stopTag, state.i)) {
      const end = html.indexOf(">", state.i);
      state.i = end + 1;
      return out;
    }
    if (html[state.i] === "<") {
      if (html.startsWith("<!--", state.i)) {
        const end = html.indexOf("-->", state.i);
        out += html.slice(state.i, end + 3);
        state.i = end + 3;
        continue;
      }
      const tag = readTag(state);
      if (tag.closing) continue;
      const lname = tag.name.toLowerCase();
      if (lname === "sc-for") {
        const listExpr = unwrap(tag.attrs.list || "") || "[]";
        const as = tag.attrs.as || "item";
        const inner = readInner(state, "sc-for");
        let list = [];
        try { list = evalExpr(listExpr, scope) || []; } catch { list = []; }
        if (!Array.isArray(list)) list = [];
        list.forEach((item, index) => {
          out += expand(inner, { ...scope, [as]: item, index }, ctx).html;
        });
        continue;
      }
      if (lname === "sc-if") {
        const valueExpr = unwrap(tag.attrs.value || "") || "false";
        const inner = readInner(state, "sc-if");
        let show = false;
        try { show = !!evalExpr(valueExpr, scope); } catch { show = false; }
        if (show) out += expand(inner, scope, ctx).html;
        continue;
      }
      if (lname === "image-slot") {
        out += renderSlot(tag, scope, ctx);
        if (!tag.selfClosing) readInner(state, "image-slot");
        continue;
      }
      const emitted = emitOpen(tag, scope, ctx, state);
      if (lname === "img") {
        out += `<picture style="display:contents">${emitted.open}</picture>`;
        continue;
      }
      out += emitted.open;
      if (!tag.selfClosing && !VOID.has(lname)) {
        out += parseNodes(state, scope, ctx, lname);
        out += `</${tag.name}>`;
      }
      continue;
    }
    const next = html.indexOf("<", state.i);
    const text = html.slice(state.i, next === -1 ? html.length : next);
    state.i = next === -1 ? html.length : next;
    out += interpolateText(text, scope, ctx);
  }
  return out;
}

function readInner(state, tagName) {
  const start = state.i;
  let depth = 1;
  while (state.i < state.html.length && depth > 0) {
    if (state.html.startsWith("<!--", state.i)) {
      state.i = state.html.indexOf("-->", state.i) + 3;
      continue;
    }
    if (state.html[state.i] !== "<") {
      state.i += 1;
      continue;
    }
    const before = state.i;
    const tag = readTag(state);
    if (tag.name.toLowerCase() !== tagName) continue;
    if (tag.closing) depth -= 1;
    else if (!tag.selfClosing) depth += 1;
    if (depth === 0) return state.html.slice(start, before);
  }
  return state.html.slice(start);
}

function readTag(state) {
  const html = state.html;
  if (html[state.i] !== "<") throw new Error("expected tag at " + state.i);
  state.i += 1;
  const closing = html[state.i] === "/";
  if (closing) state.i += 1;
  const nameMatch = /^[\w:-]+/.exec(html.slice(state.i));
  if (!nameMatch) throw new Error("bad tag near " + html.slice(state.i, state.i + 40));
  const name = nameMatch[0];
  state.i += name.length;
  const attrs = {};
  let selfClosing = false;
  while (state.i < html.length) {
    const ch = html[state.i];
    if (ch === " " || ch === "\n" || ch === "\t" || ch === "\r") { state.i += 1; continue; }
    if (ch === ">") { state.i += 1; break; }
    if (ch === "/" && html[state.i + 1] === ">") { selfClosing = true; state.i += 2; break; }
    const attrMatch = /^[^\s=\/>]+/.exec(html.slice(state.i));
    if (!attrMatch) throw new Error("bad attr near " + html.slice(state.i, state.i + 40));
    const attrName = attrMatch[0];
    state.i += attrName.length;
    while (html[state.i] === " ") state.i += 1;
    let value = "";
    if (html[state.i] === "=") {
      state.i += 1;
      while (html[state.i] === " ") state.i += 1;
      const quote = html[state.i];
      if (quote === '"' || quote === "'") {
        state.i += 1;
        const end = html.indexOf(quote, state.i);
        value = html.slice(state.i, end);
        state.i = end + 1;
      } else {
        const raw = /^[^\s>]+/.exec(html.slice(state.i));
        value = raw ? raw[0] : "";
        state.i += value.length;
      }
    }
    attrs[attrName] = value;
  }
  return { name, attrs, closing, selfClosing };
}

function interpolateMixed(raw, scope) {
  return raw.replace(/\{\{([\s\S]*?)\}\}/g, (_, expr) => {
    const value = interpolateValue(expr.trim(), scope);
    if (value == null || typeof value === "function" || typeof value === "object") return "";
    return String(value);
  });
}

function interpolateText(text, scope, ctx) {
  return text.replace(/\{\{([\s\S]*?)\}\}/g, (_, expr) => {
    const value = interpolateValue(expr.trim(), scope);
    return valueToHtml(expr.trim(), value, ctx, true);
  });
}

function valueToHtml(expr, value, ctx, asText) {
  if (value == null || typeof value === "function") return "";
  if (isReactEl(value)) {
    let html = renderReact(value);
    if (/\d+ days/.test(html)) {
      html = html.replace("<span", '<span data-countdown="2026-12-11T23:59:59+10:30"');
    }
    return html;
  }
  if (typeof value === "object") return "";
  const text = String(value);
  if (asText && OUTPUT_KEYS.has(expr)) {
    const live = expr === "totalLine" ? ' aria-live="polite"' : "";
    return `<span data-ee-val="${expr}"${live}>${escapeHtml(text)}</span>`;
  }
  return asText ? escapeHtml(text) : text;
}

function emitOpen(tag, scope, ctx, state) {
  const lname = tag.name.toLowerCase();
  const events = [];
  const attrs = [];
  let srcValue = null;
  for (const [name, raw] of Object.entries(tag.attrs)) {
    const expr = unwrap(raw);
    if (!expr) {
      let value = raw.includes("{{") ? interpolateMixed(raw, scope) : raw;
      if (name === "href") value = rewriteHref(value, ctx.pageMap);
      if (name === "src") {
        const next = rewriteSrc(value, ctx.imageMap);
        value = next || (value.startsWith("/") || /^(https?:|data:)/.test(value) ? value : "/assets/placeholder.svg");
        srcValue = value;
      }
      attrs.push([name, value]);
      continue;
    }
    const value = interpolateValue(expr, scope);
    if (typeof value === "function" && /^on/i.test(name)) {
      const id = state.handlers.length;
      state.handlers.push(value);
      const ev = name.slice(2).toLowerCase() === "change" && (lname === "input" || lname === "textarea")
        ? "input"
        : name.slice(2).toLowerCase();
      events.push(`${ev}:${id}`);
      const inputName = INPUT_EXPR[expr];
      if (inputName) attrs.push(["data-ee-input", inputName]);
      continue;
    }
    if (isRef(value)) {
      const id = state.refs.length;
      state.refs.push(value);
      attrs.push(["data-ee-ref", String(id)]);
      if (expr === "glowRef") attrs.push(["data-glow", ""]);
      continue;
    }
    if (value == null || typeof value === "function" || (typeof value === "object" && !isReactEl(value))) continue;
    if (typeof value === "boolean" || ["disabled", "checked", "readonly", "required", "hidden", "selected"].includes(name)) {
      if (value && value !== "false") attrs.push([name, name]);
      continue;
    }
    let rendered = isReactEl(value) ? renderReact(value) : String(value);
    if (name === "href") rendered = rewriteHref(rendered, ctx.pageMap);
    if (name === "src") {
      const next = rewriteSrc(rendered, ctx.imageMap);
      srcValue = next || (rendered.startsWith("/") || /^(https?:|data:)/.test(rendered) ? rendered : "/assets/placeholder.svg");
      rendered = srcValue;
    }
    attrs.push([name, rendered]);
  }
  if (events.length) attrs.push(["data-ee-on", events.join(" ")]);
  if (lname === "button" && scope.c && scope.c.id) attrs.push(["data-kb-chip", String(scope.c.id)]);
  if (lname === "div" && scope.g && scope.g.id && unwrap(tag.attrs.id || "") === "g.id") {
    attrs.push(["data-kb-group", String(scope.g.id)]);
  }
  if (lname === "a" && scope.it && scope.it.title) {
    attrs.push(["data-kb-item", ""]);
    attrs.push(["data-search", String(scope.it.title + " " + (scope.it.blurb || "")).toLowerCase()]);
  }
  if (lname === "input") {
    const label = attrs.find(([name]) => name === "aria-label");
    if (label && /search guides/i.test(label[1])) attrs.push(["data-kb-search", ""]);
    const which = attrs.find(([name]) => name === "data-ee-input");
    if (which) {
      const aria = which[1] === "kw" ? "Solar array size in kilowatts" : "Battery usable capacity in kilowatt hours";
      if (!attrs.some(([name]) => name === "aria-label")) attrs.push(["aria-label", aria]);
    }
  }
  if (lname === "img") decorateImg(attrs, ctx, state);
  if (lname === "button" && tag.attrs["data-see-more"] !== undefined) {
    if (!attrs.some(([name]) => name === "aria-expanded")) attrs.push(["aria-expanded", "false"]);
  }
  const open = `<${tag.name}${attrs.map(([name, value]) => value === "" ? ` ${name}=""` : ` ${name}="${escapeHtml(value)}"`).join("")}>`;
  if (lname === "img" && !tag.selfClosing) return { open };
  return { open };
}

function decorateImg(attrs, ctx, state) {
  const src = attrs.find(([name]) => name === "src");
  const dim = src && ctx.dims.get(src[1]);
  if (dim && !attrs.some(([name]) => name === "width")) {
    attrs.push(["width", String(dim.w)]);
    attrs.push(["height", String(dim.h)]);
  }
  const hero = src && /hero-coastal-daynight|earthed-energy-hero/.test(src[1]) && !state.heroUsed;
  if (hero) {
    state.heroUsed = true;
    attrs.push(["fetchpriority", "high"]);
    attrs.push(["decoding", "async"]);
  } else if (!attrs.some(([name]) => name === "loading")) {
    attrs.push(["loading", "lazy"]);
    attrs.push(["decoding", "async"]);
  }
}

function renderSlot(tag, scope, ctx) {
  const idExpr = unwrap(tag.attrs.id || "");
  const id = String(idExpr ? interpolateValue(idExpr, scope) : (tag.attrs.id || ""));
  const srcExpr = unwrap(tag.attrs.src || "");
  let src = srcExpr ? interpolateValue(srcExpr, scope) : (tag.attrs.src || "");
  if (typeof src !== "string") src = "";
  const phExpr = unwrap(tag.attrs.placeholder || "");
  const placeholder = phExpr ? interpolateValue(phExpr, scope) : (tag.attrs.placeholder || "Photo coming");
  const style = tag.attrs.style || "";
  const fit = tag.attrs.fit || "cover";
  const radius = tag.attrs.radius || (String(tag.attrs.shape || "") === "rounded" ? "8" : "0");
  const slotAlt = {
    "img-solar-glass": "Solar panels",
    "img-battery-glass": "Home battery",
    "img-ev-glass": "Home EV charger",
    "img-aircon-glass": "Split system air conditioner",
    "img-heatpump-glass": "Heat pump hot water system",
  };
  let label = slotAlt[id] || String(placeholder || "Photo coming");
  if (/^drop /i.test(label)) label = label.replace(/^drop\s+/i, "").replace(/\s+photo$/i, "");
  const mapped = src.startsWith("/") ? src : rewriteSrc(src, ctx.imageMap);
  const missing = !mapped || EMPTY_SLOTS.has(id) || /render-/.test(src);
  if (missing) return placeholderBox(label, style);
  const dim = ctx.dims.get(mapped) || { w: 1600, h: 900 };
  const eager = /hero/.test(mapped);
  return `<picture style="${escapeHtml(style)};display:block;overflow:hidden">` +
    `<img src="${escapeHtml(mapped)}" alt="${escapeHtml(label)}" width="${dim.w}" height="${dim.h}"` +
    `${eager ? ' fetchpriority="high"' : ' loading="lazy"'} decoding="async"` +
    ` style="width:100%;height:100%;object-fit:${escapeHtml(fit)};border-radius:${escapeHtml(radius)}px;display:block">` +
    `</picture>`;
}

function placeholderBox(label, style) {
  return `<div class="ee-ph" style="${escapeHtml(style)};display:flex;align-items:center;justify-content:center;background:#e4dfd6;color:#3a2947;text-align:center;padding:28px;min-height:180px">` +
    `<p style="margin:0;max-width:36ch;font:500 15px/1.45 'Open Sans',sans-serif">${escapeHtml(label)}</p></div>`;
}

function findTagStart(html, index) {
  return html.lastIndexOf("<", index);
}

function removeBalanced(html, start) {
  if (start < 0 || html[start] !== "<") return html;
  const slice = html.slice(start);
  const nameMatch = /^<\/?([\w:-]+)/.exec(slice.slice(1) ? "<" + slice.slice(1) : slice);
  const name = /^<([\w:-]+)/.exec(slice)?.[1];
  if (!name) return html;
  const voidish = VOID.has(name.toLowerCase());
  let i = start;
  let depth = 0;
  while (i < html.length) {
    if (html.startsWith("<!--", i)) {
      i = html.indexOf("-->", i) + 3;
      continue;
    }
    if (html[i] !== "<") { i += 1; continue; }
    const isClose = html[i + 1] === "/";
    const end = html.indexOf(">", i);
    const tagName = /^<\/?([\w:-]+)/.exec(html.slice(i))?.[1] || "";
    const selfClose = html[end - 1] === "/";
    if (tagName.toLowerCase() === name.toLowerCase()) {
      if (isClose) depth -= 1;
      else if (!selfClose && !voidish) depth += 1;
      else if (depth === 0) { i = end + 1; break; }
    }
    i = end + 1;
    if (depth === 0) break;
  }
  return html.slice(0, start) + html.slice(i);
}

function removeAttrElements(html, attr) {
  let cursor = 0;
  while (true) {
    const at = html.indexOf(attr, cursor);
    if (at < 0) break;
    const start = findTagStart(html, at);
    html = removeBalanced(html, start);
    cursor = start;
  }
  return html;
}

export function stripChrome(html) {
  let footer = "";
  const marker = 'alt="Earthed home battery beside a modern house at dusk';
  const markerAt = html.indexOf(marker);
  if (markerAt >= 0) {
    const start = html.lastIndexOf('<div style="position:relative;z-index:1;overflow:hidden">', markerAt);
    if (start >= 0) {
      footer = html.slice(start).trim();
      html = html.slice(0, start);
    }
  }
  html = html.replace(/<a\b[^>]*data-skip=""[^>]*>[\s\S]*?<\/a>/g, "");
  html = removeAttrElements(html, "data-mob-nav");
  html = removeAttrElements(html, "data-sticky-cta");
  html = removeAttrElements(html, "data-desk-nav");
  const sticky = html.indexOf("position:sticky;top:0;z-index:5");
  if (sticky >= 0) html = removeBalanced(html, findTagStart(html, sticky));
  return { html, footer };
}

export function rewriteTreeUrls(html, pageMap, imageMap) {
  return html.replace(/\b(src|href)="([^"]*)"/g, (full, attr, value) => {
    if (attr === "href") return `${attr}="${rewriteHref(value, pageMap)}"`;
    const next = rewriteSrc(value, imageMap);
    return `${attr}="${next || value}"`;
  });
}

export function runComponent(script, props, groups) {
  const React = makeReact();
  class DCLogic {
    constructor() {
      this.props = props || {};
      this.state = {};
    }
    setState(partial, cb) {
      const patch = typeof partial === "function" ? partial(this.state) : partial;
      this.state = { ...this.state, ...patch };
      if (cb) cb();
    }
  }
  const factory = new Function(
    "DCLogic",
    "React",
    "window",
    "document",
    "performance",
    "requestAnimationFrame",
    "EE_GROUPS",
    "scriptSource",
    `eval(scriptSource + "\\n;globalThis.__EE_C = Component;");
     return globalThis.__EE_C;`
  );
  const windowStub = {
    matchMedia: () => ({ matches: false }),
    addEventListener() {},
    removeEventListener() {},
    location: { search: "" },
    setTimeout,
    clearTimeout,
  };
  const Component = factory(DCLogic, React, windowStub, { addEventListener() {} }, { now: () => Date.now() }, () => 0, groups || [], script);
  const inst = new Component();
  inst.props = props || {};
  if (inst.state && Array.isArray(inst.state.groups) && groups) inst.state.groups = groups;
  const scope = typeof inst.renderVals === "function" ? inst.renderVals() : {};
  return scope || {};
}

export function mountInteractive(root, template, script) {
  const React = makeReact();
  const ctx = { pageMap: new Map(), imageMap: new Map(), dims: new Map() };
  class DCLogic {
    constructor() {
      this.props = {};
      this.state = {};
    }
    setState(partial, cb) {
      const patch = typeof partial === "function" ? partial(this.state) : partial;
      this.state = { ...this.state, ...patch };
      if (cb) cb();
      if (this.draw) this.schedule();
    }
    schedule() {
      if (this.queued) return;
      this.queued = true;
      requestAnimationFrame(() => {
        this.queued = false;
        this.draw();
      });
    }
  }
  const factory = new Function(
    "DCLogic",
    "React",
    "window",
    "document",
    "performance",
    "requestAnimationFrame",
    "EE_GROUPS",
    "scriptSource",
    `eval(scriptSource + "\\n;globalThis.__EE_C = Component;");
     return globalThis.__EE_C;`
  );
  const Component = factory(DCLogic, React, window, document, performance, requestAnimationFrame, [], script);
  const inst = new Component();
  inst.props = {};
  inst.draw = () => {
    const focus = document.activeElement;
    const focusKey = focus && root.contains(focus) ? (focus.id || focus.getAttribute("name") || focus.getAttribute("autocomplete") || focus.getAttribute("aria-label") || "") : "";
    const caret = focus && typeof focus.selectionStart === "number" ? focus.selectionStart : null;
    const scope = inst.renderVals() || {};
    const rendered = expand(template, scope, ctx);
    root.innerHTML = rendered.html;
    root.querySelectorAll("[data-ee-ref]").forEach((el) => {
      const ref = rendered.refs[Number(el.getAttribute("data-ee-ref"))];
      if (ref) ref.current = el;
    });
    const ons = root.querySelectorAll("[data-ee-on]");
    ons.forEach((el) => {
      el.getAttribute("data-ee-on").split(/\s+/).forEach((pair) => {
        const [event, id] = pair.split(":");
        const fn = rendered.handlers[Number(id)];
        if (event && fn) {
          el.addEventListener(event, (ev) => {
            try { fn.call(inst, ev); }
            catch (error) { console.error("ee handler", String(error)); }
          });
        }
      });
    });
    if (focusKey) {
      const next = root.querySelector(`#${CSS.escape(focusKey)}`)
        || root.querySelector(`[name="${CSS.escape(focusKey)}"]`)
        || root.querySelector(`[autocomplete="${CSS.escape(focusKey)}"]`)
        || root.querySelector(`[aria-label="${CSS.escape(focusKey)}"]`);
      if (next) {
        next.focus();
        if (caret != null && next.setSelectionRange) {
          try { next.setSelectionRange(caret, caret); } catch { /* range inputs */ }
        }
      }
    }
  };
  inst.draw();
  if (typeof inst.componentDidMount === "function") inst.componentDidMount();
  return inst;
}

export function defaultProps(raw) {
  if (!raw) return {};
  const decoded = raw.replace(/&quot;/g, '"');
  let data = {};
  try { data = JSON.parse(decoded); } catch { return {}; }
  const props = {};
  for (const [key, value] of Object.entries(data)) {
    if (value && typeof value === "object" && "default" in value) props[key] = value.default;
    else props[key] = value;
  }
  return props;
}
