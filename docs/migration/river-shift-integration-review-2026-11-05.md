# RiverShift integration review — 2026-11-05

**Scope:** Monorepo RiverShift GCOV engine, FastAPI dispatch, GitHub Actions workflow, retries, private Drive storage and status reconciliation.  
**Branch:** migration/source-snapshot-import  
**Disposition:** source promotion and static contract review complete; current-head GitHub regression tests pass. The credentialed 20-job RiverShift end-to-end dry-run, signed callback/Drive receipt integration and runtime data pilot remain unverified. Production dispatch remains disabled.

## 1. Source lineage and exact promoted blobs

The current Backend main workflow and worker remain the compatibility baseline. The selected source files below were fetched from moshiour0/SARGuardian-backend main and compared with the promoted Monorepo destinations. Every listed source/promoted Git blob SHA is identical:

| RiverShift file | Source and promoted blob SHA | Result |
|---|---|---|
| tools/river_shift/process_gcov_job.py | 7e57dc2cb053128aa70833c98af036031b923ff0 | Exact |
| tools/river_shift/batched_gcov_job.py | 7e34e1b762c8d0ac3257ba5e98637a738ff4176c | Exact |
| tools/river_shift/drive_upload_adapter.py | 5a3b0be509a7a1f67f0bb98a7ca40fb7d9c6da29 | Exact |
| tools/river_shift/download_gcov_product.py | 80d21e13a5cd90b3f4f20d5095e6c27a79bef980 | Exact |
| tools/river_shift/inspect_gcov_product.py | a59bc6de683a3bc203299a84a09e17f982f6d2ee | Exact |
| tools/river_shift/export_gcov_layer.py | aece2a278a9c6c4cb5304091170b96981b4479e5 | Exact |
| tools/river_shift/discover_gcov_products.py | aa06c3cc41047d92a6a804cd8441cc30397d0fde | Exact |
| tools/river_shift/audit_gcov_acquisitions.py | 3c617f5f4850051a550e9eda8d850c1841ec6ab6 | Exact |
| tools/river_shift/environment.yml | f75182746701f28bd928ae18d39362e225af0bd4 | Exact |

The application-facing API is also an exact copy of Dynamic main at the time of source import; five high-risk source/snapshot/promoted files were separately checked in the engine-promotion report.

The source processing workflow is Backend main blob 1720bc68ffb286d22caf48e94433301c8053a1a3. The Monorepo root workflow is blob e5dc6ae68c3effba0392c3fb766f77ea5a61c1bd. They are intentionally not byte-identical: the Monorepo adds one credential-free fail-closed preflight gate, pins action references, and adapts paths to the promoted package. The source workflow's 20 job definitions remain present in the Monorepo workflow. A comparison of each job's scheduling/needs/condition/runner, max-parallel, retry-wave and selected worker/artifact contract found no unintended divergence; the only additional job is preflight.

## 2. API-to-workflow dispatch contract

The API apps/api/app/river_shift_jobs.py _dispatch function emits exactly 17 workflow_dispatch inputs. The root workflow declares the same 17 names; programmatic name-set comparison returned no missing or extra input:

- job_id
- aoi_wkt
- start_date
- end_date
- analysis_mode
- event_date
- maturity
- main_band_polarization
- flight_direction
- frame_coverage
- frequency
- covariance_term
- threshold_method
- threshold_db
- granule_names_json
- request_fingerprint
- callback_url

The API test test_dispatch_payload_includes_exact_discovery_filters asserts the complete input-key set, string typing, exact workflow URL/ref, callback URL, optional empty values, request fingerprint and granule JSON. Additional tests cover sanitized HTTP 422 messages, persistence of dispatch failure and no stuck queued job when the DISPATCHING transition cannot be stored.

The root workflow run-name is constructed as “RiverShift ” followed by the submitted job UUID. The API's _find_workflow_run matches GitHub display_title against the same value. The run ID is then bound into the HMAC callback sequence.

## 3. Processing and retry contract

The selected GCOV processing workflow has 21 jobs:
- one preflight gate added for Monorepo safety;
- one prepare job;
- four 15-product matrix jobs and four corresponding reconciliation barriers;
- three retry prepare/dispatch/product waves;
- one final retry reconciliation job;
- one final assembly/private-publication job.

