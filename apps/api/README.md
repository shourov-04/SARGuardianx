# SARGuardian API — Monorepo

This is the active FastAPI service promoted to `apps/api/`. The current Production Dynamic API and its existing Backend Actions targets remain authoritative until an independently approved cutover. The Monorepo API is a separate Vercel project; this guide does not configure Render or change Production routing.

## Local setup

Run from the repository root:

```bash
cd apps/api
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health endpoint: `GET /health`.

API regression tests:

```bash
cd apps/api
python -m pytest -q
node --test tests/google_maps_dashboard_adapter.test.mjs
```

Do not commit `.env`, Firebase service-account JSON, Supabase service keys, GitHub tokens, Google Drive OAuth values, Earthdata credentials or callback secrets.

## Vercel deployment

Create a separate Vercel project for `apps/api/` and set its Root Directory to `apps/api`. The FastAPI entry point is `index.py`; dependencies are installed from `requirements.txt`. Use Vercel Preview for migration acceptance and keep Production aliases untouched.

The Web project is separate at `apps/web/`. The API's `CORS_ORIGINS` must explicitly include the Web Preview origin for a browser smoke test. Vercel Preview deployments are SSO-protected in this migration.

## Authentication and persistence

- Firebase Admin uses Application Default Credentials locally or the server-only `FIREBASE_SERVICE_ACCOUNT_JSON` value on Vercel. Never put Firebase Admin credentials in Web variables or `VITE_*` values.
- The API uses `SUPABASE_URL` and server-only `SUPABASE_SERVICE_ROLE_KEY`. The service key must never enter the Web project, source control, Actions logs or client responses.
- The Monorepo staging Supabase project is documented in `../../docs/migration/supabase-target.md`; migration history and outstanding version/name reconciliation are documented in `../../docs/migration/supabase-migration-lineage.md`.
- Do not run `supabase db push`, replay historical migrations or reset the project as a shortcut. Follow the migration lineage review first.

The API verifies Firebase identity before every owner-scoped job read/write. Supabase is not treated as the Firebase identity provider.

## Google Drive result access

The API reads an existing private result file using its Drive file ID and receipt. Its runtime needs `GOOGLE_DRIVE_OAUTH_CLIENT_JSON` and `GOOGLE_DRIVE_REFRESH_TOKEN`.

The processing workflow that creates folders or uploads files additionally needs the Actions secret `GOOGLE_DRIVE_PARENT_FOLDER_ID`. The canonical variable is `GOOGLE_DRIVE_PARENT_FOLDER_ID`; the promoted API upload configuration rejects the legacy `GOOGLE_DRIVE_FOLDER_ID` alias. Never put Drive credentials in Web/`VITE_*` variables.

## GitHub Actions dispatch and cutover

The current environment example retains legacy-compatible destinations. Do not change those Production values during source migration. The isolated Monorepo Preview destinations and exact workflow names are documented in [API dispatch cutover map](../../docs/migration/api-dispatch-cutover-map.md).

The API-side switches remain fail-closed:

- `DISPLACEMENT_ACTIONS_ENABLED=false` controls Find Displacements and both Known Place dispatch routes.
- `RIVERSHIFT_ACTIONS_ENABLED=false` controls the independent RiverShift API dispatcher.

The Monorepo Actions repository also has separate repository **Variables** (not Secrets) that gate processing before a worker receives credentials. Keep `MONOREPO_DISPLACEMENT_ACTIONS_ENABLED`, `MONOREPO_KNOWN_PLACE_ACTIONS_ENABLED`, `MONOREPO_KNOWN_PLACE_PAPER_REPRODUCTION_ENABLED`, `MONOREPO_RIVERSHIFT_PROCESSING_ENABLED` and `MONOREPO_SARGUARDIAN_LIVE_VALIDATION_ENABLED` false until the matching workflow, secret, callback, persistence and rollback checks are accepted.

**Important displacement input distinction:** `sarguardian-displacement.yml` is the legacy Dynamic wrapper. It is not present in the Monorepo root. The Monorepo API adapter must target `sarguardian-aoi-wkt-dashboard.yml`, whose `workflow_dispatch` inputs use the Backend dashboard schema. Sending the Dynamic wrapper's `product_type` / `acquisition_window` / `retention_mode` / `processing_profile` fields to that workflow is invalid and GitHub will reject the dispatch.

The API's generic Known Place and author-exact P05023 routes are separate. Generic Known Place supports catalog/series-plan dry-run without raw downloads; raw downloads require explicit user consent plus the repository gate. The author-exact route requires separate explicit consent and stays tied to the fixed research benchmark. RiverShift is an independent GCOV workflow; do not send GOFF/GUNW displacement payloads to it.

The API's `GITHUB_ACTIONS_TOKEN` must be server-side and capable of dispatching the configured private repository workflows. RiverShift may use a separately scoped `RIVERSHIFT_GITHUB_ACTIONS_TOKEN`; when blank, the code falls back to the shared API token. Do not give a browser or Vite bundle any token.

## Operational notes

- ASF catalogue search is metadata-only. It does not download NISAR products.
- GitHub Actions processing workers receive Earthdata and Drive secrets from repository Actions Secrets, not from Vercel Web variables.
- The Actions variable `GOOGLE_DRIVE_PARENT_FOLDER_ID` must be the same parent folder used by the workflow's uploader.
- A successful API submission is not scientific validation. Workflow PASS covers structural/data-contract checks as defined by the engine; it is not independent geophysical validation.
- See `../../docs/migration/readiness-and-remaining-work.md` before any production cutover.
