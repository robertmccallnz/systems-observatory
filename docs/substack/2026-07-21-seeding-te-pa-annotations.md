---
title: "Seeding the Systems Observatory: what lives on Hugging Face, and why"
subtitle: "An honest walk-through of standing up te-pa/systems-observatory-annotations under the Maori Data Governance Model"
date: 2026-07-21
author: "Robert McCall"
publication: "Kiwi Dialectic"
tags: [systems-observatory, hugging-face, indigenous-data-sovereignty, leverage-points, kaupapa-maori, open-source]
status: draft
---

## The 30-second version

The Systems Observatory now has a public, versioned home for its annotations:
https://huggingface.co/datasets/te-pa/systems-observatory-annotations

Today's session took a repo full of scraping scripts and a leverage-points
annotation schema, and turned it into a live, forkable dataset with a Creative
Commons licence and a Maori Data Governance Model note baked into the dataset
card. This post is the receipt: what we did, what we didn't, and what the
blockers were.

## Why Hugging Face for a systems observatory

A reasonable question. The observatory scrapes public data - RBNZ Official
Cash Rate, MPI dwelling consents, Aotearoa Data Explorer environmental-economic
accounts, and so on. None of that *needs* Hugging Face to exist.

HF's role is downstream of the numbers. The observatory's actual output isn't
the raw data (it's already public elsewhere) - it's the **annotations**: for
each data point, a small human/AI-authored record that (a) cites whakapapa
/ source, (b) tags it to a Meadows leverage-point tier, and (c) proposes an
intervention. That layer is what makes the site an *observatory* and not just
a mirror.

The annotations need a home that is:

- Public and forkable (so others can build on the work)
- Versioned (so citations stay stable)
- Cheap to host (Hugging Face is free for datasets under a sensible size)
- Easy to consume (`datasets.load_dataset('te-pa/systems-observatory-annotations')`)

Hugging Face gives all four. The org page - Te Pa Tuwatawata - carries the
kaupapa in the namespace itself. Everything published there sits under CC BY
4.0 with the Maori Data Governance Model as its ethical scaffolding.

## Today's leverage-point mapping

In parallel to the seeding, we merged a mapping document from Aotearoa Data
Explorer tag families to leverage-point tiers LP9-LP12:

| LP | Meaning | Tag families |
|----|---------|--------------|
| LP12 | Constants, parameters, numbers | `RBNZ`, `OCR`, `CONST`, `PARAM` |
| LP11 | Sizes of buffers and stabilising stocks | `DWLLNG`, `CONSENT`, `HOUS`, `BUFFER`, `STOCK` |
| LP10 | Structure of material stocks and flows | `ENV`, `EMISS`, `CO2`, `GHG`, `AGR`, `ENERGY` |
| LP9 | Length of delays relative to rate of change | `DELAY`, `RATE`, `LAG` |

The kaupapa remains LP2 (paradigms) - restoring Te Tiriti relationships - but
tractable interventions live down the ladder at LP9-LP12. This mapping is what
lets us take an RBNZ B2 series row and say: *this is a LP12 lever, so any
critique of monetary policy has to name the parameter, not the paradigm*.

## What actually went wrong (the honest bit)

Three friction points worth naming:

1. **`huggingface-cli` is deprecated.** The new CLI is `hf`, and
   `hf auth login` replaces `huggingface-cli login`. Old docstrings needed
   updating - trivial once you notice it.
2. **Fine-grained tokens default to your user, not your org.** The first
   token issued only had `robertnz` scope. Creating a repo under `te-pa`
   returned a 403 that surfaced as a misleading `RepositoryNotFoundError`.
   Fix: create the HF org first, then issue a token with explicit write
   scope on that org's namespace.
3. **Credential hygiene matters even in a private chat.** A token pasted
   into a chat log is a compromised token - revoke, rotate, and only ever
   paste into an interactive CLI prompt in your own terminal.

## What's next

The dataset currently has one row - the LP2 kaupapa seed. The observatory's
fetch scripts (`fetch_incidence.py`, `lp12_rss.py`, `normalise_ade_catalog.py`)
can now start writing LP9-12 annotations against the schema. A follow-up PR
will add a `--push` flag to `lp_backfill.py` so the `leverage_point` field can
be written back to Hugging Face once real rows exist.

If you want to fork the work, everything is on `main`:

- Code: https://github.com/robertmccallnz/systems-observatory
- Dataset: https://huggingface.co/datasets/te-pa/systems-observatory-annotations
- ADE mapping proposal: `docs/ADE_MAPPING_PROPOSAL.md`
- Leverage points schema: `docs/LEVERAGE_POINTS.md`

## A note on the kaupapa

Publishing a first commit to a public dataset that carries an iwi-linked name
is not a trivial act. The choice to seed under `te-pa` rather than `robertnz`
is deliberate - the namespace signals collective stewardship, and the licence
(CC BY 4.0) plus the MDGM note in the dataset card signal how the data can
and cannot be re-used. Individuals build the pipes; the taonga live under the
collective name.

---

*This post is part of the Kiwi Dialectic series on building public
infrastructure for indigenous political education. Draft written 21 July 2026
in Otepoti / Dunedin.*
