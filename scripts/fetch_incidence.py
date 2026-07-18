#!/usr/bin/env python3
"""Validate and normalise data/incidence.json.

Rules (matches the 'no fabricated data' invariant of the Observatory):
- Every bears_cost / benefits row must have a resolvable source_url.
- Rows missing source_url are dropped and counted in per-LP diagnostics.
- If both lists end up empty for an LP, its status is set to 'pending distributional analysis'.
- Writes back to data/incidence.json with a fresh 'generated' timestamp.
- Emits per-LP log lines like: [incidence:LP6] rows=8 dropped=2
"""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "incidence.json"

def _is_valid_url(u):
    if not isinstance(u, str):
        return False
    u = u.strip()
    return u.startswith("http://") or u.startswith("https://")

def _clean_rows(rows, lp_id, bucket):
    kept = []
    dropped = 0
    if not isinstance(rows, list):
        return kept, 0
    for r in rows:
        if not isinstance(r, dict):
            dropped += 1
            continue
        if _is_valid_url(r.get("source_url")):
            kept.append(r)
        else:
            dropped += 1
    return kept, dropped

doc = json.loads(SRC.read_text())
lps = doc.get("leverage_points", [])
total_kept = 0
total_dropped = 0
for lp in lps:
    lp_id = lp.get("id", "?")
    inc = lp.get("incidence") or {}
    bc, bc_drop = _clean_rows(inc.get("bears_cost"), lp_id, "bears_cost")
    bn, bn_drop = _clean_rows(inc.get("benefits"), lp_id, "benefits")
    inc["bears_cost"] = bc
    inc["benefits"] = bn
    kept = len(bc) + len(bn)
    dropped = bc_drop + bn_drop
    total_kept += kept
    total_dropped += dropped
    if kept == 0:
        inc["status"] = "pending distributional analysis"
    else:
        inc["status"] = "published"
    lp["incidence"] = inc
    print("[incidence:LP" + str(lp_id) + "] rows=" + str(kept) + " dropped=" + str(dropped), flush=True)

doc["leverage_points"] = lps
doc["generated"] = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
SRC.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print("[incidence] total kept=" + str(total_kept) + " dropped=" + str(total_dropped), flush=True)
