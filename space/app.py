"""Te Pā Systems Observatory — companion Gradio Space.

Two responsibilities:

1. `/gradio_api/call/detect_anomaly` — takes a JSON series, returns a rolling
   z-score and a flag. The static dashboard already ships pre-computed
   anomalies from GH Actions, but this endpoint lets researchers run their
   own series against the same detector.

2. `/gradio_api/call/submit_annotation` — appends a community annotation to
   the public dataset `te-pa/systems-observatory-annotations`.

Environment variables (set in HF Space settings):
  HF_TOKEN — a write token for the te-pa org (dataset scope)
  DATASET_REPO — defaults to te-pa/systems-observatory-annotations
"""
from __future__ import annotations

import json
import math
import os
import statistics
import uuid
from datetime import datetime, timezone

import gradio as gr
from huggingface_hub import HfApi

DATASET_REPO = os.environ.get("DATASET_REPO", "te-pa/systems-observatory-annotations")
HF_TOKEN = os.environ.get("HF_TOKEN")

MEADOWS_TIERS = {
    12: "Constants & Parameters",
    11: "Buffers & Stocks",
    10: "Material Stocks & Flows",
    9: "Delays",
    8: "Negative Feedback Loops",
    7: "Positive Feedback Loops",
    6: "Information Flows",
    5: "Rules",
    4: "Self-Organisation",
    3: "Goals",
    2: "Paradigms",
    1: "Transcending Paradigms",
}


# ---------------------------------------------------------------------
# 1. Anomaly detection
# ---------------------------------------------------------------------
def detect_anomaly(series_json: str, window: int = 24, threshold: float = 2.5) -> dict:
    """Compute rolling z-score for the latest observation.

    `series_json` is a JSON array of {period, value} objects OR a bare
    array of numbers. Returns a JSON-serialisable dict.
    """
    try:
        data = json.loads(series_json) if isinstance(series_json, str) else series_json
    except json.JSONDecodeError as e:
        return {"error": f"invalid JSON: {e}"}
    if not isinstance(data, list) or not data:
        return {"error": "series must be a non-empty list"}
    values: list[float] = []
    for row in data:
        if isinstance(row, dict) and "value" in row:
            values.append(float(row["value"]))
        else:
            values.append(float(row))
    if len(values) < 6:
        return {"error": "need at least 6 observations"}
    tail = values[-(window + 1):-1] if len(values) > window else values[:-1]
    mu = statistics.fmean(tail)
    sd = statistics.pstdev(tail)
    if sd == 0 or math.isnan(sd):
        return {"z_score": 0.0, "flag": False,
                "message": "baseline has zero variance; no signal"}
    z = (values[-1] - mu) / sd
    flag = abs(z) >= threshold
    return {
        "latest": values[-1],
        "baseline_mean": round(mu, 4),
        "baseline_stddev": round(sd, 4),
        "z_score": round(z, 3),
        "flag": bool(flag),
        "direction": "high" if z > 0 else "low",
        "threshold": threshold,
        "window": window,
        "message": (
            f"|z|={abs(z):.2f} vs prior {len(tail)}-observation baseline — "
            + ("PARADIGM-CHALLENGING deviation." if flag else "within normal range.")
        ),
    }


# ---------------------------------------------------------------------
# 2. Community annotation → HF Dataset append
# ---------------------------------------------------------------------
def _append_to_dataset(row: dict) -> str:
    """Append a JSONL row to the dataset. Returns a status string."""
    if not HF_TOKEN:
        # In dev / when the Space has no write token, we still validate and
        # echo back — so the front-end can render success in local demos.
        return "no-op (HF_TOKEN not configured — annotation validated only)"
    api = HfApi(token=HF_TOKEN)
    # We append to a single annotations.jsonl file via a small download-append-upload
    # cycle. For very high volume this would move to a Dataset repo with parquet
    # shards, but for a research artefact JSONL is transparent and forkable.
    from huggingface_hub import hf_hub_download, upload_file
    import tempfile, pathlib
    try:
        local = hf_hub_download(
            repo_id=DATASET_REPO, filename="annotations.jsonl",
            repo_type="dataset", token=HF_TOKEN,
        )
        existing = pathlib.Path(local).read_text(encoding="utf-8")
    except Exception:
        existing = ""
    new_line = json.dumps(row, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                     encoding="utf-8") as f:
        f.write(existing + new_line)
        tmp_path = f.name
    upload_file(
        path_or_fileobj=tmp_path,
        path_in_repo="annotations.jsonl",
        repo_id=DATASET_REPO,
        repo_type="dataset",
        token=HF_TOKEN,
        commit_message=f"annotation {row['id'][:8]}",
    )
    return "appended"


