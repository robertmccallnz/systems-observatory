# Governance Audit · Method Note

The Governance Audit is the inward-facing companion to the outward-facing Systems Observatory. The observatory watches wider Aotearoa political-economy indicators through Meadows' twelve leverage points; the audit watches Te Pā's own decision-making, feedback loops, delays, rules, and pathway capacities through the same lens.

## Why two views coexist

Meadows' 1999 framework was designed to make systems inspectable from the outside *and* from the inside. Applying it only to the state and the market — while leaving one's own governance opaque — reproduces the exact information asymmetry Meadows warns against. The audit closes that loop.

- **Observatory** — Aotearoa political-economy indicators. Public data. Outward gaze.
- **Governance Audit** — Te Pā's own governance system. Public evidence only. Inward gaze.

Both views use the same repo, the same shared footer, and the same Kōrero comment layer.

## What the audit contains

- **`data/governance-graph.json`** — nodes (signals, outcomes, decision points, delays, rules, resources), edges, feedback loops, decision routes, snapshots, prompts, and notes. Every node carries a Meadows depth, an intervention-candidate list, and `evidence_refs`.
- **`data/comparison.json`** — six systems axes (authority distribution, information flow, delay visibility, feedback closure, rule depth, self-organisation) scored qualitatively for current state vs rhizome-integrated target, each with `meadows_focus`, `priority`, and `evidence_refs`.
- **`reports/governance-audit-report.md`** — the plain-language audit findings and priority interventions.
- **`governance.html`** — the interactive dashboard that renders the two data files.

## Provenance rule

Every `evidence_refs` array in the governance data files points to public, forkable references — repo files, GitHub Discussions threads, published government pages, or published Māori data governance documents. This mirrors the observatory's indicator sources.

If a governance claim cannot yet be cited to a public source, the node is intentionally omitted rather than filled with a private trustee reference. This is the same rule the observatory applies to indicator data: no private data, ever, even where it would strengthen the argument.

## How to update the graph

1. Open a PR against `data/governance-graph.json` or `data/comparison.json`.
2. Include the public evidence link that justifies the change in `evidence_refs`.
3. Tag the PR to a Discussions thread if the change originates from community feedback.
4. Merge only after a kaitiaki review, following the `governance-change` decision route in the graph.

## How to interpret priorities

- **Critical** — the axis is both far from the target and blocking other axes.
- **High** — the axis is materially off-target and can be moved without waiting for structural change.
- **Medium** — the axis is comparatively strong; the task is to preserve it while other axes catch up.

## How this connects to Meadows

The audit uses the same twelve leverage points as `docs/LEVERAGE_POINTS.md`. Because Te Pā's own governance sits mainly at the deeper leverage tiers — information flows, feedback loops, rules, self-organisation, goals, paradigms — the audit focuses there rather than on parameter tweaks. The observatory watches the shallower tiers of the wider system; the audit watches the deeper tiers of our own.

## Related documents

- [`LEVERAGE_POINTS.md`](./LEVERAGE_POINTS.md) — the Meadows → Aotearoa indicator mapping.
- [`reports/governance-audit-report.md`](../reports/governance-audit-report.md) — the findings.
- [Māori Data Governance Model · Te Kāhui Raraunga](https://www.kahuiraraunga.io/) — the kaupapa foundation.
