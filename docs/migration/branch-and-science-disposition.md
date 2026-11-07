# SARGuardian source-branch and science disposition

**Audit date:** 2026-11-05  
**Working branch:** migration/source-snapshot-import

## Decision rule

A branch is not promoted merely because it is newer than a repository's main branch. For every candidate, this audit distinguishes active workflow use, exact source-history preservation, superseded work, test coverage, and scientific impact. Original repositories remain unchanged.

## Science repository — open PRs and branch lineage

| Source work | Source state | Verified lineage / active use | Monorepo disposition |
|---|---|---|---|
| [PR #8 — guarded GUNW masks, AOI pixel attrition and science inversion](https://github.com/moshiour0/SARGuardian/pull/8) | Open, non-draft; 61 files; head 3b227f968b9a9ea068d06ef4424c6906302d3caa | Active Backend pin 006d4cd descends from this exact head. | Preserved through the exact 006d4cd source pin and Git history; no duplicate copy. |
| [PR #11 — exact GUNW acquisition networks and sparse spatial-null withholding](https://github.com/moshiour0/SARGuardian/pull/11) | Open, non-draft; head 006d4cd1485cf80e509eaf8717c12e9c6390ac09; 10 commits over baseline 3b227f9 | This is the exact science SHA used by the Backend main product-worker workflow. The worker verifies this pin and runs science diagnostics on retained PR-GUNW exports. | Active science implementation; exact source snapshot and historical commit are preserved in Monorepo. |
| [PR #12 — exact-compatible-network pixel-stack backport](https://github.com/moshiour0/SARGuardian/pull/12) | Open, non-draft; one changed file, src/pixel_stack.py; head 323be74bdb1db22b19e48bd041a3127a0a58772e | Its pixel_stack.py blob SHA 74cf89c878d193d481b99acd2e578a255c1ad85f is identical to the file at active pin 006d4cd. It adds no tests file. | No new runtime code is missing. Treat as a science-main backport, not a separate Monorepo engine. The active worker already runs this exact code from 006d4cd. |
| [PR #9 — Find Displacements script-by-script audit](https://github.com/moshiour0/SARGuardian/pull/9) | Open, non-draft; documentation-only; 12 files; head af3fd7185fae23bef631f09d75ad9b365d7c8aea | Original audit was written against f038e4d. The comparison to active 006d4cd shows a 13-commit delta affecting only goff_reader.py, pixel_stack.py, test_detectability.py and test_goff_reader.py. | Adapted under docs/scientific-validation/find-displacements. Pins and changed blob SHAs were updated; the GOFF and pixel-stack pages incorporate the newer changes. |
| [PR #5 — Target 4/9 raw-data diagnostics and scientific audit](https://github.com/moshiour0/SARGuardian/pull/5) | Open draft; head 3a6f74a65f84c6daf49503e083de7caa51bfaafa | Branch comparison shows it is an ancestor of 006d4cd (69 commits behind, no unique commits ahead). Its code and history are reachable through the imported pin. | No separate code snapshot required. Preserve findings and limitations as evidence; unresolved DEM/physical validation is not promoted as PASS. |

## Exact active science pins

The active Backend main product-worker uses:

- SCIENCE_COMMIT: 006d4cd1485cf80e509eaf8717c12e9c6390ac09
- src/pixel_stack.py blob: 74cf89c878d193d481b99acd2e578a255c1ad85f
- src/goff_reader.py blob: 606cc9dd1cfcbb4cf590d8742f204af65bef95b3

Both blobs were fetched from the original science repository and from the Monorepo at the reachable historical commit; SHA identities match. The commit 006d4cd itself is addressable in the Monorepo Git object graph. The inactive Find Displacements workflow candidates check out this exact commit from moshiour0/SARGuardian-Monorepo.

The separately promoted science/nisar-core directory represents the audited science main snapshot 9fcb543. It is intentionally not the same tree as the historical worker pin. Keep the explicit 006d4cd pin until a coordinated science release updates workflow, tests and provenance together.

## Active Find Displacements call graph

The Backend main workflow and code establish this path:

1. The product worker checks out and verifies science commit 006d4cd.
2. It processes each selected GUNW/GOFF product with the pinned readers and retains validated AOI-clipped exports.
3. tools/aggregate_aoi_run.py calls tools/run_export_science_diagnostics.py.
4. The diagnostics script verifies the science checkout SHA, runs science-source/src/pixel_stack.py on compatible retained PR-GUNW exports, and records common-mode-removed and common-mode-retained variants separately.
5. The diagnostics classifier preserves WITHHELD_NO_COMPATIBLE_REPEATED_NETWORK as non-testable; it does not translate it into NO DETECTION.
6. The aggregator separately calls dashboard.aoi_displacement_candidates and dashboard.aoi_relative_pixel_timeseries. GOFF candidate screening and GUNW LOS time-series diagnostics remain separate.

The current active dashboard modules are promoted under:

- engines/find-displacements/dashboard/aoi_displacement_candidates.py
- engines/find-displacements/dashboard/aoi_relative_pixel_timeseries.py

These modules preserve full acquisition-network identity, support counts, and explicit WITHHELD statuses. The relative GUNW module records that its background reference is not independently validated.

## Other science branches

- science/valid-pixel-target4-9-audit, baseline/run-409985-science-commit-3b227, fix/science-regression-guards-20261029, science/aoi-wkt-dynamic-e2e and ci/science-regression-base-10639 are ancestors of 006d4cd. No separate runtime promotion is required.
- Closed prototype PRs #6/#7 and science/goff-spatial-screen-prototype-20261029 introduce an earlier standalone goff_spatial_screen.py. This is not the active Backend call path. The active path uses the integrated dashboard candidate engine and AOI-wide displacement screen; do not add the prototype as another production screen without separate design and test review.
- The baseline 3b227 GOFF optional variance-band metadata fix is included in the history leading to 006d4cd. The current goff_reader.py pin records actual optional exported band indices rather than assuming fixed positions.

## Dynamic and Backend branch disposition

- Older Dynamic Known Place two-polygon, results-dashboard and Google-raster branches were not used to overwrite current Dynamic main; current main has the newer UI implementation.
- RiverShift place-search page/CSS in feat/rivershift-map-place-search-20261105 has the same blob identity as Dynamic main. The older RiverShift phase-2 branch has a matching Supabase migration, but other API/UI files differ; current main remains the source of truth.
- Older RiverShift overlay, impact-context, preview and download/retry branches were not mechanically merged over current main. The current Backend main RiverShift worker and current Dynamic main RiverShift page are the promoted baseline.
- Backend Known Place PR #85 must remain a separate source pin because Backend main alone does not contain the full Known Place engine. It is already imported under migration/source-snapshots/backend-known-place-pr85 and promoted under engines/known-place.

## Deferred acceptance gates

This audit establishes source lineage and code-path selection. It does not complete production readiness.

1. Obtain a successful current-head Monorepo run for the latest workflow/archive/contract changes. Several later GitHub Actions runs created jobs but failed before any runner step/log was produced; that state is unresolved, not green.
2. Obtain a fresh full-history secret scan after the latest archive and documentation additions.
3. Refresh both Monorepo Vercel Preview projects to the current source head; the account returned api-deployments-free-per-day (>100 deployments/day), so the known READY previews are stale.
4. Run an isolated Monorepo Find Displacements pilot against retained data; verify the exact 006d4cd checkout, both pixel-stack common-mode variants, GOFF candidate output and withheld statuses without unnecessarily repeating raw downloads.
5. Review workflow permissions, Drive retention receipts, API callbacks, Supabase migration history and rollback before production dispatch is redirected.

**Disposition:** preserve the exact active science pin and source histories; use the newer integrated dashboard implementation; keep optional or prototype work separate unless its active call site and validation are demonstrated; do not declare production cutover complete from branch import or unit-test success alone.
