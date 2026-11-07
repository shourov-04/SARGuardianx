# Deployment and secret migration constraints

**Purpose:** map configuration requirements without copying secret values.

## Deployment ownership

- Current web/API hosting is Vercel according to the project handoff.
- Do not treat historical `render.yaml` in backend source as proof that Render is still used.
- Dynamic has separate frontend and API Vercel configuration. Verify project Root Directory, build command, output directory, function settings, environment scopes, and production branch before changing paths.
- Keep production alias and callback destinations unchanged until preview passes.
- RiverShift map search uses Google Places autocomplete; verify Places API (New) is enabled for the Google Cloud project associated with the browser key.

## Configuration categories

Secret values must remain in GitHub/Vercel secret stores and must never be committed here.

| Category | Examples | Handling |
|---|---|---|
| Frontend public config | Firebase web config, Google Maps browser key, backend URL | Vite-prefixed public variables only when intended for browser exposure |
| API identity | Firebase Admin service-account JSON | Server-side only; never place in Vite env |
| Supabase | Project URL, service-role key | Service-role key server-side only; preserve RLS and persistence |
| GitHub Actions | Fine-grained token, dispatch repository/workflow/ref | Minimum required repository and Actions permissions |
| Callbacks | Displacement and RiverShift callback URLs/secrets | Preserve auth contracts; never log secret values |
| ASF/Drive | ASF catalogue and Drive credentials | Server/Actions only; verify cleanup and remote receipt semantics |

## Exact-name compatibility

Preserve existing variable names until every consumer is mapped. In particular, backend Actions has an existing variable named `Google drive parent folder id`. Do not silently replace it with `GOOGLE_DRIVE_FOLDER_ID` or introduce a second parent-folder variable.

Never place service-account JSON, Firebase Admin JSON, PATs, API keys, Supabase service-role keys, callback secrets, or signed URLs in Git commits, sample files, Actions logs, PR descriptions, artifacts, or issue comments.

## Live API dispatch contract — preserve during Preview

The active Dynamic API is configured to dispatch processing into `moshiour0/SARGuardian-backend@main`:

| API path | Current repository/workflow/ref | Contract |
|---|---|---|
| Find Displacements | `moshiour0/SARGuardian-backend` / `sarguardian-aoi-wkt-dashboard.yml` / `main` | `GITHUB_ACTIONS_REPOSITORY`, `GITHUB_ACTIONS_WORKFLOW`, `GITHUB_ACTIONS_REF`; signed displacement callback to `PUBLIC_API_URL` |
| RiverShift | `moshiour0/SARGuardian-backend` / `river-shift-gcov-process.yml` / `main` | `RIVERSHIFT_GITHUB_ACTIONS_REPOSITORY`, `RIVERSHIFT_GITHUB_ACTIONS_WORKFLOW`, `RIVERSHIFT_GITHUB_ACTIONS_REF`; signed RiverShift callback to `RIVERSHIFT_PUBLIC_API_URL` |
| Known Place two-polygon | Compatibility default: `moshiour0/SARGuardian-backend` / `know-place-aoi-dispatcher.yml` / `main` | API reads `KNOWN_PLACE_GITHUB_ACTIONS_REPOSITORY`, `KNOWN_PLACE_GITHUB_ACTIONS_WORKFLOW`, `KNOWN_PLACE_GITHUB_ACTIONS_REF`; defaults preserve current Backend dispatcher; Monorepo cutover only after root workflow validation |
| Known Place author-exact P05023 | Compatibility default: `moshiour0/SARGuardian-backend` / `know-place-paper-reproduction-dispatcher.yml` / `main` | API independently reads `KNOWN_PLACE_PAPER_GITHUB_ACTIONS_REPOSITORY`, `KNOWN_PLACE_PAPER_GITHUB_ACTIONS_WORKFLOW`, `KNOWN_PLACE_PAPER_GITHUB_ACTIONS_REF`; exact author/product/code pin remains independently enforced |

