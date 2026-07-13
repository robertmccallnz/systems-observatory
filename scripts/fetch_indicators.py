#!/usr/bin/env python3
"""Te Pa Systems Observatory - indicator fetcher."""
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
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "indicators.json"
UA = "TePaSystemsObservatory/1.0 (+https://te-pa.org)"
TIMEOUT = 90


def _get(url):
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
        anomaly = {"z_score": z, "direction": "high" if z > 0 else "low",
                   "at": series[-1].get("period"),
                   "message": f"|z|={abs(z):.2f} vs prior 24-period baseline."}
    return latest, anomaly


def fetch_ocr():
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
    return sorted(seen.values(), key=lambda x: x["period"])[-120:]


MONTHS = ["january","february","march","april","may","june","july","august","september","october","november","december"]


def _find_latest_consents_release_url():
    today = date.today()
    y, m = today.year, today.month
    for _ in range(24):
        url = f"https://www.stats.govt.nz/information-releases/building-consents-issued-{MONTHS[m-1]}-{y}/"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                if r.status == 200:
                    return url
        except Exception:
            pass
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return None


def fetch_dwelling_consents():
    release_url = _find_latest_consents_release_url()
    if not release_url:
        return []
    try:
        html = _get(release_url).decode("utf-8", errors="replace")
    except Exception:
        return []
    zm = re.search(r'https?://[^"\'\s<>]+building-consents-issued[^"\'\s<>]*?\.zip', html, re.I)
    if zm:
        zip_url = zm.group(0)
    else:
        rm = re.search(r'(/assets/[^"\'\s<>]+building-consents-issued[^"\'\s<>]*?\.zip)', html, re.I)
        if not rm:
            return []
        zip_url = "https://www.stats.govt.nz" + rm.group(1)
    try:
        zip_bytes = _get(zip_url)
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except Exception:
        return []
    target = None
    for name in zf.namelist():
        low = name.lower()
        if low.endswith(".csv") and "institutional" in low and "monthly" in low:
            target = name
            break
    if target is None:
        for name in zf.namelist():
            if name.lower().endswith(".csv") and "monthly" in name.lower():
                target = name
                break
    if target is None:
        for name in zf.namelist():
            if name.lower().endswith(".csv"):
                target = name
                break
    if target is None:
        return []
    try:
        text = zf.read(target).decode("utf-8", errors="replace")
    except Exception:
        return []
    rows = list(csv.reader(io.StringIO(text)))
    if len(rows) < 2:
        return []
    header = rows[0]
    period_idx = 0
    for i, cell in enumerate(rows[1]):
        if re.match(r"^\d{4}[-/]\d{2}", (cell or "").strip()):
            period_idx = i
            break
    value_idx = None
    for i, h in enumerate(header):
        hl = (h or "").lower()
        if "total" in hl and ("dwelling" in hl or "unit" in hl):
            value_idx = i
            break
    if value_idx is None:
        for i in range(len(rows[1]) - 1, -1, -1):
            try:
                float((rows[1][i] or "").replace(",", ""))
                value_idx = i
                break
            except (ValueError, IndexError):
                continue
    if value_idx is None:
        return []
    out = []
    for row in rows[1:]:
        if len(row) <= max(period_idx, value_idx):
            continue
        pm = re.match(r"^(\d{4})[-/]?(\d{2})", (row[period_idx] or "").strip())
        if not pm:
            continue
        try:
            v = float((row[value_idx] or "").replace(",", ""))
        except ValueError:
            continue
        out.append({"period": f"{pm.group(1)}-{pm.group(2)}", "value": v})
    seen = {}
    for p in out:
        seen[p["period"]] = p
    return sorted(seen.values(), key=lambda x: x["period"])[-120:]


def fetch_ombudsman_oia():
    return []


def fetch_waitangi_tribunal():
    return []


FETCHERS = {12: fetch_ocr, 11: fetch_dwelling_consents, 6: fetch_ombudsman_oia, 1: fetch_waitangi_tribunal}


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
        status.append(f"LP{lp['id']} ok - {len(lp.get('series') or [])} points, latest={latest}, anomaly={'yes' if anomaly else 'no'}")
    doc["meta"]["fetch_status"] = status
    DATA_FILE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n".join(status))
    return 0


if __name__ == "__main__":
    sys.exit(main())
