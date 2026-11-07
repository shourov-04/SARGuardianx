# Supabase migration lineage and Monorepo ownership

**Source:** `moshiour0/SARGuardian_Dynamic@dd64b7adc90594f1d7f316b352e39fbac2013cb6`  
**Promoted destination:** `infrastructure/supabase/`  
**Current status (supersedes earlier nine-row checkpoint):** the dedicated Free Tokyo Monorepo target reports 11 remote migration rows, and all 11 version/name pairs match the canonical filenames in `infrastructure/supabase/migrations/`. Four Monorepo forward migrations are present and verified: catalogue-preflight retention, public default-privilege hardening, the processing-jobs preflight FK index, and owner-read RLS initplan optimization. The earlier nine-row tables below are preserved as historical checkpoints; the current 11-row table is at the end of this document. The existing Dynamic Production database is a separate target whose legacy history remains unrepaired.

## Files imported

| Destination file | Source blob SHA |
|---|---|
| `config.toml` | `3292dc6443b23652e9077c13cd0c61284abd226f` |
| `migrations/20261106000844_20261017143644_processing_jobs.sql` | `0c62c69b8eecf674f65af5022e81e09d65fbecef` |
| `migrations/20261106000850_20261022203034_displacement_jobs.sql` | `a894b4d28d5fcda3df143629b9e70d613d3b727d` |
| `migrations/20261106000856_20261023141449_displacement_active_request_guard.sql` | `536d8c473f3d19de29b532d42127550262c33104` |
| `migrations/20261106000901_20261024111404_scientific_request_contract.sql` | `65c64d04c179bf4c1228a5d7edbd73510ad2b6fd` |
| `migrations/20261106000905_20261027003643_place_target_contract.sql` | `f588c72bcd064779a5790f979db709b86b23dff2` |
| `migrations/20261106000909_20261103100000_river_shift_jobs.sql` | `4d2fce5612c84baf2e8b06a9df02f05b2e0b0204` |
| `migrations/20261106000923_20261104120000_river_shift_analysis_modes.sql` | `895cade15db273e233433c228a7e20e85118f043` |

All seven imported SQL blobs are promoted without content rewriting. To align the Monorepo target's live history, their destination filenames use the remote 14-digit version followed by the original migration name; the immutable source snapshot retains the original source filenames. The exact source/destination blob, file mode and Git object identity are verified by `migration/supabase-history-alignment.json` and `tools/verify_source_snapshots.py`.

## Live remote migration-history mapping

The existing Supabase project `SARGuardian_Dynamic` reports these eight remote migration records after the new forward migration:

| Remote version | Remote recorded name | Matching local source file |
|---|---|---|
| `20261026023221` | `20261017143644_processing_jobs` | `20261017143644_processing_jobs.sql` |
| `20261026023229` | `20261022203034_displacement_jobs` | `20261022203034_displacement_jobs.sql` |
| `20261026023233` | `20261023141449_displacement_active_request_guard` | `20261023141449_displacement_active_request_guard.sql` |
| `20261026023237` | `20261024111404_scientific_request_contract` | `20261024111404_scientific_request_contract.sql` |
| `20261027003643` | `place_target_contract` | `20261027003643_place_target_contract.sql` |
| `20261103021845` | `river_shift_jobs` | `20261103100000_river_shift_jobs.sql` |
| `20261103230606` | `river_shift_analysis_modes_phase2` | `20261104120000_river_shift_analysis_modes.sql` |
| `20261105205909` | `catalog_preflight_retention` | `20261105205909_catalog_preflight_retention.sql` |

The first four records have a remote `version` that differs from the timestamp embedded in the local filename. The two RiverShift records also have timestamp and/or recorded-name differences. The new eighth forward migration is aligned exactly by version and name. The actual schema/functions and analysis-mode constraints were read and checked against the migration intent, but this is not a migration-history reconciliation.

## Required before any `supabase db push`

This section applies only to the existing Dynamic Production project `SARGuardian_Dynamic` (`ufwjmhivvnoewjsbteey`). Do not apply its legacy version/name observations to the Monorepo target. Matching SQL content or table structure does not make migration-history records interchangeable. The old project's first four local filenames have UTC-style source-commit prefixes while its remote history contains deployment timestamps; the RiverShift names/timestamps also differ. The Monorepo target has a separate twelve-row alignment manifest and CI contract.

