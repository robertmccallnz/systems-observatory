#!/usr/bin/env python3
"""Te Pa Systems Observatory - indicator fetcher (with LP11 diagnostics)."""
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
        zurl = f"https://www.stats.govt.nz/assets/Uploads/Building-consents-issued/Building-consents-issued-{MONTHS[m-1].capitalize()}-{y}/Download-data/building-consents-issued-{MONTHS[m-1]}-{y}.zip"
        try:
            req = urllib.request.Request(zurl, method="HEAD", headers={"User-Agent": UA})
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
    print(f"[LP11] release_url={release_url}", flush=True)
    if not release_url:
        return []
    try:
        html = _get(release_url).decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[LP11] release fetch error: {e}", flush=True)
        return []
    zm = re.search(r'https?://[^"\'\s<>]+building-consents-issued[^"\'\s<>]*?\.zip', html, re.I)
    if zm:
        zip_url = zm.group(0)
    else:
        rm = re.search(r'(/[^"\'\s<>]*building-consents-issued[^"\'\s<>]*?\.zip)', html, re.I)
        if not rm:
            print("[LP11] no zip URL found on release page", flush=True)
            # Print first 400 chars of any csv/zip mentions for debugging
            for m2 in re.finditer(r'[^"\'\s<>]{0,80}\.zip', html)[:5]:
                print(f"[LP11] zip-like: {m2.group(0)}", flush=True)
            return []
        zip_url = "https://www.stats.govt.nz" + rm.group(1)
    print(f"[LP11] zip_url={zip_url}", flush=True)
    try:
        zip_bytes = _get(zip_url)
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except Exception as e:
        print(f"[LP11] zip fetch/open error: {e}", flush=True)
        return []
    names = zf.namelist()
    print(f"[LP11] zip contains {len(names)} files", flush=True)
    for n in names[:30]:
        print(f"[LP11]   {n}", flush=True)
    target = None
    for name in names:
        low = name.lower()
        if low.endswith(".csv") and "institutional" in low and "monthly" in low:
            target = name
            break
    if target is None:
        for name in names:
            if name.lower().endswith(".csv") and "monthly" in name.lower():
                target = name
                break
    if target is None:
        for name in names:
            if name.lower().endswith(".csv"):
                target = name
                break
    print(f"[LP11] target={target}", flush=True)
    if target is None:
        return []
    try:
        text = zf.read(target).decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[LP11] csv read error: {e}", flush=True)
        return []
    rows = list(csv.reader(io.StringIO(text)))
    print(f"[LP11] csv has {len(rows)} rows", flush=True)
    if rows:
        print(f"[LP11] header: {rows[0]}", flush=True)
    if len(rows) >= 2:
        print(f"[LP11] row1: {rows[1]}", flush=True)
    if len(rows) >= 3:
        print(f"[LP11] row2: {rows[2]}", flush=True)
    return []


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
