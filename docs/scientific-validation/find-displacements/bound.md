# Scientific validation: `src/bound.py`

> **Monorepo audit provenance:** adapted from [SARGuardian PR #9](https://github.com/moshiour0/SARGuardian/pull/9), originally audited against `f038e4dfdb53c8d9793aaaefe173570a1032026c`. The active Backend worker pin is now `006d4cd1485cf80e509eaf8717c12e9c6390ac09`; the source-history comparison found a 13-commit delta affecting only `src/goff_reader.py`, `src/pixel_stack.py`, `tests/test_detectability.py`, and `tests/test_goff_reader.py`. This document is reviewed with that delta and is not evidence of independent geophysical validation.

**Code pin:** `f038e4dfdb53c8d9793aaaefe173570a1032026c`  
**Blob:** `833d7086db528e9871dba12034157c0790cbd884`  
**Find Displacements use:** `NOT_APPLICABLE_GENERIC_AOI`; fixed source-event/candidate priors only.

## Purpose

Computes a source-study observability comparison from committed candidate tables, local floor outputs, common-reference diagnostics and hard-coded event/context assumptions. It compares like-for-like LOS quantities and separates pixel floor from block-median floor.

## Scientific assessment

The dimensional and eligibility checks are useful: floor values must be finite and positive, sample support must be adequate, candidates must be inside the exact source polygon, and LOS precursor rates are compared to LOS floors. However, constants such as event date, source elevation band, candidate CSV names, selected track and precursor-rate interpretation are fixed to the research reproduction. These are not valid inputs for arbitrary user AOIs.

The precursor rate's interpretation is explicitly conditional: the source reporting does not specify the direction, so the code interprets it as LOS. This is not independent validation of the reported motion or the NISAR detection limit.

## Tests and evidence

`tests/test_bound.py` covers maturity classification, block-floor correlation, re-reference, sample support, pre-event date gates, LOS-to-LOS comparisons, source polygon eligibility and stale/invalid floor refusal.

## Required additions

Keep this research bound unchanged. A future AOI-general product needs a separate parameterized calculation fed by new AOI-specific measurements and externally sourced assumptions, with uncertainty propagation and no inherited source candidate tables.

**Verdict:** PASS for its fixed research-bound contract; NOT APPLICABLE to arbitrary AOI Find Displacements.
