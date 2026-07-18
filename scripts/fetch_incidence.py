#!/usr/bin/env python3
"""Fetch incidence data from Aotearoa Data Explorer (ADE / Stats NZ SDMX API)
and normalise it into data/incidence.json.

ADE base URL: https://apis.stats.govt.nz/ade-api/rest/v2
Auth: header `Ocp-Apim-Subscription-Key: <ADE_API_KEY>`
Data endpoint: /data/{context}/{agencyId}/{resourceId}/{version}/{key}

Mapping: data/incidence_sources.json declares, per leverage point, which ADE
dataflow queries feed `bears_cost` vs `benefits`. Empty lists are allowed --
those LPs stay in status 'pending distributional analysis'.

Rules (matches the 'no fabricated data' invariant of the Observatory):
- Every bears_cost / benefits row must have a resolvable source_url.
- Rows missing source_url are dropped and counted in per-LP diagnostics.
- If both lists end up empty for an LP, its status is set to
  'pending distributional analysis'.
- Writes back to data/incidence.json with a fresh 'generated' timestamp.
- Emits per-LP log lines like: [incidence:LP6] rows=8 dropped=2
"""
import json, os, pathlib, datetime, sys
import urllib.request, urllib.parse, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "incidence.json"
MAP = ROOT / "data" / "incidence_sources.json"

ADE_BASE = os.environ.get("ADE_API_BASE", "https://apis.stats.govt.nz/ade-api/rest/v2")
ADE_KEY = os.environ.get("ADE_API_KEY", "")


def _is_valid_url(u):
    if not isinstance(u, str):
        return False
    return u.startswith("http://") or u.startswith("https://")


def _clean_rows(rows, lp_id, label):
    kept, dropped = [], 0
    for r in rows or []:
        if isinstance(r, dict) and _is_valid_url(r.get("source_url")):
            kept.append(r)
        else:
            dropped += 1
    return kept, dropped


def _ade_get(path, params=None):
    if not ADE_KEY:
        print("[incidence] WARN: ADE_API_KEY not set; skipping remote fetch", flush=True)
        return None
    url = ADE_BASE.rstrip("/") + "/" + path.lstrip("/")
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Ocp-Apim-Subscription-Key": ADE_KEY,
        "Accept": "application/vnd.sdmx.data+json;version=1.0.0",
        "User-Agent": "systems-observatory/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("[incidence] HTTP " + str(e.code) + " on " + url, flush=True)
    except Exception as e:
        print("[incidence] fetch error on " + url + ": " + str(e), flush=True)
    return None


def _rows_from_sdmx(payload, source_url):
    out = []
    try:
        data = payload.get("data", payload)
        datasets = data.get("dataSets", [])
        struct = data.get("structure", {})
        time_vals = []
        for dim in (struct.get("dimensions", {}).get("observation") or []):
            if dim.get("id", "").upper().startswith("TIME"):
                time_vals = [v.get("id") or v.get("name") for v in dim.get("values", [])]
        for ds in datasets:
            series = ds.get("series", {}) or {}
            for _, s in series.items():
                obs = s.get("observations", {}) or {}
                for tk, ov in obs.items():
                    try:
                        idx = int(tk.split(":")[0])
                        period = time_vals[idx] if idx < len(time_vals) else tk
                    except Exception:
                        period = tk
                    val = ov[0] if isinstance(ov, list) and ov else None
                    out.append({"period": period, "value": val, "source_url": source_url})
    except Exception as e:
        print("[incidence] parse error: " + str(e), flush=True)
    return out


def _fetch_query(q):
    path = "/data/" + "/".join([
        q.get("context", "dataflow"),
        q["agencyId"],
        q["resourceId"],
        q.get("version", "1.0"),
        q.get("key", "all"),
    ])
    src = ADE_BASE.rstrip("/") + path
    payload = _ade_get(path, q.get("params"))
    if not payload:
        return []
    return _rows_from_sdmx(payload, src)


def main():
    doc = json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else {"leverage_points": []}
    mapping = json.loads(MAP.read_text(encoding="utf-8")) if MAP.exists() else {}
    lps = doc.get("leverage_points", [])
    total_kept = total_dropped = 0
    for lp in lps:
        lp_id = lp.get("id") or lp.get("lp_id") or "LP?"
        inc = lp.get("incidence") or {}
        src_map = (mapping.get(lp_id) or {})
        fetched_bc, fetched_bn = [], []
        for q in src_map.get("bears_cost", []) or []:
            fetched_bc.extend(_fetch_query(q))
        for q in src_map.get("benefits", []) or []:
            fetched_bn.extend(_fetch_query(q))
        merged_bc = (inc.get("bears_cost") or []) + fetched_bc
        merged_bn = (inc.get("benefits") or []) + fetched_bn
        bc, bc_drop = _clean_rows(merged_bc, lp_id, "bears_cost")
        bn, bn_drop = _clean_rows(merged_bn, lp_id, "benefits")
        inc["bears_cost"] = bc
        inc["benefits"] = bn
        kept = len(bc) + len(bn)
        dropped = bc_drop + bn_drop
        total_kept += kept
        total_dropped += dropped
        inc["status"] = "published" if kept else "pending distributional analysis"
        lp["incidence"] = inc
        print("[incidence:" + str(lp_id) + "] rows=" + str(kept) + " dropped=" + str(dropped), flush=True)
    doc["leverage_points"] = lps
    doc["generated"] = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    SRC.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("[incidence] total kept=" + str(total_kept) + " dropped=" + str(total_dropped), flush=True)


if __name__ == "__main__":
    sys.exit(main() or 0)
