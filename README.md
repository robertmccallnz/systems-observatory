# Te Pā Systems Observatory

A living dashboard of Donella Meadows' [12 leverage points](https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/), mapped to Aotearoa NZ political-economy indicators, with a community annotation archive.

A **Te Pā Collective Action Lab** artefact — sibling to Thinkers Mapper, Kōrero, and the Kiwi Dialectic hub.

## What it does

- **Twelve panels** — one per Meadows tier (12 shallowest → 1 deepest).
- **Live indicators** — public NZ government sources (RBNZ, Stats NZ, Treasury, MSD, Waitangi Tribunal, Ombudsman).
- **Anomaly surfacing** — rolling z-score against a 24-period baseline; deviations flagged as paradigm-challenging.
- **Community annotation** — users rank interventions by leverage tier; entries written to the public HF dataset `te-pa/systems-observatory-annotations`.
- **Kōrero comments** — Giscus + GitHub Discussions, matching your existing sites.

## Three components

```
┌──────────────────────────┐    reads    ┌────────────────────┐
│ GitHub Pages static site │◀───────────▶│ data/indicators.json│
│  (index.html + assets)   │             │  (versioned in repo)│
└──────────┬───────────────┘             └──────────▲─────────┘
           │ POST                                    │ writes
           ▼                                          │ weekly
┌──────────────────────────┐                          │
│ Hugging Face Space       │            ┌────────────┴────────┐
│  space/app.py (Gradio)   │            │ GitHub Actions cron │
│  · detect_anomaly        │            │  scripts/fetch_...  │
│  · submit_annotation ────┼───────────▶│  (writes JSON back) │
└──────────┬───────────────┘            └─────────────────────┘
           │ appends to
           ▼
┌──────────────────────────┐
│ HF Dataset (public)      │
│  te-pa/systems-obs...    │
│  annotations.jsonl       │
└──────────────────────────┘
```

## Deploy (one-time)

**1. Push this folder to GitHub**

```bash
cd systems-observatory
git init && git add . && git commit -m "Te Pā Systems Observatory v1"
gh repo create robertmccallnz/systems-observatory --public --source=. --push
```

**2. Turn on GitHub Pages**

Settings → Pages → Source: `Deploy from a branch`, branch `main`, folder `/`. The site becomes live at `https://robertmccall.github.io/systems-observatory/`.

To use `observatory.te-pa.org`: Settings → Pages → Custom domain → `observatory.te-pa.org`, then add a `CNAME` DNS record pointing to `robertmccall.github.io`.

**3. Wire Kōrero (Giscus)**

In your existing Giscus config, get the repo-id and General category-id, then replace the two `REPLACE_WITH_…` placeholders in `index.html` (identical pattern to your other sites — you already have `assets/community.css` and `assets/community.js` conventions).

**4. Create the HF Dataset**

```bash
huggingface-cli login  # paste a write token
python scripts/init_dataset.py   # creates te-pa/systems-observatory-annotations + seed row
```

**5. Deploy the Space**

Create a new Space at `huggingface.co/new-space` → name `systems-observatory-anomaly`, org `te-pa`, SDK Gradio. Push the `space/` directory:

```bash
cd space
git init && git remote add origin https://huggingface.co/spaces/te-pa/systems-observatory-anomaly
git add . && git commit -m "v1" && git push -u origin main
```

Then in Space Settings → Variables & Secrets, add:
- `HF_TOKEN` — a write token scoped to `te-pa/systems-observatory-annotations`.

**6. Optional — Stats NZ live wiring**

Sign up at [portal.apis.stats.govt.nz](https://portal.apis.stats.govt.nz/), subscribe to Aotearoa Data Explorer, generate a primary key, then in the GitHub repo → Settings → Secrets and variables → Actions, add `STATSNZ_API_KEY`. The weekly workflow will start populating the remaining panels.

## Kaupapa

Built under the [Māori Data Governance Model](https://www.kahuiraraunga.io/) of Te Kāhui Raraunga. Public, aggregated, non-personal data only. Every indicator cites its source; every annotation is public and forkable. Te reo Māori terminology is used deliberately as a paradigm-shifting act at leverage point #2.

See [`docs/LEVERAGE_POINTS.md`](docs/LEVERAGE_POINTS.md) for the full mapping.
