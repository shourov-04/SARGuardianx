# Live Supabase inventory — read-only audit

**Audited:** 2026-11-05  
**Project:** `SARGuardian_Dynamic` (`ufwjmhivvnoewjsbteey`)  
**Region:** `ap-northeast-2`  
**Database:** PostgreSQL 17.11.0.003  
**Change scope:** read-only queries only; no SQL or migration was applied.

## Project and tables

The connected Supabase project inventory returned one active healthy SARGuardian project, `SARGuardian_Dynamic`.

| Public table | Approx. rows at audit | RLS enabled | Purpose |
|---|---:|---|---|
| `catalog_preflights` | 3 | Yes | Immutable ASF preflight manifest metadata |
| `processing_jobs` | 2 | Yes | Durable metadata for GUNW/GOFF processing jobs |
| `displacement_jobs` | 50 | Yes | Authenticated displacement requests and signed callbacks |
| `river_shift_jobs` | 23 | Yes | Independent GCOV engine requests and callback receipts |

The listed approximate row counts are live values at audit time, not a frozen data snapshot.

## Row access and API ownership

The database has one `SELECT` owner policy per table for the `authenticated` role:
`(select auth.jwt() ->> 'sub') = owner_uid`.

Read-only privilege inspection showed:
- `anon` has no SELECT privilege on these tables.
- `authenticated` has no SELECT privilege on these tables.
- the server-only `service_role` has table access used by the Dynamic API.
- RLS is enabled on all four tables; it is not FORCE RLS.

The browser is not intended to query these tables directly. The active API initializes a server-side Supabase client with `SUPABASE_SERVICE_ROLE_KEY`; the service layer's user-facing read methods explicitly filter by verified Firebase `owner_uid` for preflights, processing jobs, displacement jobs, and RiverShift jobs. Signed worker callbacks use separate callback authentication and conditional state/sequence updates.

**Security implication:** because the API uses a privileged server role, owner isolation depends on the API consistently deriving the owner UID from the verified Firebase identity and including it in every user-facing read. Keep those filters in code review and tests; the database's authenticated SELECT policy does not constrain a service-role query.

Supabase security advisor returned **no security lints** at audit time. This is not a guarantee that every API-level authorization path is correct.

## Migration history observed remotely

The remote migration-history table returned seven entries:

| Remote version | Recorded name |
|---|---|
| `20261026023221` | `20261017143644_processing_jobs` |
| `20261026023229` | `20261022203034_displacement_jobs` |
| `20261026023233` | `20261023141449_displacement_active_request_guard` |
| `20261026023237` | `20261024111404_scientific_request_contract` |
| `20261027003643` | `place_target_contract` |
| `20261103021845` | `river_shift_jobs` |
| `20261103230606` | `river_shift_analysis_modes_phase2` |

The source migration directory currently contains seven files, including:
- `20261103100000_river_shift_jobs.sql`
- `20261104120000_river_shift_analysis_modes.sql`

The last two local filename prefixes and recorded remote versions do not match, and the recorded remote names differ from those local suffixes. Their resulting database structures and functions were inspected and match the source intent at the schema level:
- `analysis_mode` permits `general_scan` and `event_based`;
- `general_scan` requires a NULL `event_date`;
- `event_based` requires an in-window `event_date`;
- 366-day window and threshold range checks exist;
- the one-active-job-per-owner unique partial index exists;
- immutable accepted request fields, callback sequence checks, state transitions, and terminal immutability are enforced by the transition trigger.

This is **migration-history naming/version drift**, not evidence that the live schema is missing those features. Before any future `supabase db push` or deployment operation, compare the local/remote CLI migration list and reconcile version history explicitly. Do not reapply or rename already-applied SQL blindly.

## No migration performed

No table, column, index, trigger, policy, extension, privilege, row, or migration-history entry was changed by this audit. Supabase remains the existing production data store; the Monorepo should reuse it during first Preview only after environment mapping, not create a new database or migrate live rows.

## Performance-advisor recheck — 2026-11-05 03:31 UTC

A second read-only call to the Supabase Performance Advisor returned:
- one INFO `unindexed_foreign_keys` finding: `processing_jobs.preflight_id` has no covering B-tree index;
- four WARN `auth_rls_initplan` findings, one for each owner-read policy;
- two INFO `unused_index` findings for `catalog_preflights_owner_created_idx` and `processing_jobs_state_idx`.

The four live policy definitions were inspected directly through `pg_policies`. Each uses the scalar-subquery form:
`(( SELECT (auth.jwt() ->> 'sub'::text)) = owner_uid)`.
This is already the documented init-plan pattern for avoiding per-row JWT function evaluation. The advisor warning appears inconsistent with the live policy expression; classify it as a likely advisor false positive, not an instruction to rewrite an already-correct owner check. The policy remains an owner filter and is not relaxed.

The live index list for `processing_jobs` confirms there is no index whose leading key covers `preflight_id`; the only indexes are the primary key, owner/created ordering, owner/idempotency uniqueness, state, and one-active-heavy uniqueness. A small supporting index on `preflight_id` is a performance candidate, but do not apply it during source migration. Evaluate query plans and expected preflight/job retention volume first, then add a reviewed migration after local/remote migration history is reconciled.

