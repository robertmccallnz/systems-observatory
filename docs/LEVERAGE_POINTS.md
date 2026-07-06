# Meadows' 12 Leverage Points → Aotearoa Indicators

Donella Meadows' *[Leverage Points: Places to Intervene in a System](https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/)* (1999), ordered from **shallowest (12)** to **deepest (1)**. Each is mapped to a concrete Aotearoa NZ indicator, a public data source, and the paradigm question it surfaces.

The observatory is a **Te Pā Collective Action Lab** artefact. It is not neutral: it treats data through Meadows' explicitly systems-critical lens and through the [Māori Data Governance Model](https://www.kahuiraraunga.io/) of Te Kāhui Raraunga.

| # | Leverage Point | NZ Indicator | Source | Paradigm Question |
|---|---|---|---|---|
| **12** | Constants, parameters, numbers (subsidies, taxes, standards) | Official Cash Rate (OCR) | RBNZ B2 series | Whose cost of living moves when the number moves? |
| **11** | Sizes of buffers & stabilising stocks | Weeks of housing supply / months of grocery stock | Stats NZ dwelling consents; MPI | Are our buffers thick enough to survive a shock, or optimised for extraction? |
| **10** | Structure of material stocks & flows | Emissions intensity per $GDP | Stats NZ env-economic accounts | Does the physical economy match ecological limits? |
| **9** | Length of delays relative to rate of change | OIA response times; RMA consent processing | data.govt.nz; MfE | Does the state react at the speed the system actually moves? |
| **8** | Strength of negative feedback loops | Union density; Employment Court cases | Stats NZ HLFS; MoJ | Can workers correct their own conditions, or has the loop been cut? |
| **7** | Gain around positive feedback loops | Wealth held by top 1% vs bottom 50% | Stats NZ HES; IRD | Which snowballs faster — capital compounding, or wages? |
| **6** | Structure of information flows | Media plurality; OIA denial rate | NZ On Air; Ombudsman | Who gets to know what, and when? |
| **5** | Rules of the system (incentives, punishments, constraints) | Benefit sanctions issued; corporate tax rate | MSD monthly benefits; IRD | Whose behaviour do the rules discipline? |
| **4** | Power to add, change, evolve, or self-organise system structure | Iwi co-governance arrangements active | data.govt.nz / TPK | Who is allowed to redesign the system from inside? |
| **3** | Goals of the system | Wellbeing Budget priorities vs GDP growth targets | Treasury LSF; Budget documents | What is the system actually optimising for? |
| **2** | Mindset / paradigm the system arises from | Framing ratio: "growth" vs "wellbeing" vs "tino rangatiratanga" in Hansard | NZ Parliament Hansard search | What is thinkable in this political culture? |
| **1** | Power to transcend paradigms | Recognition of Te Tiriti as constitutional foundation; alternative economies in practice | Waitangi Tribunal outputs; cooperative registrations | Can the system see beyond itself? |

## Anomaly detection

For each indicator we compute a **rolling z-score** (window = 24 observations by default) and flag any point where `|z| ≥ 2.5` as a **paradigm-challenging anomaly**. Anomalies are not "errors" — they are places where the current paradigm fails to predict behaviour.

## Community annotation

For every anomaly, kaimahi (community members) can:

1. **Rank** which of the 12 leverage points would most effectively intervene.
2. **Propose** an intervention, tagged to a leverage point tier.
3. **Cite** whakapapa — prior interventions in Aotearoa or elsewhere that operated at the same tier.

All annotations are written to the public HF Dataset [`te-pa/systems-observatory-annotations`](https://huggingface.co/datasets/te-pa/systems-observatory-annotations) as a transparent, forkable archive.

## Kaupapa

This observatory is built under the [Māori Data Governance Model](https://www.kahuiraraunga.io/). It uses only public, aggregated, non-personal data. It cites the source of every number. It does not display individual-level Māori data. Te reo Māori terminology is used deliberately as a paradigm-shifting act at leverage point #2.
