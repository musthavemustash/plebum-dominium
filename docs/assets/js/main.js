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

/* Ticker price: free mempool.space fetch, no key, no account, no user
   data asked for. Loads once, then refreshes every minute. On any
   failure the readout stays hidden and the bar looks as it did before. */
(function () {
  var el = document.getElementById("ticker-price");
  if (!el) return;
  function load() {
    fetch("https://mempool.space/api/v1/prices")
      .then(function (r) { return r.json(); })
      .then(function (p) {
        if (!p || typeof p.USD !== "number") return;
        el.textContent = "BTC $" + p.USD.toLocaleString("en-US");
        el.hidden = false;
      })
      .catch(function () { /* stay hidden */ });
  }
  load();
  setInterval(load, 60000);
})();

/* ---------- Ask the guide: header search over a build-time index ----------
   The index is a static JSON file on this same site, fetched once when the
   visitor first opens the search. Nothing typed is sent anywhere: matching
   happens in this script, and only a tap on an email link leaves the page. */
(function () {
  "use strict";
  var btn = document.getElementById("ask-btn");
  var backdrop = document.getElementById("ask-backdrop");
  var input = document.getElementById("ask-input");
  var results = document.getElementById("ask-results");
  if (!btn || !backdrop || !input || !results) return;

  var CONTACT = "Muststackmoresats@gmail.com";
  var SUBJECT = "Question about Plebum Dominium";
  var START = ["checklist", "verify", "airgap", "faq"];
  var index = null, indexFailed = false, loading = false;
  var selected = -1, lastFocus = null;

  function basePath() {
    var s = document.querySelector('script[src$="assets/js/main.js"]');
    if (s) {
      var src = s.getAttribute("src") || "";
      var i = src.indexOf("assets/js/main.js");
      if (i !== -1) return src.slice(0, i);
    }
    return "/";
  }

  function mailto(q) {
    return "mailto:" + CONTACT + "?subject=" + encodeURIComponent(SUBJECT) +
      "&body=" + encodeURIComponent("Question about Plebum Dominium:\n\n" + q);
  }

  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function words(q) {
    return q.toLowerCase().split(/\s+/).filter(function (w) { return w.length > 1; });
  }

  function highlight(text, ws) {
    var out = esc(text);
    ws.forEach(function (w) {
      var re = new RegExp("(" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
      out = out.replace(re, '<mark class="ask-hit">$1</mark>');
    });
    return out;
  }

  function snippet(e, ws) {
    var text = e.text, lower = text.toLowerCase(), pos = -1;
    ws.forEach(function (w) {
      var p = lower.indexOf(w);
      if (p !== -1 && (pos === -1 || p < pos)) pos = p;
    });
    if (pos === -1) return highlight(text.slice(0, 140), ws);
    var start = Math.max(0, pos - 60), end = Math.min(text.length, pos + 90);
    var s = text.slice(start, end);
    if (start > 0) s = "…" + s;
    if (end < text.length) s = s + "…";
    return highlight(s, ws);
  }

  function search(q) {
    var ws = words(q), scored = [];
    index.forEach(function (e) {
      var title = e.title.toLowerCase(), body = e.text.toLowerCase(), score = 0;
      if (q.trim() === e.num) score += 200;
      ws.forEach(function (w) {
        if (title.indexOf(w) !== -1) score += 50;
        if (body.indexOf(w) !== -1) score += 10;
      });
      if (score > 0) scored.push({ e: e, score: score });
    });
    scored.sort(function (a, b) { return b.score - a.score; });
    return scored.slice(0, 6).map(function (s) { return s.e; });
  }

  function rowHTML(e, ws, withSnippet) {
    var snip = withSnippet ? '<span class="ask-snippet">' + snippet(e, ws) + "</span>" : "";
    return '<a class="ask-row" href="' + esc(e.url) + '"><span class="ask-num">' +
      esc(e.num) + '</span><span><span class="ask-row-title">' +
      highlight(e.title, ws) + "</span>" + snip + "</span></a>";
  }

  function findEntry(slug) {
    for (var i = 0; i < index.length; i++) if (index[i].slug === slug) return index[i];
    return null;
  }

  function renderStart() {
    var html = '<p class="ask-start-label">Start with</p>';
    START.forEach(function (slug) {
      var e = findEntry(slug);
      if (e) html += rowHTML(e, [], false);
    });
    results.innerHTML = html;
    selected = -1;
  }

  function renderResults(q) {
    var ws = words(q);
    if (!ws.length) { renderStart(); return; }
    var hits = search(q);
    if (!hits.length) {
      results.innerHTML = '<p class="ask-empty">Nothing in the guide matches \u2018' +
        esc(q) + '\u2019 yet.</p><p class="ask-action-row"><a href="' + mailto(q) +
        '">Email this question</a><a href="' + basePath() +
        '">Browse the full program</a></p>';
      selected = -1;
      return;
    }
    var html = hits.map(function (e) { return rowHTML(e, ws, true); }).join("");
    html += '<p class="ask-email-row">Not what you needed? <a href="' + mailto(q) +
      '">Email this question</a></p>';
    results.innerHTML = html;
    selected = -1;
  }

  function loadIndex() {
    if (loading) return;
    loading = true;
    fetch(basePath() + "assets/search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        loading = false;
        index = data;
        if (input.value) renderResults(input.value); else renderStart();
      })
      .catch(function () {
        loading = false;
        indexFailed = true;
        results.innerHTML = '<p class="ask-empty">Search is not available right now.</p>';
      });
  }

  function open() {
    lastFocus = document.activeElement;
    backdrop.hidden = false;
    input.focus();
    if (index) renderStart();
    else if (indexFailed) results.innerHTML = '<p class="ask-empty">Search is not available right now.</p>';
    else {
      results.innerHTML = '<p class="ask-empty">Loading the guide index…</p>';
      loadIndex();
    }
  }

  function close() {
    backdrop.hidden = true;
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  btn.addEventListener("click", open);
  backdrop.addEventListener("click", function (e) { if (e.target === backdrop) close(); });
  input.addEventListener("input", function () { if (index) renderResults(input.value); });
  input.addEventListener("keydown", function (e) {
    var rows = results.querySelectorAll(".ask-row");
    if (e.key === "Escape") { close(); return; }
    if (e.key === "ArrowDown" && rows.length) {
      e.preventDefault();
      selected = Math.min(selected + 1, rows.length - 1);
    } else if (e.key === "ArrowUp" && rows.length) {
      e.preventDefault();
      selected = Math.max(selected - 1, 0);
    } else if (e.key === "Enter" && rows.length) {
      e.preventDefault();
      var r = rows[selected >= 0 ? selected : 0];
      if (r) window.location.href = r.getAttribute("href");
      return;
    } else return;
    rows.forEach(function (r, i) { r.classList.toggle("selected", i === selected); });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !backdrop.hidden) { close(); return; }
    if (e.key !== "/") return;
    if (!backdrop.hidden) return;
    var t = document.activeElement;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
    e.preventDefault();
    open();
  });
})();

