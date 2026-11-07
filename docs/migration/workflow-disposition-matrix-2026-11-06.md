# SARGuardian workflow disposition matrix — 2026-11-06

**Purpose:** close the gap between source workflow inventory and actual Monorepo root Actions. This matrix covers every workflow file from the three audited source trees, including branch-specific Known Place variants.

## Audited immutable source sets

| Source | Ref | Workflow files |
|---|---|---:|
| moshiour0/SARGuardian_Dynamic main | dd64b7adc90594f1d7f316b352e39fbac2013cb6 | 7 |
| moshiour0/SARGuardian-backend main | 97d849454918b1425ac41bb70e7a32d11cfd3833 | 35 |
| moshiour0/SARGuardian-backend Known Place PR #85 head | bfde7dde8ada92a03054cd8dbad8daa7a5c119f8 | 40 |
| **Total source workflow instances** | | **82** |

The Backend main and Known Place PR #85 inventories are separate source lineages. The 17 exact-shared and eight changed-same-path PR #85 variants must not be collapsed by filename. The three source directories are preserved under migration/source-snapshots/.

## Current Monorepo root inventory

At base head 3420eaea6b3d97175c075d4eb4da00423d89c176, root .github/workflows/ contained 38 files. The retention-archive port raised this to 39, the fixed P05023 live-retention port to 40, the dual-pin AOI code-validation port to 41, and the full Backend source snapshot regression port raises the expected root inventory to 42. Root files added for migration CI (snapshot regression, metadata, secret scan and runner diagnostics) are not source-engine workflows. Root paths listed below are candidate ports or consolidated coverage; root presence alone does not imply parity.

## Dynamic main source workflows (7)

| Source workflow | Source blob | Monorepo root destination | Disposition |
|---|---|---|---|
| **backend-tests.yml** | 1d20d3021976 | .github/workflows/snapshot-regression-tests.yml | Consolidated CI — parity review open |
| **frontend-tests.yml** | de7ad2eb1caf | .github/workflows/snapshot-regression-tests.yml | Consolidated CI — parity review open |
| **known-place-analysis.yml** | 2fec69265f9b | .github/workflows/know-place-aoi-dispatcher.yml, .github/workflows/know-place-aoi-analysis.yml | Renamed root port — contract review open |
| **known-place-paper-reproduction.yml** | bfdec667a618 | .github/workflows/know-place-paper-reproduction-dispatcher.yml, .github/workflows/know-place-author-exact-replay.yml | Renamed root port — contract review open |
| **sarguardian-aoi-product-worker.yml** | 656d105a9b15 | .github/workflows/sarguardian-aoi-product-worker.yml | Root exists — contract review open |
| **sarguardian-aoi-wkt-dashboard.yml** | ed74c64295de | .github/workflows/sarguardian-aoi-wkt-dashboard.yml, .github/workflows/sarguardian-aoi-dashboard-engine.yml | Renamed root port — contract review open |
| **sarguardian-displacement.yml** | eb6f8fd76fd9 | .github/workflows/sarguardian-aoi-wkt-dispatcher.yml, .github/workflows/sarguardian-aoi-wkt-dashboard.yml | API dispatcher replacement — schema review open |

- **backend-tests.yml:** Promoted Dynamic API suite runs in the root Snapshot Regression workflow. Verify every Dynamic backend test file and dependency is included in promoted-dynamic-api.
- **frontend-tests.yml:** Promoted Web test/build/lint suite runs in the root Snapshot Regression workflow. Verify the source frontend job's exact test and path-filter coverage.
- **known-place-analysis.yml:** Dynamic Known Place caller is represented by the Monorepo dispatcher plus local reusable engine. Verify payload and callback schema; keep generic two-polygon AOI separate from author-exact P05023.
- **known-place-paper-reproduction.yml:** Dynamic author-exact caller maps to its separate Monorepo dispatcher/reusable workflow. Preserve explicit consent and exact P05023 historical pins.
- **sarguardian-aoi-product-worker.yml:** Root reusable AOI worker exists; compare the Dynamic worker's source checkout, environment variables, artifact and cleanup contracts against Backend and PR #85 variants.
- **sarguardian-aoi-wkt-dashboard.yml:** Root has a workflow_dispatch API-facing wrapper and local workflow_call engine. Dynamic and Backend dashboard inputs are not interchangeable; verify exact caller/callee and terminal callback semantics.
- **sarguardian-displacement.yml:** Legacy Dynamic dispatcher wrapper is represented by the Monorepo API adapter plus manual dispatcher/API-facing workflow. Its product_type/acquisition_window/retention_mode/processing_profile schema differs from the Backend dashboard schema; do not wire it as a direct replacement without tests.