Before any future database write:
1. run read-only `supabase migration list --remote` (CLI v3) against the **Dynamic Production project** and compare it with that project's exact original local migration directory;
2. inspect the original deployment/release history that created remote versions `20261026023221` through `20261103230606`;
3. compare remote migration statements/functions/triggers and the local SQL contents, including transaction effects and later hotfixes;
4. produce a separate reviewed Dynamic Production history plan;
5. do not run repair/replay or `db push` until that project-specific plan is approved. Monorepo filename alignment is tracked independently later in this document.

Do not rename Dynamic Production's original files, reapply these SQL statements, delete remote migration records, or use `db reset`. No Supabase migration command that writes to the Dynamic Production project has been executed during this migration.

## Runtime ownership

The Dynamic API remains the active service and currently talks to the existing Supabase project through server-side `SUPABASE_SERVICE_ROLE_KEY`. The Monorepo should reuse this project for the first isolated Preview only after:
- Preview secret/env scopes are configured separately;
- RLS and owner filtering pass API-level tests;
- PostgREST exposed-schema settings are confirmed after the Data API exposure change;
- retention and cleanup policy is reviewed;
- migration history is reconciled without reapplying existing DDL.

The server-only service-role key must never be placed in frontend `VITE_*` variables or committed to source.

## Live schema verification — read-only recheck 2026-11-05

The connected Supabase MCP project inventory confirms that the seven remote migration-history rows above are the current set; a separate read-only catalog query confirms all four expected public tables exist.

### RiverShift local-to-remote contract parity

The two local RiverShift source files were compared with live PostgreSQL catalog metadata, not merely with migration names:

- `river_shift_jobs.analysis_mode` exists as `text NOT NULL DEFAULT 'event_based'`.
- `event_date` is nullable.
- `analysis_mode` accepts only `general_scan` and `event_based`.
- `general_scan` requires `event_date IS NULL`; `event_based` requires a non-null date within the requested start/end range.
- Existing 366-day window, maturity, frequency, covariance term, threshold method/value, request fingerprint, callback sequence and owner/idempotency constraints are present.
- `river_shift_jobs_one_active_per_owner_idx`, owner-created index and state index are present.
- `river_shift_jobs_transition_guard` calls `public.enforce_river_shift_job_transition()`. Its live definition preserves accepted-request immutability (including `analysis_mode`), callback sequence monotonicity, allowed state transitions and terminal-row immutability.
- Owner-read policy uses the scalar-subquery `auth.jwt() ->> 'sub'` check.

These are schema and function-body parity checks for the **post-migration state**. They do not prove that the original remote migration SQL bytes equal the local SQL file bytes; the remote migration-history record exposes version and name, not an immutable source-file blob. The two RiverShift migration identities therefore remain an explicit history-reconciliation task even though the live database has the expected final contract.

### Live RLS and privilege check

Read-only PostgreSQL catalog inspection confirmed:

- RLS is enabled on `catalog_preflights`, `processing_jobs`, `displacement_jobs` and `river_shift_jobs`; `FORCE ROW LEVEL SECURITY` is false on all four.
- Each table has the expected `authenticated` SELECT policy that restricts `owner_uid` to the JWT `sub` value.
- No `anon` or `authenticated` table grant appeared in the live privilege inventory; the trusted `service_role` has table access for the server-side API.
- Security Advisor returned no lints in this recheck.

The API uses privileged server-side access, so the database owner-read policy is not a substitute for API authorization. Every user-facing read must continue to derive the owner UID from the verified Firebase identity and filter by it. Keep these checks in API regression tests.

#

## Live retention and access recheck — pre-migration baseline, read-only 2026-11-06

The active `SARGuardian_Dynamic` project was `ACTIVE_HEALTHY` in `ap-northeast-2`, PostgreSQL 17.11.0. At this pre-migration baseline, seven remote migration rows existed. The following findings led to the bounded forward migration recorded below.

### Access contract

Read-only catalog and privilege queries reconfirmed all four job tables have RLS enabled and `FORCE ROW LEVEL SECURITY` disabled. Each has one `authenticated` SELECT owner policy using the verified JWT `sub` claim in a scalar subquery. The `anon` and `authenticated` database roles currently have no direct SELECT table privilege on these four tables; `service_role` does. This is consistent with the current API-mediated access model, not a grant for browser-direct reads. The API must continue verifying Firebase identity and filtering every user-visible read by that UID.

