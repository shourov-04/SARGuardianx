# Active API — Monorepo operations runbook

This FastAPI service provides the frontend's metadata-only archive preflight.
It queries the official ASF Search API for NISAR `GUNW` and `GOFF` metadata only. It does not
download satellite data, run scientific processing, or fabricate catalogue products.
Set `ASF_CATALOG_ENABLED=false` to disable the adapter; otherwise valid searches use the real
ASF endpoint and return `ready` or `no_data`.

## Setup

Use Python 3.11+ in this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

During local development, the API loads `apps/api/.env` through `python-dotenv`.
Existing host environment variables take precedence. Set `APP_ENV=production` in a
hosted environment; production skips local dotenv loading and requires hosting-provided
environment variables, including an explicit `CORS_ORIGINS` value.

Configure Firebase Admin with Application Default Credentials or a server-only
`GOOGLE_APPLICATION_CREDENTIALS` path. On Vercel, use the server-only
`FIREBASE_SERVICE_ACCOUNT_JSON` environment variable instead; it contains the full JSON
object supplied by the hosting environment and is parsed in memory. Do not commit its value,
print it in logs, or place service-account credentials in `Frontend/`
or any `VITE_*` variable. The frontend sends a Firebase ID token as `Authorization: Bearer ...`.
Set `APP_ENV=production` and an explicit comma-separated `CORS_ORIGINS` allowlist in production;
the server refuses to start in production without that allowlist. `PORT` is honored for hosting
platforms and defaults to `8000` locally.

For durable jobs, set `SUPABASE_URL` and the server-only `SUPABASE_SERVICE_ROLE_KEY`.
That variable may contain either a modern opaque `sb_secret_...` key or a legacy
`service_role` JWT. Modern keys are sent to Supabase as `apikey` and are never used
as `Authorization: Bearer ...`; the Firebase ID token remains the separate client
authentication credential.
There is no in-memory fallback: missing values produce a safe configuration error. Apply
`supabase/migrations/20261017143644_processing_jobs.sql` to the Supabase project before enabling job creation.
Supabase does not automatically treat Firebase identities as Supabase Auth identities. The
backend verifies Firebase first and filters every persistence operation by that verified UID;
the SQL RLS policies are defense-in-depth for a future Supabase JWT integration.
The manual, approval-gated staging procedure is documented in
[`STAGING_MIGRATION_RUNBOOK.md`](STAGING_MIGRATION_RUNBOOK.md). It explicitly warns against
selecting the old paused project and does not authorize this local environment to contact
Supabase.

## Safe local configuration preflight

Do not commit `apps/api/.env`. Create it manually from `apps/api/.env.example` only after
obtaining staging values. The current code expects these names:

