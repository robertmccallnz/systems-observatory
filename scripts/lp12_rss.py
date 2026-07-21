#!/usr/bin/env python3
"""LP12 OCR fetcher.

Two public entry points:
  * fetch_ocr_schedule() -> list[{"date": "YYYY-MM-DD", "value": float}]
      Parses the RBNZ 'Official Cash Rate decisions' page (via r.jina.ai
      reader proxy to bypass Cloudflare 403) and returns every dated OCR
      decision it can find, sorted ascending by date.
  * fetch_rbnz_ocr_rss() -> float
      Legacy single-rate fallback using RSS/Atom feeds.
"""
from __future__ import annotations
import re, ssl, urllib.request, urllib.error
import xml.etree.ElementTree as ET
from datetime import date
from typing import Optional

_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")

_DECISIONS_URL = "https://www.rbnz.govt.nz/monetary-policy/official-cash-rate-decisions"
_FEEDS = [
    _DECISIONS_URL,
    "https://www.rbnz.govt.nz/rss/news",
    "https://www.rbnz.govt.nz/rss/monetary-policy",
    "https://www.rbnz.govt.nz/rss/official-cash-rate",
]

_MONTHS = {m:i for i,m in enumerate(
    ["January","February","March","April","May","June",
     "July","August","September","October","November","December"], start=1)}

_SCHEDULE_RE = re.compile(
    r"\b([0-3]?[0-9])\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20[2-9][0-9])\s+(\d+(?:\.\d{1,2})?)\b"
)
_OCR_RATE_RE = re.compile(r"(\d+\.\d{1,2})\s*(?:%|percent)", re.IGNORECASE)
_OCR_MENTION_RE = re.compile(r"official\s+cash\s+rate|OCR\b", re.IGNORECASE)


def _http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": _UA,
        "Accept": "text/html, application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.5",
        "Accept-Language": "en-NZ,en;q=0.9",
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code in (403, 429, 503) and not url.startswith("https://r.jina.ai/"):
            proxied = "https://r.jina.ai/" + url
            print(f"[LP12] {e.code} on {url}; retrying via reader proxy", flush=True)
            req2 = urllib.request.Request(proxied, headers={"User-Agent": _UA, "Accept": "text/plain, */*;q=0.5"})
            with urllib.request.urlopen(req2, timeout=timeout, context=ctx) as resp:
                return resp.read().decode("utf-8", errors="replace")
        raise


def fetch_ocr_schedule():
    body = _http_get("https://r.jina.ai/" + _DECISIONS_URL)
    seen = {}
    for m in _SCHEDULE_RE.finditer(body):
        d, mon, yr, rate = m.group(1), m.group(2), m.group(3), m.group(4)
        try:
            iso = date(int(yr), _MONTHS[mon], int(d)).isoformat()
            val = float(rate)
        except (ValueError, KeyError):
            continue
        if not (0.0 <= val <= 15.0):
            continue
        seen.setdefault(iso, val)
    if not seen:
        raise RuntimeError("RBNZ decisions page yielded no dated OCR entries")
    return [{"date": k, "value": v} for k, v in sorted(seen.items())]


def _extract_rate_from_text(text):
    if not _OCR_MENTION_RE.search(text): return None
    m = _OCR_RATE_RE.search(text)
    if not m: return None
    try: v = float(m.group(1))
    except ValueError: return None
    return v if 0.0 <= v <= 15.0 else None


def fetch_rbnz_ocr_rss():
    last_error = None
    for url in _FEEDS:
        try: body = _http_get(url)
        except Exception as exc:
            last_error = f"{url}: {type(exc).__name__}: {exc}"; continue
        try: root = ET.fromstring(body)
        except ET.ParseError as exc:
            rate_txt = _extract_rate_from_text(body)
            if rate_txt is not None: return rate_txt
            last_error = f"{url}: parse error: {exc}"; continue
        for elem in root.iter():
            tag = elem.tag.rsplit("}", 1)[-1].lower()
            if tag not in ("item", "entry"): continue
            parts = [c.text for c in elem.iter() if c.text]
            rate = _extract_rate_from_text(" ".join(parts))
            if rate is not None: return rate
        last_error = f"{url}: no OCR announcement found"
    raise RuntimeError(f"RBNZ RSS OCR fetch failed: {last_error}")


if __name__ == "__main__":
    import json, sys
    try:
        sched = fetch_ocr_schedule()
        today = date.today().isoformat()
        enacted = [e for e in sched if e["date"] <= today]
        forward = [e for e in sched if e["date"] >  today]
        print(json.dumps({"today": today,
                          "enacted_latest": enacted[-1] if enacted else None,
                          "forward": forward,
                          "n_enacted": len(enacted),
                          "n_forward": len(forward)}, indent=2))
    except Exception as exc:
        print("schedule fetch failed:", exc, file=sys.stderr)
        try: print("RSS fallback OCR:", fetch_rbnz_ocr_rss())
        except Exception as exc2:
            print("RSS fallback also failed:", exc2, file=sys.stderr); sys.exit(1)