The Supabase Security Advisor returned no security lints.

### Retention gap — action required before production acceptance

A read-only row-age check found:

| Table | Rows | Oldest created | Retention observation |
|---|---:|---|---|
| `catalog_preflights` | 3 | 2026-11-01 19:02 UTC | All 3 rows already have `expires_at < now()` |
| `processing_jobs` | 2 | 2026-11-01 19:05 UTC | No table-level expiry column |
| `displacement_jobs` | 51 | 2026-10-26 03:30 UTC | No table-level expiry column |
| `river_shift_jobs` | 24 | 2026-11-03 05:31 UTC | No table-level expiry column |

At the pre-migration baseline, no installed `pg_cron` extension or database-side cleanup function/job was found. No external cleanup owner was evidenced.

A more important conflict exists for `catalog_preflights`: its `catalog_preflights_immutable_guard` trigger fires on both UPDATE and DELETE and calls `public.enforce_catalog_preflight_immutable()`, whose current implementation always raises `catalog preflight snapshots are immutable`. Therefore the three expired rows cannot be purged through an ordinary DELETE while this trigger remains unchanged. The `expires_at` field currently acts as expiry metadata, not proof that rows are automatically removed.

A narrow preflight policy has since been applied as a forward migration. Job-table and artifact retention remains intentionally undefined and is not automatically purged.

### Performance advisor observations

The read-only Performance Advisor returned:
- one INFO finding: `processing_jobs.preflight_id` has no covering index;
- four WARN findings for owner-read RLS policies being re-evaluated per row, although the inspected policy expressions already wrap `auth.jwt()` in a scalar subquery; verify the advisor finding against an EXPLAIN/test before changing the policies;
- two INFO unused-index findings on `catalog_preflights_owner_created_idx` and `processing_jobs_state_idx`. Do not remove indexes solely from a low-volume observation.

These are performance observations, not Security Advisor findings. The forward migration later added the expiry lookup index; no policy was changed.



## Forward retention migration — 2026-11-06

The canonical forward migration is maintained at the infrastructure source-of-truth path:

- `infrastructure/supabase/migrations/20261106000928_20261105205909_catalog_preflight_retention.sql`

Its Git blob is `d37e18839e4b143dd3cc8dbbab17f8d2289f17a1`. The imported `apps/api/supabase/` tree remains byte-identical to the Dynamic source snapshot and was intentionally not modified. The migration was applied successfully to live project `ufwjmhivvnoewjsbteey` (API response `success: true`) and verified. It implements a narrowly scoped policy derived from the API's existing default preflight TTL (24 hours):

- Preserve expired catalogue preflight snapshots for a further **7-day support grace period**.
- Once the grace period has elapsed, delete only preflights that are **not referenced** by `processing_jobs`.
- Process no more than 500 rows per daily run; row locks use `SKIP LOCKED`.
- Keep the original immutable guard for all ordinary UPDATE/DELETE operations. A transaction-local, owner-only SECURITY DEFINER purge path is the only exception.
- Schedule one Supabase Cron job, `sarguardian-expired-preflight-cleanup`, daily at **03:20 UTC**.
- No browser role or API `service_role` can execute the purge function directly.

The current live inventory contains three expired preflights: one unreferenced and two referenced by the two existing `processing_jobs` rows. None has been expired for more than seven days yet. Therefore the first scheduled execution is expected to delete **zero** existing rows; the referenced records remain protected regardless of age. The migration does not purge `processing_jobs`, `displacement_jobs`, or `river_shift_jobs`, nor does it delete Google Drive files, GitHub artifacts, raw NISAR source data, or scientific result bundles. Those retention windows require separate explicit policies.

For the existing Dynamic Production project `ufwjmhivvnoewjsbteey`, the seven pre-existing remote migration records in this historical checkpoint remained version/name-mismatched; the eighth retention migration was aligned at remote version `20261105205909`. This paragraph is about Dynamic Production only, not the dedicated Monorepo target. No historical migration repair or old DDL replay was performed there.

## Safe future CLI operation after Supabase CLI v3

