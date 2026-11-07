# SARGuardian API → GitHub Actions dispatch cutover map

**Status:** migration wiring reference only. No runtime destination, secret, feature flag or Production alias is changed by this document.

## Separate API flows

| API flow | Runtime destination settings | Monorepo root workflow | API-level switch | Root repository Variable |
|---|---|---|---|---|
| Find Displacements | `GITHUB_ACTIONS_REPOSITORY`, `GITHUB_ACTIONS_WORKFLOW`, `GITHUB_ACTIONS_REF`, `GITHUB_ACTIONS_TOKEN`, `DISPLACEMENT_CALLBACK_SECRET`, `PUBLIC_API_URL` | `sarguardian-aoi-wkt-dashboard.yml` | `DISPLACEMENT_ACTIONS_ENABLED=false` | `MONOREPO_DISPLACEMENT_ACTIONS_ENABLED=false` |
| Known Place — generic two-polygon | `KNOWN_PLACE_GITHUB_ACTIONS_REPOSITORY`, `KNOWN_PLACE_GITHUB_ACTIONS_WORKFLOW`, `KNOWN_PLACE_GITHUB_ACTIONS_REF`, `GITHUB_ACTIONS_TOKEN` | `know-place-aoi-dispatcher.yml` | `DISPLACEMENT_ACTIONS_ENABLED=false` | `MONOREPO_KNOWN_PLACE_ACTIONS_ENABLED=false` |
| Known Place — author-exact P05023 | `KNOWN_PLACE_PAPER_GITHUB_ACTIONS_REPOSITORY`, `KNOWN_PLACE_PAPER_GITHUB_ACTIONS_WORKFLOW`, `KNOWN_PLACE_PAPER_GITHUB_ACTIONS_REF`, `GITHUB_ACTIONS_TOKEN` | `know-place-paper-reproduction-dispatcher.yml` | `DISPLACEMENT_ACTIONS_ENABLED=false` plus exact `[run-know-place]` consent | `MONOREPO_KNOWN_PLACE_PAPER_REPRODUCTION_ENABLED=false` |
| RiverShift — NISAR GCOV | `RIVERSHIFT_GITHUB_ACTIONS_REPOSITORY`, `RIVERSHIFT_GITHUB_ACTIONS_WORKFLOW`, `RIVERSHIFT_GITHUB_ACTIONS_REF`, `RIVERSHIFT_GITHUB_ACTIONS_TOKEN`, `RIVERSHIFT_CALLBACK_SECRET`, `RIVERSHIFT_PUBLIC_API_URL` | `river-shift-gcov-process.yml` | `RIVERSHIFT_ACTIONS_ENABLED=false` | `MONOREPO_RIVERSHIFT_PROCESSING_ENABLED=false` |
| Fixed P05023 live retention validation | manual `workflow_dispatch`, no API route | `sarguardian-live-validation.yml` | n/a | `MONOREPO_SARGUARDIAN_LIVE_VALIDATION_ENABLED=false` |

Known Place currently reuses the API's `DISPLACEMENT_ACTIONS_ENABLED` setting as its server-side master dispatch switch. The generic raw-download path additionally requires user consent and `MONOREPO_KNOWN_PLACE_ACTIONS_ENABLED=true`. The author-exact P05023 path has a separate `MONOREPO_KNOWN_PLACE_PAPER_REPRODUCTION_ENABLED=true` repository Variable and still requires the exact `[run-know-place]` consent marker; a closed gate fails before credentials or source acquisition. RiverShift is independent and has its own API switch/token/callback. Do not unify their payloads or callback secrets.

## Monorepo Preview destination values

For an isolated Preview-only API project:

```dotenv
GITHUB_ACTIONS_REPOSITORY=moshiour0/SARGuardian-Monorepo
GITHUB_ACTIONS_WORKFLOW=sarguardian-aoi-wkt-dashboard.yml
GITHUB_ACTIONS_REF=migration/source-snapshot-import

KNOWN_PLACE_GITHUB_ACTIONS_REPOSITORY=moshiour0/SARGuardian-Monorepo
KNOWN_PLACE_GITHUB_ACTIONS_WORKFLOW=know-place-aoi-dispatcher.yml
KNOWN_PLACE_GITHUB_ACTIONS_REF=migration/source-snapshot-import

KNOWN_PLACE_PAPER_GITHUB_ACTIONS_REPOSITORY=moshiour0/SARGuardian-Monorepo
KNOWN_PLACE_PAPER_GITHUB_ACTIONS_WORKFLOW=know-place-paper-reproduction-dispatcher.yml
KNOWN_PLACE_PAPER_GITHUB_ACTIONS_REF=migration/source-snapshot-import

RIVERSHIFT_GITHUB_ACTIONS_REPOSITORY=moshiour0/SARGuardian-Monorepo
RIVERSHIFT_GITHUB_ACTIONS_WORKFLOW=river-shift-gcov-process.yml
RIVERSHIFT_GITHUB_ACTIONS_REF=migration/source-snapshot-import
```

