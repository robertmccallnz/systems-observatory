#!/usr/bin/env python3
"""Te Pa Systems Observatory - indicator fetcher (ADE v2 SDMX)."""
from __future__ import annotations

import csv
import io
import json
import math
import os
import statistics
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "indicators.json"

ADE_BASE = "https://api.stats.govt.nz/opendata/v2"
ADE_KEY = "".join(os.environ.get("ADE_API_KEY", "").split())
TIMEOUT = 90


def _ade_csv(resource_id, key="all", start=None, agency="STATSNZ", version="1.0"):
  if not ADE_KEY:
    print(f"[ADE] no ADE_API_KEY in env - cannot fetch {resource_id}", flush=True)
    return []
  url = f"{ADE_BASE}/data/dataflow/{agency}/{resource_id}/{version}/{key}"
  params = ["dimensionAtObservation=TIME_PERIOD", "format=csv"]
  if start:
    params.append(f"startPeriod={start}")
  url = f"{url}?{'&'.join(params)}"
  req = urllib.request.Request(url, headers={
    "Ocp-Apim-Subscription-Key": ADE_KEY,
    "Accept": "application/vnd.sdmx.data+csv;version=1.0.0",
    "User-Agent": "TePaSystemsObservatory/2.0",
  })
  try:
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
      body = r.read().decode("utf-8", errors="replace")
  except urllib.error.HTTPError as e:
    print(f"[ADE] {resource_id} HTTP {e.code}: {e.reason}", flush=True)
    return []
  except Exception as e:
    print(f"[ADE] {resource_id} error: {e}", flush=True)
    return []
  rows = list(csv.DictReader(io.StringIO(body)))
  print(f"[ADE] {resource_id}: {len(rows)} raw rows", flush=True)
  return rows


def _rows_to_series(rows, period_col="TIME_PERIOD", value_col="OBS_VALUE", filter_fn=None):
  series = []
  for row in rows:
    if filter_fn and not filter_fn(row):
      continue
    p = (row.get(period_col) or "").strip()
    v = (row.get(value_col) or "").strip()
    if not p or not v:
      continue
    try:
      series.append({"period": p, "value": float(v)})
    except ValueError:
      continue
  series.sort(key=lambda x: x["period"])
  return series


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


def fetch_lp1_waitangi():
  print("[LP1] no ADE dataflow - keeping last known value", flush=True)
  return []


def fetch_lp2_hansard():
  print("[LP2] no ADE dataflow - keeping last known value", flush=True)
  return []


def fetch_lp3_wellbeing_budget():
  rows = _ade_csv("NAC_GDPE_Q", start="2015-Q1")
  return _rows_to_series(rows)[-40:]


def fetch_lp4_cogovernance():
  print("[LP4] no ADE dataflow - keeping last known value", flush=True)
  return []


def fetch_lp5_jobseeker():
  rows = _ade_csv("HLF_HLFQ", start="2015-Q1")
  return _rows_to_series(rows)[-40:]


def fetch_lp6_ombudsman():
  print("[LP6] no ADE dataflow - keeping last known value", flush=True)
  return []


def fetch_lp7_wealth():
  rows = _ade_csv("HES_HNWQ", start="2015")
  return _rows_to_series(rows)[-40:]


def fetch_lp8_union():
  print("[LP8] no ADE dataflow - keeping last known value", flush=True)
  return []


def fetch_lp9_oia_timeliness():
  print("[LP9] no ADE dataflow - keeping last known value", flush=True)
  return []


def fetch_lp10_emissions():
  rows = _ade_csv("ENV_ANZSIC_EMISSIONS", start="2000")
  return _rows_to_series(rows)[-40:]


def fetch_lp11_consents():
  rows = _ade_csv("BLD_BCIC_M", start="2015-01")
  return _rows_to_series(rows)[-120:]


def fetch_lp12_ocr():
  print("[LP12] no ADE dataflow (RBNZ series) - keeping last known value", flush=True)
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
  print(f"[MAIN] ADE_API_KEY present: {bool(ADE_KEY)}", flush=True)
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