## Backend main source workflows (35)

| Source workflow | Source blob | Monorepo root destination | Disposition |
|---|---|---|---|
| **dashboard-assets-test.yml** | 75926ca204fd | .github/workflows/dashboard-assets-test.yml | Root exists — contract review open |
| **dashboard-real-artifact-smoke.yml** | 9179d9b58adb | .github/workflows/dashboard-real-artifact-smoke.yml | Root exists — contract review open |
| **earthdata-auth-test.yml** | 0d6001ebb9e4 | .github/workflows/earthdata-auth-test.yml | Root exists — contract review open |
| **earthdata-token-smoke-test.yml** | 23f8fea2706b | .github/workflows/earthdata-token-smoke-test.yml | Root exists — contract review open |
| **know-place-aoi-dispatcher.yml** | 90b254a68dae | .github/workflows/know-place-aoi-dispatcher.yml | Root exists — contract review open |
| **know-place-paper-reproduction-dispatcher.yml** | 42216b46f0b4 | .github/workflows/know-place-paper-reproduction-dispatcher.yml | Root exists — contract review open |
| **nisar-discovery-test.yml** | fd5405888c26 | .github/workflows/nisar-discovery-test.yml | Root exists — contract review open |
| **nisar-goff-timeseries-test.yml** | e2fb0400ef42 | .github/workflows/nisar-goff-timeseries-test.yml | Root exists — contract review open |
| **nisar-gunw-earthaccess-discovery-test.yml** | 3a4cac2e9a72 | .github/workflows/nisar-gunw-earthaccess-discovery-test.yml | Root exists — contract review open |
| **nisar-gunw-earthaccess-read-test.yml** | 8c9d879aad01 | .github/workflows/nisar-gunw-earthaccess-read-test.yml | Root exists — contract review open |
| **nisar-gunw-science-test.yml** | 3de36c147846 | .github/workflows/nisar-gunw-science-test.yml | Root exists — contract review open |
| **nisar-gunw-timeseries-test.yml** | 63ecf84b3498 | .github/workflows/nisar-gunw-timeseries-test.yml | Root exists — contract review open |
| **nisar-multi-granule-storage-test.yml** | 4e9ea77e0c37 | .github/workflows/nisar-multi-granule-storage-test.yml | Root exists — contract review open |
| **nisar-single-download-test.yml** | cfb86b48e127 | .github/workflows/nisar-single-download-test.yml | Root exists — contract review open |
| **retention-archive-tests.yml** | 3a81ad4c8adc | .github/workflows/retention-archive-tests.yml | Root exists — contract review open |
| **river-shift-gcov-process.yml** | 1720bc68ffb2 | .github/workflows/river-shift-gcov-process.yml | Root exists — contract review open |
| **river-shift-independent-reference-validation.yml** | adc1fd557885 | .github/workflows/river-shift-independent-reference-validation.yml | Root exists — contract review open |
| **river-shift-opera-dswx-s1-retained-replay.yml** | 4615e2f4ae82 | .github/workflows/river-shift-opera-dswx-s1-retained-replay.yml | Root exists — contract review open |
| **river-shift-run36-retrospective-replay.yml** | 7e2e6449ff7d | .github/workflows/river-shift-run36-retrospective-replay.yml | Root exists — contract review open |
| **river-shift-sentinel2-retained-replay.yml** | 79291b782a51 | .github/workflows/river-shift-sentinel2-retained-replay.yml | Root exists — contract review open |
| **river-shift-tests.yml** | d9f69946b85b | .github/workflows/snapshot-regression-tests.yml | Consolidated CI — parity review open |
| **runner-test.yml** | afba718f35d3 | — | Manual benchmark — promote/retire decision open |
| **sarguardian-aoi-code-validation.yml** | 1bbff061aae4 | .github/workflows/sarguardian-aoi-code-validation.yml | Consolidated CI — parity review open |
| **sarguardian-aoi-live-discovery-check.yml** | 30bbadd02b42 | .github/workflows/find-displacements-live-catalogue-diagnostic.yml | Renamed root port — contract review open |
| **sarguardian-aoi-product-worker.yml** | 15dc032db32a | .github/workflows/sarguardian-aoi-product-worker.yml | Root exists — contract review open |
| **sarguardian-aoi-wkt-dashboard.yml** | eabdc43e0e0b | .github/workflows/sarguardian-aoi-wkt-dashboard.yml | Root exists — contract review open |
| **sarguardian-aoi-wkt-dispatcher.yml** | 54298d915902 | .github/workflows/sarguardian-aoi-wkt-dispatcher.yml | Root exists — contract review open |
| **sarguardian-extended-science.yml** | c615376a2b73 | .github/workflows/sarguardian-extended-science.yml | Root exists — contract review open |
| **sarguardian-live-validation.yml** | e5d73c5b7301 | .github/workflows/sarguardian-live-validation.yml | Root exists — contract review open |
| **sarguardian-product-worker.yml** | 8220ed86db68 | .github/workflows/sarguardian-product-worker.yml | Root exists — contract review open |
| **sarguardian-reassemble-existing.yml** | f4cb4d515568 | .github/workflows/find-displacements-reassemble-existing.yml | Renamed root port — contract review open |
| **sarguardian-retention-ci.yml** | 6e7e46fcbaa1 | .github/workflows/snapshot-regression-tests.yml | Consolidated CI — parity review open |
| **sarguardian-retention-pilot.yml** | 1e6f1b0d3c83 | .github/workflows/find-displacements-retention-pilot.yml | Renamed root port — contract review open |
| **sarguardian-science-worker.yml** | a096ecc12f27 | — | Archived from root — legacy API/fork contract |
| **sarguardian-streaming-batch.yml** | 0215889d1447 | .github/workflows/sarguardian-streaming-batch.yml | Root exists — contract review open |

