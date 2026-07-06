/*
 * Te Pā Systems Observatory — shared site footer.
 *
 * Both index.html and governance.html include this script and provide a
 * <div id="site-footer"></div> placeholder. Edit the FOOTER_HTML template
 * below once; both pages update. If JS is disabled, each page can still
 * ship a static fallback inside the placeholder — this script replaces it.
 *
 * The footer is intentionally kept as plain HTML (no framework) so it can
 * be forked, audited, and served from GitHub Pages without a build step.
 */

(function () {
  var FOOTER_HTML = [
    '<footer class="site-footer">',
    '  <div class="footer-grid">',
    '    <div class="footer-block footer-intro">',
    '      <h2>Te Pā Systems Observatory</h2>',
    '      <p>A public systems observatory and governance-audit tool developed as a Te Pā Collective Action Lab artefact, in relation to Te Pā Tūwatawata and The Kiwi Dialectic.</p>',
    '      <p>This repo is a standalone, forkable research artefact. Te Pā remains the kaupapa and charitable-trust anchor; the observatory remains an open technical and pedagogical tool.</p>',
    '    </div>',
    '    <div class="footer-block">',
    '      <h3>Views</h3>',
    '      <ul>',
    '        <li><a href="./index.html" data-nav="index">Observatory</a></li>',
    '        <li><a href="./governance.html" data-nav="governance">Governance Audit</a></li>',
    '      </ul>',
    '    </div>',
    '    <div class="footer-block">',
    '      <h3>Ecosystem</h3>',
    '      <ul>',
    '        <li><a href="https://www.te-pa.org" target="_blank" rel="noopener">Te Pā</a></li>',
    '        <li><a href="https://thekiwidialectic.substack.com/" target="_blank" rel="noopener">Kiwi Dialectic</a></li>',
    '        <li><a href="https://github.com/robertmccallnz/systems-observatory/discussions" target="_blank" rel="noopener">Kōrero</a></li>',
    '      </ul>',
    '    </div>',
    '    <div class="footer-block">',
    '      <h3>Context</h3>',
    '      <ul>',
    '        <li><a href="./docs/LEVERAGE_POINTS.md">Leverage points mapping</a></li>',
    '        <li><a href="./docs/GOVERNANCE_AUDIT.md">Governance audit method</a></li>',
    '        <li><a href="./reports/governance-audit-report.md">Governance audit report</a></li>',
    '        <li><a href="https://github.com/robertmccallnz/systems-observatory" target="_blank" rel="noopener">GitHub repository</a></li>',
    '      </ul>',
    '    </div>',
    '  </div>',
    '  <div class="footer-meta">',
    '    <p>Built under the <a href="https://www.kahuiraraunga.io/" target="_blank" rel="noopener">Māori Data Governance Model</a> of Te Kāhui Raraunga. Public, aggregated, non-personal data only.</p>',
    '  </div>',
    '</footer>'
  ].join('\n');

  function inject() {
    var slot = document.getElementById('site-footer');
    if (!slot) return;
    slot.outerHTML = FOOTER_HTML;

    // Mark the current page's Views link, so the footer echoes the top nav.
    var page = (document.body && document.body.dataset && document.body.dataset.page) || '';
    if (!page) {
      var path = (location.pathname || '').toLowerCase();
      if (path.indexOf('governance') !== -1) page = 'governance';
      else page = 'index';
    }
    var current = document.querySelector('.site-footer a[data-nav="' + page + '"]');
    if (current) current.setAttribute('aria-current', 'page');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
