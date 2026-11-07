# SARGuardian-Monorepo Supabase target

## Project identity

- Project: `SARGuardian-Monorepo`
- Project ref: `qbmhpdprvxssqinnommz`
- Region: Japan/Tokyo (`ap-northeast-1`)
- API URL: `https://qbmhpdprvxssqinnommz.supabase.co`
- Plan: Free; configured target cost $0/month
- PostgreSQL: 17.11.0.018
- Live state at the 2026-11-06 recheck: `ACTIVE_HEALTHY`

The canonical Monorepo migration directory is `infrastructure/supabase/migrations/`.
The duplicate `apps/api/supabase/` tree is an intentionally preserved source snapshot
and is not the canonical Monorepo deployment migration path. Do not add new target
migrations to that source-snapshot tree.

All future CLI commands must explicitly target project ref
`qbmhpdprvxssqinnommz`. The imported `infrastructure/supabase/config.toml` is
retained as exact provenance; do not infer a target from its historical
`project_id` value.

## Current schema and metadata mirror

The four historical application/job tables remain present and RLS-enabled. A fifth private owner-mapping table, `known_place_requests`, has been added for Known Place request correlation. The target contains
an **80-row metadata-only mirror** of the original Dynamic Production inventory:

| Table | Rows | Current interpretation |
|---|---:|---|
| `catalog_preflights` | 3 | Historical catalogue preflight manifests |
| `processing_jobs` | 2 | Historical queued metadata; linked preflights have expired |
| `displacement_jobs` | 51 | 36 succeeded, 14 failed, 1 cancelled |
| `river_shift_jobs` | 24 | 4 succeeded, 20 failed |
| **Total** | **80** | **Historical metadata mirror; no raw NISAR binaries copied** |

The new `public.known_place_requests` table currently has **0 rows**. It stores only
`request_id`, Firebase `owner_uid`, `request_kind` (`generic` or
`paper_reproduction`), `dispatch_state`, and `created_at`. It stores no AOI WKT,
polygon geometry, science payload, or artifact body. It is not part of the 80-row
historical mirror.

Post-copy source/target comparisons reconciled every field except trigger-managed
`updated_at` on the 75 Displacement and RiverShift rows. The target lifecycle
trigger refreshed those timestamps during permitted state-transition replay; source
timestamps in the original Production project were not modified. No pre-copy full-row
checksum snapshot was captured, so do not describe that particular part of the copy as
a before/after cryptographic snapshot. All other compared fields, IDs, owners,
request snapshots, callback sequences, run references, Drive references and result
summaries matched.

All three catalogue preflights are expired. The two historical `processing_jobs`
rows remain `queued`, but their linked preflights expired on 2026-11-02. Preserve
them as history; **never re-dispatch them**. There are zero active
`displacement_jobs` and zero active `river_shift_jobs` in the copied snapshot.
No source rows were updated or deleted by the metadata-copy process.

## Access control and advisors

- RLS is enabled on all four historical application/job tables and the new
  `known_place_requests` table.
- The application tables grant direct table access to `service_role`; `anon` and
  `authenticated` have no direct table SELECT/INSERT/UPDATE privileges.
- Four owner-read policies exist on the four historical tables for authenticated
  identities, using the JWT `sub` claim against `owner_uid`. They are defense in
  depth; browser table access is not the application access path.
- `known_place_requests` intentionally has **no browser policy** and no browser
  grants. Its only application grants are `service_role` SELECT/INSERT/UPDATE;
  DELETE remains revoked. Its RLS-enabled/no-policy INFO notice is expected for
  this server-only mapping table, not an access path for browser clients.
- The API uses a server-only Supabase key and adds explicit `owner_uid` filters to
  the owner-scoped job queries. Do not expose the server key in the Web project.
- Security Advisor: the existing four tables had no security findings. After the
  owner-mapping table was added, the Advisor reports one INFO-level
  `rls_enabled_no_policy` notice for `known_place_requests`. This is intentional:
  no browser role has table grants or a row policy; only the API server role is
  granted the three required operations.
