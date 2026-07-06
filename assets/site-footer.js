/*
 * Te Pā / Kiwi Dialectic — cross-site shared footer.
 *
 * Single source of truth for every site in the ecosystem.
 * Served from jsDelivr:
 *   https://cdn.jsdelivr.net/gh/robertmccallnz/systems-observatory@main/assets/site-footer.js
 *
 * Embed (any site that allows <script>):
 *   <div id="tepa-site-footer"
 *        data-tepa-page="ai-warrior"
 *        data-tepa-support='[{"label":"Koha via Ko-fi","href":"https://ko-fi.com/thekiwidialectic"}]'></div>
 *   <script src=".../site-footer.js" defer></script>
 *
 * Per-page hooks:
 *   data-tepa-page      — highlight the current site in the Ecosystem column
 *   data-tepa-support   — JSON array of {label, href} for the Support column
 *                         (falls back to a default Ko-fi + Substack pair)
 *   data-tepa-theme     — "light" on <html> or <body> to invert the palette
 *
 * jsDelivr caches ~12h; bust with ?v=YYYYMMDD on the src.
 * Pin production sites to a tag: replace @main with @v1.0.0.
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
    '  display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr 1fr;gap:1.5rem;',
    '}',
    '@media(max-width:1180px){.tepa-footer .tepa-grid{grid-template-columns:1.4fr 1fr 1fr;}}',
    '@media(max-width:820px){.tepa-footer .tepa-grid{grid-template-columns:1fr 1fr;}}',
    '@media(max-width:520px){.tepa-footer .tepa-grid{grid-template-columns:1fr;}}',
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
    '.tepa-footer .tepa-block a{color:#e8a83a;text-decoration:none;}',
    '.tepa-footer .tepa-block a:hover,.tepa-footer .tepa-block a:focus-visible{',
    '  color:#d7261e;text-decoration:underline;',
    '}',
    '.tepa-footer .tepa-block a[aria-current="page"]{color:#f4ecd8;font-weight:600;}',
    '.tepa-footer .tepa-block p{color:#d9d1bd;margin:0 0 0.6rem;line-height:1.5;}',
    '.tepa-footer .tepa-meta{',
    '  margin-top:2rem;padding-top:1rem;border-top:1px solid #1e1e1e;',
    '  color:#7a7268;font-size:0.85rem;',
    '}',
    '.tepa-footer .tepa-meta a{color:#e8a83a;text-decoration:none;}',
    '.tepa-footer .tepa-meta a:hover{color:#d7261e;text-decoration:underline;}',
    /* light-theme override */
    '[data-tepa-theme="light"] .tepa-footer{color:#3a3630;border-top-color:#d8d1c5;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-block h2{color:#1a1a1a;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-block h3{color:#6d655c;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-block p{color:#3a3630;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-block a{color:#c1712f;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-meta{color:#6d655c;border-top-color:#d8d1c5;}',
    '[data-tepa-theme="light"] .tepa-footer .tepa-meta a{color:#c1712f;}'
  ].join('');

  // Ecosystem — every property in the network. `key` matches data-tepa-page.
  var ECOSYSTEM = [
    { key: 'kiwi-dialectic',        label: 'The Kiwi Dialectic',       href: 'https://www.kiwidialectic.com/' },
    { key: 'te-pa',                 label: 'Te Pā',                    href: 'https://te-pa.org/' },
    { key: 'observatory',           label: 'Systems Observatory',      href: 'https://robertmccallnz.github.io/systems-observatory/' },
    { key: 'governance',            label: 'Governance Audit',         href: 'https://robertmccallnz.github.io/systems-observatory/governance.html' },
    { key: 'leverage-points',       label: 'Twelve Leverage Points',   href: 'https://robertmccallnz.github.io/leverage-points-course/' },
    { key: 'ai-warrior',            label: 'AI Warrior',               href: 'https://robertmccallnz.github.io/ai-warrior/' },
    { key: 'ai-warrior-te-pa',      label: 'AI Warrior × Te Pā',       href: 'https://robertmccallnz.github.io/ai-warrior-te-pa/' },
    { key: 'ai-literacy-families',  label: 'AI Literacy for Families', href: 'https://robertmccallnz.github.io/ai-literacy-for-families/' },
    { key: 'six-thinkers',          label: 'Six Thinkers',             href: 'https://robertmccallnz.github.io/six-thinkers/' },
    { key: 'cooperative-aotearoa',  label: 'Cooperative Aotearoa',     href: 'https://robertmccallnz.github.io/cooperative-aotearoa/' },
    { key: 'thinkers-mapper',       label: 'Thinkers Mapper',          href: 'https://robertmccallnz.github.io/thinkers-mapper/' },
    { key: 'kd-dialogues',          label: 'KD Dialogues',             href: 'https://robertmccallnz.github.io/kd-dialogues/' },
    { key: 'calendar',              label: 'Course Calendar',          href: 'https://robertmccallnz.github.io/kiwidialecticcalendar-/github-calendar-connector.html' },
    { key: 'te-pa-minisite',        label: 'Te Pā Minisite',           href: 'https://kiwi-dialectic-te-pa-minisite.vercel.app/' },
    { key: 'korero',                label: 'Kōrero (Discussions)',     href: 'https://github.com/robertmccallnz/systems-observatory/discussions' }
  ];

  var READ_WATCH = [
    { label: 'Substack',  href: 'https://www.kiwidialectic.com/' },
    { label: 'Facebook',  href: 'https://www.facebook.com/kiwidialectic/' },
    { label: 'Bluesky',   href: 'https://bsky.app/profile/robertmccallnz.bsky.social' },
    { label: 'Kōrero (Discussions)', href: 'https://github.com/robertmccallnz/systems-observatory/discussions' }
  ];

  var CONTEXT_LINKS = [
    { label: 'Leverage points mapping', href: 'https://github.com/robertmccallnz/systems-observatory/blob/main/docs/LEVERAGE_POINTS.md' },
    { label: 'Governance audit method', href: 'https://github.com/robertmccallnz/systems-observatory/blob/main/docs/GOVERNANCE_AUDIT.md' },
    { label: 'Governance audit report', href: 'https://github.com/robertmccallnz/systems-observatory/blob/main/reports/governance-audit-report.md' },
    { label: 'Embed guide',             href: 'https://github.com/robertmccallnz/systems-observatory/blob/main/docs/EMBED.md' },
    { label: 'GitHub org',              href: 'https://github.com/robertmccallnz' }
  ];

  var DEFAULT_SUPPORT = [
    { label: 'Koha via Ko-fi',        href: 'https://ko-fi.com/thekiwidialectic' },
    { label: 'Pou Tohu — badges',     href: 'https://robertmccallnz.github.io/kiwidialecticcalendar-/badges/' },
    { label: 'Subscribe on Substack', href: 'https://www.kiwidialectic.com/subscribe' }
  ];

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c];
    });
  }

  function link(item, currentKey) {
    var current = item.key && item.key === currentKey ? ' aria-current="page"' : '';
    var data = item.key ? ' data-tepa-nav="' + esc(item.key) + '"' : '';
    return '<li><a href="' + esc(item.href) + '"' + data + current + '>' + esc(item.label) + '</a></li>';
  }

  function block(title, items, currentKey) {
    return '<div class="tepa-block"><h3>' + esc(title) + '</h3><ul>' +
      items.map(function (i) { return link(i, currentKey); }).join('') +
      '</ul></div>';
  }

  function inject() {
    var slot = document.getElementById('tepa-site-footer') ||
               document.getElementById('site-footer');
    if (!slot) return;

    // Inject CSS once.
    if (!document.getElementById('tepa-footer-style')) {
      var style = document.createElement('style');
      style.id = 'tepa-footer-style';
      style.textContent = CSS;
      document.head.appendChild(style);
    }

    // Resolve current page key.
    var page =
      (slot.dataset && slot.dataset.tepaPage) ||
      (document.body && document.body.dataset && document.body.dataset.tepaPage) ||
      (document.documentElement && document.documentElement.dataset && document.documentElement.dataset.tepaPage) ||
      '';
    if (!page) {
      var h = (location.host || '').toLowerCase();
      var p = (location.pathname || '').toLowerCase();
      if (h.indexOf('kiwidialectic.com') !== -1) page = 'kiwi-dialectic';
      else if (h.indexOf('te-pa.org') !== -1) page = 'te-pa';
      else if (h.indexOf('kiwi-dialectic-te-pa-minisite') !== -1) page = 'te-pa-minisite';
      else if (p.indexOf('systems-observatory/governance') !== -1) page = 'governance';
      else if (p.indexOf('systems-observatory') !== -1) page = 'observatory';
      else if (p.indexOf('ai-warrior-te-pa') !== -1) page = 'ai-warrior-te-pa';
      else if (p.indexOf('ai-warrior') !== -1) page = 'ai-warrior';
      else if (p.indexOf('ai-literacy-for-families') !== -1) page = 'ai-literacy-families';
      else if (p.indexOf('six-thinkers') !== -1) page = 'six-thinkers';
      else if (p.indexOf('cooperative-aotearoa') !== -1) page = 'cooperative-aotearoa';
      else if (p.indexOf('thinkers-mapper') !== -1) page = 'thinkers-mapper';
      else if (p.indexOf('leverage-points-course') !== -1) page = 'leverage-points';
      else if (p.indexOf('kd-dialogues') !== -1) page = 'kd-dialogues';
      else if (p.indexOf('kiwidialecticcalendar') !== -1) page = 'calendar';
    }

    // Per-site Support column (default falls back to Ko-fi + Substack).
    var support = DEFAULT_SUPPORT;
    var raw = slot.dataset && slot.dataset.tepaSupport;
    if (raw) {
      try {
        var parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length) support = parsed;
      } catch (e) { /* keep default */ }
    }

    var currentEcosystem = ECOSYSTEM.find(function (e) { return e.key === page; });
    var currentLabel = currentEcosystem ? currentEcosystem.label : 'This site';

    var html =
      '<footer class="tepa-footer" role="contentinfo">' +
      '  <div class="tepa-grid">' +
      '    <div class="tepa-block">' +
      '      <h2>The Kiwi Dialectic × Te Pā</h2>' +
      '      <p>An open ecosystem of courses, kōrero, and public systems tooling. Free HTML, Creative Commons–licensed, forkable. Every site here is part of the same kaupapa.</p>' +
      '      <p style="font-size:0.85rem;color:#7a7268;">You are on <strong style="color:#f4ecd8;">' + esc(currentLabel) + '</strong>.</p>' +
      '    </div>' +
           block('Ecosystem', ECOSYSTEM.slice(0, 7), page) +
           block('Also in the network', ECOSYSTEM.slice(7), page) +
           block('Read & Watch', READ_WATCH, null) +
           block('Support', support, null) +
      '  </div>' +
      '  <div class="tepa-meta">' +
      '    <p>Built under the <a href="https://www.kahuiraraunga.io/">Māori Data Governance Model</a> of Te Kāhui Raraunga. Public, aggregated, non-personal data only. Content licensed CC BY-SA 4.0 unless noted. Kaupapa: The Kiwi Dialectic × Te Pā Collective Action Lab · Dunedin, Aotearoa.</p>' +
      '  </div>' +
      '</footer>';

    var tmp = document.createElement('div');
    tmp.innerHTML = html;

    // Open external links in a new tab.
    var host = location.host;
    tmp.querySelectorAll('a[href^="http"]').forEach(function (a) {
      try {
        var u = new URL(a.href);
        if (u.host !== host) {
          a.setAttribute('target', '_blank');
          a.setAttribute('rel', 'noopener');
        }
      } catch (e) { /* ignore */ }
    });

    slot.replaceWith(tmp.firstElementChild);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
