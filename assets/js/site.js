(function () {
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  var panel = document.getElementById("mobile-nav");
  var closeBtn = panel ? panel.querySelector(".nav-close") : null;

  function paintHeader() {
    if (!header || header.getAttribute("data-solid") === "always") return;
    header.classList.toggle("is-solid", window.scrollY > 8);
  }
  paintHeader();
  window.addEventListener("scroll", paintHeader, { passive: true });

  function setOpen(open) {
    if (!panel || !toggle) return;
    panel.hidden = !open;
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    document.body.style.overflow = open ? "hidden" : "";
  }

  if (toggle && panel) {
    toggle.addEventListener("click", function () { setOpen(panel.hidden); });
    if (closeBtn) closeBtn.addEventListener("click", function () { setOpen(false); });
    panel.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () { setOpen(false); });
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setOpen(false);
    });
  }

  var search = document.querySelector("[data-kb-search]");
  var filters = document.querySelectorAll("[data-kb-filter]");
  var items = document.querySelectorAll("[data-kb-item]");
  var groups = document.querySelectorAll("[data-kb-group]");
  var empty = document.querySelector("[data-kb-empty]");
  var current = "all";

  function applyKb() {
    if (!items.length) return;
    var q = (search && search.value || "").trim().toLowerCase();
    var shown = 0;
    items.forEach(function (item) {
      var cat = item.getAttribute("data-cat");
      var hay = item.getAttribute("data-search") || "";
      var ok = (current === "all" || cat === current) && (!q || hay.indexOf(q) !== -1);
      item.hidden = !ok;
      if (ok) shown += 1;
    });
    groups.forEach(function (group) {
      group.hidden = group.querySelectorAll("[data-kb-item]:not([hidden])").length === 0;
    });
    if (empty) empty.classList.toggle("is-shown", shown === 0);
  }

  if (search) search.addEventListener("input", applyKb);
  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      current = btn.getAttribute("data-kb-filter");
      filters.forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      applyKb();
    });
  });
})();
