#!/usr/bin/env python3
"""Generate a Substack-ready draft from the current monthly State of the System report."""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "reports" / "manifest.json"
DATA = ROOT / "data" / "indicators.json"
OUT_DIR = ROOT / "reports"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SITE = "https://robertmccallnz.github.io/systems-observatory"
DASH = "\u2014"

manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
current = manifest.get("current") or {}
month = current.get("month") or datetime.date.today().strftime("%Y-%m")
md_name = current.get("md") or ("state-of-the-system-" + month + ".md")

report_md_path = ROOT / "reports" / md_name
report_md = report_md_path.read_text() if report_md_path.exists() else ""

indicators = json.loads(DATA.read_text()).get("leverage_points", [])

def latest_value(lp):
    s = lp.get("series") or []
    if not s:
        return DASH
    v = s[-1].get("value")
    return DASH if v is None else str(v)

title = "State of the System \u00b7 " + month
subtitle = "Twelve leverage points \u00b7 Aotearoa political-economy indicators \u00b7 no fabricated data"

lines = []
lines.append("# " + title)
lines.append("")
lines.append("_" + subtitle + "_")
lines.append("")
lines.append("This is the automated monthly digest from the Te P\u0101 Systems Observatory. Every figure below is pulled from a public source; where a source did not respond, we hold the last-known value and mark it. No numbers are invented.")
lines.append("")
lines.append("[Dashboard](" + SITE + "/) \u00b7 [Reports](" + SITE + "/reports.html) \u00b7 [CSV](" + SITE + "/reports/indicators-latest.csv)")
lines.append("")
lines.append("## Snapshot: the twelve leverage points")
lines.append("")
lines.append("| # | Leverage point | Latest | Source |")
lines.append("|---|---|---|---|")
for lp in indicators:
    lp_id = str(lp.get("id", "?"))
    name = (lp.get("name") or "").replace("|", "\\|")
    val = latest_value(lp)
    src = (lp.get("source") or "").replace("|", "\\|")
    lines.append("| LP" + lp_id + " | " + name + " | " + val + " | " + src + " |")
lines.append("")
lines.append("## This month's report")
lines.append("")
if report_md:
    lines.append(report_md.strip())
else:
    lines.append("_Monthly narrative not yet generated for " + month + "._")
lines.append("")
lines.append("---")
lines.append("")
lines.append("**Method.** Data is refreshed on a schedule via GitHub Actions. Fetchers hit public APIs and web pages; on failure the last-known value is preserved. Code and data: [systems-observatory](https://github.com/robertmccallnz/systems-observatory).")
lines.append("")
lines.append("**License.** Data: as per each source. Text: CC BY 4.0. Te P\u0101 Collective Action Lab.")
lines.append("")

out_path = OUT_DIR / ("substack-" + month + ".md")
out_path.write_text("\n".join(lines))
print("[substack] wrote " + str(out_path), flush=True)
