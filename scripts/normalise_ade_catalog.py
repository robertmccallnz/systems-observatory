#!/usr/bin/env python3
"""Normalise an SDMX 2.1 XML dataflow listing into a compact JSON catalog.

Input : raw SDMX-ML structure message from ADE (ade_catalog.raw.json/xml).
Output: {"fetched_at": ISO8601, "count": N, "dataflows": [{id, agency, version, name, description}]}
"""
import json, sys, datetime, xml.etree.ElementTree as ET

NS = {
    "m":   "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "s":   "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "c":   "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}

def main(argv):
    if len(argv) < 3:
        print("usage: normalise_ade_catalog.py <in> <out>", file=sys.stderr); return 2
    raw = open(argv[1], "rb").read()
    root = ET.fromstring(raw)
    dataflows = []
    for df in root.iter("{%s}Dataflow" % NS["s"]):
        name_en = desc_en = ""
        for n in df.findall("c:Name", NS):
            if n.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "en") == "en":
                name_en = (n.text or "").strip(); break
        for d in df.findall("c:Description", NS):
            if d.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "en") == "en":
                desc_en = (d.text or "").strip(); break
        dataflows.append({
            "id":      df.attrib.get("id", ""),
            "agency":  df.attrib.get("agencyID", ""),
            "version": df.attrib.get("version", ""),
            "name":    name_en,
            "description": desc_en,
        })
    out = {
        "fetched_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "count": len(dataflows),
        "dataflows": sorted(dataflows, key=lambda d: (d["agency"], d["id"])),
    }
    with open(argv[2], "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"dataflows={out['count']}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