- **dashboard-assets-test.yml:** Root CI file exists with adapted content; compare asset paths, generated-output checks and branch/path filters.
- **dashboard-real-artifact-smoke.yml:** Root smoke exists; verify same-repository Preview run guard, exact run-attempt artifact identity, and no raw HDF5 replay.
- **earthdata-auth-test.yml:** Root manual auth test exists; verify secret names, token handling and redacted logs.
- **earthdata-token-smoke-test.yml:** Root manual token smoke exists; verify pinned science source and least-scope Earthdata credentials.
- **know-place-aoi-dispatcher.yml:** Root Known Place dispatcher exists with fail-closed preflight; verify original six worker-secret and request/callback contract.
- **know-place-paper-reproduction-dispatcher.yml:** Root author-exact dispatcher exists; preserve P05023, P05023 product identity, exact historical code/science pins and explicit consent.
- **nisar-discovery-test.yml:** Root manual discovery test exists; verify catalogue query and no hidden download side effects.
- **nisar-goff-timeseries-test.yml:** Root manual GOFF test exists; preserve GOFF-only semantics and exact historical science checkout provenance.
- **nisar-gunw-earthaccess-discovery-test.yml:** Root manual GUNW discovery test exists; compare Earthaccess/catalogue contract and old science source pin.
- **nisar-gunw-earthaccess-read-test.yml:** Root manual GUNW read test exists; verify remote read behavior and credential handling.
- **nisar-gunw-science-test.yml:** Root manual GUNW science test exists; ensure tests remain tied to the intended historical science revision.
- **nisar-gunw-timeseries-test.yml:** Root manual GUNW time-series test exists; verify three-acquisition/time-series constraints and no GOFF blending.
- **nisar-multi-granule-storage-test.yml:** Root storage test exists but is separately gated; verify the 15-GB storage experiment is opt-in and never part of routine CI.
- **nisar-single-download-test.yml:** Root single-download test exists; verify manual trigger, bounded download and no Drive writes unless explicitly required.
- **retention-archive-tests.yml:** The secret-free root port creates an isolated fixture tree from the immutable Backend snapshot and runs the four archive/pipeline test files, including the directly imported pinned-science helper. Current-head CI must pass before closure.
- **river-shift-gcov-process.yml:** Root GCOV workflow exists with one fail-closed preflight around the 20-job source graph; static tests pass but real GCOV, Drive receipt and signed callback round-trip remain unverified.
- **river-shift-independent-reference-validation.yml:** Root independent-reference workflow exists and remains separate from GCOV processing; verify provenance and manual-only trigger.
- **river-shift-opera-dswx-s1-retained-replay.yml:** Root retained replay exists; original push trigger must remain removed, manual-only and evidence/fixture scoped.
- **river-shift-run36-retrospective-replay.yml:** Root Run #36 replay exists; original push trigger must remain removed and replay must use retained run identity.
- **river-shift-sentinel2-retained-replay.yml:** Root Sentinel-2 replay exists; original push trigger must remain removed and cross-sensor validation must stay separate from GCOV.
- **river-shift-tests.yml:** RiverShift worker tests are executed by the promoted-engine job in Snapshot Regression Tests. Verify the full source test contract, geospatial environment, GDAL driver checks and workflow-contract assertions remain equivalent.
- **runner-test.yml:** Legacy benchmark writes a 5 GB file and allocates about 4 GB RAM. The root runner-allocation diagnostic is not equivalent. Decide whether to port behind a strict manual gate or retire with an explicit rationale; do not run as routine CI.
- **sarguardian-aoi-code-validation.yml:** A dedicated root CI workflow now tests the exact 006d parser/GOFF pin, promoted Find Displacements tools/dashboard, generated JavaScript syntax and root AOI YAML. PR #85's 10639 source variant is also tested by the same root workflow, but its branch-specific trigger/test diff remains open. The historic Backend Run-32 artifact download is not reused; a separate same-repository Dashboard Real Artifact Smoke owns that integration check.
- **sarguardian-aoi-live-discovery-check.yml:** Renamed to an isolated Find Displacements catalogue-only diagnostic. Verify WKT/date input contract, immutable science-source selection, ASF diagnostics and the new fail-closed gate; do not enable downloads or Drive writes.
- **sarguardian-aoi-product-worker.yml:** Root reusable AOI product worker exists; compare required inputs, source pin, cleanup, artifact names and failure status semantics.
- **sarguardian-aoi-wkt-dashboard.yml:** Root API-facing caller exists separately from the workflow_call engine; compare dispatch schema, callbacks, retries, artifact identity and terminal status.
- **sarguardian-aoi-wkt-dispatcher.yml:** Root manual AOI dispatcher exists; it is not interchangeable with the API-facing dashboard workflow.
- **sarguardian-extended-science.yml:** Root extended-science workflow exists; verify its historical science pin, input/output contract and manual gate.
- **sarguardian-live-validation.yml:** The new root port is manual-only and double-gated; it preserves the exact P05023 GUNW+GOFF product pair, materializes the ab547 science commit from Monorepo history, uses only promoted Find Displacements retention tools, verifies Drive receipts, and performs no automatic raw deletion. The first structural run found a validator-only quote-escaping mismatch; the check now inspects parsed shell run blocks directly. The current CI also verifies the exact ab547 Git commit object exists and all eight Backend-main retention tool/requirements blobs match the promoted Find Displacements package byte-for-byte. No live run has been dispatched.
- **sarguardian-product-worker.yml:** Root streaming reusable worker exists and remains distinct from the AOI product worker; compare inputs, outputs, retries and cleanup.
- **sarguardian-reassemble-existing.yml:** Renamed/scoped as Find Displacements retained-artifact reassembly. Verify run-ID inputs, historical artifact names, six artifact classes, pinned science revision and Drive receipt parity.
- **sarguardian-retention-ci.yml:** Snapshot Regression covers promoted engines, but exact legacy backend tests/, requirements and pinned-science-regression must be compared. Add any missing isolated retention assertions rather than assuming filename-level consolidation.
- **sarguardian-retention-ci.yml:** Both Backend main and Known Place PR #85 source variants now run their complete source `tests/` suite in a separate secret-free matrix workflow. The same workflow compiles all `tools/` and `tests/` and validates the source retention workflow YAML; the pinned-science half is covered by Snapshot Regression's imported NISAR science job.
- **sarguardian-retention-pilot.yml:** Root pilot is engine-scoped and fail-closed. Verify all source inputs, one-granule constraint, science pin, no-delete invariant and Drive receipt handling.
- **sarguardian-science-worker.yml:** Legacy worker checks out Sagormodak/SARGuardian@77cc9646..., uses WORKER_CALLBACK_SECRET and RENDER_CALLBACK_URL. Keep its exact snapshot; resolve whether its old callback/service is still required before porting or retiring. Never silently redirect it to current Vercel or moshiour0/SARGuardian.
- **sarguardian-streaming-batch.yml:** Root streaming batch exists; verify manifest, 15-at-a-time batching where applicable, failed-only retries, preassembly checks and final failure propagation.

