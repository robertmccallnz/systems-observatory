# Te Pā Systems Observatory

A two-part systems platform, built as a **Te Pā Collective Action Lab** artefact:

1. **[Observatory](./index.html)** — a living dashboard of Donella Meadows' [12 leverage points](https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/), mapped to Aotearoa NZ political-economy indicators.
2. **[Governance Audit](./governance.html)** — a reflexive systems audit of Te Pā's own decision-making, feedback loops, decision routes, and pathway growth, using the same Meadows lens turned inward.

Sibling to Thinkers Mapper, Kōrero, and the Kiwi Dialectic hub.

## Two views, one method

- The **Observatory** watches the *wider* system — Aotearoa institutions and indicators.
- The **Governance Audit** watches the *inner* system — how Te Pā itself decides, delays, closes loops, and lets pathways emerge.

Both views use the same twelve leverage points, the same repo, the same footer, and the same [Kōrero](https://github.com/robertmccallnz/systems-observatory/discussions) comment layer.

## What each view does

### Observatory (`index.html`)
- **Twelve panels** — one per Meadows tier (12 shallowest → 1 deepest).
- **Live indicators** — public NZ government sources (RBNZ, Stats NZ, Treasury, MSD, Waitangi Tribunal, Ombudsman).
- **Anomaly surfacing** — rolling z-score against a 24-period baseline; deviations flagged as paradigm-challenging.
- **Community annotation** — users rank interventions by leverage tier; entries written to the public HF dataset `te-pa/systems-observatory-annotations`.

### Governance Audit (`governance.html`)
- **Governance graph** — nodes, edges, feedback loops, and decision routes for Te Pā's own governance system, each with `evidence_refs` pointing to public sources.
- **Meadows interventions** — nodes grouped by leverage-point depth with intervention candidates.
- **Comparison** — six systems axes (authority distribution, information flow, delay visibility, feedback closure, rule depth, self-organisation) scored qualitatively for current vs rhizome-integrated target.
- **Audit findings** — priority interventions and Meadows reading in [`reports/governance-audit-report.md`](./reports/governance-audit-report.md).

## Repo structure

```
systems-observatory/
├── index.html                    # Observatory dashboard
├── governance.html               # Governance Audit dashboard
├── data/
│   ├── indicators.json           # Twelve NZ indicators (observatory)
│   ├── governance-graph.json     # Te Pā governance graph (audit)
│   └── comparison.json           # Six systems axes (audit)
├── docs/
│   ├── LEVERAGE_POINTS.md        # Meadows × Aotearoa indicators mapping
│   └── GOVERNANCE_AUDIT.md       # Method note for the audit
├── reports/
│   └── governance-audit-report.md  # Plain-language audit findings
├── assets/
│   ├── observatory.{css,js}      # Observatory dashboard
│   ├── community.{css,js}        # Kōrero styling
│   └── governance.css            # Governance Audit dashboard
├── scripts/
│   ├── fetch_indicators.py       # Weekly indicator refresh
│   └── init_dataset.py           # HF dataset bootstrap
├── space/                        # HF Gradio Space for anomaly detection
└── .github/workflows/refresh.yml # Weekly cron
```

## Three components (observatory pipeline)

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

## Provenance rule

Every observatory indicator cites its public NZ government source. Every governance-graph node, loop, decision-route step, and comparison axis cites a public evidence reference — repo files, GitHub Discussions threads, published government pages, or published Māori data governance documents. If a claim cannot yet be publicly cited, the node is intentionally omitted rather than filled with a private reference.

This is the same rule both views apply: public, aggregated, non-personal.

## Deploy (one-time)

**1. Push this folder to GitHub**

```bash
cd systems-observatory
git init && git add . && git commit -m "Te Pā Systems Observatory v1"
gh repo create robertmccallnz/systems-observatory --public --source=. --push
```

**2. Turn on GitHub Pages**

Settings → Pages → Source: `Deploy from a branch`, branch `main`, folder `/`. The site becomes live at `https://robertmccallnz.github.io/systems-observatory/`.

To use `observatory.te-pa.org`: Settings → Pages → Custom domain → `observatory.te-pa.org`, then add a `CNAME` DNS record pointing to `robertmccallnz.github.io`.

**3. Wire Kōrero (Giscus)**

In your existing Giscus config, get the repo-id and General category-id, then replace the two `REPLACE_WITH_…` placeholders in `index.html` and `governance.html`.

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

Built under the [Māori Data Governance Model](https://www.kahuiraraunga.io/) of Te Kāhui Raraunga. Public, aggregated, non-personal data only. Every indicator cites its source; every annotation is public and forkable; every governance node cites public evidence. Te reo Māori terminology is used deliberately as a paradigm-shifting act at leverage point #2.

See [`docs/LEVERAGE_POINTS.md`](docs/LEVERAGE_POINTS.md) for the observatory mapping and [`docs/GOVERNANCE_AUDIT.md`](docs/GOVERNANCE_AUDIT.md) for the audit method.