The original backend workflow has 20 jobs; all 20 source job names remain in the promoted workflow. Every batch has max-parallel 15. Product selection is bounded to at most four batches (60 products), and later batch dispatch waits for the previous reconciliation barrier.

The worker and its tests establish these invariants:

1. A product runner validates immutable job/fingerprint/granule/date identity before work.
2. Each successful download produces an exact HDF5 checksum receipt and inventory. AOI COG and provenance sidecar must be present and bound to the exact downloaded source SHA-256.
3. Batch reconciliation counts successful, failed and unverifiable products. It does not block subsequent first-attempt batches merely because one product failed.
4. Retry selection contains only failed/missing/unverifiable products. Verified products are excluded and are not downloaded again.
5. There are up to three delayed retry waves, each on a fresh runner, with a maximum of 15 concurrent product jobs and staged backoff of 15/30/60 seconds.
6. Every retry wave has a distinct output/artifact namespace and a validated matrix bound to the expected wave and request. Later waves can continue after a previous product failure only when the prior retry-matrix handoff itself validated.
7. Final retry reconciliation emits a terminal failed callback if any originally failed product remains unverified or a retry handoff failed.
8. Assembly verifies the complete selected product set, every result/artifact checksum and source-provenance receipt before date mosaics and science processing.
9. The result manifest is completed before private Drive upload begins. Drive remote receipts are required before the API accepts a succeeded callback.

### Conservative workflow conclusion semantics

The workflow deliberately does not set matrix product jobs to continue-on-error. If a first-attempt product job fails but its product is subsequently recovered by a delayed retry and assembly completes, the signed application job can receive a final succeeded callback because all required products and private receipts ultimately verified; the GitHub Actions workflow run can still conclude failure because the original matrix job failed. This preserves a red run-level signal instead of hiding an inner worker failure. It is a deliberate distinction between final result-package validity and the history of the workflow attempt; it must not be rewritten to green without an explicit release-policy decision.

For unrecovered failures, the retry reconciler sends a terminal failure callback and raises a nonzero worker result; assembly is gated on successful retry reconciliation. If GitHub completes without a terminal signed callback, API polling marks the durable job failed. If no workflow run appears before the configured timeout, API polling marks the dispatch failed. Transient GitHub API polling errors leave the last durable state unchanged rather than inventing success.

## 4. Private Drive storage contract

The source worker and promoted worker both use GOOGLE_DRIVE_PARENT_FOLDER_ID, not GOOGLE_DRIVE_FOLDER_ID. Source and promoted drive_upload_adapter.py have identical blob SHA. The adapter treats the configured folder as the only parent; it creates/reuses a fixed RiverShift child folder, then a job-specific folder and output subfolders. It checks that the storage root is private, avoids overwriting a different existing scientific artifact, reuses byte-identical artifacts, verifies remote content checksums, and writes receipt information into the result manifest.

The root workflow maps:
- GOOGLE_DRIVE_OAUTH_CLIENT_JSON
- GOOGLE_DRIVE_REFRESH_TOKEN
- GOOGLE_DRIVE_PARENT_FOLDER_ID

Do not substitute the legacy Vercel API project's separate GOOGLE_DRIVE_FOLDER_ID variable; the two names belong to different consumers.

## 5. RiverShift API configuration hardening added in this review

The API already defaulted to:
- RIVERSHIFT_ACTIONS_ENABLED=false;
- repository moshiour0/SARGuardian-backend;
- workflow river-shift-gcov-process.yml;
- ref main.

This preserves current production worker routing until an explicit cutover. For production, if RiverShift is enabled, the API already required its server-side token, callback secret and HTTPS callback URL. This review adds format validation for:
- repository: owner/repository form;
- workflow: a simple .yml or .yaml filename (no path traversal);
- ref: a safe branch/ref string, rejecting .., leading/trailing slash and double slash.

New configuration tests reject unsafe repository, workflow and ref values and accept a normal slash-delimited branch such as migration/river-shift-preview. These changes are isolated to the RiverShift-enabled production validation branch; Find Displacements and Known Place defaults/validation are unchanged.

These are code and test changes only. They do not change current Vercel Production variables, enable processing, add secrets, or repoint API dispatch.