## Known Place PR #85 workflow variants (40)

| Source workflow | Source blob | Monorepo root destination | Disposition |
|---|---|---|---|
| **dashboard-assets-test.yml** | 591e8568e6f0 | .github/workflows/dashboard-assets-test.yml | PR #85 variant — canonical selection open |
| **earthdata-auth-test.yml** | 0d6001ebb9e4 | .github/workflows/earthdata-auth-test.yml | PR #85 variant — canonical selection open |
| **earthdata-token-smoke-test.yml** | 23f8fea2706b | .github/workflows/earthdata-token-smoke-test.yml | PR #85 variant — canonical selection open |
| **know-place-analysis-reanalysis.yml** | 9d0f1fb81be9 | — | Manual research workflow — port decision open |
| **know-place-analysis-run.yml** | 2cc394e91126 | — | Author-exact research workflow — disposition open |
| **know-place-analysis-validation.yml** | c2b2888bc1c8 | .github/workflows/snapshot-regression-tests.yml | Split deterministic CI from live ASF check |
| **know-place-aoi-analysis.yml** | deb45457be51 | .github/workflows/know-place-aoi-analysis.yml | PR #85 variant — canonical selection open |
| **know-place-author-dashboard.yml** | fe3dbec37caf | — | Manual renderer — root port decision open |
| **know-place-author-exact-consent-bridge.yml** | c6e0cc8c72d6 | — | Preserve inactive — source push trigger unsafe |
| **know-place-author-exact-replay.yml** | 0b425fd118ca | .github/workflows/know-place-author-exact-replay.yml | PR #85 variant — canonical selection open |
| **know-place-author-map-render.yml** | c40c001b791a | — | Manual renderer — root port decision open |
| **know-place-dem-source-acquisition.yml** | c2cb89429b90 | .github/workflows/know-place-dem-source-acquisition.yml | PR #85 variant — canonical selection open |
| **know-place-displacement-null-audit.yml** | e7b4fc1cd097 | .github/workflows/know-place-displacement-null-audit.yml | PR #85 variant — canonical selection open |
| **know-place-generic-aoi-consent-bridge.yml** | 5b149a4e4267 | — | Preserve inactive — source push trigger unsafe |
| **know-place-generic-aoi-drive-retry.yml** | 7d9f281d1d9c | — | Drive retry — receipt/consent review open |
| **know-place-generic-map-browser-smoke.yml** | e84367af84c8 | .github/workflows/know-place-generic-map-browser-smoke.yml | PR #85 variant — canonical selection open |
| **know-place-retained-crown-audit.yml** | c1ad0e3bb883 | — | Manual research workflow — port decision open |
| **know-place-terrain-datum-sensitivity.yml** | 256797411c41 | — | Manual research workflow — port decision open |
| **nisar-discovery-test.yml** | fd5405888c26 | .github/workflows/nisar-discovery-test.yml | PR #85 variant — canonical selection open |
| **nisar-goff-timeseries-test.yml** | e2fb0400ef42 | .github/workflows/nisar-goff-timeseries-test.yml | PR #85 variant — canonical selection open |
| **nisar-gunw-earthaccess-discovery-test.yml** | 3a4cac2e9a72 | .github/workflows/nisar-gunw-earthaccess-discovery-test.yml | PR #85 variant — canonical selection open |
| **nisar-gunw-earthaccess-read-test.yml** | 8c9d879aad01 | .github/workflows/nisar-gunw-earthaccess-read-test.yml | PR #85 variant — canonical selection open |
| **nisar-gunw-science-test.yml** | 3de36c147846 | .github/workflows/nisar-gunw-science-test.yml | PR #85 variant — canonical selection open |
| **nisar-gunw-timeseries-test.yml** | 63ecf84b3498 | .github/workflows/nisar-gunw-timeseries-test.yml | PR #85 variant — canonical selection open |
| **nisar-multi-granule-storage-test.yml** | 4e9ea77e0c37 | .github/workflows/nisar-multi-granule-storage-test.yml | PR #85 variant — canonical selection open |
| **nisar-single-download-test.yml** | cfb86b48e127 | .github/workflows/nisar-single-download-test.yml | PR #85 variant — canonical selection open |
| **retention-archive-tests.yml** | 3a81ad4c8adc | .github/workflows/retention-archive-tests.yml | Root exists — contract review open |
| **runner-test.yml** | afba718f35d3 | — | Manual benchmark — promote/retire decision open |
| **sarguardian-aoi-code-validation.yml** | bc05df58d653 | .github/workflows/sarguardian-aoi-code-validation.yml | PR #85 variant — canonical selection open |
| **sarguardian-aoi-live-discovery-check.yml** | 30bbadd02b42 | .github/workflows/find-displacements-live-catalogue-diagnostic.yml | PR #85 variant — canonical selection open |
| **sarguardian-aoi-product-worker.yml** | eb2baa483366 | .github/workflows/sarguardian-aoi-product-worker.yml | PR #85 variant — canonical selection open |
| **sarguardian-aoi-wkt-dashboard.yml** | 595dff2527b0 | .github/workflows/sarguardian-aoi-wkt-dashboard.yml | PR #85 variant — canonical selection open |
| **sarguardian-aoi-wkt-dispatcher.yml** | 4b2549dbccf5 | .github/workflows/sarguardian-aoi-wkt-dispatcher.yml | PR #85 variant — canonical selection open |
| **sarguardian-live-validation.yml** | e5d73c5b7301 | .github/workflows/sarguardian-live-validation.yml | Root exists — contract review open |
| **sarguardian-product-worker.yml** | 5dbc8259f292 | .github/workflows/sarguardian-product-worker.yml | PR #85 variant — canonical selection open |
| **sarguardian-reassemble-existing.yml** | f4cb4d515568 | .github/workflows/find-displacements-reassemble-existing.yml | PR #85 variant — canonical selection open |
| **sarguardian-retention-ci.yml** | e02ca99b48a6 | .github/workflows/snapshot-regression-tests.yml | PR #85 variant — canonical selection open |
| **sarguardian-retention-pilot.yml** | 1e6f1b0d3c83 | .github/workflows/find-displacements-retention-pilot.yml | PR #85 variant — canonical selection open |
| **sarguardian-science-worker.yml** | a096ecc12f27 | — | Legacy source/callback review required |
| **sarguardian-streaming-batch.yml** | 9dfc42d715f5 | .github/workflows/sarguardian-streaming-batch.yml | PR #85 variant — canonical selection open |

