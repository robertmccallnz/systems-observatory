# ADE Mapping Proposal (LP1-12)


Catalog fetched: `2026-07-21T02:44:00Z` — `911` verified Stats NZ ADE dataflows.


This document is a **review-first proposal** for filling `data/incidence_sources.json`.
No `resourceId` values are written until you and Ade sign off on the shortlists below.
The 12 Leverage Points come from `docs/LEVERAGE_POINTS.md` (Meadows 1999, shallow → deep).

## Scope note

ADE holds Stats NZ material. Roughly half the LPs are indicated by data outside ADE
(RBNZ, MoJ, MSD, IRD, Treasury, Hansard, Ombudsman, TPK, MfE). Those LPs are listed
below with `resourceId: []` and a `# NOT IN ADE` marker so the pipeline emits
`pending distributional analysis` cleanly until a non-ADE fetcher is added.

## Governance flag: IWI18 series

The 24 IWI18 dataflows carry iwi-level statistics. Per the Māori Data Governance Model
cited in the README, these must not be batch-approved. Ade / Te Kāhui Raraunga review
required before any IWI18 id becomes a live `resourceId`. Candidates are still listed,
but marked `# GOVERNANCE REVIEW REQUIRED`.

## LP12 — Constants, parameters, numbers

*Indicator note (from LEVERAGE_POINTS.md):* RBNZ Official Cash Rate; RBNZ B2 series. NOT in ADE.

_No ADE dataflows in scope. `resourceId: []` — pipeline will emit `pending distributional analysis`._

## LP11 — Sizes of buffers & stabilising stocks

*Indicator note (from LEVERAGE_POINTS.md):* Housing weeks, grocery weeks, MPI dwelling consents.

| Candidate id | Agency | Name |
|---|---|---|
| `CEN13_FHH_026` | STATSNZ | Household composition, for households in occupied private dwellings, 2001, 2006, and 2013 Censuses (RC, TA, AU) |
| `CEN13_FHH_027` | STATSNZ | Household composition, for people in households in occupied private dwellings, 2001, 2006, and 2013 Censuses (RC, TA, AU) |
| `CEN13_FHH_028` | STATSNZ | Household composition by child dependency status, for households in occupied private dwellings, 2001, 2006, and 2013 Censuses (RC) |
| `CEN13_FHH_029` | STATSNZ | Household composition by number of dependent children in household, for households in occupied private dwellings, 2013 Census (RC, TA) |
| `CEN13_FHH_030` | STATSNZ | Number of usual residents in household, for households in occupied private dwellings, 2001, 2006, and 2013 Censuses (RC, TA, AU) |
| `CEN13_FHH_031` | STATSNZ | Sex and age group, for people in one-person households in occupied private dwellings, 2001, 2006, and 2013 Censuses (RC, TA) |
| `CEN13_FHH_032` | STATSNZ | Household composition by tenure of household, for households with dependent child(ren) in occupied private dwellings, 2001, 2006, and 2013 Censuses (RC ,TA) |
| `CEN13_HOU_004` | STATSNZ | Occupied dwelling type by number of usual residents in household, for households in occupied private dwellings, 2013 Census (RC, TA, AU) |

## LP10 — Structure of material stocks & flows

*Indicator note (from LEVERAGE_POINTS.md):* Env-economic accounts, emissions intensity per $GDP.

| Candidate id | Agency | Name |
|---|---|---|
| `AGR_AGR_001` | STATSNZ | Forestry by Regional Council |
| `AGR_AGR_002` | STATSNZ | Horticulture by Regional Council |
| `AGR_AGR_003` | STATSNZ | Livestock Numbers by Regional Council |

## LP9 — Length of delays vs rate of change

*Indicator note (from LEVERAGE_POINTS.md):* OIA response times, RMA consent processing. NOT in ADE (Ombudsman / MfE / data.govt.nz).

_No ADE dataflows in scope. `resourceId: []` — pipeline will emit `pending distributional analysis`._

## LP8 — Strength of negative feedback loops

