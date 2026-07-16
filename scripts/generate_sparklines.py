#!/usr/bin/env python3
"""Emit one SVG sparkline per leverage point into assets/social/.
Black/white typographic style (Kiwi Dialectic zine aesthetic).
Read-only: no fabricated values; empty series -> a placeholder SVG with a hyphen.
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "social"
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((ROOT / "data" / "indicators.json").read_text())

W, H, PAD = 480, 200, 24
DASH = "\u2014"
MID = "\u00b7"

def render(lp):
    s = lp.get("series") or []
    vals = []
    for pt in s:
        try:
            vals.append(float(pt.get("value")))
        except (TypeError, ValueError):
            pass
    label = "LP" + str(lp.get("id", "?"))
    name = (lp.get("name") or "").replace("&", "&amp;")
    latest = str(s[-1].get("value", DASH)) if s else DASH
    path = ""
    if len(vals) >= 2:
        mn = min(vals)
        mx = max(vals)
        rng = (mx - mn) or 1.0
        n = len(vals)
        pts = []
        i = 0
        for v in vals:
            x = PAD + i * (W - 2*PAD) / (n - 1)
            y = H - PAD - ((v - mn) / rng) * (H - 2*PAD - 60)
            pts.append(str(round(x,1)) + "," + str(round(y,1)))
            i += 1
        path = "M " + " L ".join(pts)
    svg = "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 " + str(W) + " " + str(H) + "\" role=\"img\" aria-label=\"" + label + " " + name + "\">"
    svg += "<rect width=\"" + str(W) + "\" height=\"" + str(H) + "\" fill=\"#ffffff\"/>"
    svg += "<text x=\"" + str(PAD) + "\" y=\"36\" font-family=\"Georgia, serif\" font-size=\"20\" font-weight=\"700\" fill=\"#000\">" + label + " " + MID + " " + name + "</text>"
    svg += "<text x=\"" + str(PAD) + "\" y=\"64\" font-family=\"Georgia, serif\" font-size=\"14\" fill=\"#000\">Latest: " + latest + "</text>"
    svg += "<path d=\"" + path + "\" fill=\"none\" stroke=\"#000\" stroke-width=\"2\"/>"
    svg += "<text x=\"" + str(PAD) + "\" y=\"" + str(H-8) + "\" font-family=\"Georgia, serif\" font-size=\"11\" fill=\"#000\" opacity=\"0.7\">systems-observatory " + MID + " kiwidialectic.com</text>"
    svg += "</svg>\n"
    return svg

for lp in DATA.get("leverage_points", []):
    p = OUT / ("lp" + str(lp.get("id", "x")) + ".svg")
    p.write_text(render(lp))
    print("[sparklines] wrote " + str(p), flush=True)
