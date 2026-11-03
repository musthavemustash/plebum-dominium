#!/usr/bin/env python3
"""Build the official descriptor tool page for the test site.

From the v6 wizard: swap the TEST banner for official copy, add the
online/offline pill and the stop screen (same pattern as the dice converter).
"""
import os
import re

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(TOOLS_DIR, 'descriptor-tool-source.html')

PILL_CSS = '''
  .topbar{display:flex;justify-content:flex-end;padding:0.5rem 0;}
  .online-pill{display:inline-flex;align-items:center;gap:8px;font-size:14px;color:#a89c88;white-space:nowrap;font-family:Arial,Helvetica,sans-serif;}
  .online-pill[hidden]{display:none;}
  .online-dot{width:12px;height:12px;border-radius:50%;background:#e07856;flex-shrink:0;}
  .online-dot.safe{background:#3aa655;}
  #netblock{position:fixed;inset:0;background:rgba(14,13,11,.97);z-index:50;display:flex;align-items:center;justify-content:center;padding:24px;}
  #netblock[hidden]{display:none;}
  .stopcard{max-width:560px;background:#161310;border:1px solid #5a2a22;border-radius:14px;padding:28px;font-family:Arial,Helvetica,sans-serif;}
  .stopcard h2{color:#e0a396;margin:0 0 10px;font-size:26px;}
  .stopcard p{color:#a89c88;margin:10px 0;line-height:1.55;}
  .dl-guide{margin-top:18px;padding-top:16px;border-top:1px solid #3a2f28;}
  .dl-guide p{margin:8px 0;}
  a.dl-btn{display:inline-block;background:#c4a484;color:#14100b;border-radius:10px;padding:10px 20px;font-size:15px;font-weight:700;text-decoration:none;}
'''

PILL_HTML = '''<div class="topbar"><span class="online-pill" id="online-pill" role="status" hidden><span class="online-dot" id="online-dot"></span><span id="online-word">Online</span></span></div>
'''

BLOCK_HTML = '''<div id="netblock" hidden>
  <div class="stopcard" role="alert">
    <p><span class="online-pill"><span class="online-dot"></span><span>Online</span></span></p>
    <h2>Stop. This computer is online.</h2>
    <p>A passphrase typed on a computer that can reach the network can be leaked by malware, a bad extension, or the network itself. One leak burns the passphrase, and a burned passphrase means the locked maps must be treated as readable.</p>
    <p>Close this page. Boot Tails with networking set to Disabled, or disconnect this machine from the network, then open the file again. If this page still says Online on a machine you believe is offline, trust the page. Something is still connected.</p>
    <div class="dl-guide">
      <p><strong>Get this file onto your offline machine.</strong></p>
      <p><a class="dl-btn" data-dl href="descriptor-tool.html" download="descriptor-tool.html">Download descriptor-tool.html</a></p>
      <p>Then check its fingerprint on the verify page, copy it to your data USB, and open it on Tails with networking disabled.</p>
    </div>
  </div>
</div>
'''

GUARD_JS = '''
<script>
(function(){
  "use strict";
  function $(id){return document.getElementById(id);}
  var netBlocked=true; // fail closed until the probe confirms offline
  function probeOnline(){
    return Promise.resolve(location.protocol === 'https:');
  }
  function wipe(){
    document.querySelectorAll('textarea').forEach(function(t){t.value='';});
    document.querySelectorAll('.pw').forEach(function(p){p.textContent='';});
    var s=document.querySelectorAll('.status');s.forEach(function(x){x.textContent='';});
  }
  async function renderNet(){
    var pill=$('online-pill'),dot=$('online-dot'),word=$('online-word'),block=$('netblock');
    if(pill){pill.hidden=false;dot.classList.remove('safe');word.textContent='Checking\u2026';}
    if(block){block.hidden=false;}
    // Protocol-only status. navigator.onLine is not consulted: it is unreliable
    // and must never block a local file or certify an air gap.
    // file: = opened as a local file (does NOT prove networking is disabled).
    // http(s): = served over the network; secrets are blocked.
    var servedOverNetwork = (location.protocol === 'https:' || location.protocol === 'http:');
    var wasBlocked=netBlocked;
    netBlocked=servedOverNetwork;
    if(pill){dot.classList.toggle('safe',!servedOverNetwork);word.textContent=servedOverNetwork?'Network detected':'Local file';}
    if(block){
      block.hidden=false;
      if(servedOverNetwork){
        block.innerHTML='<strong>Blocked:</strong> This tool was loaded over the network ('+location.protocol+'). For real keys, download this file, disconnect from the network, verify networking is disabled, then open the local copy. This page cannot verify air-gap status for you.';
      } else {
        block.innerHTML='<strong>Note:</strong> Opened as a local file. This does not prove networking is disabled. Before entering real secrets, disable networking on this computer and verify it stays disabled.';
      }
    }
    if(servedOverNetwork&&!wasBlocked){wipe();}
  }
  window.addEventListener('online',renderNet);
  window.addEventListener('offline',renderNet);
  document.addEventListener('click',function(e){
    if(netBlocked&&!(e.target.closest&&e.target.closest('[data-dl]'))){e.stopPropagation();e.preventDefault();}
  },true);
  document.addEventListener('keydown',function(e){
    if(netBlocked&&!(e.target.closest&&e.target.closest('[data-dl]'))){e.stopPropagation();e.preventDefault();}
  },true);
  renderNet();
})();
</script>
'''

def main(out):
    h = open(SRC).read()

    h = h.replace('<h1>Descriptor tool (TEST ONLY)</h1>', '<h1>Descriptor tool</h1>')

    old_banner = '<div class="banner"><strong>TEST ONLY. TEST VERSION 2.</strong> Updated Oct 25, 2026: window-wide drop + JavaScript diagnostic. Never enter a real descriptor or a real passphrase here. This page is for testing with a fake map only. This is a test file. It is not part of the guide yet. On Tails with networking disabled, this same file runs entirely in your browser. Nothing leaves this page. Nothing is stored. Use Tor Browser Standard security level. Safest disables the code this page needs.</div>'
    new_banner = '<div class="banner"><strong>Offline use only.</strong> This page runs entirely in your browser. Nothing leaves this page. Nothing is stored. On Tails with networking disabled, open this file in Tor Browser. Use Tor Browser Standard security level. Safest disables the code this page needs. If the pill at the top ever says Online, stop and close the page.</div>'
    assert old_banner in h, 'banner not found'
    h = h.replace(old_banner, new_banner)

    assert '</style>' in h
    h = h.replace('</style>', PILL_CSS + '</style>', 1)

    assert '<main>' in h
    h = h.replace('<main>', '<main>\n' + PILL_HTML, 1)

    assert '</main>' in h
    h = h.replace('</main>', '</main>\n' + BLOCK_HTML, 1)

    assert '</body>' in h
    h = h.replace('</body>', GUARD_JS + '</body>', 1)

    assert 'TEST ONLY. TEST VERSION 2.' not in h, 'test banner remnants'
    assert '<h1>Descriptor tool</h1>' in h
    open(out, 'w').write(h)
    print(f'wrote {out} ({len(h)} bytes)')

if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else '/home/hatch/workspace/.test-site/plebum-dominium-test/docs/descriptor-tool.html')
