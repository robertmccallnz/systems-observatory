#!/usr/bin/env python3
"""Fetch NZ news via RSS and map headlines to Meadows leverage points.

Writes data/news-events.json in the schema consumed by assets/news-feed.js:
{headline, url, tier, impact, reasoning, date, source, auto}
"""
import json, os, re, sys
from datetime import datetime, timezone

try:
    import feedparser
except ImportError:
    sys.exit("feedparser not installed: pip install feedparser")

# Meadows 12 leverage points -> keyword patterns (specific first).
KEYWORD_MAP = [
    (r"\b(transcend|paradigm shift|abolish|reimagin|transformation)\b", "1-transcend"),
    (r"\b(treaty|tiriti|decoloni|indigenous rights|structural racism|constitution)\b", "2-paradigm"),
    (r"\b(goal|target|mission|wellbeing|living standards|strategy)\b", "3-goals"),
    (r"\b(self-govern|autonomy|tino rangatiratanga|devolution|co-govern|cooperative)\b", "4-self-org"),
    (r"\b(law|legislation|\bact\b|policy|regulation|reform|repeal|bill)\b", "5-rules"),
    (r"\b(data|transparency|oia|disclosure|report|publish|official information)\b", "6-info"),
    (r"\b(growth|viral|escalat|compound|accelerat|cascade|boom|surge)\b", "7-pos-loops"),
    (r"\b(watchdog|oversight|enforcement|audit|sanction|penalty|inquiry)\b", "8-neg-loops"),
    (r"\b(delay|lag|slow|response time|reporting period|data gap|backlog)\b", "9-feedback"),
    (r"\b(spending|immigration|birth rate|investment|migration|budget|funding)\b", "10-flows"),
    (r"\b(reserve|fund|stockpile|infrastructure|capacity|housing stock|supply)\b", "11-buffers"),
    (r"\b(ocr|interest rate|inflation|cpi|gdp|wage|unemployment|tax)\b", "12-parameters"),
]

IMPACT_MAP = [
    (r"\b(cut|fall|drop|decline|loss|crisis|fail|reject|scandal|warn|risk)\b", "negative"),
    (r"\b(rise|boost|gain|invest|expand|approve|win|record|improve|launch)\b", "positive"),
]

FEEDS = [
    ("https://www.rnz.co.nz/rss/national.xml", "RNZ"),
    ("https://www.rnz.co.nz/rss/political.xml", "RNZ Politics"),
    ("https://thespinoff.co.nz/feed", "The Spinoff"),
    ("https://www.stats.govt.nz/rss/", "Stats NZ"),
]

MAX_PER_FEED = 6


def classify(text, table, default):
    for pattern, label in table:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return default


def norm_date(entry):
    for key in ("published", "updated"):
        val = entry.get(key)
        if val:
            return val[:10] if re.match(r"\d{4}-\d{2}-\d{2}", val[:10]) else _parse(entry, key)
    return datetime.now(timezone.utc).date().isoformat()


def _parse(entry, key):
    tm = entry.get(key + "_parsed")
    if tm:
        return datetime(*tm[:6]).date().isoformat()
    return datetime.now(timezone.utc).date().isoformat()


def main():
    events = []
    for url, source in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:MAX_PER_FEED]:
            title = entry.get("title", "").strip()
            if not title:
                continue
            blob = title + " " + re.sub(r"<[^>]+>", " ", entry.get("summary", ""))
            events.append({
                "headline": title,
                "url": entry.get("link", ""),
                "tier": classify(blob, KEYWORD_MAP, "6-info"),
                "impact": classify(blob, IMPACT_MAP, "ambiguous"),
                "reasoning": "Auto-mapped via keyword analysis. Verify via the Add event form.",
                "date": _parse(entry, "published") if entry.get("published_parsed") else norm_date(entry),
                "source": source,
                "auto": True,
            })

    # newest first
    events.sort(key=lambda e: e["date"], reverse=True)

    out = os.path.join("data", "news-events.json")
    os.makedirs("data", exist_ok=True)
    if not events:
        print("WARNING: no events fetched; leaving existing file untouched")
        return
    with open(out, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(events)} events to {out}")


if __name__ == "__main__":
    main()
