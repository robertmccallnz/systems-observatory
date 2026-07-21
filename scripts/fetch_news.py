import json
import os
import re
from datetime import datetime, timezone

import feedparser

KEYWORD_MAP = [
    (r'\b(ocr|interest rate|inflation|cpi|gdp|wage|unemployment|tax rate|subsidy|tariff|fine|fee|penalty|benefit rate)\b', '12-parameters'),
    (r'\b(reserve|fund|stockpile|infrastructure|capacity|housing stock|buffer|inventory|resource)\b', '11-buffers'),
    (r'\b(spending|flow|throughput|immigration rate|birth rate|death rate|investment|migration)\b', '10-flows'),
    (r'\b(delay|lag|slow|response time|reporting period|data gap|latency)\b', '9-feedback'),
    (r'\b(regulation|watchdog|oversight|enforcement|audit|sanction|corrective|penalty|review)\b', '8-neg-loops'),
    (r'\b(growth|viral|escalat|compound|accelerat|reinfor|cascade|boom|amplif)\b', '7-pos-loops'),
    (r'\b(data|transparency|OIA|disclosure|report|publish|inform|media|censorship|propaganda)\b', '6-info'),
    (r'\b(law|legislation|act|policy|rule|constitution|charter|regulation|reform|repeal|bill passed)\b', '5-rules'),
    (r'\b(self-govern|autonomy|tino rangatiratanga|devolution|self-organis|local decision|co-govern)\b', '4-self-org'),
    (r'\b(goal|target|objective|mission|vision|purpose|wellbeing|living standard)\b', '3-goals'),
    (r'\b(treaty|tiriti|decoloni|paradigm|worldview|kaupapa|indigenous|systemic|structural racism|colonialism)\b', '2-paradigm'),
    (r'\b(transcend|beyond|new world|transformation|revolution|shift|reimagin|abolish)\b', '1-transcend'),
]

FEEDS = [
    ('https://www.rnz.co.nz/rss/news.xml', 'RNZ'),
    ('https://thespinoff.co.nz/feed', 'The Spinoff'),
    ('https://www.stats.govt.nz/feed/', 'Stats NZ'),
    ('https://www.treasury.govt.nz/news-and-events/rss.xml', 'The Treasury'),
]

def auto_tier(text):
    for pattern, tier in KEYWORD_MAP:
        if re.search(pattern, text or '', re.IGNORECASE):
            return tier
    return '6-info'

def norm_date(entry):
    for key in ('published_parsed', 'updated_parsed'):
        val = entry.get(key)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc).date().isoformat()
            except Exception:
                pass
    for key in ('published', 'updated'):
        val = entry.get(key)
        if val:
            m = re.search(r'(\d{4}-\d{2}-\d{2})', val)
            if m:
                return m.group(1)
    return datetime.now(timezone.utc).date().isoformat()

events = []
seen = set()

for url, source in FEEDS:
    feed = feedparser.parse(url)
    for entry in (feed.entries or [])[:10]:
        headline = (entry.get('title') or '').strip()
        link = (entry.get('link') or '').strip()
        summary = (entry.get('summary') or entry.get('description') or '').strip()
        if not headline:
            continue
        key = headline.lower()[:120]
        if key in seen:
            continue
        seen.add(key)
        events.append({
            'headline': headline,
            'url': link or None,
            'tier': auto_tier(f'{headline} {summary}'),
            'impact': 'ambiguous',
            'reasoning': 'Auto-mapped via keyword analysis — verify and correct via the annotation form below.',
            'date': norm_date(entry),
            'source': source,
            'auto': True
        })

events.sort(key=lambda x: x.get('date', ''), reverse=True)

os.makedirs('data', exist_ok=True)
with open('data/news-events.json', 'w', encoding='utf-8') as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

print(f'wrote {len(events)} events to data/news-events.json')
