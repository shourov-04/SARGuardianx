# Production Supabase data migration plan — 2026-11-06

## Decision and current migration status

The schema/history migration and a copy-only Production metadata transfer have both been executed. On 2026-11-06, 80 rows were copied from the active source project `SARGuardian_Dynamic` (`ufwjmhivvnoewjsbteey`) into the isolated target `SARGuardian-Monorepo` (`qbmhpdprvxssqinnommz`, Tokyo / `ap-northeast-1`). The source remains the live Production database. It was not updated, deleted from, reset, or used to dispatch any new workflow.

Final source/target counts match exactly: 3 `catalog_preflights`, 2 `processing_jobs`, 51 `displacement_jobs`, and 24 `river_shift_jobs`. The two queued `processing_jobs` rows were copied as metadata only and were not dispatched. All 75 Displacement/RiverShift jobs were terminal in the observed source snapshot; state histograms, primary IDs, callback sequences, accepted request data, result/manifest metadata, GitHub run references, and Drive artifact references were preserved. Because the target's lifecycle triggers set `updated_at = now()` on permitted state transitions, the 51 Displacement and 24 RiverShift target rows have a new `updated_at` timestamp reflecting the copy operation. Their source timestamps were not changed. `created_at` and all other compared fields match.

This is **not a Production cutover**. The old Production project remains authoritative and active. The target copy is isolated; no live traffic, custom domain, Production environment, Action dispatch, or old Supabase project was switched.

## Aggregate-only source inventory

Observed on 2026-11-06 using read-only counts and aggregate status queries:

| Table | Source rows | Owner count | State / retention detail |
|---|---:|---:|---|
| `catalog_preflights` | 3 | 1 | All 3 expired; 2 are FK-referenced by `processing_jobs`; 1 is unreferenced |
| `processing_jobs` | 2 | 1 | 2 queued metadata rows; neither is an active dispatched worker |
| `displacement_jobs` | 51 | 5 | 36 succeeded, 14 failed, 1 cancelled; 44 have a GitHub run ID; 0 queued/dispatching/running |
| `river_shift_jobs` | 24 | 2 | 4 succeeded, 20 failed; 23 have a GitHub run ID; 0 queued/dispatching/running |
| **Total** | **80** | — | No active Displacement or RiverShift job at the time of this snapshot |

The query returned only counts, distinct-owner counts and state groupings. No owner UID, AOI WKT, artifact URL, result payload or row body was read into this report. See the machine-readable aggregate snapshot at [`migration/supabase-production-data-inventory-2026-11-06.json`](../../migration/supabase-production-data-inventory-2026-11-06.json).

## Schema compatibility

The four source and target public tables were compared read-only:

| Table | Source columns | Target columns | RLS | Result |
|---|---:|---:|---|---|
| `catalog_preflights` | 7 | 7 | enabled | Match |
| `processing_jobs` | 13 | 13 | enabled | Match |
| `displacement_jobs` | 28 | 28 | enabled | Match |
| `river_shift_jobs` | 27 | 27 | enabled | Match |

All four table names, all column names/counts, RLS enablement and the FK contract match. The FK is `processing_jobs.preflight_id → catalog_preflights.id`. The target is schema-compatible for a controlled metadata migration, but schema parity alone is not a data migration.

## Data preservation rules

1. **Take a source backup/snapshot first.** Use an authenticated, encrypted, out-of-repository transfer method. Do not export database rows into GitHub issues, commit history or ChatGPT.
2. **Use a cutover snapshot, not this staleable row count.** Recheck source row counts, states, owner counts and active states immediately before import. The source may continue to receive writes until a controlled freeze.
3. **Preserve identity and ownership.** Keep primary UUIDs, `owner_uid`, idempotency keys, request fingerprints, callback sequence numbers, `created_at`, accepted request snapshots, result summaries, artifact manifests and error/status metadata unchanged. Exception: on 51 Displacement and 24 RiverShift terminal rows, the target lifecycle trigger rewrites `updated_at` during the permitted state-transition replay. Those source `updated_at` values remain unchanged in the original Production database; the target's refreshed timestamps are explicitly recorded and excluded from row checksums.
4. **Import in dependency order:** `catalog_preflights` → `processing_jobs` → `displacement_jobs` → `river_shift_jobs`. Preserve the two expired preflight rows referenced by queued processing records. The unreferenced expired preflight remains subject to the existing expiry/grace-period cleanup policy; do not weaken retention to keep it indefinitely.
5. **Never re-dispatch imported rows.** The two legacy `processing_jobs` entries are queued metadata, not an instruction to create new NISAR downloads. Import them as metadata only unless the owner separately authorizes a new processing request.
6. **Keep worker-run provenance.** The 44 Displacement and 23 RiverShift non-null GitHub run IDs/URLs in the current source point to historical Backend runs. At this snapshot all Displacement/RiverShift states are terminal, so they do not need live-run polling. If a later final snapshot contains any `dispatching` or `running` job, let it finish on the original Backend or explicitly preserve its original repository/ref before redirecting API status polling.
7. **Keep Drive artifacts external.** Supabase stores Drive file IDs, byte/SHA receipts and artifact metadata; the binary artifacts remain in Drive. Do not redownload/reupload raw NISAR data as a side effect of job-row migration. Verify read access to successful result objects using the intended Monorepo API Drive identity before cutover.
8. **Verify before switching.** Compare per-table counts, distinct-owner counts, state histograms, primary-key sets/checksums, FK references, request fingerprints, callback sequences and artifact receipt structure. Test result retrieval for a successful Displacement and RiverShift job. Keep the original Production project read-only/available for rollback.