- **dashboard-assets-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root CI file exists with adapted content; compare asset paths, generated-output checks and branch/path filters.
- **earthdata-auth-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root manual auth test exists; verify secret names, token handling and redacted logs.
- **earthdata-token-smoke-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root manual token smoke exists; verify pinned science source and least-scope Earthdata credentials.
- **know-place-analysis-reanalysis.yml:** Separate credentialed reanalysis workflow. Preserve only after confirming whether a distinct reanalysis capability is still needed; if promoted, remove automatic push execution and require explicit run consent.
- **know-place-analysis-run.yml:** Fixed five-pair research runner with a pinned NISAR source and push trigger. Keep as immutable evidence until exact author consent and the benchmark's current role are resolved; never activate the source push trigger.
- **know-place-analysis-validation.yml:** Contains pure-kernel tests plus live ASF catalogue contract. Keep deterministic tests in CI and move live ASF checks to a separately gated manual workflow; current engine tests alone do not prove the live half.
- **know-place-aoi-analysis.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root counterpart exists with adapted content; verify original trigger, inputs/outputs, source pins, secrets, callbacks, artifacts, retries and failure semantics.
- **know-place-author-dashboard.yml:** Separate retained-artifact dashboard renderer. Review artifact identity and source ownership; keep independent from raw acquisition and generic AOI analysis.
- **know-place-author-exact-consent-bridge.yml:** Push-triggered author-exact consent bridge. Preserve in the immutable snapshot; do not promote an automatic push trigger. Rebuild only as a manual consent-gated bridge if a real caller still requires it.
- **know-place-author-exact-replay.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root counterpart exists with adapted content; verify original trigger, inputs/outputs, source pins, secrets, callbacks, artifacts, retries and failure semantics.
- **know-place-author-map-render.yml:** Push-triggered author map renderer. Preserve source; decide whether root author-dashboard renderer replaces it. Do not promote the source push trigger.
- **know-place-dem-source-acquisition.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root counterpart exists with adapted content; verify original trigger, inputs/outputs, source pins, secrets, callbacks, artifacts, retries and failure semantics.
- **know-place-displacement-null-audit.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root counterpart exists with adapted content; verify original trigger, inputs/outputs, source pins, secrets, callbacks, artifacts, retries and failure semantics.
- **know-place-generic-aoi-consent-bridge.yml:** Push-triggered generic AOI consent bridge. Preserve exact source only; no automatic processing or Drive side effects on repository pushes.
- **know-place-generic-aoi-drive-retry.yml:** Credentialed derived-only Drive retry with a push trigger. Decide whether this capability is covered by the generic Known Place finalizer; if separately promoted, require manual consent, strict receipt identity and failed-only retry.
- **know-place-generic-map-browser-smoke.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root counterpart exists with adapted content; verify original trigger, inputs/outputs, source pins, secrets, callbacks, artifacts, retries and failure semantics.
- **know-place-retained-crown-audit.yml:** Retained-output audit. Preserve until artifact identity/retention rules and the intended operator workflow are confirmed.
- **know-place-terrain-datum-sensitivity.yml:** Credentialed terrain/vertical-datum sensitivity research. Keep manual and separate from the standard Known Place result path.
- **nisar-discovery-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root manual discovery test exists; verify catalogue query and no hidden download side effects.
- **nisar-goff-timeseries-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root manual GOFF test exists; preserve GOFF-only semantics and exact historical science checkout provenance.
- **nisar-gunw-earthaccess-discovery-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root manual GUNW discovery test exists; compare Earthaccess/catalogue contract and old science source pin.
- **nisar-gunw-earthaccess-read-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root manual GUNW read test exists; verify remote read behavior and credential handling.
- **nisar-gunw-science-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root manual GUNW science test exists; ensure tests remain tied to the intended historical science revision.
- **nisar-gunw-timeseries-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root manual GUNW time-series test exists; verify three-acquisition/time-series constraints and no GOFF blending.
- **nisar-multi-granule-storage-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root storage test exists but is separately gated; verify the 15-GB storage experiment is opt-in and never part of routine CI.
- **nisar-single-download-test.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root single-download test exists; verify manual trigger, bounded download and no Drive writes unless explicitly required.
- **retention-archive-tests.yml:** The secret-free root port creates an isolated fixture tree from the immutable Backend snapshot and runs the four archive/pipeline test files, including the directly imported pinned-science helper. Current-head CI must pass before closure.
- **runner-test.yml:** Legacy benchmark writes a 5 GB file and allocates about 4 GB RAM. The root runner-allocation diagnostic is not equivalent. Decide whether to port behind a strict manual gate or retire with an explicit rationale; do not run as routine CI.
- **sarguardian-aoi-code-validation.yml:** The PR #85 variant uses NISAR pin 10639 rather than Backend main pin 006d and has a different test/trigger set. The new root CI runs parser/GOFF-reader tests against both imported pins plus the promoted AOI tools/dashboard. The old Backend Run-32 cross-repository artifact step is replaced by the separate same-repository Dashboard Real Artifact Smoke workflow; verify this split is acceptable before closing the variant.
- **sarguardian-aoi-live-discovery-check.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Renamed to an isolated Find Displacements catalogue-only diagnostic. Verify WKT/date input contract, immutable science-source selection, ASF diagnostics and the new fail-closed gate; do not enable downloads or Drive writes.
- **sarguardian-aoi-product-worker.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root reusable AOI product worker exists; compare required inputs, source pin, cleanup, artifact names and failure status semantics.
- **sarguardian-aoi-wkt-dashboard.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root API-facing caller exists separately from the workflow_call engine; compare dispatch schema, callbacks, retries, artifact identity and terminal status.
- **sarguardian-aoi-wkt-dispatcher.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root manual AOI dispatcher exists; it is not interchangeable with the API-facing dashboard workflow.
- **sarguardian-live-validation.yml:** The new root port is manual-only and double-gated; it preserves the exact P05023 GUNW+GOFF product pair, materializes the ab547 science commit from Monorepo history, uses only promoted Find Displacements retention tools, verifies Drive receipts, and performs no automatic raw deletion. The first structural run found a validator-only quote-escaping mismatch; the check now inspects parsed shell run blocks directly. No live run has been dispatched.
- **sarguardian-product-worker.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root streaming reusable worker exists and remains distinct from the AOI product worker; compare inputs, outputs, retries and cleanup.
- **sarguardian-reassemble-existing.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Renamed/scoped as Find Displacements retained-artifact reassembly. Verify run-ID inputs, historical artifact names, six artifact classes, pinned science revision and Drive receipt parity.
- **sarguardian-retention-ci.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Snapshot Regression covers promoted engines, but exact legacy backend tests/, requirements and pinned-science-regression must be compared. Add any missing isolated retention assertions rather than assuming filename-level consolidation.
- **sarguardian-retention-pilot.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root pilot is engine-scoped and fail-closed. Verify all source inputs, one-granule constraint, science pin, no-delete invariant and Drive receipt handling.
- **sarguardian-science-worker.yml:** Legacy worker checks out Sagormodak/SARGuardian@77cc9646..., uses WORKER_CALLBACK_SECRET and RENDER_CALLBACK_URL. Keep its exact snapshot; resolve whether its old callback/service is still required before porting or retiring. Never silently redirect it to current Vercel or moshiour0/SARGuardian.
- **sarguardian-streaming-batch.yml:** Known Place PR #85 version differs from Backend main at this path. The root counterpart is an adapted workflow, not a byte-identical copy. Compare the PR #85 caller/worker fields, science pins, callbacks and output artifacts before declaring which source variant is canonical. Root streaming batch exists; verify manifest, 15-at-a-time batching where applicable, failed-only retries, preassembly checks and final failure propagation.

