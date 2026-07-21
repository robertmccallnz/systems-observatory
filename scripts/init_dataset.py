#!/usr/bin/env python3
"""Create the community annotations dataset on the Hugging Face Hub.

Run once after `hf auth login`.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

from huggingface_hub import HfApi, create_repo, upload_file

REPO_ID = os.environ.get("DATASET_REPO", "te-pa/systems-observatory-annotations")


def main() -> int:
    api = HfApi()
    try:
        create_repo(REPO_ID, repo_type="dataset", exist_ok=True,
                    private=False)
    except Exception as e:  # noqa: BLE001
        print(f"create_repo warning: {e}", file=sys.stderr)

    readme = f"""---
license: cc-by-4.0
language:
- en
- mi
pretty_name: Te Pā Systems Observatory — Community Annotations
tags:
- systems-thinking
- meadows-leverage-points
- aotearoa
- new-zealand
- indigenous-data-sovereignty
size_categories:
- n<1K
---

# Te Pā Systems Observatory · Community Annotations

Public archive of community-submitted rankings of interventions against Donella
Meadows' twelve leverage points, in the Aotearoa New Zealand political-economy
context. Ranked by kaimahi (community members) through the
[Systems Observatory dashboard](https://github.com/robertmccallnz/systems-observatory).

Built under the [Māori Data Governance Model](https://www.kahuiraraunga.io/) of
Te Kāhui Raraunga. Public, aggregated, non-personal data only.

## Schema (JSON Lines)

Each row in `annotations.jsonl`:

| field | type | notes |
|---|---|---|
| `id` | string | UUID |
| `created_at` | string | ISO-8601 UTC |
| `handle` | string | ≤ 80 chars, any pseudonym |
| `leverage_point` | int | 1–12 (12 shallowest, 1 deepest) |
| `tier` | string | Meadows tier name |
| `intervention` | string | one-sentence proposal, ≤ 240 chars |
| `rank` | int | 1 (surface tweak) – 5 (paradigm shift) |
| `whakapapa` | string | prior intervention cited, ≤ 500 chars |
| `reasoning` | string | ≤ 1200 chars |

## Licence

CC BY 4.0 — please cite Te Pā Systems Observatory when you re-use the archive.
"""

    seed_row = {
        "id": "00000000-0000-4000-8000-000000000000",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "handle": "te-pa-seed",
        "leverage_point": 2,
        "tier": "Paradigms",
        "intervention": ("Reframe the state's core purpose from 'economic growth' "
                          "to 'restoration of Te Tiriti relationships and "
                          "collective wellbeing'."),
        "rank": 5,
        "whakapapa": ("Living Standards Framework (2018) — a partial move at tier 3; "
                       "He Ara Waiora (2019) — a partial move at tier 2."),
        "reasoning": ("Meadows warns that changes at tiers 12–5 rarely hold if the "
                       "underlying paradigm remains extractive. Aotearoa already "
                       "has a paradigm alternative in Te Ao Māori; the leverage is "
                       "in institutionalising it, not inventing it."),
    }

    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                     encoding="utf-8") as f:
        f.write(json.dumps(seed_row, ensure_ascii=False) + "\n")
        annotations_path = f.name

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as f:
        f.write(readme)
        readme_path = f.name

    upload_file(path_or_fileobj=readme_path, path_in_repo="README.md",
                repo_id=REPO_ID, repo_type="dataset",
                commit_message="init: dataset card")
    upload_file(path_or_fileobj=annotations_path, path_in_repo="annotations.jsonl",
                repo_id=REPO_ID, repo_type="dataset",
                commit_message="init: seed annotation")
    print(f"✔ dataset ready at https://huggingface.co/datasets/{REPO_ID}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
