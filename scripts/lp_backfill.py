#!/usr/bin/env python3
"""Dry-run backfill of `leverage_point` for te-pa/systems-observatory-annotations.

Mapping derived from docs/ADE_MAPPING_PROPOSAL.md (LP9-LP12).
Never pushes to HF; writes reports/lp_backfill_dryrun.json when the dataset is reachable.
Handles three states cleanly:
  1. `datasets` lib missing       -> print rule table, exit 0
  2. dataset missing / no auth    -> print reason, exit 0
  3. dataset reachable            -> compute coverage report
"""
from __future__ import annotations
import json, pathlib, collections, sys

LP_RULES = {
    'LP12': {'RBNZ', 'OCR', 'CONST', 'PARAM'},
    'LP11': {'DWLLNG', 'CONSENT', 'HOUS', 'BUFFER', 'STOCK'},
    'LP10': {'ENV', 'EMISS', 'CO2', 'GHG', 'AGR', 'ENERGY'},
    'LP9':  {'DELAY', 'RATE', 'LAG'},
}
DATASET = 'te-pa/systems-observatory-annotations'

def assign_lp(tags):
    tagset = {t.upper() for t in (tags or [])}
    for lp, keys in LP_RULES.items():
        if tagset & keys:
            return lp
    return None

def print_rules():
    for lp, keys in LP_RULES.items():
        print(f'  {lp}: {sorted(keys)}')

def main():
    try:
        from datasets import load_dataset
        from datasets.exceptions import DatasetNotFoundError
    except ImportError:
        print('[info] `datasets` not installed; rule table only:')
        print_rules(); return 0
    try:
        ds = load_dataset(DATASET, split='train')
    except Exception as e:
        print(f'[info] Cannot load {DATASET}: {type(e).__name__}: {e}')
        print('[info] Rule table (for review):')
        print_rules(); return 0
    counts = collections.Counter()
    unmapped = []
    for row in ds:
        lp = assign_lp(row.get('tags', []))
        counts[lp or 'UNMAPPED'] += 1
        if lp is None:
            unmapped.append(row.get('id'))
    report = {'dataset': DATASET, 'total': len(ds),
             'counts': dict(counts), 'unmapped_sample': unmapped[:25]}
    pathlib.Path('reports').mkdir(exist_ok=True)
    pathlib.Path('reports/lp_backfill_dryrun.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())
