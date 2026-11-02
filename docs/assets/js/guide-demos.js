/* Guide demos: lightweight controller for handout demo panels. */
(function () {
  'use strict';
  function initDemo(container) {
    var stages;
    try { stages = JSON.parse(container.getAttribute('data-stages') || '[]'); }
    catch (e) { return; }
    if (!stages.length) return;
    var current = 0, playing = false, timer = null;
    var stageEl = container.querySelector('.guide-demo-stage');
    var progressEl = container.querySelector('.guide-demo-progress');
    var backBtn = container.querySelector('[data-demo="back"]');
    var nextBtn = container.querySelector('[data-demo="next"]');
    var playBtn = container.querySelector('[data-demo="play"]');
    var resetBtn = container.querySelector('[data-demo="reset"]');
    function escapeHtml(t) {
      var d = document.createElement('div');
      d.textContent = t;
      return d.innerHTML;
    }
    function render() {
      var s = stages[current];
      stageEl.innerHTML = '<div><h4 style="margin:0 0 .5rem;color:#c4a484;">' +
        escapeHtml(s.title) + '</h4><p style="margin:0;line-height:1.6;">' +
        escapeHtml(s.text) + '</p></div>';
      progressEl.textContent = 'Demo step ' + (current + 1) + ' of ' + stages.length;
      backBtn.disabled = current === 0;
      nextBtn.disabled = current === stages.length - 1;
    }
    function stop() {
      playing = false;
      if (timer) { clearInterval(timer); timer = null; }
      playBtn.textContent = 'Play';
    }
    function go(n) {
      stop();
      current = Math.max(0, Math.min(stages.length - 1, n));
      render();
    }
    backBtn.addEventListener('click', function () { go(current - 1); });
    nextBtn.addEventListener('click', function () { go(current + 1); });
    resetBtn.addEventListener('click', function () { go(0); });
    playBtn.addEventListener('click', function () {
      if (playing) { stop(); }
      else {
        playing = true;
        playBtn.textContent = 'Pause';
        timer = setInterval(function () {
          if (current < stages.length - 1) { current++; render(); }
          else { stop(); }
        }, 3000);
      }
    });
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      playBtn.style.display = 'none';
    }
    render();
  }
  document.addEventListener('DOMContentLoaded', function () {
    var demos = document.querySelectorAll('.guide-demo[data-stages]');
    for (var i = 0; i < demos.length; i++) { initDemo(demos[i]); }
  });
})();
