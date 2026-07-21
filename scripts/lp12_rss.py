#!/usr/bin/env python3
"""LP12 OCR fetcher via RBNZ RSS/Atom feeds.

RBNZ blocks non-browser HTML scraping (HTTP 403), but publishes machine-readable
RSS/Atom feeds for monetary policy announcements. This module attempts a small
set of known RBNZ feed URLs, extracts the most recent OCR announcement, and
parses the percentage rate. On any failure it raises RuntimeError; callers
should preserve the last-known value.
"""
from __future__ import annotations

import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from typing import Optional

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# Candidate RBNZ feeds - tried in order. Extend as new URLs are discovered.
_FEEDS = [
    "https://www.rbnz.govt.nz/monetary-policy/official-cash-rate-decisions",
    "https://www.rbnz.govt.nz/rss/news",
    "https://www.rbnz.govt.nz/rss/monetary-policy",
    "https://www.rbnz.govt.nz/rss/official-cash-rate",
]

_OCR_RATE_RE = re.compile(r"(\d+\.\d{1,2})\s*(?:%|percent)", re.IGNORECASE)
_OCR_MENTION_RE = re.compile(r"official\s+cash\s+rate|OCR\b", re.IGNORECASE)


def _http_get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": _UA,
            "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.5",
            "Accept-Language": "en-NZ,en;q=0.9",
        },
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code in (403, 429, 503) and not url.startswith("https://r.jina.ai/"):
            proxied = "https://r.jina.ai/" + url
            print(f"[LP12] direct {e.code} on {url}; retrying via reader proxy", flush=True)
            req2 = urllib.request.Request(proxied, headers={"User-Agent": _UA, "Accept": "text/plain, */*;q=0.5"})
            with urllib.request.urlopen(req2, timeout=timeout, context=ctx) as resp:
                return resp.read().decode("utf-8", errors="replace")
        raise


def _extract_rate_from_text(text: str) -> Optional[float]:
    if not _OCR_MENTION_RE.search(text):
        return None
    m = _OCR_RATE_RE.search(text)
    if not m:
        return None
    try:
        v = float(m.group(1))
    except ValueError:
        return None
    # Guard: OCR is realistically 0.0-15.0 %
    if 0.0 <= v <= 15.0:
        return v
    return None


def fetch_rbnz_ocr_rss() -> float:
    """Return the latest OCR (as a float percent, e.g. 2.5).

    Raises RuntimeError if no feed yields a parseable OCR announcement.
    """
    last_error: Optional[str] = None
    for url in _FEEDS:
        try:
            body = _http_get(url)
        except Exception as exc:  # noqa: BLE001
            last_error = f"{url}: {type(exc).__name__}: {exc}"
            continue
        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            last_error = f"{url}: parse error: {exc}"
            continue
        for elem in root.iter():
            tag = elem.tag.rsplit("}", 1)[-1].lower()
            if tag not in ("item", "entry"):
                continue
            parts = []
            for child in elem.iter():
                if child.text:
                    parts.append(child.text)
            blob = " ".join(parts)
            rate = _extract_rate_from_text(blob)
            if rate is not None:
                return rate
        last_error = f"{url}: no OCR announcement found in feed"
    raise RuntimeError(f"RBNZ RSS OCR fetch failed: {last_error}")


if __name__ == "__main__":
    try:
        print("LP12 OCR (RSS):", fetch_rbnz_ocr_rss())
    except Exception as exc:  # noqa: BLE001
        print("LP12 OCR fetch failed:", exc)
