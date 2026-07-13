#!/usr/bin/env python3
"""Te Pa Systems Observatory - indicator fetcher (all 12 LPs wired)."""
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


def _fred_csv(series_id):
  url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
  text = _get(url).decode("utf-8", errors="replace")
  rows = list(csv.reader(io.StringIO(text)))
  out = []
  for row in rows[1:]:
    if len(row) < 2:
      continue
    d, v = row[0].strip(), row[1].strip()
    if not d or v in ("", "."):
      continue
    try:
      dt = datetime.strptime(d, "%Y-%m-%d").date()
      val = float(v)
    except Exception:
      continue
    out.append({"period": dt.isoformat()[:7], "value": val})
  out.sort(key=lambda x: x["period"])
  return out


# ---------- LP1: Waitangi Tribunal reports released (annual) ----------
def fetch_lp1_waitangi():
  print("[LP1] no automated fetcher yet - keeping last known value", flush=True)
  return []


# ---------- LP2: Hansard framing ratio ----------
def fetch_lp2_hansard():
  print("[LP2] no automated fetcher yet - keeping last known value", flush=True)
  return []


# ---------- LP3: Wellbeing budget ratio ----------
def fetch_lp3_wellbeing_budget():
  print("[LP3] no automated fetcher yet - keeping last known value", flush=True)
  return []


# ---------- LP4: Iwi/hapu co-governance arrangements ----------
def fetch_lp4_cogovernance():
  print("[LP4] no automated fetcher yet - keeping last known value", flush=True)
  return []


# ---------- LP5: Jobseeker proxy (FRED NZ unemployment rate, quarterly) ----------
def fetch_lp5_jobseeker():
  try:
    series = _fred_csv("LRHUTTTTNZQ156S")
    print(f"[LP5] FRED unemployment-rate proxy: {len(series)} points", flush=True)
    return series[-40:]
  except Exception as e:
    print(f"[LP5] fetch error: {e}", flush=True)
    return []


# ---------- LP6: OIA complaints upheld by Ombudsman (annual) ----------
def fetch_lp6_ombudsman():
  print("[LP6] no automated fetcher yet - keeping last known value", flush=True)
  return []


# ---------- LP7: Household net worth - top 1% share (annual) ----------
def fetch_lp7_wealth():
  print("[LP7] no automated fetcher yet - keeping last known value", flush=True)
  return []


# ---------- LP8: Trade union membership rate ----------
def fetch_lp8_union():
  print("[LP8] no automated fetcher yet - keeping last known value", flush=True)
  return []


# ---------- LP9: OIA responses within statutory timeframe (%) ----------
def fetch_lp9_oia_timeliness():
  print("[LP9] no automated fetcher yet - keeping last known value", flush=True)
  return []


# ---------- LP10: Greenhouse-gas emissions, gross (annual, OWID CSV) ----------
def fetch_lp10_emissions():
  url = ("https://ourworldindata.org/grapher/annual-co2-emissions-per-country.csv"
         "?v=1&csvType=full&useColumnShortNames=true")
  try:
    text = _get(url).decode("utf-8", errors="replace")
  except Exception as e:
    print(f"[LP10] OWID fetch error: {e}", flush=True)
    return []
  reader = csv.DictReader(io.StringIO(text))
  series = []
  for row in reader:
    if row.get("Entity", "").strip() != "New Zealand":
      continue
    y = row.get("Year", "").strip()
    v = row.get("emissions_total", "").strip()
    if not y or not v:
      continue
    try:
      series.append({"period": f"{int(y):04d}", "value": float(v)})
    except ValueError:
      continue
  series.sort(key=lambda x: x["period"])
  print(f"[LP10] OWID New Zealand CO2: {len(series)} points", flush=True)
  return series[-60:]


# ---------- LP11: New dwelling consents (monthly, Stats NZ) ----------
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


def fetch_lp11_consents():
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


# ---------- LP12: OCR (monthly proxy via FRED interbank rate) ----------
def fetch_lp12_ocr():
  try:
    series = _fred_csv("IRSTCI01NZM156N")
    print(f"[LP12] FRED IRSTCI01NZM156N: {len(series)} points", flush=True)
    return series[-120:]
  except Exception as e:
    print(f"[LP12] FRED fetch error: {e}", flush=True)
    return []


FETCHERS = {
  1: fetch_lp1_waitangi,
  2: fetch_lp2_hansard,
  3: fetch_lp3_wellbeing_budget,
  4: fetch_lp4_cogovernance,
  5: fetch_lp5_jobseeker,
  6: fetch_lp6_ombudsman,
  7: fetch_lp7_wealth,
  8: fetch_lp8_union,
  9: fetch_lp9_oia_timeliness,
  10: fetch_lp10_emissions,
  11: fetch_lp11_consents,
  12: fetch_lp12_ocr,
}


def main():
  doc = json.loads(DATA_FILE.read_text(encoding="utf-8"))
  now = datetime.now(timezone.utc).isoformat()
  for lp in doc.get("leverage_points", []):
    num = lp.get("id")
    fetcher = FETCHERS.get(num)
    if not fetcher:
      print(f"[LP{num}] no fetcher registered", flush=True)
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
