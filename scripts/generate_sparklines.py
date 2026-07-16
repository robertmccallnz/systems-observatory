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

def _svg(lp):
    series = lp.get("series") or []
    values = []
    for pt in series:
        try:
            values.append(float(pt.get("value")))
        except (TypeError, ValueError):
            pass
    label = f"LP{lp.get('id','?')}"
    name = (lp.get("name") or "").replace("&", "&amp;")
    latest = "\u2014"
    if series:
                            latest = str(series[-1].get('value', '\u2014'))
        if len(values) < 2:
        path = ""
    else:
        mn, mx = min(values), max(values)
        rng = (mx - mn) or 1.0
        n = len(values)
        pts = []
        for i, v in enumerate(values):
            x = PAD + i * (W - 2*PAD) / (n - 1)
            y = H - PAD - ((v - mn) / rng) * (H - 2*PAD - 60)
            pts.append(f"{x:.1f},{y:.1f}")
        path = "M " + " L ".join(pts)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{label} {name}">
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  <text x="{PAD}" y="36" font-family="Georgia, serif" font-size="20" font-weight="700" fill="#000">{label} \u00b7 {name}</text>
  <text x="{PAD}" y="64" font-family="Georgia, serif" font-size="14" fill="#000">Latest: {latest}</text>
  <path d="{path}" fill="none" stroke="#000" stroke-width="2"/>
  <text x="{PAD}" y="{H - 8}" font-family="Georgia, serif" font-size="11" fill="#000" opacity="0.7">systems-observatory \u00b7 kiwidialectic.com</text>
</svg>\n'''

for lp in DATA.get("leverage_points", []):
    path = OUT / f"lp{lp.get('id','x')}.svg"
    path.write_text(_svg(lp))
    print(f"[sparklines] wrote {path}", flush=True)