- `APP_ENV` (`development` locally; `production` on a host)
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` (the server-only modern secret API key, or a legacy service-role JWT)
- `GOOGLE_APPLICATION_CREDENTIALS` (local file path, optional when Application Default Credentials are configured)
- `FIREBASE_SERVICE_ACCOUNT_JSON` (Vercel-only full JSON secret, parsed in memory)
- `ASF_CATALOG_ENABLED`, `ASF_SEARCH_URL`, `ASF_MAX_RESULTS`, and `ASF_TIMEOUT_SECONDS`
- `CORS_ORIGINS` (comma-separated origins; required in production)
- `PREFLIGHT_TTL_SECONDS` (60 through 604800 seconds)
- `DISPLACEMENT_ACTIONS_ENABLED`, `GITHUB_ACTIONS_TOKEN`, `GITHUB_ACTIONS_REPOSITORY`, `GITHUB_ACTIONS_WORKFLOW`, `GITHUB_ACTIONS_REF`, `DISPLACEMENT_CALLBACK_SECRET`, and `PUBLIC_API_URL` for durable scientific-processing dispatch
- `KNOWN_PLACE_GITHUB_ACTIONS_REPOSITORY`, `KNOWN_PLACE_GITHUB_ACTIONS_WORKFLOW`, and `KNOWN_PLACE_GITHUB_ACTIONS_REF` for the generic two-polygon workflow
- `KNOWN_PLACE_PAPER_GITHUB_ACTIONS_REPOSITORY`, `KNOWN_PLACE_PAPER_GITHUB_ACTIONS_WORKFLOW`, and `KNOWN_PLACE_PAPER_GITHUB_ACTIONS_REF` for the separate author-exact P05023 workflow
- Known Place worker-side GitHub Actions secrets: `EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD` or `EARTHDATA_TOKEN`, `GOOGLE_DRIVE_OAUTH_CLIENT_JSON`, `GOOGLE_DRIVE_REFRESH_TOKEN`, and `GOOGLE_DRIVE_PARENT_FOLDER_ID`
- API-side server secrets: `GITHUB_ACTIONS_TOKEN` must have Actions read/write access to each configured Known Place repository so the API can dispatch the workflow, poll its exact run, list its artifact, and download the artifact. The API does **not** need the worker's Google Drive OAuth credentials to retrieve the current GitHub Actions result artifact.
- `PORT` (optional; defaults to 8000)

Manual setup:

1. Copy `apps/api/.env.example` to `apps/api/.env` locally; do not commit the copy.
2. Set `APP_ENV=development` and the staging `SUPABASE_URL`.
3. Put the modern server-only Supabase secret key in `SUPABASE_SERVICE_ROLE_KEY`.
4. Set either `GOOGLE_APPLICATION_CREDENTIALS` to a local server-side credential path, or configure Application Default Credentials. Do not put the credential JSON in this repository.
5. Set `ASF_CATALOG_ENABLED` deliberately, review `CORS_ORIGINS`, and keep `PREFLIGHT_TTL_SECONDS` within its supported range.
6. From `apps/api`, run the non-networking diagnostic:

```powershell
python -m app.config_diagnostic
```

The diagnostic reports only variable names and shape/status messages. It does not initialize
Supabase or Firebase, contact ASF or Supabase, apply migrations, print values or key prefixes,
or read the Firebase credential file. It exits with code 0 only when all checks pass. The
Supabase secret is an API key for the server-side `apikey` header; it is not a Firebase token
and is never the end-user `Authorization: Bearer` credential.

## Known Place workflow routing

Known Place has two independent GitHub Actions destinations. The generic two-polygon analysis uses
`KNOWN_PLACE_GITHUB_ACTIONS_REPOSITORY`, `KNOWN_PLACE_GITHUB_ACTIONS_WORKFLOW`, and
`KNOWN_PLACE_GITHUB_ACTIONS_REF`. The author-exact P05023 reproduction uses the corresponding
`KNOWN_PLACE_PAPER_GITHUB_ACTIONS_*` variables. The defaults in `.env.example` deliberately
retain the existing Backend dispatchers. Set either destination to Monorepo root workflows only
after the matching workflow is promoted, its inputs/status/artifacts are contract-tested, and the
coordinated production cutover is approved. Do not point author-exact reproduction at the generic
workflow or substitute the author-pinned product/code revision.

## Known Place result storage and retrieval

For a raw-download run, the GitHub Actions worker builds a derived-only ZIP and uploads it to the configured
private Google Drive parent folder using `GOOGLE_DRIVE_PARENT_FOLDER_ID`. It then writes a receipt containing
the Drive folder/file IDs, local SHA-256 and a SHA-256 recomputed from bytes downloaded back from Drive.
Raw HDF5 source files and credentials are excluded from that retained bundle.

The API's current result adapter is a separate path: it locates the exact completed GitHub Actions run by
the opaque request UUID in the run title, downloads the run's GitHub Actions artifact with the server-side
`GITHUB_ACTIONS_TOKEN`, and validates `result.json`, the generated dashboard/map HTML, and the optional
Drive receipt. The API's authenticated bundle endpoint returns that same bounded Actions artifact to the
signed-in browser. It does not currently call the Google Drive API directly; do not add Drive OAuth
credentials to the Vercel API unless a separately reviewed Drive-backed retrieval implementation is added.

Keep the GitHub Actions worker secrets in the repository that runs the Known Place worker. The Vercel API
needs its own server-side GitHub token with Actions read/write permissions on the configured dispatcher
repository, plus the existing Firebase Admin and Supabase server-only settings. No Google Drive token,
OAuth client JSON or parent-folder ID belongs in a browser-visible `VITE_*` variable.


## Vercel deployment preparation

The Monorepo uses two separate Vercel projects:

- Web project root: `apps/web/`; Vite build command `npm run build`; output directory `dist`.
- API project root: `apps/api/`; Python/FastAPI runtime with `apps/api/index.py` as the entrypoint.

The isolated Monorepo Preview projects have been created and the initial Web and API builds
completed successfully from `migration/source-snapshot-import`. Preview has no production
Supabase/Firebase/Google Drive/GitHub credentials, and processing dispatch is disabled there.
The Preview is therefore a build and routing checkpoint, not yet an authenticated end-to-end
processing environment. Those deployments are pinned to earlier migration commits; a fresh
Preview build of the current branch head remains blocked by the Vercel account's deployment
rate limit and must be refreshed before UI/API integration is accepted.

Before production cutover, configure the Preview/Production environment variables from
`.env.example` and `../docs/operations/deployment-and-secret-map.md` using the appropriate
server-side secrets. Never put Firebase Admin credentials, Supabase service-role keys, GitHub
tokens, Drive OAuth credentials, or callback secrets in browser-visible `VITE_*` variables.

Supabase SQL files are retained under `../../infrastructure/supabase/migrations/`. The remote
migration-history inventory currently has naming/version drift against the local files. Do not
run `db push`, replay migrations, or alter the live schema until a read-only reconciliation
proves which versions are already applied and a backup/rollback plan is approved.

## Run

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health: `GET http://localhost:8000/health`
Catalogue preflight: `POST http://localhost:8000/api/catalog/search`
Create confirmed queued job: `POST http://localhost:8000/api/jobs`
List current user's jobs: `GET http://localhost:8000/api/jobs`
Inspect current user's job: `GET http://localhost:8000/api/jobs/{job_id}`

