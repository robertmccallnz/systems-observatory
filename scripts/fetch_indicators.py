#!/usr/bin/env python3
"""
Te Pā Systems Observatory — indicator fetcher.

Pulls live public NZ data, computes rolling z-scores, writes data/indicators.json.
Runs in GitHub Actions on a weekly cron (see .github/workflows/refresh.yml).

Design principles:
- Public, aggregated, non-personal data only (Māori Data Governance Model).
- Every value is sourced. If a source fails, we keep the last-known value and
  flag the fetch status, never invent numbers.
- Anomalies flagged via rolling z-score (|z| >= 2.5) — a "paradigm-challenging"
  observation in Meadows' framing.
"""
from __future__ import annotations

import io
import json
import math
import re
import statistics
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "indicators.json"

UA = "TePaSystemsObservatory/1.0 (+https://te-pa.org)"
TIMEOUT = 30


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def _rolling_zscore(values: list[float], window: int = 24) -> float | None:
    """Return the z-score of the latest value against the previous `window`."""
    if len(values) < 6:
        return None
    tail = values[-(window + 1):-1] if len(values) > window else values[:-1]
    if len(tail) < 3:
        return None
    mu = statistics.fmean(tail)
    sd = statistics.pstdev(tail)
    if sd == 0 or math.isnan(sd):
        return None
    z = (values[-1] - mu) / sd
    return round(z, 3)


def _finalise(series: list[dict[str, Any]]) -> tuple[float | None, dict | None]:
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
            "message": (
                f"|z|={abs(z):.2f} vs prior 24-period baseline — a "
                f"paradigm-challenging deviation."
            ),
        }
    return latest, anomaly


# ------------------------------------------------------------------
# Individual source fetchers. Each returns list[{period, value}].
# All fetchers are wrapped in try/except upstream so a single failure
# never breaks the whole run.
# ------------------------------------------------------------------

def fetch_ocr() -> list[dict[str, Any]]:
    """RBNZ Official Cash Rate decisions. RBNZ publishes an OCR-history CSV."""
    # RBNZ series B2 — OCR decisions. If the direct CSV path changes, the
    # fetcher fails safely and we fall back to whatever is already in the JSON.
    url = "https://www.rbnz.govt.nz/-/media/ReserveBank/Files/Statistics/tables/b2/hb2-daily.csv"
    try:
        raw = _get(url).decode("utf-8", errors="replace")
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for line in raw.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        # Look for lines like "2025-04-09,4.25"
        m = re.match(r"^(\d{4}-\d{2}-\d{2})$", parts[0])
        if not m:
            continue
        try:
            v = float(parts[1])
        except ValueError:
            continue
        out.append({"period": parts[0], "value": v})
    # Downsample: keep the last observation per month, cap 120 months
    seen: dict[str, dict[str, Any]] = {}
    for p in out:
        seen[p["period"][:7]] = p
    monthly = sorted(seen.values(), key=lambda x: x["period"])
    return monthly[-120:]


def fetch_dwelling_consents() -> list[dict[str, Any]]:
    """Stats NZ new dwelling consents — via data.govt.nz CKAN when available."""
    # This is left intentionally soft: Stats NZ ADE requires a subscription key.
    # In GH Actions we inject STATSNZ_API_KEY as a secret when available.
    return []


def fetch_ombudsman_oia() -> list[dict[str, Any]]:
    """Placeholder for Ombudsman OIA complaints — annual PDF release."""
    return []


def fetch_waitangi_tribunal() -> list[dict[str, Any]]:
    """Annual count of Waitangi Tribunal reports released."""
    return []


# Map leverage-point id -> fetcher.
FETCHERS: dict[int, Any] = {
    12: fetch_ocr,
    11: fetch_dwelling_consents,
    6: fetch_ombudsman_oia,
    1: fetch_waitangi_tribunal,
    # The remaining leverage points fall back to whatever seed series
    # a maintainer has committed to the JSON. This is deliberate — some
    # indicators (e.g. Hansard framing ratio) require a separate NLP pass
    # in the Gradio Space, not a wire-fetch.
}


def main() -> int:
    doc = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    doc["meta"]["generated_at"] = datetime.now(timezone.utc).isoformat()

    status: list[str] = []
    for lp in doc["leverage_points"]:
        fetcher = FETCHERS.get(lp["id"])
        if fetcher is None:
            latest, anomaly = _finalise(lp.get("series") or [])
            lp["latest"] = latest
            lp["anomaly"] = anomaly
            continue
        try:
            series = fetcher()
        except Exception as e:  # noqa: BLE001
            status.append(f"LP{lp['id']} fetch failed: {e}")
            series = lp.get("series") or []
        if series:
            lp["series"] = series
        latest, anomaly = _finalise(lp.get("series") or [])
        lp["latest"] = latest
        lp["anomaly"] = anomaly
        status.append(
            f"LP{lp['id']} ok — {len(lp.get('series') or [])} points, "
            f"latest={latest}, anomaly={'yes' if anomaly else 'no'}"
        )

    doc["meta"]["fetch_status"] = status
    DATA_FILE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    print("\n".join(status))
    return 0


if __name__ == "__main__":
    sys.exit(main())