## Cross-cutting review requirements

1. **Canonical caller/callee choice:** Dynamic, Backend main and Known Place PR #85 have similarly named AOI workflows with different input schemas and callbacks. Compare every caller and local/external reusable callee before choosing one root contract.
2. **Historical source identity:** preserve the Sagormodak/SARGuardian, moshiour0/SARGuardian, NISAR historical refs, and Known Place author-exact b825df code pin as separate source identities. Never retarget a historical checkout solely because a Monorepo package now exists.
3. **Trigger safety:** source push-triggered research bridges and retained replays must not run because a Monorepo docs/UI commit changed. Keep acquisition, Drive, retained replays and live catalogue operations manual and fail-closed.
4. **Least privilege:** root workflows need explicit permissions; map each secret only to the job that uses it. Public-data diagnostics should not receive Earthdata, Drive or callback secrets.
5. **Failure semantics:** required worker failure must make the outer workflow fail. continue-on-error is allowed only where a later reconciliation job explicitly converts the result into the correct terminal conclusion.
6. **Artifacts and callbacks:** preserve exact artifact names, run-attempt identity, HMAC request correlation, callback ordering, Drive receipt verification and failed-only retry behavior.
7. **Live proof:** static YAML tests are not live processing proof. Do not enable dispatch flags until mock API dispatch, callback/status polling, Drive-receipt and rollback tests pass for each engine.