/* --- online status dot: green on the live site, orange on a saved copy or with no network --- */
(function () {
  "use strict";
  var pill = document.getElementById("online-pill");
  if (!pill) return;
  var dot = document.getElementById("online-dot");
  var word = document.getElementById("online-word");
  function render() {
    var offline = (location.protocol === "file:") || !navigator.onLine;
    pill.hidden = false;
    dot.classList.toggle("offline", offline);
    word.textContent = offline ? "Offline" : "Online";
  }
  window.addEventListener("online", render);
  window.addEventListener("offline", render);
  render();
})();

/* --- hero keyring as quorum demo: the animation runs until a tap takes over --- */
(function () {
  "use strict";
  var ring = document.getElementById("keyring");
  if (!ring) return;
  var lock = document.getElementById("keyring-lock");
  var caption = document.getElementById("keyring-caption");
  var desc = document.getElementById("keyring-descriptor");
  var resetBtn = document.getElementById("keyring-reset");
  var keys = ring.querySelectorAll(".key");
  function update() {
    var n = 0;
    keys.forEach(function (k) { if (k.classList.contains("sel")) n++; });
    if (lock) lock.classList.toggle("open", n >= 2);
    if (n === 0) {
      caption.innerHTML = "<strong>Vault locked.</strong> No keys selected.";
      desc.textContent = "Descriptor: not shown yet. Tap keys to see if it is needed.";
    } else if (n === 1) {
      caption.innerHTML = "<strong>Vault locked.</strong> One key alone cannot spend.";
      desc.textContent = "Descriptor: not enough yet. One key alone cannot spend, with or without the map.";
    } else if (n === 2) {
      caption.innerHTML = "<strong>Vault opens, but a descriptor is needed.</strong>";
      desc.textContent = "Descriptor: needed. Two seeds alone cannot rebuild the third key, so you need the wallet map (the descriptor) to rebuild the wallet.";
    } else {
      caption.innerHTML = "<strong>Vault opens, no descriptor needed.</strong>";
      desc.textContent = "Descriptor: not needed. Three seeds rebuild the map exactly.";
    }
  }
  keys.forEach(function (k) {
    k.addEventListener("click", function () {
      ring.classList.add("tapped");
      k.classList.toggle("sel");
      k.setAttribute("aria-pressed", k.classList.contains("sel") ? "true" : "false");
      update();
      if (resetBtn) resetBtn.hidden = false;
    });
  });
  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      keys.forEach(function (k) {
        k.classList.remove("sel");
        k.setAttribute("aria-pressed", "false");
      });
      if (lock) lock.classList.remove("open");
      caption.innerHTML = "<strong>Any two keys</strong> open it. One alone cannot.";
      desc.textContent = "Select keys to see if the descriptor is needed.";
      resetBtn.hidden = true;
    });
  }
})();

/* ---------- motion: one toggle stops all motion, saved on this device ---------- */
(function () {
  var root = document.documentElement;
  var btn = document.getElementById("motion-btn");
  function applyMotion(m) {
    root.setAttribute("data-motion", m);
    if (btn) {
      btn.setAttribute("aria-pressed", m === "on" ? "true" : "false");
      btn.textContent = m === "on" ? "Motion on" : "Motion off";
    }
    var frames = document.querySelectorAll("iframe");
    for (var i = 0; i < frames.length; i++) {
      try { frames[i].contentWindow.postMessage({ type: "pd-motion", motion: m }, "*"); } catch (e) {}
    }
  }
  function setMotion(m) {
    try { localStorage.setItem("pd-motion", m); } catch (e) {}
    applyMotion(m);
  }
  if (btn) {
    btn.addEventListener("click", function () {
      setMotion(root.getAttribute("data-motion") === "off" ? "on" : "off");
    });
  }
  applyMotion(root.getAttribute("data-motion") || "on");
  try {
    var mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    mq.addEventListener("change", function (e) {
      if (!localStorage.getItem("pd-motion")) applyMotion(e.matches ? "off" : "on");
    });
  } catch (e) {}
})();