## Important runtime dependencies

- Current Displacement and RiverShift status polling uses the configured GitHub repository when it looks up a `github_run_id`. Old run IDs belong to `moshiour0/SARGuardian-backend`. This is safe for the observed snapshot because all 75 Displacement/RiverShift rows are terminal; recheck at cutover. Never assume a run ID can be queried in Monorepo merely because the job row was copied.
- Successful Displacement dashboard/artifact routes use stored Drive artifact IDs and checksums. RiverShift artifact retrieval uses the stored `artifact_manifest` Drive IDs, byte count and SHA-256. The Monorepo API therefore needs an authorized Drive reader that can still access the existing result folder.
- Generic/author-exact Known Place history lives in GitHub Actions runs/artifacts, not in these four Supabase tables. Keep Backend run URLs/artifacts available as historical evidence; new Monorepo Known Place requests create new Monorepo runs.

## Completed copy-only transfer evidence

- Source and target row counts were re-read after import. Both sides report 3 / 2 / 51 / 24 rows respectively (80 total).
- Per-row comparisons matched all fields for the 3 preflight and 2 processing rows. For the 51 Displacement and 24 RiverShift rows, every compared field except `updated_at` matched; `created_at`, state and callback sequence were exact.
- The FK check found zero orphan processing jobs.
- All four target tables retain RLS. The owner-read policies remain restricted to `authenticated` and compare JWT subject to `owner_uid`. All six user-defined integrity/immutability/lifecycle triggers were rechecked enabled after import.
- The target's transition triggers were not disabled. Historical terminal job states were recreated through the allowed lifecycle path; no workflow dispatch was made.
- A forward migration adds `processing_jobs_preflight_id_idx` for the `preflight_id` foreign key; the unindexed-FK Advisor finding cleared. It is recorded as remote migration `20261106133548_processing_jobs_preflight_id_index`.
- A second forward migration rewrites all four owner-read policies to use `((select auth.jwt()) ->> 'sub') = owner_uid`; the RLS initplan Advisor warnings cleared without changing the `authenticated`-only ownership rule. It is recorded as remote migration `20261106134132_optimize_owner_read_rls_initplan`. Security Advisor: zero findings. Remaining `unused_index` notices are informational on a new/just-migrated database; no index was removed.
- The separate Production backup requirement was not retroactively satisfied by this copy. Keep the source project available and make an independent backup before any future cutover or destructive operation.

## Remaining cutover gates and safety boundary

1. Recheck source counts, owner/state aggregates and active rows immediately before cutover; this copy is a snapshot and the source remains writable.
2. Create and verify an independent source backup. Do not use the target copy as the only rollback point.
3. Validate the Monorepo API's real Firebase Admin verification and Supabase service-role connectivity with a signed-in browser session. The public `/health` route alone is not proof.
4. Verify read access to existing successful Displacement and RiverShift Google Drive artifacts with the Monorepo API's configured Drive identity. Metadata references were copied; the external binaries were not.
5. Validate GitHub Actions token scope, workflow files/refs and callback secrets without starting science workflows. Keep `DISPLACEMENT_ACTIONS_ENABLED=false` and `RIVERSHIFT_ACTIONS_ENABLED=false` until explicit positive pilots are authorized.
6. Test rollback and result retrieval, recheck any queued/active work, and obtain an explicit cutover decision before changing production routing.

The copy-only data milestone is complete; the migration as a whole is **not production-ready and not cut over**. The original Production Supabase project remains untouched and authoritative.
