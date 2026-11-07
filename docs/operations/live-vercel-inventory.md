# Live Vercel inventory — read-only audit

**Audited:** 2026-11-05  
**Team:** `moshiour-rahman-sarkers-projects-2cebe363`  
**Plan:** Hobby  
**Change scope:** inspection only; no project, root directory, environment, alias, or deployment changed.

## Existing Git-linked projects

| Existing project | Project ID | Framework | Linked repository | Latest observed production |
|---|---|---|---|---|
| `sar-guardian-dynamic` | `prj_2wYF8FsOkzI0acPS0qINWGTZfwKQ` | Vite | `moshiour0/SARGuardian_Dynamic` | READY, deployment `dpl_CLi5LFvrGUVKXuHyAbYXhBdQ9C9f`, main `42d977b5abd186866ac0d78454239563eebb18d2` |
| `sarguardian-backend-api` | `prj_Dzh0myaGpcseGXWIj2PIZVSW2vXS` | FastAPI | `moshiour0/SARGuardian_Dynamic` | READY, deployment `dpl_P7BBnE7PG7EiowYB2w7hS64ZmfMs`, main `42d977b5abd186866ac0d78454239563eebb18d2` |

Verified domains:
- Frontend: `sar-guardian-dynamic-lilac.vercel.app`
- API: `sarguardian-backend-api.vercel.app`

The API project also has a newer READY **Preview** deployment:
- Deployment: `dpl_9T8d5NAwNDkRSYHpNdYTpGFCqZoW`
- Branch: `feat/rivershift-map-place-search-20261105`
- Commit: `c5ff0c1273ddf75d9e7ea270a039e2ca5f9723e9`
- Preview target: not production; no production domain alias was assigned in the returned deployment metadata.

The latest project metadata for the frontend points to the READY production deployment above. The API project's latest deployment metadata points to the Preview build, while the production deployment list confirms `dpl_P7BB...` remains the active latest production entry. This distinction prevents confusing a READY Preview with a production cutover.

At the initial source inventory the Monorepo had not yet been linked. Two separate Monorepo Preview projects were subsequently created and are documented below. No existing Production project was repointed or modified.

## Existing root/build evidence

The team-scoped Vercel deployment/build logs were read:
- Frontend production build runs `npm run build` and completes `tsc -b && vite build`. The source repository's frontend root is `Frontend/`, where `package.json`, `package-lock.json`, `vite.config.ts`, and `vercel.json` live. This build evidence is consistent with the current project's root being the frontend workspace, but the exact `rootDirectory` setting is not included in the project metadata response.
- API production build reports `Installing required dependencies from Backend/requirements.txt` and builds the FastAPI/Python functions. The source repository's API root is `Backend/`, where `index.py`, `requirements.txt`, and `vercel.json` live. The exact configured `rootDirectory` field was not included in the project metadata response.

The project-detail endpoint currently returns project ID/name/framework/deployment/aliases/protection fields, but not `rootDirectory`, `buildCommand`, `installCommand`, or `outputDirectory`. The project list can be read using the team slug; that result also does not include those settings. Therefore the build evidence identifies the current source workspaces, but the exact Vercel Settings values still need dashboard verification before any project root is changed.

## Existing environment-variable inventory (names and non-secret routing only)

### Frontend project

The project contains production and preview configuration for:
- `VITE_SARGUARDIAN_API_URL`
- Firebase browser configuration: `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_STORAGE_BUCKET`, `VITE_FIREBASE_MESSAGING_SENDER_ID`, `VITE_FIREBASE_APP_ID`, `VITE_FIREBASE_MEASUREMENT_ID`
- `VITE_GOOGLE_MAPS_API_KEY`

The production `VITE_SARGUARDIAN_API_URL` points to the existing API domain. A branch-scoped Preview override exists for a previous frontend integration branch. Sensitive browser key values were not decrypted.

One unexplained Production environment entry named `re` was also returned by the Vercel inventory. It was not decrypted, edited, or removed. It should be reviewed by the project owner in the Vercel dashboard to determine whether it is obsolete or a typo.

### API project

