# Production hosting and database configuration audit

**Read-only audit date:** 2026-11-05  
**Target:** `moshiour0/SARGuardian-Monorepo`  
**Rule:** no production Vercel alias, environment value, Supabase schema, migration, or credential was changed during this audit.

## Vercel project ownership and Git source

The authenticated Vercel Hobby team currently has two active SARGuardian projects:

| Project | Framework | Connected Git repository | Current production commit | Production deployment |
|---|---|---|---|---|
| `sar-guardian-dynamic` | Vite | `moshiour0/SARGuardian_Dynamic` | `42d977b5abd186866ac0d78454239563eebb18d2` | `dpl_CLi5LFvrGUVKXuHyAbYXhBdQ9C9f` |
| `sarguardian-backend-api` | FastAPI | `moshiour0/SARGuardian_Dynamic` | `42d977b5abd186866ac0d78454239563eebb18d2` | `dpl_P7BBnE7PG7EiowYB2w7hS64ZmfMs` |

Both production deployments are READY and currently point to the Dynamic repository, not the new Monorepo. The API project also has a newer READY Preview deployment from Dynamic commit `c5ff0c1273ddf75d9e7ea270a039e2ca5f9723e9`; that does not replace its current production target.

The current Dynamic source baseline imported into this Monorepo is `dd64b7adc90594f1d7f316b352e39fbac2013cb6`. Therefore, the existing production deployments are not yet proof of the latest imported Dynamic source being live.

No Vercel project is currently linked to `moshiour0/SARGuardian-Monorepo`.

### Vercel settings still requiring dashboard confirmation

The connector returned project identity, framework, domain aliases, Git commit metadata, and environment-variable metadata, but did not expose the configured `rootDirectory`/build settings. Verify these settings directly before changing or creating deployment roots:
- current frontend and API Root Directory;
- install/build/output commands;
- Python runtime and function timeout;
- production branch and preview branch rules;
- deployment protection for Preview;
- project-level CORS and allowed origins.

Do not point either existing production project at the Monorepo during this migration phase. New Preview project(s), when created, must be separate from the existing production aliases.

## Current production dispatch configuration (names and non-secret values only)

The active Dynamic API's production environment currently has:
- `APP_ENV=production`;
- `DISPLACEMENT_ACTIONS_ENABLED=true`;
- `GITHUB_ACTIONS_REPOSITORY=moshiour0/SARGuardian-backend`;
- `GITHUB_ACTIONS_WORKFLOW=sarguardian-aoi-wkt-dashboard.yml`;
- `GITHUB_ACTIONS_REF=main`;
- `RIVERSHIFT_ACTIONS_ENABLED=true`;
- `RIVERSHIFT_GITHUB_ACTIONS_REPOSITORY=moshiour0/SARGuardian-backend`;
- `RIVERSHIFT_GITHUB_ACTIONS_WORKFLOW=river-shift-gcov-process.yml`;
- `RIVERSHIFT_GITHUB_ACTIONS_REF=main`;
- `PUBLIC_API_URL` and `RIVERSHIFT_PUBLIC_API_URL` currently point to the existing API Vercel domain.

The frontend's `VITE_SARGUARDIAN_API_URL` in both Production and Preview points to the existing API Vercel domain. Preview also contains a branch-specific override for an older Dynamic feature branch.

These settings intentionally continue to dispatch to the original backend workflows. They must not be changed to Monorepo paths until root workflow migration, API dispatch tests, callback signatures, and rollback are complete.

Sensitive environment-variable values were not decrypted. Only variable names, target environments, and non-secret configuration metadata were inspected.

## Supabase production project

Project: `SARGuardian_Dynamic`  
Region: `ap-northeast-2`  
Database: PostgreSQL 17.11.0.003  
Project status: ACTIVE_HEALTHY

### Active tables and controls

| Public table | RLS enabled | Policies observed | Server-role access |
|---|---|---:|---|
| `catalog_preflights` | Yes | 1 SELECT policy | SELECT/INSERT/UPDATE/DELETE |
| `processing_jobs` | Yes | 1 SELECT policy | SELECT/INSERT/UPDATE/DELETE |
| `displacement_jobs` | Yes | 1 SELECT policy | SELECT/INSERT/UPDATE/DELETE |
| `river_shift_jobs` | Yes | 1 SELECT policy | SELECT/INSERT/UPDATE/DELETE |

The row policies include a predicate. Direct table SELECT grants are absent for `anon` and `authenticated`; the server-side `service_role` has the required table privileges. Public-schema usage is present for the roles, but row-level policy and table privileges remain the access boundary.

Seven migrations are recorded through the RiverShift analysis-mode migration dated 2026-11-03. The database already contains RiverShift job persistence. The Monorepo source move does not require a new schema migration.

Supabase Security Advisor returned no security lints at the time of audit. Performance Advisor returned:
- one unindexed foreign key: `processing_jobs.preflight_id`;
- four RLS policy initialization-plan warnings (one per active table);
- two unused-index informational findings.

These are performance review items, not grounds to change the schema during code migration. Revisit after normal job volume has accumulated; do not drop indexes based only on the current low-volume observation.

### Data API compatibility check

Supabase's changelog states that automatic Data API exposure defaults changed on 2026-05-30 for new projects and were enforced across all projects on 2026-10-30. See the [Supabase breaking-change changelog](https://supabase.com/changelog?types=breaking-change).

The current application is server-side and uses the service-role key; the table privilege checks confirm that role has table-level CRUD access. Do not grant `anon` or `authenticated` direct table privileges as part of this Monorepo migration. Verify PostgREST exposed-schema settings in the Preview environment before cutover.

Supabase also announced removal of an outdated subset of TLS 1.2 ciphers on 2026-11-10. No custom low-level TLS client is introduced by this repository move, but the Preview smoke test should verify that the deployed Python/HTTP clients negotiate successfully after the announced date.

## Secret/configuration migration rules

- Copy environment variable **names and consumers**, never secret values, into the migration manifest.
- Preserve separate Production and Preview scopes.
- Keep Firebase Admin JSON, Supabase service-role key, GitHub token, callback secrets, Drive OAuth data, Earthdata credentials, and ASF credentials server-side only.
- Preserve the current GitHub Actions variable name `Google drive parent folder id` in the backend workflow environment. The Vercel API project separately has a `GOOGLE_DRIVE_FOLDER_ID` variable; these are different configuration surfaces and must not be silently renamed or conflated.
- For a new Preview, add only the minimal Preview-specific Firebase browser configuration, Maps key, API URL, and server-side secrets required for its isolated contract tests. Keep Production values and callback destinations unchanged.

## Cutover gate

No production deployment, domain, callback URL, Supabase schema, GitHub dispatch repository/ref, or worker owner should change until:
1. the Monorepo has separate Vercel Preview deployment(s) with verified root/build settings;
2. Firebase auth and Supabase persistence pass from those Preview deployments;
3. all three workflow dispatch contracts are validated from the Monorepo, including error and rollback cases;
4. RiverShift's staged retry/assemble behavior passes isolated workflow tests;
5. the Preview callback origins are configured without widening Production CORS unnecessarily;
6. the original Dynamic deployments and backend workflows remain available as rollback.