*Indicator note (from LEVERAGE_POINTS.md):* Union density; Employment Court cases; HLFS unemployment; MoJ.

| Candidate id | Agency | Name |
|---|---|---|
| `BDS_BDS_008` | STATSNZ | Enterprises by business type and employee count size 2000-2025 |
| `BDS_BDS_009` | STATSNZ | Enterprises by institutional sector and employee count size 2000-2025 |
| `BDS_BDS_010` | STATSNZ | Enterprises by overseas equity and employee count size 2000-2025 |
| `BDS_BDS_011` | STATSNZ | Enterprises by industry and enterprise employee count size group 2000-2025 |
| `BDS_BDS_012` | STATSNZ | Geographic units by region and enterprise employee count size group 2000-2025 |
| `BDS_BDS_014` | STATSNZ | Enterprises by control classification and employee count size 2000-2025 |
| `CEN13_ECI_019` | STATSNZ | Selected ethnic groups (total responses) and work and labour force status by sex, for the census usually resident population count aged 15 years and over, 2001, 2006, and 2013 Censuses (RC, TA, AU) |
| `CEN13_ECI_020` | STATSNZ | Selected ethnic groups (total responses) by occupation (ANZSCO V1.1 major group), for the employed census usually resident population count aged 15 years and over, 2006 and 2013 (RC, TA, AU) |

## LP7 — Gain around positive feedback loops

*Indicator note (from LEVERAGE_POINTS.md):* Wealth concentration; HES; IRD.

| Candidate id | Agency | Name |
|---|---|---|
| `CEN13_ECI_015` | STATSNZ | Selected ethnic groups (total responses) by highest qualification, for the census usually resident population count aged 15 years and over, 2006 and 2013 (RC, TA, AU) |
| `CEN13_ECI_017` | STATSNZ | Selected ethnic groups (total responses) by total personal income (grouped), for the census usually resident population count aged 15 years and over, 2013 (RC, TA, AU) |
| `CEN13_ECI_018` | STATSNZ | Selected ethnic groups (total responses) by sources of personal income, for the census usually resident population count aged 15 years and over, 2001, 2006, and 2013 Censuses (RC, TA, AU) |
| `CEN13_ECI_024` | STATSNZ | Birthplace (detailed overseas born) and years since arrival in New Zealand by sex, for the overseas born census usually resident population count, 2001, 2006, and 2013 Censuses (RC, TA) |
| `CEN13_ECI_025` | STATSNZ | Birthplace (broad geographic area) by years since arrival in New Zealand, for the overseas-born census usually resident population count, 2001, 2006, and 2013 Censuses (RC, TA, AU) |
| `CEN13_ECI_026` | STATSNZ | Birthplace (broad geographic area) by highest qualification, for the census usually resident population count aged 15 years and over, 2006 and 2013 Censuses (RC, TA, AU) |
| `CEN13_ECI_027` | STATSNZ | Birthplace (broad geographic area) by total personal income (grouped), for the census usually resident population count aged 15 years and over, 2013 Census (RC, TA, AU) |
| `CEN13_ECI_028` | STATSNZ | Birthplace (broad geographic area) by sources of personal income, for the census usually resident population count aged 15 years and over, 2001, 2006, and 2013 Censuses (RC, TA, AU) |

## LP6 — Structure of information flows

*Indicator note (from LEVERAGE_POINTS.md):* Media plurality; OIA denial rate; Ombudsman. NOT in ADE.

_No ADE dataflows in scope. `resourceId: []` — pipeline will emit `pending distributional analysis`._

## LP5 — Rules of the system

*Indicator note (from LEVERAGE_POINTS.md):* Benefit sanctions; corporate tax rate; MSD monthly benefits; IRD. Mostly outside ADE (MSD / IRD).

