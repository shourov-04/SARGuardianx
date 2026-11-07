# Supabase Production metadata copy run — 2026-11-06

## Scope

This records a copy-only metadata migration from the still-active Dynamic Production Supabase project (`ufwjmhivvnoewjsbteey`) into the isolated Monorepo target (`qbmhpdprvxssqinnommz`, Tokyo / `ap-northeast-1`). It is not a traffic cutover and does not make the Monorepo Production.

No raw NISAR binaries, Cloud Drive files, or GitHub Actions runs were copied or re-executed. Only the four Supabase job metadata tables were copied.

## Reconciled row counts

| Table | Dynamic source | Monorepo target | Result |
|---|---:|---:|---|
| `catalog_preflights` | 3 | 3 | Exact row comparison |
| `processing_jobs` | 2 | 2 | Exact row comparison |
| `displacement_jobs` | 51 | 51 | All fields except trigger-managed `updated_at` match |
| `river_shift_jobs` | 24 | 24 | All fields except trigger-managed `updated_at` match |
| **Total** | **80** | **80** | **80 / 80 copied** |

Source row counts were re-read after the copy and remained unchanged. The target copy preserves the source primary UUIDs, owner identifiers, idempotency keys, request fingerprints, AOI/request snapshots, product settings, result summaries, manifests, callback sequences, GitHub run IDs/URLs, Drive artifact references, errors, and `created_at` values.

The target database's state-transition functions intentionally set `updated_at = now()` on permitted job updates. To preserve those guards, the 51 Displacement and 24 RiverShift rows were recreated through allowed lifecycle transitions rather than disabling triggers. As a result, their target `updated_at` timestamps represent the migration replay time; the source rows and source timestamps were not changed. State and callback-sequence values were restored and verified exact.

## State and integrity checks

- `processing_jobs`: 2 queued metadata records. They remain metadata only; no worker was dispatched.
- `displacement_jobs`: 36 succeeded, 14 failed, 1 cancelled; 0 active.
- `river_shift_jobs`: 4 succeeded, 20 failed; 0 active.
- `catalog_preflights`: 3 copied, including expired preflights referenced by the queued processing records.
- FK check: 0 orphan `processing_jobs.preflight_id` references and owner match preserved.
- RLS: enabled on all four target tables.
- Owner-read policies: `authenticated` role only; JWT subject must match `owner_uid`.
- Integrity/lifecycle triggers: all six user-defined triggers rechecked enabled after the transfer.
- Row integrity: each preflight and processing row matched fully; all Displacement/RiverShift columns other than trigger-managed `updated_at` matched per-row checksums. The `created_at`, state, and callback sequence columns matched exactly.

## Operational boundary

- No source Production row was updated or deleted.
- No target job was dispatched to GitHub Actions.
- `DISPLACEMENT_ACTIONS_ENABLED=false` and `RIVERSHIFT_ACTIONS_ENABLED=false` remain the Preview configuration.
- Existing Drive artifact binaries remain in Drive. Their metadata pointers were copied, but live Drive read access from the Monorepo API has **not** yet been tested.
- No independent pre-copy source backup was created. The original source project remains active and available, but that does not replace the separate backup required before a future cutover or destructive operation.
- The source is not frozen. A final cutover must take a fresh source snapshot and repeat all counts/checks before routing is switched.

## Follow-on schema optimization

Two additive forward migrations were applied and recorded in `migration/supabase-history-alignment.json`:

- `20261106133548_processing_jobs_preflight_id_index` adds `processing_jobs_preflight_id_idx` to support the `preflight_id` foreign key. The unindexed-FK advisor finding cleared.
- `20261106134132_optimize_owner_read_rls_initplan` rewrites all four owner-read predicates as `((select auth.jwt()) ->> 'sub') = owner_uid`. The RLS initplan advisor warnings cleared; the Security Advisor remains at zero findings.

The remaining `unused_index` notices are informational on a new/just-migrated database and do not justify dropping operational indexes. No owner scope, integrity trigger, or existing index was removed.