## 6. Focused test coverage currently present

The following suites were statically inspected:

| Suite | Test functions |
|---|---:|
| test_batched_gcov_job.py | 17 |
| test_workflow_retry_contract.py | 4 |
| test_validate_retry_matrix.py | 8 |
| test_process_gcov_job.py | 25 |
| Dynamic API test_river_shift_jobs.py | 28 |
| API test_config.py after the new target-validation tests | 14 |

These counts describe test functions present in the repository, not executed tests. The API suite now includes four direct workflow-status reconciliation tests: terminal GitHub success without a signed success callback becomes failed, a completed failed GitHub run fails the durable job, a dispatch timeout fails a job with no run, and a previously verified signed success is not overwritten by later run-level history. The other tests cover the batch barrier, failed-only retry, fresh runner wave, matrix identity, callback ordering/HMAC, idempotency/owner scoping, private artifact verification, dispatch target and failure-path contracts.

## 7. Validation state and release gates

The runner-allocation failures recorded in the following 2026-11-05 sections are historical and have been superseded by the current-head verification recorded below. On 2026-11-06, the Monorepo Snapshot Regression Tests completed with **17/17 jobs successful**. The RiverShift GCOV worker regression job, promoted RiverShift GCOV engine regression job, active API regression job and full source/history checks all completed their steps successfully. The minimal credential-free Runner Allocation Diagnostic also completed successfully, proving that a GitHub-hosted runner was allocated and executed shell steps.

The successful CI run does not itself execute the credentialed RiverShift 20-job processing workflow against ASF/Earthdata/Google Drive. Keep all release gates below:

- do not enable `MONOREPO_RIVERSHIFT_PROCESSING_ENABLED` until the 20-job mock/dry-run, artifact failure cases and callback contract pass;
- do not set API `RIVERSHIFT_ACTIONS_ENABLED=true` against the Monorepo until API-to-workflow request/run/status binding is tested;
- do not dispatch real GCOV downloads or copy Production secrets into Preview;
- do not promote the migration PR to production.

After CI pass, use approved non-production credentials for the signed callback, artifact and private Drive receipt integration test. Production cutover remains a separate explicit decision.


## Historical Preview deployment state — 2026-11-05 (superseded by current 2026-11-06 build)

The RiverShift API configuration-hardening change and its tests are committed in the migration branch, but the latest API Preview deployment is still older (commit 4f9ed1ad09cce1261afd5e68938bc4a12a8685cc). A direct API Preview deployment request for migration branch head 280af486a49eb42b18e0de41aaa7817a287b2591 returned Vercel HTTP 402, resource api-deployments-free-per-day, because the free API deployment allowance (>100) had been reached; Vercel indicated a 24-hour retry window. No new deployment was created. Therefore the new API config code remains unbuilt by Vercel and must not be considered deployment-verified.


## Latest validation observation — 2026-11-05

After the RiverShift API config hardening and status-polling tests, the latest PR head is 70c780d2bee11dc2a821040b4d10209ac519affa. The newest Actions attempts were still **queued** when inspected:
- Runner Allocation Diagnostic: run 42002234943 (one minimal ubuntu-latest job).
- Snapshot Regression Tests: run 42002235091 (17 regression jobs).
- Migration Metadata Validation: run 42002235044.
- Historical Secret Scan: run 42002234981.

At that observation all jobs had null runner IDs, no runner names and zero steps, but were not yet completed. This differs from the earlier immediate pre-allocation failures; it is not yet a successful runner allocation. Recheck these same run IDs before deciding whether the GitHub runner issue is resolved.

The latest API Preview code has not been deployed. Vercel rejected a direct Preview redeploy with HTTP 402 (api-deployments-free-per-day; daily free API deployment allowance exceeded). Latest inspectable API Preview remains older than the RiverShift API hardening commit. Do not treat the added config/status tests as passed or the new API code as Vercel-built until runner access and deployment quota both permit validation.


## New API regression tests and latest runner status — 2026-11-05

Four additional API tests were added for workflow status reconciliation in test_river_shift_jobs.py:
- completed GitHub run without signed success callback -> terminal failed job;
- completed GitHub run with failed conclusion -> terminal failed job;
- missing workflow run past dispatch timeout -> terminal failed job;
- previously verified signed success callback remains terminal and is not overwritten by later run-level history.

