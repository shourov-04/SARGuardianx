# API to GitHub Actions dispatch cutover map

**Audit date:** 2026-11-05  
**Current behavior:** the Dynamic API remains the live dispatcher; the Monorepo root has no operational processing workflows enabled.

## 1. Find Displacements

### Current API adapter

`apps/api/app/displacements.py` chooses the exact workflow_dispatch input schema from:
- `GITHUB_ACTIONS_REPOSITORY`;
- `GITHUB_ACTIONS_WORKFLOW`;
- `GITHUB_ACTIONS_REF`.

For the current Production Vercel configuration:
- repository: `moshiour0/SARGuardian-backend`;
- workflow: `sarguardian-aoi-wkt-dashboard.yml`;
- ref: `main`;
- dispatch enabled: `true`.

The input mapping for `sarguardian-aoi-wkt-dashboard.yml` uses `request_fingerprint`, `date_filter_mode`, `run_profile`, and `retention_profile`. The Dynamic wrapper workflow has a different schema (`product_type`, `acquisition_window`, `retention_mode`, `processing_profile`). These are intentionally not interchangeable: GitHub returns HTTP 422 for undeclared workflow inputs.

### Target contract

Promote the backend AOI dashboard workflow and its reusable worker chain into the root workflow directory only after:
- exact checkout revisions are internalized or pinned;
- required artifact names and retention are preserved;
- callback sequence and HMAC verification remain unchanged;
- GOFF and GUNW diagnostics stay separate;
- the API input mapping is tested against the new workflow's actual `workflow_dispatch.inputs`.

Do not change Production `GITHUB_ACTIONS_REPOSITORY` or `GITHUB_ACTIONS_WORKFLOW` during this phase.

## 2. Known Place Analysis

### Current API adapter

`apps/api/app/known_place.py` currently pins:
- generic two-polygon dispatcher: `moshiour0/SARGuardian-backend/.github/workflows/know-place-aoi-dispatcher.yml@main`;
- fixed author-exact benchmark dispatcher: `moshiour0/SARGuardian-backend/.github/workflows/know-place-paper-reproduction-dispatcher.yml@main`.

These constants are intentionally separate from Find Displacements. The Known Place engine implementation is sourced from backend PR #85 head `bfde7dde8ada92a03054cd8dbad8daa7a5c119f8`, not backend main. The dispatcher files are present in backend main, while the expanded research implementation and branch-specific workflows are in PR #85 lineage.

### Target contract

The Monorepo must contain:
- the generic dispatcher with its original input names;
- the author-exact P05023 replay with explicit consent and source/product identity checks;
- the PR #85 Known Place code/tests and required evidence files;
- the two-polygon Measurement/Reference contract and cleanup-after-remote-receipt behavior.

Before switching the API constants, add tests for both workflow dispatch schemas and run them against the root workflows. Keep the author-exact replay manual/consent-gated; do not activate its PR #85 push-triggered workflow variants unchanged.

## 3. River Shift

### Current API adapter

`apps/api/app/river_shift_jobs.py` dispatches to configured:
- repository: `RIVERSHIFT_GITHUB_ACTIONS_REPOSITORY`;
- workflow: `RIVERSHIFT_GITHUB_ACTIONS_WORKFLOW`;
- ref: `RIVERSHIFT_GITHUB_ACTIONS_REF`;
- callback base: `RIVERSHIFT_PUBLIC_API_URL`.

Current Production values target `moshiour0/SARGuardian-backend`, `river-shift-gcov-process.yml`, and `main`. RiverShift dispatch is enabled independently from Find Displacements.

The root GCOV workflow must preserve its 20-job graph, 15-product batches, status barriers, up to three retry waves, failed-only retries, callbacks, artifact names, Drive receipt verification, and final failure propagation.

### Target contract

Before switching the repository/ref:
- copy the full workflow and every called worker/reassembly script to Monorepo root/engine paths;
- internalize any external source pins that must no longer check out the old repository;
- validate all dispatch inputs and maximum GitHub input size;
- run synthetic failure cases proving successful product IDs are never retried;
- test signed callback order and missing-callback terminal failure;
- keep RiverShift independent from GOFF/GUNW processing.

## 4. Dispatch cutover sequence

1. Keep old Vercel API and original backend workflows live.
2. Build Monorepo root workflows under a migration-only branch with no production triggers.
3. Use a dedicated Preview API environment and a migration-only Actions token to invoke dry-run/mock workflows.
4. Test each dispatch schema, callback signature, status polling, cancellation, retry, Drive receipt, and final error state.
5. Switch one engine at a time only after its tests are green; preserve the old workflow path and rollback config.
6. Do not enable old and new production workers for the same request.
7. Change Vercel Production environment values only after Preview success and explicit cutover approval.

## 5. Secret/config mapping (names only)

| Consumer | Current configuration names | Destination rule |
|---|---|---|
| Displacement API | `GITHUB_ACTIONS_TOKEN`, `GITHUB_ACTIONS_REPOSITORY`, `GITHUB_ACTIONS_WORKFLOW`, `GITHUB_ACTIONS_REF`, `DISPLACEMENT_CALLBACK_SECRET`, `PUBLIC_API_URL` | New Preview-only names/secrets; do not alter Production yet |
| Known Place API | Uses the shared server Actions token, but workflow/repository/ref constants are in `known_place.py` | Make repository/ref configurable only when tests verify generic and author-exact dispatch separately |
| RiverShift API | `RIVERSHIFT_GITHUB_ACTIONS_TOKEN`, `RIVERSHIFT_GITHUB_ACTIONS_REPOSITORY`, `RIVERSHIFT_GITHUB_ACTIONS_WORKFLOW`, `RIVERSHIFT_GITHUB_ACTIONS_REF`, `RIVERSHIFT_CALLBACK_SECRET`, `RIVERSHIFT_PUBLIC_API_URL` | Separate Preview token/callback; keep enabled/disabled control independent |
| Workers/Drive | Earthdata, Drive OAuth, and existing Google Drive parent folder setting | Preserve backend Actions variable spelling `Google drive parent folder id`; never place its value in Git |

No secret values are committed or displayed in this map.
