(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce) document.documentElement.classList.add("js");

  var toggle = document.querySelector("[data-nav-toggle]");
  var panel = document.querySelector("[data-nav-panel]");
  if (toggle && panel) {
    toggle.addEventListener("click", function () {
      var open = panel.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    panel.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        panel.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  if (!reduce && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("is-in"); });
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
      var visible = group.querySelectorAll("[data-kb-item]:not([hidden])").length;
      group.hidden = visible === 0;
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
