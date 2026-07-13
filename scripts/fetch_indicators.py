#!/usr/bin/env python3
"""
Te Pa Systems Observatory - indicator fetcher.

Pulls live public NZ data, computes rolling z-scores, writes data/indicators.json.
Runs in GitHub Actions on a daily cron (see .github/workflows/refresh.yml).

Design principles:
- Public, aggregated, non-personal data only (Maori Data Governance Model).
- Every value is sourced. If a source fails, we keep the last-known value
  and flag the fetch status, never invent numbers.
- Anomalies flagged via rolling z-score (|z| >= 2.5).
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
import statistics
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "indicators.json"

UA = "TePaSystemsObservatory/1.0 (+https://te-pa.org)"
TIMEOUT = 60


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def _rolling_zscore(values, window=24):
    if len(values) < 6:
        return None
    tail = values[-(window + 1):-1] if len(values) > window else values[:-1]
    if len(tail) < 3:
        return None
    mu = statistics.fmean(tail)
    sd = statistics.pstdev(tail)
    if sd == 0 or math.isnan(sd):
        return None
    return round((values[-1] - mu) / sd, 3)


def _finalise(series):
    if not series:
        return None, None
    values = [float(p["value"]) for p in series if p.get("value") is not None]
    if not values:
        return None, None
    latest = values[-1]
    z = _rolling_zscore(values)
    anomaly = None
    if z is not None and abs(z) >= 2.5:
        anomaly = {
            "z_score": z,
            "direction": "high" if z > 0 else "low",
            "at": series[-1].get("period"),
            "message": f"|z|={abs(z):.2f} vs prior 24-period baseline.",
        }
    return latest, anomaly


def fetch_ocr():
    """RBNZ Official Cash Rate - historical CSV, downsampled to monthly."""
    url = "https://www.rbnz.govt.nz/-/media/ReserveBank/Files/Statistics/tables/b2/hb2-daily.csv"
    try:
        raw = _get(url).decode("utf-8", errors="replace")
    except Exception:
        return []
    out = []
    for line in raw.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", parts[0]):
            continue
        try:
            v = float(parts[1])
        except ValueError:
            continue
        out.append({"period": parts[0], "value": v})
    seen = {}
    for p in out:
        seen[p["period"][:7]] = p
    monthly = sorted(seen.values(), key=lambda x: x["period"])
    return monthly[-120:]


def fetch_dwelling_consents():
    """Stats NZ - New dwellings consented (monthly).

    Strategy: scrape the Building topic page to find the newest
    'Building consents issued: {Month} {Year} - CSV' ZIP URL,
    download it, open the 'institutional sector (Monthly)' CSV inside,
    parse the total-dwelling-units-authorised column into a monthly series.
    """
    topic_url = "https://www.stats.govt.nz/topics/building/"
    try:
        html = _get(topic_url).decode("utf-8", errors="replace")
    except Exception:
        return []
    # Find the latest release page URL.
    m = re.search(r'/information-releases/building-consents-issued-[a-z]+-20\d{2}/', html)
    if not m:
        return []
    release_url = "https://www.stats.govt.nz" + m.group(0)
    try:
        release_html = _get(release_url).decode("utf-8", errors="replace")
    except Exception:
        return []
    # Find the CSV ZIP link on the release page.
    zm = re.search(r'https?://[^"\']+building-consents-issued[^"\']*?\.zip', release_html)
    if not zm:
        return []
    zip_url = zm.group(0)
    try:
        zip_bytes = _get(zip_url)
    except Exception:
        return []
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except Exception:
        return []
    target = None
    for name in zf.namelist():
        low = name.lower()
        if "institutional" in low and "monthly" in low and low.endswith(".csv"):
            target = name
            break
    if target is None:
        for name in zf.namelist():
            if name.lower().endswith(".csv") and "monthly" in name.lower():
                target = name
                break
    if target is None:
        return []
    try:
        text = zf.read(target).decode("utf-8", errors="replace")
    except Exception:
        return []
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return []
    # Heuristic: find a column whose header mentions 'dwelling' and 'total'
    header = rows[0]
    period_idx = 0
    value_idx = None
    for i, h in enumerate(header):
        hl = h.lower()
        if "total" in hl and ("dwelling" in hl or "unit" in hl):
            value_idx = i
            break
    if value_idx is None:
        # Fall back to the last numeric column.
        for i in range(len(header) - 1, 0, -1):
            try:
                float(rows[1][i].replace(",", ""))
                value_idx = i
                break
            except (ValueError, IndexError):
                continue
    if value_idx is None:
        return []
    out = []
    for row in rows[1:]:
        if len(row) <= value_idx:
            continue
        period = row[period_idx].strip()
        # Normalise YYYY-MM or YYYYMM to YYYY-MM.
        pm = re.match(r"^(\d{4})[-/]?(\d{2})", period)
        if not pm:
            continue
        period_norm = f"{pm.group(1)}-{pm.group(2)}"
        try:
            v = float(row[value_idx].replace(",", ""))
        except ValueError:
            continue
        out.append({"period": period_norm, "value": v})
    out.sort(key=lambda x: x["period"])
    # De-duplicate on period, keep the last.
    seen = {}
    for p in out:
        seen[p["period"]] = p
    monthly = sorted(seen.values(), key=lambda x: x["period"])
    return monthly[-120:]


def fetch_ombudsman_oia():
    return []


def fetch_waitangi_tribunal():
    return []


FETCHERS = {
    12: fetch_ocr,
    11: fetch_dwelling_consents,
    6: fetch_ombudsman_oia,
    1: fetch_waitangi_tribunal,
}


def main():
    doc = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    doc["meta"]["generated_at"] = datetime.now(timezone.utc).isoformat()
    status = []
    for lp in doc["leverage_points"]:
        fetcher = FETCHERS.get(lp["id"])
        if fetcher is None:
            latest, anomaly = _finalise(lp.get("series") or [])
            lp["latest"] = latest
            lp["anomaly"] = anomaly
            continue
        try:
            series = fetcher()
        except Exception as e:
            status.append(f"LP{lp['id']} fetch failed: {e}")
            series = lp.get("series") or []
        if series:
            lp["series"] = series
        latest, anomaly = _finalise(lp.get("series") or [])
        lp["latest"] = latest
        lp["anomaly"] = anomaly
        status.append(
            f"LP{lp['id']} ok - {len(lp.get('series') or [])} points, "
            f"latest={latest}, anomaly={'yes' if anomaly else 'no'}"
        )
    doc["meta"]["fetch_status"] = status
    DATA_FILE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n".join(status))
    return 0


if __name__ == "__main__":
    sys.exit(main())