Supabase released CLI v3 on 2 November 2026. The 4 November breaking-change notice says hosted database commands now default to the local stack; use `--remote` for the linked hosted database. Hosted changes ask for confirmation, and unattended CI needs an explicit `--yes`. See the [Supabase CLI v2→v3 migration guide](https://supabase.com/docs/guides/local-development/cli/migrating-to-v3) and [4 November breaking-change notice](https://supabase.com/changelog?types=breaking-change).

Before any future CLI call, inspect and pin the CLI version. For the Monorepo target, use the aligned twelve-file manifest and run a read-only v3 migration list against `qbmhpdprvxssqinnommz` after CLI authentication. For Dynamic Production, use its own original local Supabase migration directory and separate project ref; never reuse the Monorepo manifest. Do not copy legacy `--linked`/`--project-ref` syntax into a v3 workflow without checking current documentation. Never add `--yes` to a hosted DDL command until project ref, change set and approval are verified. No CLI migration repair or old migration replay was executed.

## Dedicated SARGuardian-Monorepo Supabase project — verified 2026-11-06

The Monorepo database target is live and healthy:

- Project: SARGuardian-Monorepo
- Project ref: qbmhpdprvxssqinnommz
- Region: Japan/Tokyo (ap-northeast-1)
- API URL: https://qbmhpdprvxssqinnommz.supabase.co
- Organization plan: Free; project cost quote: $0/month
- PostgreSQL: 17.11.0.018
- Project status: ACTIVE_HEALTHY

The four historical public job tables exist and are RLS-enabled:
`catalog_preflights`, `processing_jobs`, `displacement_jobs`, and
`river_shift_jobs`. They contain the 80-row metadata-only mirror
(3/2/51/24); four authenticated owner-read policies bind JWT `sub` to
`owner_uid`, and browser roles have no direct table grants.

A fifth table, `known_place_requests`, has RLS enabled and 0 rows. It stores
only request UUID, Firebase owner UID, workflow kind, dispatch state and
creation timestamp—no AOI or science payload. It intentionally has no browser
policy or browser grants; `service_role` alone has SELECT/INSERT/UPDATE and
has `BYPASSRLS=true`. `anon` and `authenticated` have neither table grants
nor RLS bypass. Security Advisor's only new notice is the expected INFO-level
`rls_enabled_no_policy` for this private server-only table.

### Monorepo remote migration records

The initial Monorepo checkpoint reported nine remote migration records (the two later performance migrations and owner-mapping migration are recorded in the superseding inventory below):

| Remote version | Remote name | Local canonical file |
|---|---|---|
| 20261106000844 | 20261017143644_processing_jobs | 20261106000844_20261017143644_processing_jobs.sql |
| 20261106000850 | 20261022203034_displacement_jobs | 20261106000850_20261022203034_displacement_jobs.sql |
| 20261106000856 | 20261023141449_displacement_active_request_guard | 20261106000856_20261023141449_displacement_active_request_guard.sql |
| 20261106000901 | 20261024111404_scientific_request_contract | 20261106000901_20261024111404_scientific_request_contract.sql |
| 20261106000905 | 20261027003643_place_target_contract | 20261106000905_20261027003643_place_target_contract.sql |
| 20261106000909 | 20261103100000_river_shift_jobs | 20261106000909_20261103100000_river_shift_jobs.sql |
| 20261106000923 | 20261104120000_river_shift_analysis_modes | 20261106000923_20261104120000_river_shift_analysis_modes.sql |
| 20261106000928 | 20261105205909_catalog_preflight_retention | 20261106000928_20261105205909_catalog_preflight_retention.sql |
| 20261106064055 | 20261106100000_public_default_privileges_hardening | 20261106064055_20261106100000_public_default_privileges_hardening.sql |

At that nine-record checkpoint, the local Monorepo deployment filenames matched every observed remote version/name pair. The seven imported SQL blobs remained byte-identical to their immutable source snapshots; the two forward migrations retained their reviewed blob hashes. Later additions are recorded in the superseding twelve-record inventory below. No remote migration record was repaired, no SQL was replayed, and no database DDL was run during that filename-alignment operation.

### Live access and performance notes

- Security Advisor: no security findings on the four historical tables; one expected INFO-level `rls_enabled_no_policy` notice on `known_place_requests`.
- Performance Advisor: one unindexed FK on `processing_jobs.preflight_id`,
  four policy-evaluation warnings, and eight unused-index INFO findings on a
  newly provisioned, low-volume database. Do not drop indexes or change owner
  policies without query-plan evidence.
- Current table grants remain limited to `postgres` and `service_role`;
  `anon` and `authenticated` have no direct table grants. All five tables
  have RLS enabled. The new owner map grants only service-role SELECT/INSERT/UPDATE.
- The daily `sarguardian-expired-preflight-cleanup` job is active at 03:20
  UTC. Its owner-only SECURITY DEFINER purge function retains an empty
  `search_path` and is executable only by `postgres`.

### Future-object default ACL hardening

Migration
`20261106064055_20261106100000_public_default_privileges_hardening.sql` was applied
successfully to this Free Tokyo target. It hardens defaults for **future
objects created by `postgres`**:
- revoke table and sequence defaults from `anon` and `authenticated` in
  `public`;
- revoke function EXECUTE defaults from `anon` and `authenticated` in
  `public`, plus revoke PostgreSQL's global default `PUBLIC EXECUTE` for
  future functions created by `postgres`;
- preserve `service_role` default grants.

A post-apply transaction created a test public table, sequence and function,
verified browser roles had no inherited privileges and `service_role`
retained access, then rolled back. No test object remains. Existing objects,
table ACLs, owner policies and trigger functions were not modified by this
migration.

The connection is `postgres` and cannot assume `supabase_admin`. Therefore
future Supabase-managed objects created by `supabase_admin` retain the
provider defaults; this migration does not attempt to change provider-owned
ACLs. Keep app-created objects owned by `postgres`, enable RLS on all new
tables and grant only the roles each object requires.

### Secret key handling and API integration

The API persistence module accepts a modern opaque `sb_secret_` key or a
legacy `service_role` JWT. The Preview environment variables are branch-scoped to
`migration/source-snapshot-import`; that branch has the expected API/Web
Preview variable sets. The security PR branch has no branch-specific Preview
variables, so its READY Vercel API Preview build verifies import/route startup
only—not Firebase Admin, Supabase server-role access, GitHub dispatch or Drive
retrieval. The API Production project has the server-only credentials, but
authenticated Firebase-to-Supabase use remains unverified. Never put a
Supabase service key in Web/`VITE_*` variables, GitHub source, workflow logs
or chat. Do not reuse the Dynamic Production key.

The Dynamic Production Supabase project remains separate and unchanged. The
Monorepo database is for isolated Preview integration and eventual reviewed
cutover; workflow credential setup and API dispatch cutover remain separate
acceptance gates.


## Superseding Monorepo target inventory — 2026-11-06

The nine-row Monorepo checkpoint recorded above predates three later additive
migrations. The current Tokyo project `qbmhpdprvxssqinnommz` now reports **12 remote
migration records**, with 12 matching canonical Git filenames under
`infrastructure/supabase/migrations/`. The three later additions are:

| Remote version | Recorded name | Canonical local filename |
|---|---|---|
| `20261106133548` | `processing_jobs_preflight_id_index` | `20261106133548_processing_jobs_preflight_id_index.sql` |
| `20261106134132` | `optimize_owner_read_rls_initplan` | `20261106134132_optimize_owner_read_rls_initplan.sql` |
| `20261106171458` | `known_place_request_ownership` | `20261106171458_known_place_request_ownership.sql` |

These are additive performance migrations: the first adds the
`processing_jobs.preflight_id` index; the second changes owner-read policy
expressions to an initplan-friendly scalar `(select auth.jwt())` form. The
current Performance Advisor reports six INFO-level unused-index notices only;
the earlier unindexed-FK and four RLS initplan warnings are no longer present.
The new `known_place_requests` migration adds the service-role-only owner
ledger; its RLS-enabled/no-browser-policy INFO notice is expected, with no
anon/authenticated grants. The owner table remains empty until an accepted
Known Place request is submitted.

The canonical migration root remains `infrastructure/supabase/`. The
`apps/api/supabase/` directory remains the unchanged source-snapshot import and
must not be used as the Monorepo target's migration root. See
`supabase-target.md` for the current schema, 80-row metadata mirror, empty
Known Place owner mapping and 12/12 migration alignment. The matching
`migration/supabase-history-alignment.json` records the exact local blob SHA.