Use the API Preview's public HTTPS origin for `PUBLIC_API_URL` and `RIVERSHIFT_PUBLIC_API_URL`. The GitHub PAT stays in the API project only. `GITHUB_ACTIONS_TOKEN` needs permission to dispatch workflows in the Monorepo; RiverShift may use a separately scoped `RIVERSHIFT_GITHUB_ACTIONS_TOKEN`. Never put tokens or callback secrets in Web/Vite variables.

## Displacement schema — do not mix the wrappers

The API deliberately supports two different workflow schemas:

- `sarguardian-aoi-wkt-dashboard.yml` receives the Backend dashboard contract: `job_id`, `aoi_wkt`, `start_date`, `end_date`, `callback_url`, `request_fingerprint`, `date_filter_mode`, `run_profile`, `retention_profile`, and optional map/target context.
- `sarguardian-displacement.yml` is the legacy Dynamic wrapper and receives `product_type`, `acquisition_window`, `retention_mode`, and `processing_profile` in addition to shared fields.

The Monorepo root contains `sarguardian-aoi-wkt-dashboard.yml`; it does **not** contain `sarguardian-displacement.yml`. The Monorepo API Preview must target the former. Sending Dynamic-wrapper input names to the Backend dashboard workflow causes GitHub to reject the dispatch with HTTP 422.

## Workflow-side Actions Secrets

- Earthdata: `EARTHDATA_TOKEN` or `EARTHDATA_USERNAME` + `EARTHDATA_PASSWORD`.
- Private Google Drive uploads: `GOOGLE_DRIVE_OAUTH_CLIENT_JSON`, `GOOGLE_DRIVE_REFRESH_TOKEN`, `GOOGLE_DRIVE_PARENT_FOLDER_ID`.
- Find Displacements / Known Place signed worker callback: `DISPLACEMENT_CALLBACK_SECRET`.
- RiverShift signed callback: `RIVERSHIFT_CALLBACK_SECRET`.

The canonical Drive parent-folder variable is `GOOGLE_DRIVE_PARENT_FOLDER_ID`. The promoted API upload config rejects the legacy `GOOGLE_DRIVE_FOLDER_ID` name; do not add that variable to Vercel or Actions.

## Safe staging and cutover sequence

1. The Monorepo repository is intentionally **Public** by owner approval. This is not a migration blocker; keep every secret value outside Git history and in server-side Vercel/Actions secret stores only.
2. Configure separate Vercel API/Web Preview projects. Only the API project receives Firebase Admin, Supabase service key, GitHub token and Drive result-read OAuth values.
3. Add repository Actions Secrets and Variables to the Monorepo; keep every processing Variable false.
4. Run API mock-dispatch/HTTP 422 tests, signed callback verification, request/run correlation, failure polling, private Drive receipt checks and duplicate-dispatch tests.
5. Run catalogue-only or other non-destructive dry runs. Do not enable raw downloads or Drive writes merely because static CI passes.
6. Rehearse one isolated product/job per engine with explicit consent and rollback, then request independent science review.
7. Only after all acceptance gates and explicit owner approval: merge the Draft PR, deploy reviewed Vercel Production projects, set API repository/ref values to `main`, and update repository Variables. Do not retarget Production before that approval.

All API and root workflow processing switches remain disabled. A CI PASS is not a live dispatch test or independent scientific validation.


## Verified Known Place source lineage and current runtime pins — 2026-11-06

The feat/know-place-analysis branch itself was not merged into Backend main. PR #85 remains Draft/Open, with base feat/know-place-analysis (bd7a59c...) and head bfde7dde.... This does not mean Known Place is absent from the current application path: Backend main's generic dispatcher pins the reusable analysis workflow and backend_science_ref to 0e0611c12913044787ee84a39fa60a81d30ae516.

The filtered Backend workflow-dispatch history shows current generic Known Place dispatch usage (the first page returned 16 generic runs, 8 successful). Successful runs 41533701551 and 41533582770 used the 0e061 reusable workflow and retained result artifacts. The Monorepo generic API target is therefore a current runtime flow, not an unused research branch. The Monorepo engine package applies the ten exact runtime/test blobs from 0e061 recorded in migration/active-runtime-pins/known-place-generic-0e061.json.

PR #86 merged only the GOFF candidate handoff to main; it did not merge PR #85's two-polygon science implementation. Keep the author-exact P05023 path separate: Backend main dispatcher → reusable workflow d847b0461a2fec1bdf2abcce0a6b1d2f9dddabc9 → Backend code b825df798ea4cb9874aa10dd01174d2a8ef73cba. The observed author-exact run 41423614257 failed its final source-manifest/cleanup/science acceptance; its Monorepo gate remains false.