| Candidate id | Agency | Name |
|---|---|---|
| `CORR_CAL_001` | STATSNZ | Annual Community Sentence Offender Population for the latest Calendar Years (ANZSOC) |
| `CORR_CAL_002` | STATSNZ | Annual Completed Community Work Offender Population for the latest Calendar Years (ANZSOC) |
| `CORR_CAL_003` | STATSNZ | Annual Post-prison Offender Population for the latest Calendar Years (ANZSOC) |
| `CORR_CAL_004` | STATSNZ | Annual Remand Prisoner Population for the latest Calendar Years (ANZSOC) |
| `CORR_CAL_005` | STATSNZ | Annual Sentenced Prisoner Population for the latest Calendar Years (ANZSOC) |
| `CORR_FIS_001` | STATSNZ | Annual Community Sentence Offender Population for the latest Fiscal Years (ANZSOC) |
| `CORR_FIS_002` | STATSNZ | Annual Completed Community Work Offender Population for the latest Fiscal Years (ANZSOC) |
| `CORR_FIS_003` | STATSNZ | Annual Post-prison Offender Population for the latest Fiscal Years (ANZSOC) |

## LP4 — Power to add/change/self-organise system structure

*Indicator note (from LEVERAGE_POINTS.md):* Iwi co-governance active; TPK; data.govt.nz. IWI18 series carries Iwi statistics -- see governance note.

| Candidate id | Agency | Name |
|---|---|---|
| `IWI18_EST_001` | STATSNZ | Iwi affiliation (estimated count), for the Maori descent usually resident population, 2018 **[GOVERNANCE REVIEW]** |
| `IWI18_EST_002` | STATSNZ | Iwi affiliation (estimated count) by age group, for the Maori descent usually resident population, 2018 **[GOVERNANCE REVIEW]** |
| `IWI18_EST_003` | STATSNZ | Iwi affiliation (estimated count) by highest qualification, for the Maori descent usually resident population aged 15 years and over, 2018 **[GOVERNANCE REVIEW]** |
| `IWI18_EST_004` | STATSNZ | Iwi affiliation (estimated count) by industry, for the employed Maori descent usually resident population aged 15 years and over, 2018 **[GOVERNANCE REVIEW]** |
| `IWI18_EST_005` | STATSNZ | Iwi affiliation (estimated count) by religious affiliation, for the Maori descent usually resident population, 2018 **[GOVERNANCE REVIEW]** |
| `IWI18_EST_006` | STATSNZ | Iwi affiliation (estimated count) by sex, for the Maori descent usually resident population, 2018 **[GOVERNANCE REVIEW]** |
| `IWI18_EST_007` | STATSNZ | Iwi affiliation (estimated count) by sources of personal income, for the Maori descent usually resident population aged 15 years and over, 2018 **[GOVERNANCE REVIEW]** |
| `IWI18_EST_008` | STATSNZ | Iwi affiliation (estimated count) by status in employment, for the employed Maori descent usually resident population aged 15 years and over, 2018 **[GOVERNANCE REVIEW]** |

## LP3 — Goals of the system

*Indicator note (from LEVERAGE_POINTS.md):* Wellbeing Budget priorities vs GDP; Treasury LSF. NOT in ADE (Treasury).

_No ADE dataflows in scope. `resourceId: []` — pipeline will emit `pending distributional analysis`._

## LP2 — Mindset/paradigm giving rise to the system

*Indicator note (from LEVERAGE_POINTS.md):* Framing ratio in Hansard: growth vs wellbeing vs tino rangatiratanga. NOT in ADE (Hansard).

_No ADE dataflows in scope. `resourceId: []` — pipeline will emit `pending distributional analysis`._

## LP1 — Power to transcend paradigms

*Indicator note (from LEVERAGE_POINTS.md):* Te Tiriti recognition; Waitangi Tribunal outputs; cooperative registrations. NOT in ADE.

_No ADE dataflows in scope. `resourceId: []` — pipeline will emit `pending distributional analysis`._

## Sign-off

- [ ] Robert reviewed LP shortlists
- [ ] Ade reviewed LP shortlists (esp. IWI18 items)
- [ ] Non-ADE LPs (LP12/LP9/LP6/LP3/LP2/LP1) tracked in a separate issue for future fetcher work

Once ticked, a follow-up PR writes the selected ids into `data/incidence_sources.json`.
