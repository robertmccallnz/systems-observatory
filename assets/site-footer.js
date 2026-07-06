/*
 * Te Pā — cross-site shared footer.
 *
 * Single source of truth. Serve from jsDelivr so any site (GitHub Pages,
 * Netlify, te-pa.org, other repos) can include one <script> tag and get
 * the same footer. Substack and other JS-restricted platforms use the
 * static HTML block in EMBED.md instead.
 *
 * CDN URL:
 *   https://cdn.jsdelivr.net/gh/robertmccallnz/systems-observatory@main/assets/site-footer.js
 *
 * Embed:
 *   <div id="tepa-site-footer"></div>
 *   <script src="https://cdn.jsdelivr.net/gh/robertmccallnz/systems-observatory@main/assets/site-footer.js" defer></script>
 *
 * To pin a version (recommended for production): replace @main with a
 * tag or commit SHA, e.g. @v1.0.0 or @1a5a70d.
 *
 * Edit the FOOTER_HTML and STYLE constants below. Push to main.
 * jsDelivr caches for ~12h; bust with ?v=YYYYMMDD on the script src.
 */

(function () {
  var CSS = [
    '.tepa-footer{',
    '  max-width:1200px;margin:4rem auto 0;padding:2.5rem 1.25rem 2rem;',
    '  border-top:1px solid #1e1e1e;background:transparent;color:#d9d1bd;',
    '  font-family:"Inter",system-ui,-apple-system,Segoe UI,Roboto,sans-serif;',
    '  font-size:15px;line-height:1.5;box-sizing:border-box;',
    '}',
    '.tepa-footer *{box-sizing:border-box;}',
    '.tepa-footer .tepa-grid{',
    '  display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:1.5rem;',
    '}',
    '@media(max-width:900px){.tepa-footer .tepa-grid{grid-template-columns:1fr 1fr;}}',
    '@media(max-width:640px){.tepa-footer .tepa-grid{grid-template-columns:1fr;}}',
    '.tepa-footer .tepa-block h2{',
    '  font-family:"Bebas Neue","Inter",sans-serif;font-size:1.6rem;',
    '  letter-spacing:0.04em;margin:0 0 0.5rem;color:#f4ecd8;font-weight:400;',
    '}',
    '.tepa-footer .tepa-block h3{',
    '  font-size:0.75rem;text-transform:uppercase;letter-spacing:0.12em;',
    '  color:#7a7268;margin:0 0 0.75rem;font-weight:600;',
    '}',
    '.tepa-footer .tepa-block ul{list-style:none;margin:0;padding:0;}',
    '.tepa-footer .tepa-block li+li{margin-top:0.5rem;}',
    '.tepa-footer .tepa-block a{',
    '  color:#e8a83a;text-decoration:none;',
    '}',
    '.tepa-footer .tepa-block a:hover,.tepa-footer .tepa-block a:focus-visible{',
    '  color:#d7261e;text-decoration:underline;',
    '}',
    '.tepa-footer .tepa-block a[aria-current="page"]{',
    '  color:#f4ecd8;font-weight:600;',
    '}',
    '.tepa-footer .tepa-block p{color:#d9d1bd;margin:0 0 0.6rem;line-height:1.5;}',
    '.tepa-footer .tepa-meta{',
    '  margin-top:2rem;padding-top:1rem;border-top:1px solid #1e1e1e;',
    '  color:#7a7268;font-size:0.85rem;',
    '}',
    '.tepa-footer .tepa-meta a{color:#e8a83a;text-decoration:none;}',
    '.tepa-footer .tepa-meta a:hover{color:#d7261e;text-decoration:underline;}',
    /* light-theme override: pages that set data-tepa-theme="light" on <html> or <body> */
    '[data-tepa-theme="light"] .tepa-footer{',
    '  color:#3a3630;border-top-color:#d8d1c5;',
    '}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-block h2{color:#1a1a1a;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-block h3{color:#6d655c;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-block p{color:#3a3630;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-block a{color:#c1712f;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-meta{color:#6d655c;border-top-color:#d8d1c5;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-meta a{color:#c1712f;}'
  ].join('');

  // All URLs are absolute so the footer works on any host.
  var FOOTER_HTML = [
    '<footer class="tepa-footer" role="contentinfo">',
    '  <div class="tepa-grid">',
    '    <div class="tepa-block">',
    '      <h2>Te Pā Systems Observatory</h2>',
    '      <p>A public systems observatory and governance-audit tool developed as a Te Pā Collective Action Lab artefact, in relation to Te Pā Tūwatawata and The Kiwi Dialectic.</p>',
    '      <p>Standalone, forkable research artefact. Te Pā remains the kaupapa and charitable-trust anchor; the observatory remains an open technical and pedagogical tool.</p>',
    '    </div>',
    '    <div class="tepa-block">',
    '      <h3>Views</h3>',
    '      <ul>',
    '        <li><a href="https://robertmccallnz.github.io/systems-observatory/" data-tepa-nav="observatory">Observatory</a></li>',
    '        <li><a href="https://robertmccallnz.github.io/systems-observatory/governance.html" data-tepa-nav="governance">Governance Audit</a></li>',
    '      </ul>',
    '    </div>',
    '    <div class="tepa-block">',
    '      <h3>Ecosystem</h3>',
    '      <ul>',
    '        <li><a href="https://www.te-pa.org" data-tepa-nav="te-pa">Te Pā</a></li>',
    '        <li><a href="https://thekiwidialectic.substack.com/" data-tepa-nav="kiwi-dialectic">Kiwi Dialectic</a></li>',
    '        <li><a href="https://github.com/robertmccallnz/systems-observatory/discussions">Kōrero</a></li>',
    '      </ul>',
    '    </div>',
    '    <div class="tepa-block">',
    '      <h3>Context</h3>',
    '      <ul>',
    '        <li><a href="https://github.com/robertmccallnz/systems-observatory/blob/main/docs/LEVERAGE_POINTS.md">Leverage points mapping</a></li>',
    '        <li><a href="https://github.com/robertmccallnz/systems-observatory/blob/main/docs/GOVERNANCE_AUDIT.md">Governance audit method</a></li>',
    '        <li><a href="https://github.com/robertmccallnz/systems-observatory/blob/main/reports/governance-audit-report.md">Governance audit report</a></li>',
    '        <li><a href="https://github.com/robertmccallnz/systems-observatory">GitHub repository</a></li>',
    '      </ul>',
    '    </div>',
    '  </div>',
    '  <div class="tepa-meta">',
    '    <p>Built under the <a href="https://www.kahuiraraunga.io/">Māori Data Governance Model</a> of Te Kāhui Raraunga. Public, aggregated, non-personal data only.</p>',
    '  </div>',
    '</footer>'
  ].join('\n');

  function inject() {
    var slot = document.getElementById('tepa-site-footer');
    // Backwards-compat: also accept the old slot id from inside this repo.
    if (!slot) slot = document.getElementById('site-footer');
    if (!slot) return;

    // Inject CSS once.
    if (!document.getElementById('tepa-footer-style')) {
      var style = document.createElement('style');
      style.id = 'tepa-footer-style';
      style.textContent = CSS;
      document.head.appendChild(style);
    }

    // Set external links to open in a new tab (except same-origin).
    var host = location.host;
    var tmp = document.createElement('div');
    tmp.innerHTML = FOOTER_HTML;
    var links = tmp.querySelectorAll('a[href^="http"]');
    for (var i = 0; i < links.length; i++) {
      var a = links[i];
      try {
        var u = new URL(a.href);
        if (u.host !== host) {
          a.setAttribute('target', '_blank');
          a.setAttribute('rel', 'noopener');
        }
      } catch (e) { /* ignore */ }
    }

    // Mark current page.
    var page =
      (document.body && document.body.dataset && document.body.dataset.tepaPage) ||
      (document.documentElement && document.documentElement.dataset && document.documentElement.dataset.tepaPage) ||
      '';
    if (!page) {
      var h = (location.host || '').toLowerCase();
      var p = (location.pathname || '').toLowerCase();
      if (h.indexOf('substack.com') !== -1) page = 'kiwi-dialectic';
      else if (h.indexOf('te-pa.org') !== -1) page = 'te-pa';
      else if (p.indexOf('governance') !== -1) page = 'governance';
      else if (h.indexOf('robertmccallnz.github.io') !== -1) page = 'observatory';
    }
    if (page) {
      var current = tmp.querySelector('.tepa-footer a[data-tepa-nav="' + page + '"]');
      if (current) current.setAttribute('aria-current', 'page');
    }

    slot.replaceWith(tmp.firstElementChild);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
