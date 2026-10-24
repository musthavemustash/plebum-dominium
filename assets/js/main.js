/* Plebum Dominium: progressive enhancement only. The guide reads fully with JS off. */
(function () {
  "use strict";

  /* --- mobile drawer --- */
  var btn = document.querySelector(".menu-btn");
  var scrim = document.querySelector(".scrim");
  function closeNav() {
    document.body.classList.remove("nav-open");
    if (btn) btn.setAttribute("aria-expanded", "false");
  }
  if (btn) {
    btn.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  if (scrim) scrim.addEventListener("click", closeNav);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeNav();
  });

  /* --- copy buttons on code blocks --- */
  document.querySelectorAll("pre").forEach(function (pre) {
    var b = document.createElement("button");
    b.className = "copy-btn";
    b.type = "button";
    b.textContent = "Copy";
    b.addEventListener("click", function () {
      var code = pre.querySelector("code");
      var text = code ? code.innerText : pre.innerText;
      navigator.clipboard.writeText(text).then(function () {
        b.textContent = "Copied";
        b.classList.add("copied");
        setTimeout(function () {
          b.textContent = "Copy";
          b.classList.remove("copied");
        }, 1600);
      });
    });
    pre.appendChild(b);
  });

  /* --- scrollspy for the "On this sheet" TOC --- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll("[data-toc]"));
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute("data-toc")] = a; });
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          tocLinks.forEach(function (a) { a.classList.remove("active"); });
          var a = map[en.target.id];
          if (a) a.classList.add("active");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(map).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) obs.observe(el);
    });
  }

  /* --- sheet check-off, persisted on this device --- */
  var KEY = "plebum-dominium-done";
  var done = {};
  try { done = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { done = {}; }
  document.querySelectorAll(".sidebar a[data-sheet]").forEach(function (a) {
    var slug = a.getAttribute("data-sheet");
    if (done[slug]) a.parentElement.classList.add("done");
    // double-click a sidebar entry to toggle its checkmark
    a.addEventListener("dblclick", function (ev) {
      ev.preventDefault();
      var li = a.parentElement;
      var isDone = li.classList.toggle("done");
      if (isDone) done[slug] = true; else delete done[slug];
      try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) {}
    });
  });
  // checking off happens on the sheet itself: mark current sheet done via footer button
  var here = document.querySelector('.sidebar a.active');
  if (here) {
    var slug = here.getAttribute("data-sheet");
    var row = document.querySelector(".prevnext-row");
    if (row && !done[slug]) {
      var b = document.createElement("button");
      b.className = "prevnext";
      b.type = "button";
      b.innerHTML = "<span>✓ Mark this sheet done</span>";
      b.addEventListener("click", function () {
        done[slug] = true;
        try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) {}
        here.parentElement.classList.add("done");
        b.innerHTML = "<span>✓ Done. Nice work.</span>";
        b.disabled = true;
      });
      row.appendChild(b);
    }
  }
})();

/* ---------- theme: toggle + follow the OS when no saved choice ---------- */
(function () {
  var root = document.documentElement;
  function setTheme(t) {
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("pd-theme", t); } catch (e) {}
  }
  var btn = document.getElementById("theme-btn");
  if (btn) {
    btn.addEventListener("click", function () {
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  }
  try {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    mq.addEventListener("change", function (e) {
      if (!localStorage.getItem("pd-theme")) setTheme(e.matches ? "dark" : "light");
    });
  } catch (e) {}
})();

/* ---------- reveal fallback (browsers without scroll timelines) ---------- */
(function () {
  if (window.CSS && CSS.supports && CSS.supports("animation-timeline: view()")) return;
  var els = document.querySelectorAll(".card, .you-need, .sheet-diagram, .callout, .keyring");
  els.forEach(function (el) { el.classList.add("reveal"); });
  if (!("IntersectionObserver" in window)) {
    els.forEach(function (el) { el.classList.add("in"); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
    });
  }, { threshold: 0.1 });
  els.forEach(function (el) { io.observe(el); });
})();