- Performance Advisor: six `unused_index` findings at INFO level. The
  `processing_jobs.preflight_id` FK index and the four owner-policy
  initialization-plan improvements have already been added in forward migrations.
  Do not drop unused indexes without query-plan and production-volume evidence.

The forward migration
`20261106064055_20261106100000_public_default_privileges_hardening.sql`
revokes browser-role default privileges on future public objects created by
`postgres`, while preserving required `service_role` grants. It does not change
Supabase-managed `supabase_admin` defaults or existing managed objects.

## Migration history — current 12/12 alignment

The Tokyo target reports **12 remote migration records**. All 12 are represented by
matching local filenames under `infrastructure/supabase/migrations/`:

| Remote version | Recorded migration name | Canonical local filename |
|---|---|---|
| `20261106000844` | `20261017143644_processing_jobs` | `20261106000844_20261017143644_processing_jobs.sql` |
| `20261106000850` | `20261022203034_displacement_jobs` | `20261106000850_20261022203034_displacement_jobs.sql` |
| `20261106000856` | `20261023141449_displacement_active_request_guard` | `20261106000856_20261023141449_displacement_active_request_guard.sql` |
| `20261106000901` | `20261024111404_scientific_request_contract` | `20261106000901_20261024111404_scientific_request_contract.sql` |
| `20261106000905` | `20261027003643_place_target_contract` | `20261106000905_20261027003643_place_target_contract.sql` |
| `20261106000909` | `20261103100000_river_shift_jobs` | `20261106000909_20261103100000_river_shift_jobs.sql` |
| `20261106000923` | `20261104120000_river_shift_analysis_modes` | `20261106000923_20261104120000_river_shift_analysis_modes.sql` |
| `20261106000928` | `20261105205909_catalog_preflight_retention` | `20261106000928_20261105205909_catalog_preflight_retention.sql` |
| `20261106064055` | `20261106100000_public_default_privileges_hardening` | `20261106064055_20261106100000_public_default_privileges_hardening.sql` |
| `20261106133548` | `processing_jobs_preflight_id_index` | `20261106133548_processing_jobs_preflight_id_index.sql` |
| `20261106134132` | `optimize_owner_read_rls_initplan` | `20261106134132_optimize_owner_read_rls_initplan.sql` |
| `20261106171458` | `known_place_request_ownership` | `20261106171458_known_place_request_ownership.sql` |

The canonical path is `infrastructure/supabase/`; the 8-file
`apps/api/supabase/migrations/` directory is the unchanged imported source snapshot,
not an incomplete deployment migration directory. The 12/12 comparison above is a
read-only comparison of the remote migration inventory and canonical Git filenames.
Do not run `db push`, reset, migration repair or historical DDL replay as part of
that comparison.

## Server key and Vercel separation

The API Production environment inventory contains `SUPABASE_URL` and
`SUPABASE_SERVICE_ROLE_KEY` as server-side variables. The Web Production project
contains no server-side Supabase key. Secret values remain encrypted in Vercel and
must not be copied into Git, chat, client bundles or Actions logs.

The API service-role token was not independently decrypted or tested by this
read-only inventory. API startup now includes a zero-row access probe against
`known_place_requests`; the new owner-scoped Known Place code remains on the
unmerged PR #3 branch until its full regression checks pass. The API's live `/health` endpoint returned HTTP 200, but
that alone is not proof of an authenticated database read by a real Firebase user.
The signed-in owner-scoped API/Supabase smoke test remains an acceptance gate.

## Cutover boundary

This target is separate from the existing `SARGuardian_Dynamic` Production project.
The original Dynamic Production database, its routing and source rows remain the
rollback source. No NISAR raw files were downloaded or uploaded for this mirror.
All Monorepo processing switches remain disabled; the two historical queued
`processing_jobs` records must not be re-dispatched.
