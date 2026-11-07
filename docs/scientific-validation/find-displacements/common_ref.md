# Scientific validation: `src/common_ref.py`

> **Monorepo audit provenance:** adapted from [SARGuardian PR #9](https://github.com/moshiour0/SARGuardian/pull/9), originally audited against `f038e4dfdb53c8d9793aaaefe173570a1032026c`. The active Backend worker pin is now `006d4cd1485cf80e509eaf8717c12e9c6390ac09`; the source-history comparison found a 13-commit delta affecting only `src/goff_reader.py`, `src/pixel_stack.py`, `tests/test_detectability.py`, and `tests/test_goff_reader.py`. This document is reviewed with that delta and is not evidence of independent geophysical validation.

**Code pin:** `f038e4dfdb53c8d9793aaaefe173570a1032026c`  
**Blob:** `e5dfb7f523730489276bfa56f449f7f9c511d589`  
**Find Displacements use:** WITHHELD. The dashboard adapter requires an in-AOI target and returns before this module is loaded when no target is supplied.

## Purpose

Re-references pairwise exports to a common set of pixels that are valid in every pair and lie outside buffers around the supplied target locations. It requires at least 200 common pixels and checks exact CRS, shape and affine transform compatibility.

## Scientific assessment

The implementation correctly warns that the common AOI support is not independently surveyed stable ground. Broad real motion, an event-affected area, or unstable terrain can bias the common median. The CSV field name `stable_px` is legacy wording; the output also records that stability is unvalidated. A common median is a relative-datum diagnostic, not an absolute reference.

The current helper is target-dependent because the exclusion buffers are built around explicit target coordinates. It must not be run for target-free Find Displacements by inventing a centroid or selecting a hidden target. Its existing workflow belongs to Known Place Analysis until a distinct AOI-wide reference estimator has been scientifically designed.

## Tests and evidence

`tests/test_common_ref.py` covers duplicate pair rejection, exact grid/transform agreement and exclusion of out-of-AOI candidates using the exact polygon. `tests/test_timeseries.py` also tests removal of pair-private datum errors and avoidance of a moving target as the reference.

## Required additions for a separate target-free design

- Define a reference mask from independently supported stable ground or a transparent iterative stability model, not simply “all AOI pixels except target buffers”.
- Expose reference-pixel count, spatial distribution, temporal stability, topographic/land-cover context and sensitivity to alternate masks.
- Reject broad/common-mode movement when its stability cannot be distinguished from datum drift; report relative-only products.
- Keep the existing target-buffer implementation unchanged for Known Place Analysis.

**Verdict:** PASS for its declared target-buffered relative-datum contract; NOT APPLICABLE to current target-free Find Displacements.
