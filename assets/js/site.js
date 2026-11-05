(function () {
  document.documentElement.classList.add("js");
  window.EE_LEAD = "https://formspree.io/f/mvkzjdwe";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var narrow = window.matchMedia("(max-width: 720px)").matches;

  function promoteImage(img, eager) {
    var src = img.getAttribute("data-src");
    if (!src) return;
    img.decoding = "async";
    if (eager) {
      img.loading = "eager";
      img.setAttribute("fetchpriority", "high");
    }
    img.src = src;
    img.removeAttribute("data-src");
  }

  function loadDeferredImages() {
    var nodes = Array.prototype.slice.call(document.querySelectorAll("img[data-src]"));
    if (!nodes.length) return;
    if (narrow || !("IntersectionObserver" in window)) {
      nodes.forEach(function (img, index) { promoteImage(img, index < 8); });
      return;
    }
    var view = window.innerHeight || 800;
    var soon = [];
    var later = [];
    nodes.forEach(function (img) {
      if (img.getBoundingClientRect().top < view * 1.35) soon.push(img);
      else later.push(img);
    });
    soon.forEach(function (img, index) { promoteImage(img, index < 4); });
    if (!later.length) return;
    var imageIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        promoteImage(entry.target, false);
        imageIO.unobserve(entry.target);
      });
    }, { rootMargin: "600px 0px" });
    later.forEach(function (img) { imageIO.observe(img); });
  }
  loadDeferredImages();

  if (narrow || reduce) {
    document.querySelectorAll("[data-reveal]").forEach(function (el) { el.classList.add("is-in"); });
  }

  var legacyToggle = document.querySelector(".nav-toggle");
  var legacyPanel = document.getElementById("mobile-nav");
  if (legacyToggle && legacyPanel) {
    function setLegacy(open) {
      legacyPanel.hidden = !open;
      legacyToggle.setAttribute("aria-expanded", open ? "true" : "false");
    }
    legacyToggle.addEventListener("click", function () { setLegacy(legacyPanel.hidden); });
    var legacyClose = legacyPanel.querySelector(".nav-close");
    if (legacyClose) legacyClose.addEventListener("click", function () { setLegacy(false); });
    legacyPanel.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () { setLegacy(false); });
    });
  }

  var toggle = document.querySelector("[data-ee-menu]");
  var drawer = document.getElementById("ee-drawer");
  function setMenu(open) {
    if (!toggle || !drawer) return;
    drawer.hidden = !open;
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.textContent = open ? "CLOSE" : "MENU";
  }
  if (toggle && drawer) {
    setMenu(false);
    toggle.addEventListener("click", function () { setMenu(drawer.hidden); });
    drawer.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () { setMenu(false); });
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setMenu(false);
    });
  }

  function whenIdle(fn) {
    if ("requestIdleCallback" in window) requestIdleCallback(fn, { timeout: 1200 });
    else window.addEventListener("load", fn);
  }
  function bindLeadForms(root) {
    (root || document).querySelectorAll("form[data-ee-lead]").forEach(function (form) {
      if (form.dataset.eeBound) return;
      form.dataset.eeBound = "1";
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var ok = form.querySelector("[data-ee-ok]");
        var err = form.querySelector("[data-ee-err]");
        var button = form.querySelector("[type=submit]");
        if (ok) ok.hidden = true;
        if (err) err.hidden = true;
        if (form.hasAttribute("data-ee-estimate")) {
          var bits = ["kwLabel", "batLabel", "stcLine", "chbLine", "totalLine"].map(function (key) {
            var el = document.querySelector('[data-ee-val="' + key + '"]');
            return key + ": " + (el ? el.textContent.trim() : "");
          });
          var message = form.querySelector('[name="message"]');
          if (message) message.value = "Rebate estimate\n" + bits.join("\n");
        }
        if (button) button.disabled = true;
        fetch(window.EE_LEAD, {
          method: "POST",
          body: new FormData(form),
          headers: { Accept: "application/json" }
        }).then(function (res) {
          if (!res.ok) throw new Error(String(res.status));
          if (ok) ok.hidden = false;
        }).catch(function () {
          if (err) err.hidden = false;
          if (button) button.disabled = false;
        });
      });
    });
  }
  bindLeadForms();

  whenIdle(startPage);

  function startPage() {
  document.querySelectorAll("[style-hover]").forEach(function (el) {
    var extra = el.getAttribute("style-hover") || "";
    if (reduce) extra = extra.replace(/transform:[^;]+;?/gi, "");
    var base = el.getAttribute("style") || "";
    function apply(on) {
      el.setAttribute("style", on ? mergeStyle(base, extra) : base);
    }
    el.addEventListener("mouseenter", function () { apply(true); });
    el.addEventListener("mouseleave", function () { apply(false); });
    el.addEventListener("focus", function () { apply(true); });
    el.addEventListener("blur", function () { apply(false); });
  });

  function mergeStyle(base, extra) {
    var map = {};
    (base + ";" + extra).split(";").forEach(function (part) {
      var idx = part.indexOf(":");
      if (idx < 1) return;
      map[part.slice(0, idx).trim().toLowerCase()] = part.slice(idx + 1).trim();
    });
    return Object.keys(map).map(function (key) { return key + ":" + map[key]; }).join(";");
  }

  var glow = document.querySelector("[data-glow]");
  if (glow && !narrow && window.matchMedia("(hover: hover)").matches && !reduce) {
    window.addEventListener("mousemove", function (event) {
      glow.style.opacity = "1";
      glow.style.transform = "translate(" + event.clientX + "px," + event.clientY + "px)";
    });
    document.addEventListener("mouseleave", function () { glow.style.opacity = "0"; });
  }

  if (!narrow && !reduce && "IntersectionObserver" in window) {
    var reveal = document.querySelectorAll("[data-reveal]");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    reveal.forEach(function (el) { io.observe(el); });

    var steps = Array.prototype.slice.call(document.querySelectorAll("[data-step]"));
    if (steps.length) {
      var stepIO = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            steps.forEach(function (step) { step.classList.toggle("is-active", step === entry.target); });
          }
        });
      }, { rootMargin: "-40% 0px -45% 0px", threshold: 0.01 });
      steps.forEach(function (step) { stepIO.observe(step); });
    }
  } else {
    document.querySelectorAll("[data-reveal]").forEach(function (el) { el.classList.add("is-in"); });
  }

  var see = document.querySelector("[data-see-more]");
  var collage = document.querySelector("[data-collage]");
  if (see && collage) {
    see.addEventListener("click", function () {
      var open = collage.hasAttribute("data-open");
      if (open) {
        collage.removeAttribute("data-open");
        see.textContent = "See all 22 installs";
        see.setAttribute("aria-expanded", "false");
      } else {
        collage.setAttribute("data-open", "");
        see.textContent = "Show fewer";
        see.setAttribute("aria-expanded", "true");
      }
    });
  }

  var clock = document.querySelector("[data-countdown]");
  if (clock && !reduce) {
    var end = new Date(clock.getAttribute("data-countdown")).getTime();
    function tick() {
      var diff = Math.max(0, end - Date.now());
      var pad = function (n) { return String(n).padStart(2, "0"); };
      clock.textContent = pad(Math.floor(diff / 864e5)) + " days · " +
        pad(Math.floor(diff % 864e5 / 36e5)) + " h · " +
        pad(Math.floor(diff % 36e5 / 6e4)) + " m · " +
        pad(Math.floor(diff % 6e4 / 1e3)) + " s";
    }
    tick();
    setInterval(tick, 1000);
  }

  var search = document.querySelector("[data-kb-search]");
  if (search) {
    var chips = Array.prototype.slice.call(document.querySelectorAll("[data-kb-chip]"));
    var groups = Array.prototype.slice.call(document.querySelectorAll("[data-kb-group]"));
    var count = document.querySelector('[data-ee-val="countLabel"]');
    var current = "all";
    function paintChips() {
      chips.forEach(function (chip) {
        var on = chip.getAttribute("data-kb-chip") === current;
        chip.setAttribute("aria-pressed", on ? "true" : "false");
        chip.style.background = on ? "#5E2D89" : "rgba(255,255,255,.55)";
        chip.style.color = on ? "#ffffff" : "rgba(43,21,80,.75)";
        chip.style.borderColor = on ? "#5E2D89" : "rgba(255,255,255,.9)";
      });
    }
    function filterGuides() {
      var q = search.value.trim().toLowerCase();
      var shown = 0;
      var total = 0;
      groups.forEach(function (group) {
        var items = group.querySelectorAll("[data-kb-item]");
        var visible = 0;
        items.forEach(function (item) {
          total += 1;
          var hay = item.getAttribute("data-search") || item.textContent.toLowerCase();
          var ok = (current === "all" || group.getAttribute("data-kb-group") === current) && (!q || hay.indexOf(q) !== -1);
          item.hidden = !ok;
          if (ok) { shown += 1; visible += 1; }
        });
        group.hidden = visible === 0;
      });
      if (count) count.textContent = shown === total ? total + " guides" : shown + " of " + total + " guides";
      var empty = document.getElementById("kb-empty");
      if (!empty) {
        empty = document.createElement("p");
        empty.id = "kb-empty";
        empty.className = "ee-note";
        empty.hidden = true;
        empty.textContent = "No guides match that search. Try a suburb rule, a product, or a bill question.";
        var host = groups[0] && groups[0].parentElement;
        if (host) host.appendChild(empty);
      }
      empty.hidden = shown !== 0;
    }
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        current = chip.getAttribute("data-kb-chip");
        paintChips();
        filterGuides();
      });
    });
    search.addEventListener("input", filterGuides);
    paintChips();
  }

  var kw = document.querySelector('[data-ee-input="kw"]');
  var bat = document.querySelector('[data-ee-input="bat"]');
  if (kw && bat) {
    var fmt = function (n) { return "$" + Math.round(n).toLocaleString("en-AU"); };
    function paintRebate() {
      var kwv = Number(kw.value);
      var batv = Number(bat.value);
      var stcCerts = Math.floor(kwv * 1.382 * 5);
      var stc = stcCerts * 39;
      var chbCerts = Math.min(batv, 14) * 6.8 + Math.max(0, Math.min(batv, 28) - 14) * 4.08 + Math.max(0, batv - 28) * 1.02;
      var chb = chbCerts * 39;
      var gross = kwv * 1400 + batv * 1200;
      var values = {
        kwLabel: kwv.toFixed(1) + " kW",
        batLabel: batv ? batv + " kWh" : "No battery",
        stcLine: fmt(stc),
        chbLine: batv ? fmt(chb) : "$0",
        totalLine: fmt(stc + chb),
        totalSub: "About " + Math.round((stc + chb) / gross * 100) + "% of a " + fmt(gross) + " system, deducted before you pay",
        stcSub: stcCerts + " certificates · " + kwv.toFixed(1) + " × 1.382 × 5 yrs",
        chbSub: batv ? chbCerts.toFixed(1) + " certificates on " + batv + " kWh usable" : "Add a battery to see the CHB rebate"
      };
      Object.keys(values).forEach(function (key) {
        document.querySelectorAll('[data-ee-val="' + key + '"]').forEach(function (el) { el.textContent = values[key]; });
      });
    }
    kw.addEventListener("input", paintRebate);
    bat.addEventListener("input", paintRebate);
  }
  }
})();