## First unresolved root items

- retention-archive-tests.yml: a secret-free root CI port now runs the isolated historical archive fixture suite from the byte-verified Backend source snapshot; current-head CI must pass before closure.
- runner-test.yml: intentionally archived; its 5-GB disk and ~4-GB memory benchmark has no product caller and is not routine migration CI. The root runner-allocation diagnostic retains a low-impact smoke check.
- sarguardian-live-validation.yml: root port exists with manual consent and repository opt-in gates; keep live execution disabled until the current-head structural and dry-run tests pass.
- sarguardian-science-worker.yml: intentionally archived; the old alternate-fork GOFF worker is not called by the current Vercel API's supported dispatch contracts. Its old callback is not silently redirected or adapted.
- Known Place PR #85 has ten added workflow paths without a root counterpart; each remains explicitly dispositioned above (manual port, research, renderer, consent bridge, Drive retry or archive-only).
- Workflow entries mapped to snapshot-regression-tests.yml still need parity evidence for every original test/fixture; a shared CI target is not proof of equivalence. Full Backend main and Known Place PR #85 source test suites now have a separate explicit matrix run.

## Automated enforcement

- migration/workflow-dispositions.json records all 82 source workflow instances, source blob SHAs, dispositions, root targets and a reason.
- tools/validate_workflow_dispositions.py verifies all three source snapshot directories are completely inventoried, checks every recorded Git blob SHA against the preserved bytes, confirms every declared root target exists, and checks the root workflow count.
- .github/workflows/snapshot-regression-tests.yml runs that validator on source/migration/workflow changes.