def submit_annotation(handle: str, leverage_point: int, intervention: str,
                      rank: int, whakapapa: str, reasoning: str) -> dict:
    """Validate and append one community annotation."""
    lp = int(leverage_point)
    if lp not in MEADOWS_TIERS:
        return {"ok": False, "error": "leverage_point must be 1..12"}
    r = int(rank)
    if not 1 <= r <= 5:
        return {"ok": False, "error": "rank must be 1..5"}
    for field, val in [("handle", handle), ("intervention", intervention),
                        ("reasoning", reasoning)]:
        if not val or not str(val).strip():
            return {"ok": False, "error": f"{field} is required"}
    row = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "handle": str(handle).strip()[:80],
        "leverage_point": lp,
        "tier": MEADOWS_TIERS[lp],
        "intervention": str(intervention).strip()[:240],
        "rank": r,
        "whakapapa": str(whakapapa or "").strip()[:500],
        "reasoning": str(reasoning).strip()[:1200],
    }
    status = _append_to_dataset(row)
    return {"ok": True, "id": row["id"], "status": status}


# ---------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------
with gr.Blocks(title="Te Pā Systems Observatory — companion Space",
               theme=gr.themes.Base(primary_hue="red", neutral_hue="stone")) as demo:
    gr.Markdown(
        """
        # Te Pā Systems Observatory · companion Space
        Programmatic endpoints for the [Systems Observatory](https://github.com/robertmccallnz/systems-observatory)
        static dashboard. This Space powers anomaly detection and community-annotation
        writes. Built under the [Māori Data Governance Model](https://www.kahuiraraunga.io/).
        """
    )

    with gr.Tab("Detect anomaly"):
        gr.Markdown("Paste a JSON series (array of numbers or `{period,value}` objects) and get a rolling z-score against Meadows' paradigm-challenge threshold.")
        series_in = gr.Textbox(label="Series (JSON)", lines=6,
                               value='[{"period":"2020-03","value":0.25},{"period":"2021-11","value":0.75},{"period":"2022-05","value":2.0},{"period":"2023-05","value":5.5},{"period":"2024-11","value":4.25},{"period":"2025-11","value":2.25}]')
        window_in = gr.Slider(6, 96, value=24, step=1, label="Baseline window")
        thresh_in = gr.Slider(1.0, 4.0, value=2.5, step=0.1, label="|z| threshold")
        out = gr.JSON(label="Result")
        btn = gr.Button("Detect", variant="primary")
        btn.click(detect_anomaly, [series_in, window_in, thresh_in], out,
                  api_name="detect_anomaly")

    with gr.Tab("Submit annotation"):
        gr.Markdown("Append a community annotation to the public dataset. All fields are stored verbatim; no email/IP is recorded.")
        handle = gr.Textbox(label="Handle", max_lines=1)
        lp = gr.Dropdown(choices=[(f"{k}. {v}", k) for k, v in MEADOWS_TIERS.items()],
                         label="Leverage point", value=12)
        intervention = gr.Textbox(label="Intervention (one sentence)", max_lines=2)
        rank = gr.Slider(1, 5, value=3, step=1, label="Effectiveness rank")
        whakapapa = gr.Textbox(label="Whakapapa (prior intervention at this tier)",
                               lines=2)
        reasoning = gr.Textbox(label="Reasoning", lines=4)
        out2 = gr.JSON(label="Result")
        btn2 = gr.Button("Submit", variant="primary")
        btn2.click(submit_annotation,
                   [handle, lp, intervention, rank, whakapapa, reasoning],
                   out2, api_name="submit_annotation")


if __name__ == "__main__":
    demo.launch()