Observed configuration names include:
- Runtime/auth: `APP_ENV`, `FIREBASE_SERVICE_ACCOUNT_JSON`, `CORS_ORIGINS`, `PUBLIC_API_URL`
- Supabase: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- Dispatch: `GITHUB_ACTIONS_TOKEN`, `GITHUB_ACTIONS_REPOSITORY`, `GITHUB_ACTIONS_WORKFLOW`, `GITHUB_ACTIONS_REF`, `DISPLACEMENT_ACTIONS_ENABLED`, `DISPLACEMENT_CALLBACK_SECRET`
- RiverShift: `RIVERSHIFT_ACTIONS_ENABLED`, `RIVERSHIFT_GITHUB_ACTIONS_REPOSITORY`, `RIVERSHIFT_GITHUB_ACTIONS_WORKFLOW`, `RIVERSHIFT_GITHUB_ACTIONS_REF`, `RIVERSHIFT_PUBLIC_API_URL`, `RIVERSHIFT_CALLBACK_SECRET`
- Drive/ASF: `GOOGLE_DRIVE_OAUTH_CLIENT_JSON`, `GOOGLE_DRIVE_REFRESH_TOKEN`, `GOOGLE_DRIVE_FOLDER_ID`, plus ASF catalogue configuration.

Sensitive values were not decrypted or copied. Existing plain endpoint/repository/ref values were inspected only to establish current routing.

**Important routing decision:** the production API currently dispatches to `moshiour0/SARGuardian-backend` on `main`, including `sarguardian-aoi-wkt-dashboard.yml` and `river-shift-gcov-process.yml`. Keep those dispatch destinations and callback URLs unchanged during the first Monorepo Preview. New Monorepo root workflows must not replace old workers until request/callback/artifact/retry parity is separately tested and cutover is approved.

The existing API Vercel project contains a production `GOOGLE_DRIVE_FOLDER_ID` setting. This is not the same thing as the existing GitHub Actions variable documented in the processing workflows as `Google drive parent folder id`. Do not conflate or rename these two consumers during migration.

## Remaining Vercel checks

Before any Preview runtime smoke test or production cutover:
1. confirm the exact current frontend/API `rootDirectory`, build/install/output settings, and Git production branch in Vercel Settings (build logs indicate the source workspaces are `Frontend/` and `Backend/`, but project metadata did not expose the exact configured field);
2. confirm frontend/API Preview env scopes separately from Production;
3. confirm the Monorepo GitHub repository is accessible to the Vercel Git integration;
4. create separate Monorepo Vercel projects for `apps/web` and `apps/api` with those root directories only after settings and cross-root dependency handling are ready;
5. deploy Preview only; do not assign the current production aliases.

No production Vercel setting, environment variable, domain, or deployment was changed by this audit.


## Production deployment freshness cross-check — 2026-11-05

The latest production deployment records were checked independently from project metadata:

| Project | Latest Production deployment | Deployed commit | Current Dynamic main |
|---|---|---|---|
| Frontend `sar-guardian-dynamic` | `dpl_CLi5LFvrGUVKXuHyAbYXhBdQ9C9f` — READY | `42d977b5abd186866ac0d78454239563eebb18d2` | `dd64b7adc90594f1d7f316b352e39fbac2013cb6` |
| API `sarguardian-backend-api` | `dpl_P7BBnE7PG7EiowYB2w7hS64ZmfMs` — READY | `42d977b5abd186866ac0d78454239563eebb18d2` | `dd64b7adc90594f1d7f316b352e39fbac2013cb6` |

GitHub compare confirms `42d977b5…` is an ancestor of current Dynamic `main`; main is one commit ahead. Therefore both latest Production deployments are behind current main by one commit. The newer API Preview `c5ff0c1273ddf75d9e7ea270a039e2ca5f9723e9` is from the feature branch `feat/rivershift-map-place-search-20261105`; compare shows this branch and main have diverged, so it must not be mistaken for a production deployment or a direct main cutover.

No deployment was triggered, promoted, cancelled, or reassigned during this check. This is existing-system deployment freshness, independent of the new Monorepo's inactive migration candidate.


## Monorepo isolated Preview — live build and environment audit 2026-11-05

Two separate Vercel projects are now linked to `moshiour0/SARGuardian-Monorepo`. Both most recently inspected deployments completed with `READY`, `target=null` (Preview only), and no Production alias was assigned:

| Project | Project ID | Preview deployment | Build commit | Result |
|---|---|---|---|---|
| `sar-guardian-monorepo-web` | `prj_rxEcpqdYRJigOAnx6ekrFj8dX2ny` | `sar-guardian-monorepo-javhnc0ak.vercel.app` | `e82a42d1677e478276ee4f47830cd165eed8a83f` | `READY` |
| `sar-guardian-monorepo-api` | `prj_1XQrqFFo4dFhWzBA15zGQQWNIo2p` | `sar-guardian-monorepo-d3813s55g.vercel.app` | `078de6bd23cd7bc156f985b2d067df53a5098281` | `READY` |

The Web build log confirms `npm ci`, `tsc -b && vite build`, Vite 5.4.21 and 87 modules transformed. The generated JavaScript is 560.16 kB (minified), above Vite's 500 kB warning threshold; consider route/engine code-splitting before release. `npm ci` reported **19 vulnerabilities** (10 moderate, 7 high, 2 critical). Do not run `npm audit fix --force` blindly; inspect the exact advisories and compatible upgrades, then rerun build/tests.

The API build log confirms dependencies installed from `apps/api/requirements.txt`, Python 3.12 runtime, Python bytecode compilation/optimization, and successful Vercel output deployment. This is build evidence, not an authenticated route or database round-trip.

### Preview environment values (names and non-secret routing only)

Web Preview (branch `migration/source-snapshot-import`):
- `VITE_SARGUARDIAN_API_URL` points to the Monorepo API Preview branch alias.
- No other Web Preview env vars were returned. In particular, no Firebase browser config or `VITE_GOOGLE_MAPS_API_KEY` is configured, so Google login and Google Maps are not ready in this Preview.

