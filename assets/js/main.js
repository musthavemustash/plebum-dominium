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

/* ---------- sidebar path toggle (TEST SITE ONLY): Easy / One key / Full program, saved on this device ---------- */
(function () {
  "use strict";
  var PATHS = {
    easy: { label: "Easy", sheets: ["terms", "threat-model", "checklist", "verify", "airgap", "dice", "titanium", "faq"], summary: "Words into one trusted device. Lowest work, most trust in one device and its maker." },
    one: { label: "One key", sheets: ["terms", "threat-model", "checklist", "verify", "airgap", "dice", "single-sig", "titanium", "fire-card", "faq"], summary: "One key plus a passphrase. Medium work, trust in one key, one device, and one passphrase." },
    full: { label: "Full program", sheets: null, summary: "Three keys, three places. Highest work, no single key, device, or place." }
  };
  var VARIANTS = { faq: { easy: "faq-easy", one: "faq-one" }, titanium: { easy: "titanium-easy", one: "titanium-one" }, checklist: { easy: "checklist-easy", one: "checklist-one" }, "fire-card": { one: "fire-card-one" }, "threat-model": { easy: "threat-model-easy", one: "threat-model-one" }, dice: { easy: "dice-easy", one: "dice-one" } };
  var NOTES = {
    dice: {
      easy: "On this path, make one key, not three. Stop after the first key, stamp it in titanium, then enter the words on the device itself.",
      one: "On this path, make one key, then add a passphrase, kept on paper apart from the plate.",
      full: "Make three keys, with a full shutdown between each key."
    },
    titanium: {
      easy: "On this path, stamp the words in titanium first, before the device entry. The plate is the backup if the device fails.",
      one: "Stamp the words in titanium, and keep the passphrase paper apart from the plate.",
      full: "Stamp three plates, and keep them in three places."
    },
    verify: {
      easy: "On this path, the Later section does not apply. Sparrow, Electrum, the wallet map, and signing a file are Full program work. The checking steps above, download, fingerprint, signature, and kit check, are the work.",
      one: "On this path, Sparrow is watch-only only, Electrum is not used, and the wallet map and signing in the Later section do not apply. The checking steps above are the work."
    },
    airgap: {
      easy: "On this path, three phrases in this sheet do not apply: a watch-only wallet that broadcasts, payment files and the map on the data USB, and signing a file or exporting the map. Your work here is Tails with networking off, one seed per session, and a full shutdown. Next, make one key.",
      one: "On this path, the map, signing a file, and exporting the map do not apply. A watch-only wallet comes later, in the single-sig sheet, and the device signs. Next, make one key."
    },
    terms: {
      easy: "On this path, four entries describe the Full program, not your wallet: 2-of-3, m/48'/0'/0'/2', descriptor, and PSBT. Your wallet is one device and one plate.",
      one: "On this path, three entries describe the Full program, not your wallet: 2-of-3, m/48'/0'/0'/2', and descriptor as a map. PSBT does not apply either, the device signs. The xpub entry fits as a watch key."
    },
    single: {},
    "single-sig": {
      one: "This is your main sheet on this path. One key, one passphrase, one watch-only wallet.",
      full: "On the full program, this sheet is the spending wallet on Plate A. Savings stay in the 2-of-3."
    },
    sparrow: {
      full: "Build the 2-of-3 from the three dice keys, then practice spend before any savings move."
    },
    encryption: {
      full: "Hide the wallet map, encrypted, apart from any single plate. Two seeds alone cannot rebuild the third key without it."
    },
    inheritance: {
      full: "Write the inheritance sheet for a non-Bitcoiner, and keep it where your family can find it."
    }
  };
  function getPath() {
    try {
      var p = localStorage.getItem("pd-path");
      if (p === "easy" || p === "one" || p === "full") return p;
    } catch (e) {}
    return "full";
  }
  function currentSlug() {
    var a = document.querySelector(".sidebar a.active");
    return a ? a.getAttribute("data-sheet") : null;
  }
  function applyPath(path) {
    var info = PATHS[path];
    document.documentElement.setAttribute("data-path", path);
    document.querySelectorAll("#sidebar-path button[data-path], .path-risks-switch button[data-path], .mobile-path-seg button[data-path]").forEach(function (b) {
      var on = b.getAttribute("data-path") === path;
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.classList.toggle("sel-easy", on && path === "easy");
      b.classList.toggle("sel-one", on && path === "one");
      b.classList.toggle("sel-full", on && path === "full");
      if (!on) { b.classList.remove("sel-easy", "sel-one", "sel-full"); }
    });
    var shown = 0, total = 0;
    document.querySelectorAll(".sidebar ul li[data-paths]").forEach(function (li) {
      total++;
      var ok = li.getAttribute("data-paths").split(" ").indexOf(path) >= 0;
      li.classList.toggle("path-hidden", !ok);
      if (ok) shown++;
    });
    var count = document.getElementById("path-count");
    if (count) count.textContent = path === "full" ? "All " + total + " sheets" : "Showing " + shown + " of " + total + " sheets for " + info.label;
    var risksLabel = document.getElementById("path-risks-label");
    if (risksLabel) risksLabel.textContent = info.label;
    ["easy", "one", "full"].forEach(function (k) {
      var sec = document.getElementById("risks-" + k);
      if (sec) sec.classList.toggle("path-hidden", k !== path);
    });
    var banner = document.getElementById("path-banner");
    if (banner) {
      var label = document.getElementById("path-banner-label");
      var note = document.getElementById("path-banner-note");
      if (label) label.textContent = info.label;
      var slug = currentSlug();
      if (slug && info.sheets && info.sheets.indexOf(slug) < 0) {
        banner.classList.add("path-banner-warn");
        if (note) note.innerHTML = "This sheet is not on your " + info.label + " path. " + info.summary + " Switch to Full program in the sidebar to see all sheets, or pick a sheet on your path.";
      } else {
        banner.classList.remove("path-banner-warn");
        var n = slug && NOTES[slug] && NOTES[slug][path] ? NOTES[slug][path] : info.summary;
        if (note) note.textContent = n;
      }
      banner.hidden = false;
    }
    var gate = document.getElementById("path-gate");
    var gateNote = document.getElementById("path-gate-note");
    var gated = false;
    if (path !== "full") {
      var gslug = currentSlug();
      if (gslug && info.sheets && info.sheets.indexOf(gslug) < 0) gated = true;
    }
    document.body.classList.toggle("path-gated", gated);
    if (gate) {
      gate.hidden = !gated;
      if (gated && gateNote) gateNote.textContent = "This sheet is part of the Full program, not your " + info.label + " path, so its content is not shown here. Switch to Full program to read it, or stay on your path.";
    }
    document.querySelectorAll(".stage .card").forEach(function (card) {
      var href = card.getAttribute("href") || "";
      var m = href.match(/handouts\/([a-z0-9-]+)\.html/);
      if (!m) return;
      var on = path === "full" || (info.sheets && info.sheets.indexOf(m[1]) >= 0);
      card.classList.toggle("path-hidden", !on);
    });
    document.querySelectorAll(".stage").forEach(function (sec) {
      var cards = sec.querySelectorAll(".card");
      if (!cards.length) return;
      var any = false;
      cards.forEach(function (c) { if (!c.classList.contains("path-hidden")) any = true; });
      sec.classList.toggle("path-hidden", !any);
    });
    document.querySelectorAll(".sidebar a[data-sheet]").forEach(function (a) {
      var s = a.getAttribute("data-sheet");
      var v = VARIANTS[s] && VARIANTS[s][path];
      if (!a.getAttribute("data-base-href")) a.setAttribute("data-base-href", a.getAttribute("href"));
      if (v) a.setAttribute("href", a.getAttribute("data-base-href").replace(/[^\/]+\.html$/, v + ".html"));
      else a.setAttribute("href", a.getAttribute("data-base-href"));
    });
    var curSlug = currentSlug();
    var curFile = (window.location.pathname.split("/").pop() || "").replace(/\.html$/, "");
    if (curSlug && VARIANTS[curSlug]) {
      var want = VARIANTS[curSlug][path];
      if (want && curFile !== want) {
        window.location.href = window.location.pathname.replace(/[^\/]+\.html$/, want + ".html");
        return;
      }
      if (!want && curFile !== curSlug && (curFile === VARIANTS[curSlug].easy || curFile === VARIANTS[curSlug].one)) {
        window.location.href = window.location.pathname.replace(/[^\/]+\.html$/, curSlug + ".html");
        return;
      }
    }
    var inSite = document.querySelector(".path-seg button[data-path=\"" + path + "\"]");
    if (inSite && inSite.getAttribute("aria-pressed") !== "true") inSite.click();
  }
  function setPath(path) {
    try { localStorage.setItem("pd-path", path); } catch (e) {}
    applyPath(path);
  }
  document.querySelectorAll("#sidebar-path button[data-path], .path-risks-switch button[data-path], .mobile-path-seg button[data-path]").forEach(function (b) {
    b.addEventListener("click", function () { setPath(b.getAttribute("data-path")); });
  });
  var gateBtn = document.getElementById("path-gate-full");
  if (gateBtn) gateBtn.addEventListener("click", function () { setPath("full"); });
  applyPath(getPath());
})();