**Current disposition status:** inventory coverage is enforceable; semantic parity and production acceptance remain open. The migration is not complete until every review-required and port-required item is either validated and closed or explicitly approved as archived/retired, and all production dispatch routes are cut over with rollback.

## Backend source retention CI port

The original `sarguardian-retention-ci.yml` runs the full repository `tests/` suite, not merely the isolated HDF5 archive fixtures. The Monorepo now has `.github/workflows/backend-source-regression-tests.yml`, which runs both immutable source trees (Backend main and Known Place PR #85) in isolated matrix jobs. It compiles all `tools/` and `tests/`, installs the source-specific runtime/test dependencies, runs the complete pytest suite, and validates retention-related source workflow YAML. It uses only read-only `contents` permissions, with no Earthdata, Drive, callback or Supabase secrets. The second source workflow job (pinned NISAR science) is exercised separately by the Monorepo Snapshot Regression NISAR science job against the imported 9fcb main tree.


## Explicit archival decisions — no accidental workflow activation

Two legacy workflow families are now closed as **archive-confirmed-inactive** (their exact bytes remain in source snapshots):

- `runner-test.yml`: 5-GB disk + approximately 4-GB RAM manual stress benchmark. No product workflow or API dispatches it. The Monorepo retains the low-impact runner allocation diagnostic; the heavy benchmark stays archived unless an operator explicitly requires it later.
- `sarguardian-science-worker.yml`: alternate-fork (`Sagormodak/SARGuardian@77cc964…`) GOFF worker using `WORKER_CALLBACK_SECRET` and `RENDER_CALLBACK_URL`. The current Vercel API's displacement dispatcher contract only supports `sarguardian-aoi-wkt-dashboard.yml` or `sarguardian-displacement.yml`; the archived worker is not an active caller. It is not safe to replace its old callback URL with the Vercel URL or swap its science fork without an independent contract/science review.

The disposition validator now requires both workflow names to remain archived-only, with no declared Monorepo root workflow target.
