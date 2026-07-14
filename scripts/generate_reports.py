#!/usr/bin/env python3
"""Generate a monthly Markdown state-of-the-system report and a flat CSV
of the latest indicator values from data/indicators.json.

Outputs (committed by the refresh workflow):
  reports/state-of-the-system-YYYY-MM.md   (overwritten each run of that month)
  reports/indicators-latest.csv            (overwritten every run)

Design rules (respecting the observatory kaupapa):
- No fabricated numbers: if a series is empty, the report says so.
- Machine-readable outputs (CSV + Markdown).
- Idempotent: re-running on the same day overwrites the current month's file.
"""
from __future__ import annotations
import csv, json, pathlib, datetime as dt

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "indicators.json"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

def _last_two(series):
    if not series or len(series) < 1:
        return None, None
    last = series[-1]
    prev = series[-2] if len(series) >= 2 else None
    return prev, last

def _delta_arrow(prev, last):
    if not prev or not last:
        return "\u2192"
    try:
        d = float(last.get("value")) - float(prev.get("value"))
    except (TypeError, ValueError):
        return "\u2192"
    if d > 0: return "\u25B2"
    if d < 0: return "\u25BC"
    return "\u2192"

def _pct(prev, last):
    try:
        a = float(prev.get("value")); b = float(last.get("value"))
        if a == 0: return ""
        return f"{(b-a)/abs(a)*100:+.1f}%"
    except Exception:
        return ""

def main():
    doc = json.loads(DATA.read_text())
    lps = doc.get("leverage_points", [])
    today = dt.date.today()
    stamp = today.strftime("%Y-%m")

    # --- CSV -----------------------------------------------------------
    csv_path = REPORTS / "indicators-latest.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id","tier","name","latest_period","latest_value",
                    "prev_period","prev_value","delta_pct","source_name","source_url"])
        for lp in lps:
            prev, last = _last_two(lp.get("series") or [])
            w.writerow([
                lp.get("id",""),
                lp.get("tier",""),
                lp.get("name",""),
                (last or {}).get("period",""),
                (last or {}).get("value",""),
                (prev or {}).get("period",""),
                (prev or {}).get("value",""),
                _pct(prev, last) if prev and last else "",
                lp.get("source_name",""),
                lp.get("source_url",""),
            ])
    print(f"[reports] wrote {csv_path}", flush=True)

    # --- Markdown ------------------------------------------------------
    md_path = REPORTS / f"state-of-the-system-{stamp}.md"
    lines = [
        f"# State of the System \u2014 {stamp}",
        "",
        f"_Auto-generated {today.isoformat()} from `data/indicators.json`. "
        "Values are the latest observations returned by the refresh workflow; "
        "where a fetch fails the last-known value is preserved (no fabrication).",
        "",
        "| LP | Tier | Indicator | Latest | \u0394 | Source |",
        "|----|------|-----------|--------|---|--------|",
    ]
    for lp in lps:
        prev, last = _last_two(lp.get("series") or [])
        latest = "\u2014"
        if last:
            latest = f"{last.get('value','')} ({last.get('period','')})"
        arrow = _delta_arrow(prev, last)
        pct = _pct(prev, last)
        src = lp.get("source_name","") or ""
        src_url = lp.get("source_url","") or ""
        src_md = f"[{src}]({src_url})" if src_url else src
        lines.append(f"| {lp.get('id','')} | {lp.get('tier','')} | "
                     f"{lp.get('name','')} | {latest} | {arrow} {pct} | {src_md} |")
    lines += [
        "",
        "## Notes",
        "",
        "- \u25B2 / \u25BC / \u2192 show month-on-month or period-on-period direction.",
        "- Empty cells mean the series is not yet wired or the fetch failed on the "
        "most recent run; the dashboard shows the last-known value.",
        "- Source column links to the primary data provider (Stats NZ ADE, RBNZ, FRED, etc.).",
        "",
        "_Kaupapa: this report is produced as public accountability infrastructure. "
        "It is not investment advice or a policy recommendation._",
    ]
    md_path.write_text("\n".join(lines) + "\n")
    print(f"[reports] wrote {md_path}", flush=True)

if __name__ == "__main__":
    main()

def _build_manifest():
    import json as _json, re as _re
    reports_dir = REPORTS
    reports = []
    for md in sorted(reports_dir.glob("state-of-the-system-*.md"), reverse=True):
        month = md.stem.replace("state-of-the-system-", "")
        pdf = md.with_suffix(".pdf")
        reports.append({"month": month, "md": md.name, "pdf": pdf.name if pdf.exists() else None})
    current = reports[0] if reports else None
    manifest = {"generated": dt.datetime.utcnow().isoformat() + "Z",
                "current": current, "reports": reports}
    (reports_dir / "manifest.json").write_text(_json.dumps(manifest, indent=2))
    print(f"[reports] wrote {reports_dir/'manifest.json'} ({len(reports)} entries)", flush=True)

_build_manifest()