API Preview (same branch):
- `APP_ENV=preview`
- `CORS_ORIGINS` points to the Monorepo Web Preview branch alias.
- `DISPLACEMENT_ACTIONS_ENABLED=false`
- `RIVERSHIFT_ACTIONS_ENABLED=false`
- No `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, Firebase service-account JSON, GitHub Actions token, Earthdata token, Drive OAuth credentials or callback secrets appeared in the Preview environment list. The returned hidden Production environment count was zero.

This is intentionally fail-closed, but it means Preview cannot yet validate Firebase sign-in, map tiles/search, Supabase-backed job persistence, signed callbacks or live processing. Do not copy Production credentials into Preview by default. Configure a separately approved staging environment only after the secret-name/owner/access mapping and non-production callback route are reviewed.

Both Preview projects have SSO protection enabled. The last 30-minute Vercel runtime-log query returned no records for either deployment; this is not proof that the endpoints work or fail. A login-authorized browser/API smoke test remains outstanding.

### Existing Production routing

The Dynamic frontend and API Production deployments remain on the existing repository/project. No production deployment was triggered, promoted, rolled back, or reassigned. The Monorepo Preview projects are separate and are not production replacements.


## Monorepo Preview build and environment recheck — 2026-11-05

The Monorepo has two separate Vercel projects linked to the migration branch. The latest inspected builds are READY Preview deployments, not Production:
- Web: dpl_AHJQWERG7geqzMZSNJL2KDFsh5y9, commit e82a42d1677e478276ee4f47830cd165eed8a83f; npm ci, TypeScript build and Vite production build completed. Build emitted a 560.16 kB JS chunk warning and npm reported 19 advisories (10 moderate, 7 high, 2 critical).
- API: dpl_4A846M3FHcbVZNBaKPAXBVPHBNgf, commit 078de6bd23cd7bc156f985b2d067df53a5098281; FastAPI/Python dependency install, bytecode compilation, and Vercel output deployment completed.

Both projects enable SSO on Preview. Environment inventory (names only; no secret values decrypted) confirms Web Preview currently has only VITE_SARGUARDIAN_API_URL; Firebase browser config and VITE_GOOGLE_MAPS_API_KEY are absent. API Preview has APP_ENV=preview, matching CORS_ORIGINS, and DISPLACEMENT_ACTIONS_ENABLED=false plus RIVERSHIFT_ACTIONS_ENABLED=false. No Supabase URL/service key, Firebase service-account JSON, GitHub token, Earthdata token, Drive OAuth or callback secret was present in Preview. This is fail-closed, but Firebase login, Maps, Supabase persistence and processing cannot be considered runtime-tested.

The last 30-minute Vercel runtime-log query returned no records for either Preview deployment. This is not an endpoint smoke test; SSO-protected browser/API validation remains outstanding. The latest actual build logs establish compile/deploy readiness only. GitHub Vercel PR checks may still show a build-rate-limit failure; that status must not be confused with these two READY deployments.

No production environment variables, aliases, domains or processing destinations were changed. Do not copy production credentials into Preview automatically; configure approved staging values only after the staging auth/data/callback design is reviewed.


### Legacy-to-Monorepo environment-name crosswalk (values not decrypted)

Read-only environment inventory of the existing production projects confirms the intended names that must be deliberately mapped if an approved Preview/staging runtime is configured later.

| Consumer | Existing Production names | Current Monorepo Preview |
|---|---|---|
| Web | VITE_SARGUARDIAN_API_URL; VITE_FIREBASE_API_KEY, VITE_FIREBASE_AUTH_DOMAIN, VITE_FIREBASE_PROJECT_ID, VITE_FIREBASE_STORAGE_BUCKET, VITE_FIREBASE_MESSAGING_SENDER_ID, VITE_FIREBASE_APP_ID, VITE_FIREBASE_MEASUREMENT_ID; VITE_GOOGLE_MAPS_API_KEY | Only VITE_SARGUARDIAN_API_URL is present. |
| API runtime/auth | APP_ENV, CORS_ORIGINS, PUBLIC_API_URL, FIREBASE_SERVICE_ACCOUNT_JSON | Only APP_ENV and CORS_ORIGINS are present. |
| Supabase | SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY | Neither present. |
| ASF catalogue | ASF_CATALOG_ENABLED, ASF_SEARCH_URL, ASF_MAX_RESULTS, ASF_TIMEOUT_SECONDS, PREFLIGHT_TTL_SECONDS | None present. |
| Find Displacements | DISPLACEMENT_ACTIONS_ENABLED, GITHUB_ACTIONS_TOKEN, GITHUB_ACTIONS_REPOSITORY, GITHUB_ACTIONS_WORKFLOW, GITHUB_ACTIONS_REF, DISPLACEMENT_CALLBACK_SECRET, DISPLACEMENT_DISPATCH_TIMEOUT_SECONDS | Only DISPLACEMENT_ACTIONS_ENABLED=false is present. |
| Known Place | KNOWN_PLACE_GITHUB_ACTIONS_REPOSITORY, KNOWN_PLACE_GITHUB_ACTIONS_WORKFLOW, KNOWN_PLACE_GITHUB_ACTIONS_REF, KNOWN_PLACE_PAPER_GITHUB_ACTIONS_REPOSITORY, KNOWN_PLACE_PAPER_GITHUB_ACTIONS_WORKFLOW, KNOWN_PLACE_PAPER_GITHUB_ACTIONS_REF (plus shared GitHub token and callback/Drive credentials) | No Known Place dispatch or credential variables present. |
| RiverShift | RIVERSHIFT_ACTIONS_ENABLED, RIVERSHIFT_GITHUB_ACTIONS_REPOSITORY, RIVERSHIFT_GITHUB_ACTIONS_WORKFLOW, RIVERSHIFT_GITHUB_ACTIONS_REF, RIVERSHIFT_PUBLIC_API_URL, RIVERSHIFT_CALLBACK_SECRET | Only RIVERSHIFT_ACTIONS_ENABLED=false is present. |
| Drive | GOOGLE_DRIVE_OAUTH_CLIENT_JSON, GOOGLE_DRIVE_REFRESH_TOKEN, GOOGLE_DRIVE_FOLDER_ID | No Drive variables present. |

The old Web production project has one additional sensitive variable named `re` with no comment. It was not decrypted, changed or removed; the project owner should identify it before final secret review.

**Do not treat every name in this matrix as a request to copy the old Production value.** Preview must use an approved staging Firebase project, Maps key/referrer restrictions, Supabase database/role, GitHub token scope, callback secrets, Earthdata account and Drive destination. Prefer separate staging credentials and data. No legacy secret value was decrypted or moved by this audit.

The legacy Vercel API variable GOOGLE_DRIVE_FOLDER_ID is a project/runtime setting. It is not the GitHub Actions secret/variable documented by the source processing workflows as “Google drive parent folder id”. The Monorepo must preserve the correct consumer-specific contract; do not rename either one or assume they are interchangeable.


### Source-level expected behavior with current Preview configuration

The promoted API source was inspected alongside the environment-name inventory:

- GET /health is intentionally public and returns the API service health object. It is a code-level route contract only; the protected Preview URL was not successfully invoked in this audit.
- Other user routes require a Firebase Bearer token. The API auth adapter uses FIREBASE_SERVICE_ACCOUNT_JSON or an approved application-default credential. Neither is present in Monorepo Preview, so Firebase-protected routes are expected to return a safe 503 configuration response rather than authenticate users.
- Supabase get_job_store() requires both SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY. Both are absent from Preview; job persistence is expected to return a controlled 503 configuration error, not use an in-memory fallback.
- RiverShift /jobs is gated by RIVERSHIFT_ACTIONS_ENABLED and persistence; with the flag false, dispatch is rejected before a worker is launched.
- Find Displacements dispatch is likewise disabled by DISPLACEMENT_ACTIONS_ENABLED=false.

This validates the fail-closed configuration path by source inspection, not by live HTTP response. Do not label Preview's authenticated routes as working until the owner supplies approved staging credentials and an SSO-authorized request verifies health, auth, persistence and callbacks end to end.


## Historical API Preview redeploy attempt — 2026-11-05 (superseded by current 2026-11-06 Preview)

After the RiverShift API dispatch-target validation code was added under apps/api, a direct Git-backed Preview deployment was requested for current migration branch head 280af486a49eb42b18e0de41aaa7817a287b2591, scoped to the existing Monorepo API project only. The request was rejected by Vercel before deployment creation:

- HTTP 402 payment_required
- Resource: api-deployments-free-per-day
- Message: daily free API deployment allowance exceeded (more than 100); retry window reported as 24 hours.
- No deployment ID was returned and no deployment was created.

The latest inspectable API Preview deployment remains dpl_4jzEgnNBE4Yv7KMTqgdUbz2Y3uKe at commit 4f9ed1ad09cce1261afd5e68938bc4a12a8685cc. It predates the RiverShift API config-hardening commits, so the new config code has **not** been Vercel-built or deployed. Do not treat prior READY API Preview builds as evidence for the latest code. No Production project/alias/environment was changed. Avoid further create-deployment calls until the Vercel quota window has reset or the project owner resolves the plan/usage limit.


## Current Monorepo Preview deployments — 2026-11-06

The latest migration branch head `96bcdee42b5b6871f5638dd3e41161cccc966130` has fresh Git-linked Preview deployments in both isolated Monorepo projects:

| Project | Project ID | Deployment ID | Preview URL | Branch alias | State | Target |
|---|---|---|---|---|---|---|
| Web | `prj_rxEcpqdYRJigOAnx6ekrFj8dX2ny` | `dpl_4hDnUyXMPDYBhwNa7aT71xYigknb` | [Web Preview](https://sar-guardian-monorepo-3rqjt3ztu.vercel.app) | `sar-guardi-git-90a645-moshiour-rahman-sarkers-projects-2cebe363.vercel.app` | READY | Preview (`target=null`) |
| API | `prj_1XQrqFFo4dFhWzBA15zGQQWNIo2p` | `dpl_Hchn3asHzxWxauRqNBjBmKpWWwN8` | [API Preview](https://sar-guardian-monorepo-1zt05usqy.vercel.app) | `sar-guardi-git-ed4bd9-moshiour-rahman-sarkers-projects-2cebe363.vercel.app` | READY | Preview (`target=null`) |

Both builds cloned the same migration branch commit. The Web build completed `npm ci`, `tsc -b && vite build`, and Vite 5.4.21; its 560.17 kB minified JavaScript chunk exceeds the 500 kB warning threshold. `npm ci` audited 299 packages and reported 19 advisories (10 moderate, 7 high, 2 critical). Review exact advisories and code-split the large bundle before public release; do not use `npm audit fix --force` without compatibility review. The API build installed `apps/api/requirements.txt`, compiled and optimized Python 3.12 bytecode, and completed deployment.

Both Preview projects still have SSO protection. Current project metadata marks the Monorepo projects as non-live; their Production-target deployment records are cancelled, not serving the Production domain. The original `sar-guardian-dynamic` Web and `sarguardian-backend-api` Production projects remain `READY` on their existing main-branch deployments. No alias, Production domain, API dispatch target, callback URL or Production environment was reassigned.

The current Preview builds prove build/deployment success only. Firebase Web config, Maps access, staging Supabase credentials, authenticated user routes, signed callback round-trips, GitHub worker dispatch, Earthdata downloads and Drive receipts are not verified by these builds. Configure separate staging values from the environment templates; do not copy Production service-role keys or worker secrets into Preview.
