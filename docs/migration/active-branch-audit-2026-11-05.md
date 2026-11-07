# SARGuardian active-branch audit — 2026-11-05

**Scope:** Dynamic, Backend, NISAR science, existing Monorepo migration branches, and submission evidence.
**Decision rule:** use the newest verified, tested integration baseline—not the branch with the largest ahead count. Preserve divergent scientific work and unmerged validation work with exact provenance; do not silently merge or activate it.

## Source baselines

| Source | Selected baseline | Role |
|---|---|---|
| moshiour0/SARGuardian_Dynamic | dd64b7adc90594f1d7f316b352e39fbac2013cb6 | Current integrated React/Vite web application and Firebase/Supabase FastAPI API |
| moshiour0/SARGuardian-backend | 97d849454918b1425ac41bb70e7a32d11cfd3833 | Current integrated scientific worker and Actions baseline |
| moshiour0/SARGuardian | 9fcb543ef28a7f6fe70a379aed9cfe3e43e277ec | Current main NISAR science source |
| Backend Known Place PR #85 | bfde7dde8ada92a03054cd8dbad8daa7a5c119f8 | Distinct Known Place workflow and research lineage, not replaced by backend main |
| NISAR audit pin | 006d4cd1485cf80e509eaf8717c12e9c6390ac09 | Separately preserved research/audit revision; not silently promoted to the canonical runtime |

The source trees and provenance pins are kept in migration/source-snapshots/ and docs/migration/source-pins.json. The exact source snapshots remain immutable.

## Dynamic branch findings

### Known Place

- feat/known-place-two-polygon-map-20261102: diverged (60 commits ahead / 40 behind). Its KnownPlaceAnalysisPanel.tsx and KnownPlacePolygonEditor.tsx blobs are older than Dynamic main.
- feat/known-place-results-dashboard-20261102: diverged (21 ahead / 27 behind). Its results dashboard blob is older than Dynamic main.
- feat/known-place-google-raster-map-20261103: diverged (5 ahead / 26 behind). The current main's Google map and shared result UI blobs match the newer integrated files.
- fix/known-place-catalog-preflight-20261102: diverged (7 ahead / 29 behind); do not transplant the older component wholesale.

**Decision:** retain Dynamic main as the current integrated frontend/API baseline and Backend PR #85 as the separate Known Place scientific/workflow baseline. Keep two-polygon generic analysis separate from author-exact P05023 replay. API dispatch destinations are now independently configurable; compatibility defaults still target the old Backend dispatchers until a coordinated cutover.

### RiverShift

- feat/rivershift-map-place-search-20261105 contains the same RiverShiftPage.tsx and CSS Git blobs as Dynamic main; place search is already in the selected baseline.
- fix/rivershift-preview-api-origin-fallback-20261105 has the same API-origin and catalogue client blobs as main.
- Older divergent overlay, geometry-generalisation, audit-visibility, global-positioning and impact-context branches have fewer/older page and CSS blobs than main; their branch heads are behind main. They are not merged wholesale.
- feat/rivershift-phase2-one-click-20261104 is behind main and its key API/UI blobs differ; do not overwrite main with it.

**Decision:** use Dynamic main for the integrated UI/API. Preserve source-branch snapshots and compare any specific regression fix against current main before considering a targeted port. Do not claim a stale branch is “latest” just because it contains a feature-named commit.

### Find Displacements and AOI workers

- feat/find-displacements-target-free-analysis: 2 ahead / 84 behind.
- feat/target-free-science-candidate-fixes: 3 ahead / 82 behind.
- feat/aoi-product-worker-pool-15: 11 ahead / 80 behind.
- feat/aoi-wide-discovery-dashboard-integration: 3 ahead / 81 behind.

These branches are divergent snapshots. The selected Backend main and its tests are the current integration baseline; the Monorepo retains inactive Find Displacements workflow candidates, checks their promoted paths, and keeps GOFF and GUNW as separate measurement families. Do not replace the current worker with a stale branch without a specific failing regression and a minimal reviewed port.

## Backend branch findings

### RiverShift processing

Selected Backend main is materially newer than these divergent feature branches in the core processing files:

| Branch | Compare to Backend main | Decision |
|---|---:|---|
| feat/river-shift-15-product-batches-20261103 | behind 82; no ahead commits | Already superseded; do not merge |
| feat/rivershift-gcov-worker-20261103 | 32 ahead / 106 behind | Preserve only as historical lineage if needed; current main has newer core files |
| feat/rivershift-download-retry-fix-20261104 | 7 ahead / 45 behind | Compare targeted retry intent; do not replace newer downloader/worker |
| feat/rivershift-phase2-one-click-20261104 | 5 ahead / 46 behind | Current main's batch and process files are newer; do not overwrite |
| feat/rivershift-raster-first-previews-20261104 | 9 ahead / 61 behind | Current main has the longer integrated process worker and tests |
| feat/rivershift-run36-retrospective-replay-20261105 | 4 ahead / 18 behind | Retain the exact Run #36 replay utility/workflow as a separate validation snapshot |
| feat/rivershift-opera-dswx-s1-validation-20261104 | 26 ahead / 38 behind | Retain independent-reference code as a validation snapshot, not active worker |
| feat/rivershift-opera-rtc-s1-inventory-fallback-20261105 | 3 ahead / 26 behind | Retain the latest combined DSWx-S1 and RTC-S1 diagnostic files as a validation snapshot |

