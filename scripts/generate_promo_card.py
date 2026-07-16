#!/usr/bin/env python3
"""Emit a 1200x630 SVG promo card for the current monthly report."""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "reports" / "manifest.json"
DATA = ROOT / "data" / "indicators.json"
OUT = ROOT / "assets" / "social"
OUT.mkdir(parents=True, exist_ok=True)

DASH = "\u2014"
MID = "\u00b7"

manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
current = manifest.get("current") or {}
month = current.get("month") or datetime.date.today().strftime("%Y-%m")

indicators = json.loads(DATA.read_text()).get("leverage_points", [])

def latest_value(lp):
    s = lp.get("series") or []
    if not s:
        return DASH
    v = s[-1].get("value")
    return DASH if v is None else str(v)

W, H = 1200, 630
parts = []
parts.append("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 " + str(W) + " " + str(H) + "\" role=\"img\">")
parts.append("<rect width=\"" + str(W) + "\" height=\"" + str(H) + "\" fill=\"#ffffff\"/>")
parts.append("<text x=\"60\" y=\"110\" font-family=\"Georgia, serif\" font-size=\"56\" font-weight=\"700\" fill=\"#000\">Te P\u0101 Systems Observatory</text>")
parts.append("<text x=\"60\" y=\"170\" font-family=\"Georgia, serif\" font-size=\"36\" fill=\"#000\">State of the System " + MID + " " + month + "</text>")
parts.append("<line x1=\"60\" y1=\"200\" x2=\"1140\" y2=\"200\" stroke=\"#000\" stroke-width=\"2\"/>")

y = 250
col_x = [60, 660]
i = 0
for lp in indicators[:12]:
    lp_id = str(lp.get("id", "?"))
    name = (lp.get("name") or "").replace("&", "&amp;")
    if len(name) > 34:
        name = name[:33] + "\u2026"
    val = latest_value(lp)
    if len(val) > 10:
        val = val[:9] + "\u2026"
    cx = col_x[i % 2]
    cy = y + (i // 2) * 50
    parts.append("<text x=\"" + str(cx) + "\" y=\"" + str(cy) + "\" font-family=\"Georgia, serif\" font-size=\"22\" font-weight=\"700\" fill=\"#000\">LP" + lp_id + "</text>")
    parts.append("<text x=\"" + str(cx + 60) + "\" y=\"" + str(cy) + "\" font-family=\"Georgia, serif\" font-size=\"22\" fill=\"#000\">" + name + "</text>")
    parts.append("<text x=\"" + str(cx + 480) + "\" y=\"" + str(cy) + "\" text-anchor=\"end\" font-family=\"Georgia, serif\" font-size=\"22\" font-weight=\"700\" fill=\"#000\">" + val + "</text>")
    i += 1

parts.append("<text x=\"60\" y=\"600\" font-family=\"Georgia, serif\" font-size=\"18\" fill=\"#000\" opacity=\"0.7\">systems-observatory " + MID + " kiwidialectic.com " + MID + " no fabricated data</text>")
parts.append("</svg>\n")

svg = "".join(parts)
out_path = OUT / ("promo-" + month + ".svg")
out_path.write_text(svg)
print("[promo] wrote " + str(out_path), flush=True)
latest_path = OUT / "promo-latest.svg"
latest_path.write_text(svg)
print("[promo] wrote " + str(latest_path), flush=True)
