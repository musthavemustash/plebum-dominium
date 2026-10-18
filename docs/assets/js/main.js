/* Plebum Dominium — progressive enhancement only. The guide reads fully with JS off. */
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
        b.innerHTML = "<span>✓ Done — nice work</span>";
        b.disabled = true;
      });
      row.appendChild(b);
    }
  }
})();