The exact OPERA and Run #36 source files are archived under migration/source-branch-snapshots/ and pinned by rivershift-validation-pins.json. They are **not** promoted to root .github/workflows. The OPERA replay has a push-sentinel trigger; it must be converted to a manual, pinned, least-privilege workflow before any future activation. Required runtime imports and pinned test dependencies must be reconciled before promotion.

### Known Place

- The old feat/know-place-analysis branch is heavily diverged (659 ahead / 362 behind).
- The feat/known-place-independent-reference-20261102 head is the exact Backend PR #85 source pin selected for the Known Place engine.
- The PR #85 snapshot contains 40 workflow files, versus 35 in backend main: 15 PR-only, 8 same-path/different-content, 17 identical. Backend main also has 10 workflow files not present in PR #85. Filename equality is not evidence of workflow equivalence.

**Decision:** preserve the PR #85 source tree, plus the current Backend main snapshot, and promote only the reviewed Known Place engine paths. Keep its 15 PR-only workflows archived until each caller, secret, consent gate, artifact, callback, retention and manual trigger is audited. Generic and author-exact workflows remain separate.

## NISAR science branch decision

fix/run-409985-homogeneous-gunw-networks-and-spatial-null is 325 commits ahead of NISAR main and not behind it. It is already preserved as historical pin 006d4cd... with exact tree/blob identity, but it is **not** selected as the canonical runtime source solely because it has more commits.

That revision contains substantial reader, reference, local-floor, time-series, pixel-stack, bound, candidate-check and impoundment changes, plus a detailed scientific regression guard. The attached audit still identifies unresolved geophysical questions, including sparse P05023 GUNW target support, the ionosphere interpolation screen, independent displacement controls and material impoundment DEM output changes. The branch is retained for review and targeted, tested promotion—not silently substituted for main.

## Migration work already applied to the Monorepo branch

1. Fixed the Find Displacements inactive-workflow validator to distinguish root paths from valid promoted engine paths and normalise runner-local checkout prefixes.
2. Added independent configurable repository/workflow/ref settings for generic and author-exact Known Place dispatch, polling and artifact retrieval. Defaults remain Backend/main for compatibility.
3. Added tests for those defaults, independent destinations, unsafe workflow names, dispatch/status routing and artifact repository selection.
4. Added migration/promotion-overrides.json and a strict verifier: immutable source snapshots remain byte-for-byte unchanged; only four exact hash-pinned active API promotion files are allowed to differ.
5. Added separate RiverShift validation branch snapshots and hash pins. They remain archival/inactive.
6. Updated API environment/deployment documentation for the Monorepo paths and the independent Known Place variables.

The full snapshot regression run 41980756059 passed **17/17 jobs** after the Known Place routing/integrity changes. Subsequent docs-only commits should still receive a fresh metadata/secret-scan/regression check before being treated as the current verified head.

## Submission and scientific-claim rules

- Challenge fit is an interactive, open-source application powered by NISAR radar observations, with global AOI input where the available mission products and compatible dates allow.
- NASA data must be the measurement source, not a decorative label. Optical, OSM, gauge and other datasets are clearly separated as contextual or independent-reference sources.
- A successful unit test, source checksum, workflow run, valid raster or dashboard render is software/reproducibility evidence, not independent geophysical validation.
- RiverShift Run #36 stays PROVISIONAL / NO_MATCH_NO_SCORE when no eligible date-matched reference exists. OPERA DSWx-S1 is a SAR-derived cross-sensor water reference, not field truth; RTC-S1 is backscatter inventory only.
- NISAR GUNW phase, GOFF offsets and GCOV water/change screening must retain separate units, geometries, support, datum and interpretation.
- Missing or invalid measurements remain missing/withheld—not zero.
- Public copy should lead with capability and concrete, traceable demonstrations; limitations that materially affect a metric remain visible next to that metric. Do not advertise forecasts, field-validated damage, 3-D displacement or verified accuracy unless the relevant evidence exists.

## Remaining gates

- Import/activate no root workflow until pinned actions, least-privilege permissions, caller graphs, artifact schemas, failure propagation, callback HMAC, retries, retention and rollback are tested.
- Complete RiverShift 20-job mock for all batch barriers, failures, failed-only retries, Drive receipt mismatch and callback order.
- Reconcile Supabase remote migration history and retention policy read-only; do not reapply local SQL without proving remote status.
- Complete authenticated Preview smoke tests with nonproduction Firebase/Supabase/Google Maps credentials and staging persistence.
- Run isolated, source-checked real-data pilots and independent-reference assessment for each engine.
- Re-deploy current Preview head after the Vercel build-rate limit clears; the previous 8de4f0f... Web/API Preview builds were READY, but Vercel later rejected new build checks with build-rate-limit.
- Test rollback to the old Dynamic/Backend production route before any coordinated one-engine-at-a-time production cutover.