The Vercel Production environment inventory confirms Displacement and RiverShift Actions are enabled and both currently target backend `main`; the public callback API domain remains the existing `sarguardian-backend-api.vercel.app`. The current frontend Production and Preview `VITE_SARGUARDIAN_API_URL` both target that API. This is the operational baseline—not a target Monorepo route.

## Monorepo Known Place two-polygon candidate — not cut over

The migration branch now contains two separate root workflows:

- `.github/workflows/know-place-aoi-dispatcher.yml`: manual `workflow_dispatch` entrypoint used by the API. It sets `run-name: Known Place Analysis {request_id}`, so API status polling can bind the exact request.
- `.github/workflows/know-place-aoi-analysis.yml`: local `workflow_call` reusable workflow. It checks out the exact caller commit and verifies the imported Known Place runner/requirements Git blob SHAs.

The dispatcher/reusable pair is not active in Production while it remains only in the migration branch. The current API defaults remain the original Backend dispatcher. The author-exact P05023 workflow remains separate and continues to target its existing Backend dispatcher; it must not be redirected to the generic two-polygon workflow.

Before changing the API's generic Known Place variables to the Monorepo dispatcher, all of the following are required:

1. Merge the canonical two-job dispatcher and reusable workflow to the default `main` branch and obtain a successful current-head regression run, including `tools/validate_known_place_workflow_contract.py`.
2. Give the API's server-side GitHub token Actions **read and write** access to `moshiour0/SARGuardian-Monorepo`. It must dispatch the workflow, poll its run, list the artifact, and download the artifact for API result retrieval.
3. Add these server-side Actions secrets in the Monorepo: `EARTHDATA_TOKEN` (or `EARTHDATA_USERNAME` plus `EARTHDATA_PASSWORD`), `GOOGLE_DRIVE_OAUTH_CLIENT_JSON`, `GOOGLE_DRIVE_REFRESH_TOKEN`, and `GOOGLE_DRIVE_PARENT_FOLDER_ID`. Keep the Drive parent ID variable name unchanged; do not introduce `GOOGLE_DRIVE_FOLDER_ID`.
4. Keep repository variable `MONOREPO_KNOWN_PLACE_ACTIONS_ENABLED` unset/false during dry-run testing. Catalog-only dry runs are permitted without this variable; raw HDF5 downloads and Drive upload require it to be exactly `true`, plus the user's explicit raw-download consent marker and credential preflight.
5. Validate a manual catalog-only run, API request-ID/status matching, artifact prefix/digest retrieval, derived-only Drive receipt, and rollback to the existing Backend dispatcher before any production API environment change.

The API cutover values, when separately approved, are:

```
KNOWN_PLACE_GITHUB_ACTIONS_REPOSITORY=moshiour0/SARGuardian-Monorepo
KNOWN_PLACE_GITHUB_ACTIONS_WORKFLOW=know-place-aoi-dispatcher.yml
KNOWN_PLACE_GITHUB_ACTIONS_REF=main
```

Do not set these on Production now. The paper-reproduction `KNOWN_PLACE_PAPER_GITHUB_ACTIONS_*` variables remain independent.

**Cutover rule:** the Monorepo Preview must initially use the existing backend dispatch targets and existing Supabase project. Do not point production or Preview dispatches at Monorepo root workflows until the new workflow copies, payload schemas, callback signatures, result artifacts, retries, and retention behavior are validated together. Change the API environment and worker ownership in one controlled cutover with a rollback route; do not switch only one side.

## Required pre-cutover evidence

- Current Vercel project IDs and root directories are recorded.
- Frontend/API variable names are mapped by Development/Preview/Production.
- Workflow secrets/variables are mapped by source repository and consumer.
- No secret value was copied or exposed in the monorepo.
- Supabase project ID, schema ownership, RLS, retention, and migration history are verified.
- Callback URLs and signatures are exercised in preview/mock mode.
- Rollback to current Vercel deployment and old workflow dispatchers is tested.
