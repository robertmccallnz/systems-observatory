---
title: Te Pā Systems Observatory
emoji: 🌀
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: false
license: mit
short_description: Anomaly detection + community annotation for the Systems Observatory
---

# Te Pā Systems Observatory — companion Space

Powers two endpoints for the [Systems Observatory](https://github.com/robertmccallnz/systems-observatory) static dashboard:

- `detect_anomaly` — rolling z-score over any series.
- `submit_annotation` — appends a community annotation to the public HF Dataset [`te-pa/systems-observatory-annotations`](https://huggingface.co/datasets/te-pa/systems-observatory-annotations).

## Secrets

Set in Space settings → Variables and secrets:

- `HF_TOKEN` — write access to the annotations dataset.
- `DATASET_REPO` — optional; defaults to `te-pa/systems-observatory-annotations`.

Built under the [Māori Data Governance Model](https://www.kahuiraraunga.io/).
