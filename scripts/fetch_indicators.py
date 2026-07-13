#!/usr/bin/env python3
"""Te Pa Systems Observatory - indicator fetcher (LP11+LP12)."""
from __future__ import annotations

import csv
import io
import json
import math
import re
import statistics
import urllib.request
import urllib.error
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "indicators.json"
UA = "TePaSystemsObservatory/1.0 (+https://te-pa.org)"
BROWSER_UA = (
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
  "AppleWebKit/537.36 (KHTML, like Gecko) "
  "Chrome/126.0.0.0 Safari/537.36"
)
TIMEOUT = 90

MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]
MONTH_MAP = {name.capitalize(): i + 1 for i, name in enumerate(MONTHS)}


def _get(url):
  req = urllib.request.Request(url, headers={"User-Agent": UA})
  with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
    return r.read()


def _get_browser(url, referer=None):
  headers = {
    "User-Agent": BROWSER_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-NZ,en;q=0.9",
    "Accept-Encoding": "identity",
    "Upgrade-Insecure-Requests": "1",
  }
  if referer:
    headers["Referer"] = referer
  req = urllib.request.Request(url, headers=headers)
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
  anomaly = z is not None and abs(z) >= 2
  return latest, anomaly


def _find_latest_consents_zip():
  today = date.today()
  y, m = today.year, today.month
  for _ in range(12):
    m -= 1
    if m == 0:
      m = 12
      y -= 1
    month_name = MONTHS[m - 1]
    month_year = f"{month_name}-{y}"
    zip_url = (
      "https://www.stats.govt.nz/assets/Uploads/Building-consents-issued/"
      f"Building-consents-issued-{month_name.title()}-{y}/Download-data/"
      f"building-consents-issued-{month_year}.zip"
    )
    release_url = f"https://www.stats.govt.nz/information-releases/building-consents-issued-{month_year}/"
    try:
      req = urllib.request.Request(zip_url, headers={"User-Agent": UA}, method="HEAD")
      with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        if r.status == 200:
          return release_url, zip_url
    except Exception as e:
      print(f"[LP11] probe {month_year} miss: {e}", flush=True)
      continue
  return None, None


def fetch_dwelling_consents():
  release_url, zip_url = _find_latest_consents_zip()
  print(f"[LP11] release_url={release_url}", flush=True)
  if not release_url:
    return []
  print(f"[LP11] zip_url={zip_url}", flush=True)
  try:
    zip_bytes = _get(zip_url)
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
  except Exception as e:
    print(f"[LP11] zip fetch/open error: {e}", flush=True)
    return []
  names = zf.namelist()
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
    return []
  print(f"[LP11] target={target}", flush=True)
  try:
    text = zf.read(target).decode("utf-8", errors="replace")
  except Exception as e:
    print(f"[LP11] csv read error: {e}", flush=True)
    return []
  reader = csv.DictReader(io.StringIO(text))
  series = []
  for row in reader:
    if row.get("Series_reference", "").strip() != "BLDM.SW00001A1":
      continue
    period_raw = row.get("Period", "").strip()
    val_raw = row.get("Data_value", "").strip()
    if not period_raw or not val_raw:
      continue
    try:
      year, month = period_raw.split(".")
      period = f"{int(year):04d}-{int(month):02d}"
      val = float(val_raw)
    except (ValueError, IndexError):
      continue
    series.append({"period": period, "value": val})
  series.sort(key=lambda x: x["period"])
  print(f"[LP11] parsed {len(series)} points", flush=True)
  return series[-120:]


# LP12 - OCR: global-rates.com uses MM-DD-YYYY | X.XX %
OCR_ROW = re.compile(r"(\d{2})-(\d{2})-(\d{4})\D{1,80}?(\d+\.\d{2})\s*%")


def fetch_ocr():
  url = "https://www.global-rates.com/en/interest-rates/central-banks/23/new-zealand-official-cash-rate/"
  try:
    html = _get_browser(url).decode("utf-8", errors="replace")
  except Exception as e:
    print(f"[LP12] fetch error: {e}", flush=True)
    return []
  seen = set()
  series = []
  for m in OCR_ROW.finditer(html):
    mo, dy, yr, rate = m.group(1), m.group(2), m.group(3), m.group(4)
    try:
      d = date(int(yr), int(mo), int(dy))
      r = float(rate)
    except Exception:
      continue
    if r < 0 or r > 20:
      continue
    key = d.isoformat()
    if key in seen:
      continue
    seen.add(key)
    series.append({"period": key, "value": r})
  series.sort(key=lambda x: x["period"])
  print(f"[LP12] parsed {len(series)} OCR decisions", flush=True)
  return series[-120:]


def fetch_ombudsman_oia():
  return []


def fetch_waitangi_tribunal():
  return []


FETCHERS = {12: fetch_ocr, 11: fetch_dwelling_consents, 6: fetch_ombudsman_oia, 5: fetch_waitangi_tribunal}


def main():
  doc = json.loads(DATA_FILE.read_text(encoding="utf-8"))
  now = datetime.now(timezone.utc).isoformat()
  for lp in doc.get("leverage_points", []):
    num = lp.get("id")
    fetcher = FETCHERS.get(num)
    if not fetcher:
      continue
    try:
      series = fetcher()
    except Exception as e:
      print(f"[LP{num}] fetch error: {e}", flush=True)
      continue
    if not series:
      print(f"[LP{num}] no data - keeping last known value", flush=True)
      continue
    latest, anomaly = _finalise(series)
    lp["series"] = series
    if latest is not None:
      lp["latest_value"] = latest
    lp["anomaly"] = bool(anomaly)
    lp["updated_at"] = now
    print(f"[LP{num}] ok - {len(series)} points, latest={latest}, anomaly={'yes' if anomaly else 'no'}", flush=True)
  DATA_FILE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
  main()