/* --- "Pick your setup" chooser (homepage only, client-side only) --- */
(function () {
  var chooser = document.getElementById("chooser");
  if (!chooser) return;
  var result = document.getElementById("chooser-result");
  if (!result) return;
  var sel = {};
  function link(slug, num, title) {
    return '<a href="handouts/' + slug + '.html">Start with: ' + title + " (" + num + ")</a>";
  }
  function recommend() {
    if (sel.coins === "exchange")
      return link("single-sig", "16", "One key, done right") + " · the exchange holds your keys today. This sheet brings the coins home. The full 2-of-3 build starts at the " + link("checklist", "03", "Checklist") + ".";
    if (sel.coins === "software")
      return link("single-sig", "16", "One key, done right") + " · a seed that lived on a phone counts as exposed. This sheet makes a fresh one offline and moves the coins onto it.";
    if (sel.coins === "hardware")
      return link("single-sig", "16", "One key, done right") + " · you are closer than you think: grade the seed, add a passphrase, stamp it in metal.";
    if (sel.exp === "new")
      return link("terms", "T", "Terms") + " · learn the vocabulary first, then work the sheets in order.";
    if (sel.offline === "notyet")
      return link("airgap", "04", "Two boots") + " · get the offline computer ready before anything else.";
    if (sel.keys === "hw")
      return link("checklist", "03", "Checklist") + " · then read " + link("faq", "13", "If you get stuck") + " for hardware-wallet notes.";
    if (sel.keys === "dice")
      return link("dice", "06", "Make the three keys") + " · once you have worked sheets 03 through 05.";
    if (sel.exp === "some")
      return link("checklist", "03", "Checklist") + " · gather the kit, then work the sheets in order.";
    return null;
  }
  chooser.querySelectorAll(".chooser-q").forEach(function (q) {
    var key = q.getAttribute("data-q");
    q.querySelectorAll(".chooser-tile").forEach(function (t) {
      t.addEventListener("click", function () {
        q.querySelectorAll(".chooser-tile").forEach(function (o) {
          o.classList.remove("selected");
          o.setAttribute("aria-pressed", "false");
        });
        t.classList.add("selected");
        t.setAttribute("aria-pressed", "true");
        sel[key] = t.getAttribute("data-val");
        var r = recommend();
        if (r) result.innerHTML = r;
      });
    });
  });
})();

/* --- on-chain donate: copy address --- */
document.querySelectorAll(".btn-onchain").forEach(function (btn) {
  btn.addEventListener("click", function () {
    var addr = btn.getAttribute("data-copy");
    if (!addr || addr.indexOf("REPLACE_WITH") === 0) return;
    navigator.clipboard.writeText(addr).then(function () {
      var orig = btn.innerHTML;
      btn.classList.add("copied");
      btn.innerHTML = "\u2713 Address copied";
      setTimeout(function () {
        btn.classList.remove("copied");
        btn.innerHTML = orig;
      }, 2500);
    });
  });
});

/* --- first-visit "New to Bitcoin?" banner (homepage only) --- */
(function () {
  var banner = document.getElementById("newbie-banner");
  if (!banner) return;
  if (!document.body.classList.contains("home")) return;
  var seen = false;
  try { seen = localStorage.getItem("pd-newbie-seen") === "1"; } catch (e) {}
  if (seen) return;
  function dismiss() {
    try { localStorage.setItem("pd-newbie-seen", "1"); } catch (e) {}
    banner.hidden = true;
  }
  banner.querySelector(".newbie-close").addEventListener("click", dismiss);
  banner.querySelector(".newbie-go").addEventListener("click", dismiss);
  banner.hidden = false;
})();

/* first-visit splash: site name at the top, logo filling the screen, shown once */
(function () {
  var splash = document.getElementById("pd-splash");
  if (!splash) return;
  if (!document.body.classList.contains("home")) return;
  var seen = false;
  try { seen = localStorage.getItem("pd-splash-seen") === "1"; } catch (e) {}
  if (seen) return;
  try { localStorage.setItem("pd-splash-seen", "1"); } catch (e) {}
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  splash.hidden = false;
  document.body.classList.add("splash-lock");
  var done = false;
  function dismiss() {
    if (done) return;
    done = true;
    splash.classList.add("bye");
    document.body.classList.remove("splash-lock");
    document.removeEventListener("keydown", dismiss);
    setTimeout(function () { splash.hidden = true; }, 500);
  }
  setTimeout(dismiss, 2600);
  setTimeout(dismiss, 5000); /* hard stop: never trap a visitor */
  splash.addEventListener("click", dismiss);
  document.addEventListener("keydown", dismiss);
})();