test_river_shift_jobs.py now contains 28 test functions. test_config.py contains 14. These are still unexecuted.

For API/config code head 70c780d2bee11dc2a821040b4d10209ac519affa, latest associated runs observed:
- Runner Allocation Diagnostic 42002234943: completed failure after about 43 seconds, still runner_id=0, runner_name blank and 0 steps.
- Snapshot Regression Tests 42002235091: 17 total jobs; at the latest sample, multiple jobs had failed with runner_id=0 and no steps while others remained queued, also without runner assignment.
- Migration Metadata Validation 42002235044: completed failure with runner_id=0 and no steps.
- Historical Secret Scan 42002234981: completed failure with runner_id=0 and no steps.

No test command executed. A queued job is not a passing job, and the diagnostic still does not show a runner allocation.


## Complete RiverShift package tree parity — 2026-11-05

A recursive Git tree comparison was performed between:
- Backend main commit 97d849454918b1425ac41bb70e7a32d11cfd3833, tree 867279c8de20e43dd3d36746480052dd9625d900;
- current Monorepo migration branch head dfb14062976f6266ad1f2eeeeacc2cea12968a7c, tree ad8a698804be94147924c40b51f58ff131954fda.

The entire source directory tools/river_shift/ and promoted directory engines/river-shift/tools/river_shift/ were enumerated recursively. Result:
- source blobs: 74
- promoted blobs: 74
- exact SHA + file-mode matches: 74
- missing files: 0
- extra files: 0
- changed blobs or modes: 0
- both tree responses complete (not truncated)

This upgrades the earlier selected-file spot checks to complete byte/object-and-mode parity for the entire 74-file RiverShift runtime/test/environment package. The root processing workflow remains a separate intentional adaptation: one fail-closed Monorepo preflight gate, pinned action references and path adaptation; the source's 20 processing jobs remain present. This does not execute or validate the tests.


## Workflow action pinning and secret-scope audit — 2026-11-05

The Monorepo root workflow file is blob e5dc6ae68c3effba0392c3fb766f77ea5a61c1bd. Every external action reference is pinned to a full commit SHA:

| Action | Pinned commit |
|---|---|
| actions/checkout | 3d3c42e5aac5ba805825da76410c181273ba90b1 |
| mamba-org/setup-micromamba | f457c30a868e4760d3a6fcea5f25dc655b8edf39 |
| actions/upload-artifact | cf430e030ddbb5b0abf93d22962f4752f3646cd9 |
| actions/download-artifact | 9000827ccba6bdab643e8b6fd33ac0654aef8333 |

The preflight gate has no `uses` action and no secret input. It reads only repository variable `MONOREPO_RIVERSHIFT_PROCESSING_ENABLED` and fails closed unless the value is exactly `true`. The first worker job, `prepare`, has `needs: preflight`; all later product, retry, status and assembly jobs depend transitively or directly on it.

A complete job-to-secret scan found the following scope:

| Job class | Secrets passed |
|---|---|
| `prepare` | RIVERSHIFT_CALLBACK_SECRET; EARTHDATA_TOKEN or username/password fallback; GOOGLE_DRIVE_OAUTH_CLIENT_JSON; GOOGLE_DRIVE_REFRESH_TOKEN; GOOGLE_DRIVE_PARENT_FOLDER_ID |
| First-attempt and retry product matrix jobs (15 max parallel) | EARTHDATA_TOKEN or username/password fallback only |
| Batch status jobs | RIVERSHIFT_CALLBACK_SECRET only |
| Retry reconciliation/status job | RIVERSHIFT_CALLBACK_SECRET only |
| `assemble` | RIVERSHIFT_CALLBACK_SECRET; Earthdata token/fallback; Google Drive OAuth client, refresh token and parent-folder ID |
| Retry-prepare and retry-matrix-validation jobs | No secrets |

This matches the worker call graph: prepare calls `_ensure_credentials()` before discovery to validate Earthdata configuration and private Drive parent-folder access; product runners only need Earthdata for exact granule download; status jobs only send signed callbacks; assembly validates storage again and publishes private results. This is an environment-variable scope audit, not a proof that hosted runner secrets have been configured.