The two unused-index notices are low-confidence at the current small row counts (2 rows in `processing_jobs`, 3 in `catalog_preflights`) and must not trigger index removal. Keep them until representative production workload evidence exists.

**Change scope remains read-only:** no SQL DDL, policy, index, table, data, or migration-history entry was changed during this recheck.

## Live catalog recheck — 2026-11-05

A second read-only Supabase catalog audit after the original inventory confirmed:
- all four expected tables still exist;
- RLS is enabled and `FORCE ROW LEVEL SECURITY` is off on each;
- the four owner-read policies remain the scalar-subquery JWT `sub` predicate;
- no direct `anon` or `authenticated` table grants appear in the privilege inventory; the API's trusted `service_role` remains the database access path;
- RiverShift's analysis-mode column, event-date constraints, other request-contract constraints, indexes and transition trigger match the current local migration's expected post-migration contract;
- the current RiverShift row counts are 23 in total: 18 failed Event-Based, 1 failed General Scan, 2 succeeded Event-Based and 2 succeeded General Scan. These are aggregate state counts only, not an accuracy assessment;
- the Supabase Security Advisor returned no security lints.

No table, index, trigger, policy, privilege, row or migration-history entry was changed.

**CLI caution:** Supabase CLI v3 became the default on 2 November 2026. The 4 November breaking-change notice changes hosted-command targeting: explicitly use `--remote` for remote operations; hosted changes require confirmation and unattended runs need explicit `--yes`. Pin the intended CLI version and review the [v2→v3 guide](https://supabase.com/docs/guides/local-development/cli/migrating-to-v3) before adding any Supabase command to CI. Do not run `db push` while migration versions/names remain unreconciled.


## Default-privilege audit — additional read-only check 2026-11-05

The effective table privileges and PostgreSQL default ACLs were inspected separately.

### Current four job tables

For each of catalog_preflights, processing_jobs, displacement_jobs and river_shift_jobs:
- anon: SELECT/INSERT/UPDATE/DELETE/TRUNCATE all false;
- authenticated: SELECT/INSERT/UPDATE/DELETE/TRUNCATE all false;
- service_role: those privileges are effective;
- table owner: postgres;
- RLS enabled, FORCE RLS false.

This is consistent with the explicit per-table REVOKE from anon/authenticated in the seven local SQL migrations. The authenticated owner-read policies exist, but without table SELECT grant they do not make browser-direct table queries possible. The API is the data access path.

### Future-object default ACLs

The current public-schema default ACLs for objects created by roles postgres and supabase_admin include:
- ALL table privileges for anon, authenticated and service_role;
- sequence privileges (SELECT/USAGE/UPDATE) for anon, authenticated and service_role.

Those defaults do not retroactively grant privileges on the four existing tables because the local migrations explicitly revoke anon/authenticated on each current table. They do, however, mean a future public table or sequence created by either role will inherit broad access unless the migration explicitly revokes it.

**Release requirement:** every new public table migration must explicitly revoke anon/authenticated privileges and enable RLS before any API rollout. Add a separately reviewed default-privilege hardening plan for postgres and supabase_admin (tables and sequences) after all public-schema consumers are inventoried. Do not change the live defaults during Monorepo source migration: the defaults are schema-wide and their impact on unrelated project objects has not been reviewed.

### Privileged service role

The existing service_role has effective full DML/DDL-adjacent table privileges on these job tables and BYPASSRLS. This is a highly privileged server credential, not an end-user role. Keep it only in server-side API environments, never in VITE_* variables; every end-user read/write path must apply verified owner_uid and request-state constraints at the API/database transition boundary. No service-role credential was decrypted or copied during this audit.

No grants, default ACLs, roles, policies, tables, triggers or rows were changed by this inspection.


### Full public-schema object inventory — 2026-11-05

A full read-only catalog query returned exactly four public relations (all ordinary tables): catalog_preflights, displacement_jobs, processing_jobs, river_shift_jobs. No public views, materialized views, sequences or foreign tables were present at audit time.

The public schema contained six routines, all owned by postgres:
- enforce_catalog_preflight_immutable
- enforce_displacement_job_transition
- enforce_displacement_place_immutable
- enforce_processing_job_integrity
- enforce_processing_job_transition
- enforce_river_shift_job_transition

Each routine is a trigger function with no arguments, SECURITY INVOKER (not SECURITY DEFINER), and a fixed search_path=public. Their explicit ACL includes PUBLIC/anon/authenticated/service_role EXECUTE. PostgreSQL trigger functions cannot be called as ordinary functions; direct execution outside a trigger context is rejected. Their current grants therefore are not evidence that an unauthenticated caller can mutate job rows. However, the broad default function EXECUTE ACL means future ordinary functions created in public by postgres or supabase_admin will also be executable by PUBLIC unless explicitly revoked. Treat this with the future-object table/sequence default-ACL risk above.

The query of pg_settings for pgrst.db_schemas returned no rows because PostgREST configuration is not exposed there in this project. This does not establish which schemas the Data API exposes; verify it through Supabase API settings/appropriate config before first Preview persistence smoke testing.

No objects, grants, functions, default ACLs or rows were changed by this inventory.