The adapter uses ASF's public `services/search/param` endpoint with a WKT `intersectsWith`
polygon, `platform=NISAR`, `processingLevel=GUNW` or `GOFF`, UTC `start`/`end`,
`output=jsonlite`, and a bounded `maxResults` cap. ASF's response has no continuation token;
when the cap is reached, the response sets `truncated=true` and asks the caller to narrow the
search. Catalogue search is read-only and does not require Earthdata download credentials.

## Request

```json
{
  "coordinates": [[85.3, 27.7], [85.301, 27.7], [85.301, 27.701], [85.3, 27.7]],
  "start_date": "2026-08-01",
  "end_date": "2026-08-15",
  "product_type": "GUNW"
}
```

The endpoint validates a closed WGS84 longitude/latitude polygon, positive area, the 1,000 km2
AOI limit, date order, the 90-day limit, and `GUNW`/`GOFF` product types before the adapter
is called. Results preserve actual ASF granule names, product types, dates, direction, path,
processing level, and size metadata where ASF provides them. Missing metadata remains absent.

`POST /api/displacement-jobs` creates an authenticated durable processing request. It stores
an immutable AOI/date/product/window/retention/profile snapshot plus selected place context and
optional in-AOI target coordinates. The target is accepted only when its WGS84 point lies within
the exact submitted polygon and is bound into the request fingerprint. Place context is not a
measurement, and the target is not a stable reference point: cumulative time-series inversion
remains blocked unless the science workflow proves a compatible common datum across the connected
acquisition network. The workflow is dispatched only when server-side Actions settings are enabled,
and completion is accepted only from the bound signed worker callback. Normal catalog preflight
remains metadata-only.

## Tests

```powershell
python -m pytest
```
