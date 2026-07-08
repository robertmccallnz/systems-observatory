/* ── news-feed.js · Systems Observatory · Te Pā ─────────────────────
 *  Loads news events from data/news-events.json (local, community-curated)
 *  AND optionally from a live RSS-to-JSON proxy (rss2json.com free tier).
 *  Auto-maps headlines to leverage tiers via keyword rules.
 *  Renders the #obs-news-list feed with tier badges + impact dots.
 * ──────────────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  // ── Tier metadata ─────────────────────────────────────────────────
  const TIERS = {
    '12-parameters': { label: 'T·12', name: 'Numbers / parameters',  group: 'parameters' },
    '11-buffers':    { label: 'T·11', name: 'Buffers & stocks',       group: 'parameters' },
    '10-flows':      { label: 'T·10', name: 'Flow rates',             group: 'parameters' },
    '9-feedback':    { label: 'T·9',  name: 'Feedback delays',        group: 'structure'  },
    '8-neg-loops':   { label: 'T·8',  name: 'Negative feedback loops',group: 'structure'  },
    '7-pos-loops':   { label: 'T·7',  name: 'Positive feedback loops',group: 'structure'  },
    '6-info':        { label: 'T·6',  name: 'Information flows',      group: 'structure'  },
    '5-rules':       { label: 'T·5',  name: 'Rules of the system',    group: 'rules'      },
    '4-self-org':    { label: 'T·4',  name: 'Self-organisation',      group: 'rules'      },
    '3-goals':       { label: 'T·3',  name: 'Goals of the system',    group: 'paradigm'   },
    '2-paradigm':    { label: 'T·2',  name: 'Paradigm / mindset',     group: 'paradigm'   },
    '1-transcend':   { label: 'T·1',  name: 'Transcending paradigms', group: 'paradigm'   },
  };

  // ── Keyword → tier auto-mapper ────────────────────────────────────
  const KEYWORD_MAP = [
    { re: /\b(ocr|interest rate|inflation|cpi|gdp|wage|unemployment|tax rate|subsidy|tariff|fine|fee|penalty|benefit rate)\b/i, tier: '12-parameters' },
    { re: /\b(reserve|fund|stockpile|infrastructure|capacity|housing stock|buffer|inventory|resource)\b/i, tier: '11-buffers' },
    { re: /\b(spending|flow|throughput|immigration rate|birth rate|death rate|investment|migration)\b/i, tier: '10-flows' },
    { re: /\b(delay|lag|slow|response time|reporting period|data gap|latency)\b/i, tier: '9-feedback' },
    { re: /\b(regulation|watchdog|oversight|enforcement|audit|sanction|corrective|penalty|review)\b/i, tier: '8-neg-loops' },
    { re: /\b(growth|viral|escalat|compound|accelerat|reinfor|cascade|boom|amplif)\b/i, tier: '7-pos-loops' },
    { re: /\b(data|transparency|OIA|disclosure|report|publish|inform|media|censorship|propaganda)\b/i, tier: '6-info' },
    { re: /\b(law|legislation|act|policy|rule|constitution|charter|regulation|reform|repeal|bill passed)\b/i, tier: '5-rules' },
    { re: /\b(self-govern|autonomy|tino rangatiratanga|devolution|self-organis|local decision|co-govern)\b/i, tier: '4-self-org' },
    { re: /\b(goal|target|objective|mission|vision|purpose|wellbeing|living standard)\b/i, tier: '3-goals' },
    { re: /\b(treaty|tiriti|decoloni|paradigm|worldview|kaupapa|indigenous|systemic|structural racism|colonialism)\b/i, tier: '2-paradigm' },
    { re: /\b(transcend|beyond|new world|transformation|revolution|shift|reimagin|abolish)\b/i, tier: '1-transcend' },
  ];

  function autoMapTier(text) {
    for (const { re, tier } of KEYWORD_MAP) {
      if (re.test(text)) return tier;
    }
    return '6-info';
  }

  const IMPACT_ICONS = { stress: '🔴', reinforce: '🟢', ambiguous: '🟡' };

  // ── Seed data ─────────────────────────────────────────────────────
  const SEED_EVENTS = [
    {
      headline: 'Reserve Bank holds OCR at 3.25% amid slowing inflation',
      url: 'https://www.rnz.co.nz/',
      tier: '12-parameters',
      impact: 'reinforce',
      reasoning: 'A tier 12 parameter hold — confirms the numeric lever is being held steady, but does not address structural remit (tier 5).',
      date: '2026-07-07',
      source: 'RNZ'
    },
    {
      headline: 'Fast-track consenting bill passes third reading in Parliament',
      url: 'https://www.parliament.nz/',
      tier: '5-rules',
      impact: 'stress',
      reasoning: 'Rewrites RMA rules (tier 5), weakening environmental feedback loops (tier 8) to accelerate development flows.',
      date: '2026-07-05',
      source: 'Parliament NZ'
    },
    {
      headline: 'Stats NZ releases Wellbeing Report — median household income falls in real terms',
      url: 'https://www.stats.govt.nz/',
      tier: '12-parameters',
      impact: 'stress',
      reasoning: 'Numeric indicator worsens — signals that parameter-level interventions (wages, transfers) are insufficient.',
      date: '2026-07-04',
      source: 'Stats NZ'
    },
    {
      headline: 'Waitangi Tribunal releases report on Treaty of Waitangi principles bill',
      url: 'https://www.waitangitribunal.govt.nz/',
      tier: '2-paradigm',
      impact: 'ambiguous',
      reasoning: 'Contest over the foundational Te Tiriti paradigm — a tier 2 event that could shift goals, rules, and self-organisation simultaneously.',
      date: '2026-07-02',
      source: 'Waitangi Tribunal'
    },
    {
      headline: 'OIA delays reach record high — average 34 days for official information requests',
      url: 'https://ombudsman.parliament.nz/',
      tier: '6-info',
      impact: 'stress',
      reasoning: 'Information flow tier — degraded transparency weakens the corrective feedback (tier 8) that citizens and press apply to government.',
      date: '2026-06-28',
      source: 'Ombudsman NZ'
    },
    {
      headline: 'Co-governance model proposed for Three Waters infrastructure across iwi',
      url: 'https://www.dia.govt.nz/',
      tier: '4-self-org',
      impact: 'reinforce',
      reasoning: 'A tier 4 self-organisation event — extending tino rangatiratanga into infrastructure governance.',
      date: '2026-06-25',
      source: 'DIA'
    },
  ];

  // ── State ─────────────────────────────────────────────────────────
  let allEvents = [];
  let activeFilter = 'all';

  // ── DOM refs ──────────────────────────────────────────────────────
  const list      = document.getElementById('obs-news-list');
  const addBtn    = document.getElementById('obs-news-add-btn');
  const cancelBtn = document.getElementById('obs-news-cancel');
  const panel     = document.getElementById('news-submit-panel');
  const form      = document.getElementById('news-event-form');
  const status    = document.getElementById('news-form-status');
  const shareBtn  = document.getElementById('obs-share-btn');

  // ── Share button ──────────────────────────────────────────────────
  if (shareBtn) {
    shareBtn.addEventListener('click', async () => {
      const data = { title: 'Te Pā Systems Observatory', url: location.href };
      if (navigator.share) {
        try { await navigator.share(data); } catch (_) {}
      } else {
        await navigator.clipboard.writeText(location.href);
        shareBtn.querySelector('span').textContent = 'Copied!';
        setTimeout(() => { shareBtn.querySelector('span').textContent = 'Share'; }, 2000);
      }
    });
  }

  // ── Toggle add-event panel ────────────────────────────────────────
  if (addBtn && panel) {
    addBtn.addEventListener('click', () => {
      const open = panel.hidden;
      panel.hidden = !open;
      addBtn.setAttribute('aria-expanded', String(open));
    });
  }
  if (cancelBtn && panel) {
    cancelBtn.addEventListener('click', () => {
      panel.hidden = true;
      addBtn && addBtn.setAttribute('aria-expanded', 'false');
    });
  }

  // ── Filter buttons ────────────────────────────────────────────────
  document.querySelectorAll('.obs-news-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.obs-news-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      renderList();
    });
  });

  // ── Render ────────────────────────────────────────────────────────
  function renderList() {
    if (!list) return;
    const filtered = activeFilter === 'all'
      ? allEvents
      : allEvents.filter(e => (TIERS[e.tier] || {}).group === activeFilter);

    if (!filtered.length) {
      list.innerHTML = '<li class="obs-news-item" style="padding:1.5rem;color:rgba(232,230,224,0.4);font-size:0.8rem;">No events for this filter yet. Be the first to add one.</li>';
      return;
    }

    list.innerHTML = filtered.map(e => {
      const t = TIERS[e.tier] || { label: '?', name: e.tier, group: 'parameters' };
      const icon = IMPACT_ICONS[e.impact] || '🟡';
      const headline = e.url
        ? `<a href="${escHtml(e.url)}" target="_blank" rel="noopener noreferrer">${escHtml(e.headline)}</a>`
        : escHtml(e.headline);
      return `<li class="obs-news-item" data-filter="${escHtml(t.group)}">
  <div class="obs-news-badge">
    <span class="obs-news-badge-tier">${escHtml(t.label)}</span>
    <span class="obs-news-badge-impact">${escHtml(t.group)}</span>
  </div>
  <div class="obs-news-body">
    <p class="obs-news-headline">${headline}</p>
    <p class="obs-news-reason">${escHtml(e.reasoning || '')}</p>
  </div>
  <div class="obs-news-meta">
    <span class="obs-news-impact-dot" title="${escHtml(e.impact || '')}">${icon}</span>
    <span class="obs-news-date">${escHtml(e.date || '')}</span>
    ${e.source ? `<span class="obs-news-date">${escHtml(e.source)}</span>` : ''}
  </div>
</li>`;
    }).join('');
  }

  function escHtml(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // ── Load data/news-events.json ────────────────────────────────────
  async function loadCommunityEvents() {
    try {
      const r = await fetch('./data/news-events.json');
      if (!r.ok) throw new Error('No community data yet');
      const data = await r.json();
      return Array.isArray(data) ? data : (data.events || []);
    } catch (_) {
      return [];
    }
  }

  // ── Live RSS via rss2json free proxy ──────────────────────────────
  async function loadLiveFeed() {
    const feeds = [
      'https://www.rnz.co.nz/rss/news.xml',
      'https://thespinoff.co.nz/feed',
    ];
    const items = [];
    for (const feedUrl of feeds) {
      try {
        const apiUrl = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(feedUrl)}&count=5`;
        const r = await fetch(apiUrl);
        if (!r.ok) continue;
        const j = await r.json();
        if (j.status !== 'ok') continue;
        for (const item of (j.items || []).slice(0, 5)) {
          const tier = autoMapTier((item.title || '') + ' ' + (item.description || ''));
          items.push({
            headline: item.title || 'Untitled',
            url: item.link || '',
            tier,
            impact: 'ambiguous',
            reasoning: 'Auto-mapped via keyword analysis — verify and correct via the annotation form below.',
            date: item.pubDate ? item.pubDate.slice(0, 10) : '',
            source: j.feed && j.feed.title ? j.feed.title : feedUrl,
            auto: true,
          });
        }
      } catch (_) { /* silent */ }
    }
    return items;
  }

  // ── Form submit ───────────────────────────────────────────────────
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const event = {
        headline: fd.get('headline'),
        url:      fd.get('url') || null,
        tier:     fd.get('tier'),
        impact:   fd.get('impact'),
        reasoning:fd.get('reasoning'),
        date:     new Date().toISOString().slice(0,10),
        source:   'community',
      };
      allEvents.unshift(event);
      renderList();
      form.reset();
      panel.hidden = true;
      addBtn && addBtn.setAttribute('aria-expanded', 'false');
      if (status) {
        status.textContent = '\u2713 Event added to this session. To persist it: commit to data/news-events.json in the repo.';
        status.style.color = '#4fc3c9';
      }
    });
  }

  // ── Bootstrap ─────────────────────────────────────────────────────
  async function init() {
    if (list) list.innerHTML = '';
    const [community, live] = await Promise.allSettled([
      loadCommunityEvents(),
      loadLiveFeed(),
    ]);
    const communityEvents = community.status === 'fulfilled' ? community.value : [];
    const liveEvents      = live.status      === 'fulfilled' ? live.value      : [];
    allEvents = [...communityEvents, ...SEED_EVENTS, ...liveEvents];
    const seen = new Set();
    allEvents = allEvents.filter(e => {
      const key = (e.headline || '').toLowerCase().slice(0, 60);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
    renderList();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