The Actions event/workflow-level permissions remain read-only `contents: read`; no `GITHUB_TOKEN` write permission is requested by the root processing workflow. The external repository dispatch uses the API's separately configured server-side GitHub token, which remains pointed at the Backend main worker by default. The Monorepo root gate and worker credentials remain inactive until explicit cutover.


## Upstream action release-tag verification — 2026-11-05

The four action SHAs were queried directly against their upstream repositories and their annotated release references. All four commits exist, report GitHub commit verification reason `valid`, and each configured tag resolves to the exact commit used by the workflow:

| Upstream action | Configured tag | Configured SHA | Upstream tag match |
|---|---|---|---|
| actions/checkout | v7.0.1 | 3d3c42e5aac5ba805825da76410c181273ba90b1 | Exact |
| mamba-org/setup-micromamba | v3 | f457c30a868e4760d3a6fcea5f25dc655b8edf39 | Exact |
| actions/upload-artifact | v7.0.2 | cf430e030ddbb5b0abf93d22962f4752f3646cd9 | Exact |
| actions/download-artifact | v8.0.2 | 9000827ccba6bdab643e8b6fd33ac0654aef8333 | Exact |

The tag refs resolve to commit objects, not a different annotated-tag object SHA. This confirms the YAML comments/version labels match the actual pinned upstream commits. No action pin change was required.


## Final fresh runner recheck — 2026-11-05 09:39 UTC

The minimal credential-free diagnostic was retriggered by a one-line diagnostic-output refresh at current branch commit cf2a233b7ff1f6ed20376c8e009b9ca7a7916f86:
- Run 42004193289: completed failure in about one second; runner_id=0, runner_name blank, runner_group_id=0, zero steps.
- Run 42004181461: same minimal diagnostic on the same code/workflow head; same pre-run failure.
- Snapshot Regression run 42004193275: all 17 jobs eventually failed before runner assignment; every inspected job had runner_id=0, blank runner_name and zero steps.
- Migration Metadata run 42004193466: failed before steps with runner_id=0.
- Historical Secret Scan run 42004193489: failed before steps with runner_id=0.

This is the latest direct evidence: the platform blocker remains. The RiverShift worker, API and new tests have not executed. No additional runner retries should be spent until the repository owner confirms GitHub Actions is enabled and the account has no usage/billing restriction, or GitHub Support confirms hosted-runner provisioning is healthy. Local clone fallback was also attempted but the container could not resolve github.com, so local test execution was unavailable in this session.

The latest branch head changes only the diagnostic workflow output and audit documentation relative to the RiverShift code/test commit 70c780d2bee11dc2a821040b4d10209ac519affa; no processing code or live configuration was changed by this final recheck.


## Current-head CI and Preview confirmation — 2026-11-06

Current migration branch head: `96bcdee42b5b6871f5638dd3e41161cccc966130`.

- [Snapshot Regression Tests 42108970979](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42108970979): 17/17 jobs completed successfully. The RiverShift jobs were `RiverShift GCOV worker regression tests` and `Promoted RiverShift GCOV engine regression tests`; both executed their test steps. The active API regression job and promoted API/Web jobs also passed.
- [Runner Allocation Diagnostic 42108970973](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42108970973), [Migration Metadata Validation 42108971099](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42108971099) and [Historical Secret Scan 42108971031](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42108971031) all completed successfully.
- Vercel API Preview deployment `sar-guardian-monorepo-1zt05usqy.vercel.app` and Web Preview deployment `sar-guardian-monorepo-3rqjt3ztu.vercel.app` both reached `READY` for this exact commit. These are Preview deployments (target=null) and SSO-protected. No API health/auth/persistence/callback route smoke test is claimed.
- The API still points by default to the existing Backend worker targets. All Monorepo RiverShift processing gates remain off/unset. No NISAR GCOV product download, Drive upload, callback round-trip or real-data result was generated by this CI validation.

The next RiverShift acceptance gate is a deterministic full workflow mock/dry-run covering all 15-product batch barriers, failed-only retry waves, malformed/missing artifact receipts, callback sequencing, final nonzero failure propagation and private Drive receipt verification. A unit/regression pass must not be described as an end-to-end processing pass.
