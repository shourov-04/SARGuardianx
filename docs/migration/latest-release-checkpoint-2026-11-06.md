# Latest SARGuardian Monorepo Release Checkpoint — 2026-11-06

**Release decision: NOT READY FOR PROCESSING CUTOVER.** The source migration is
merged to `main`, the new Monorepo Web and API Production deployments are
reachable, and the Tokyo Supabase metadata mirror is verified. User-data
processing remains disabled because repository privacy, Known Place request
ownership, authenticated API integration and external credential access are not
fully accepted.

## Repository and pull-request state

- Default branch `main` is at
  `c14e1e5843176b61d4ef9dcfeae8d7a819a71352`.
- PR #1 (migration foundation) is closed and merged. Merge commit:
  `975d60def84f73aac317e4deaee4cd8ecd09f2d5`.
- PR #2 (source snapshot import and promotion) is closed and merged. Merge
  commit: `c14e1e5843176b61d4ef9dcfeae8d7a819a71352`.
- GitHub comparisons confirmed `main`, `migration/bootstrap-and-provenance`
  and `migration/source-snapshot-import` all point to the same source head.
- PR #3, [security: block user-data workflows in public repositories](https://github.com/moshiour0/SARGuardian-Monorepo/pull/3),
  is Draft/Open. It adds a credential-free private-repository preflight to the
  four user-data entry workflows: Find Displacements, generic Known Place,
  author-exact P05023 and RiverShift.
- Latest PR #3 head at this checkpoint:
  `d76d438cad9337447142737d816ed600f97f1feb`. Snapshot Regression Tests
  [42261423074](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42261423074)
  completed **19/19** successfully, including the promoted API regression
  tests and exact source-history/promotion-override integrity. AOI dual-pin
  static/parser validation
  [42261422974](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42261422974)
  and Historical Secret Scan
  [42261423025](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42261423025)
  also completed successfully on this head.
- PR #3 includes a fail-closed repository-privacy preflight for all four
  user-data entry workflows and the Known Place owner-mapping API changes,
  tests, migration and provenance overrides. PR remains Draft/Open and is
  not merged; its code is not present in the Production API deployment.
- The Vercel GitHub checks for PR #3 still report the Hobby daily
  build-rate-limit failure. This is not an application compile/test failure;
  no Vercel deployment was created for the PR #3 head.

## Vercel Production deployment state

Both separate Monorepo Production projects are deployed from the same source
commit `c14e1e5843176b61d4ef9dcfeae8d7a819a71352`.

| Project | Deployment | State | Verified endpoint |
|---|---|---|---|
| API | `dpl_2c9FJKWDDNxSDgn9BpxB5cBEmjiK` | READY | `/health` HTTP 200; `/openapi.json` HTTP 200 |
| Web | `dpl_Cu9W3u3P7hXsv4Fr8yC3n5oLLxo2` | READY | Web root, JavaScript bundle and CSS bundle HTTP 200 |

The canonical domains are `sar-guardian-monorepo-api.vercel.app` and
`sar-guardian-monorepo-web.vercel.app`. The Web bundle contains the canonical
API origin four times and no old Preview API alias. The API OpenAPI document
contains the displacement, RiverShift and Known Place route groups.

The Web build completed with `tsc -b && vite build`. Vite reported a
568.68 kB minified JavaScript chunk, and `npm audit` reported 19 advisories
(10 moderate, 7 high, 2 critical). No `npm audit fix --force` was run. These
dependency and bundle findings require review before a public release.

No authenticated browser-to-API session was available to this verification,
so HTTP 200 on `/health` is not evidence that Firebase Admin token verification
and owner-scoped Supabase reads have passed end to end. The Vercel runtime-error
queries for both projects returned no errors in the selected last-hour window.

## Supabase Tokyo target

The dedicated Free Tokyo project `qbmhpdprvxssqinnommz` is
`ACTIVE_HEALTHY`, PostgreSQL 17.11.0.018. Its canonical migration root is
`infrastructure/supabase/migrations/`; the duplicate `apps/api/supabase/`
tree is preserved source-snapshot material, not the Monorepo deployment
migration root.

The target contains an 80-row historical metadata mirror plus a separate,
empty Known Place ownership table:

| Table | Rows |
|---|---:|
| `catalog_preflights` | 3 |
| `processing_jobs` | 2 |
| `displacement_jobs` | 51 |
| `river_shift_jobs` | 24 |
| **Historical mirror total** | **80** |
| `known_place_requests` | **0** (new owner map; not part of the mirror) |

The copy preserved IDs, owners, request/manifest snapshots, state, callback
sequence, creation time and historical run/Drive references. Trigger-managed
`updated_at` changed on the 75 Displacement/RiverShift rows during permitted
state-transition replay; all other compared fields matched. No raw NISAR
binary products were copied. The source Production rows were not updated or
deleted.

All five tables have RLS enabled. On the four historical job tables, browser
roles have no direct table SELECT/INSERT/UPDATE privileges, and four owner-read
policies remain in place. The new `known_place_requests` table stores only
`request_id`, `owner_uid`, `request_kind`, `dispatch_state` and
`created_at`; it stores no AOI or science payload. It currently has **0 rows**.
Its only application grants are `service_role` SELECT/INSERT/UPDATE; anon and
authenticated have no table grants or policy. Security Advisor now reports one
INFO-level `rls_enabled_no_policy` notice for this intentionally server-only
table; no browser access is granted. The FK index and four RLS initplan
improvements remain applied.

The target now reports **12 remote migration records**, all matched by
canonical Git filenames under `infrastructure/supabase/migrations/`. The new
entry is `20261106171458_known_place_request_ownership.sql`; its local blob
SHA is recorded in `migration/supabase-history-alignment.json`. The full
12-row mapping is in [supabase-target.md](supabase-target.md) and
[supabase-migration-lineage.md](supabase-migration-lineage.md).

Two historical `processing_jobs` rows remain queued but reference expired
preflights. They are historical metadata and must not be re-dispatched. There
are zero active Displacement or RiverShift jobs in the mirrored snapshot.

## Configuration and integration state

- Production Vercel environment inventory: API 35 variables, Web 9 variables.
  Server credentials are on the API project; the Web project has no
  server-side Supabase, Firebase Admin, GitHub Actions or Drive secret.
- Both API production processing switches,
  `DISPLACEMENT_ACTIONS_ENABLED` and `RIVERSHIFT_ACTIONS_ENABLED`, are
  explicitly `false`.
- The owner reports Firebase signup and Google sign-in now succeed after the
  two Preview domains were added to Authorized Domains. Server-side Firebase
  Admin ID-token verification by the Production API remains unverified.
- GitHub Actions token repository/workflow scope has not been independently
  proven by a dispatch-free authenticated API probe.
- Google Drive artifact retrieval using the Monorepo API identity remains
  unverified.
- No workflow was dispatched during this checkpoint. No NISAR raw data was
  downloaded, processed or uploaded by the Monorepo engines.

## Security blockers before enabling any user-data workflow

### 1. Public repository boundary

GitHub reports `SARGuardian-Monorepo` as **Public**. Repository visibility
has not been changed. PR #3 adds a read-only GitHub metadata check and stops
all four user-data entry workflows unless `private=true`, before checkout,
Earthdata/Drive credentials or result-artifact steps. Therefore the new
Monorepo user-data workflows remain intentionally blocked while the
repository is public. A private worker repository with a reviewed workflow
target is the alternative if the source Monorepo is to remain public.

### 2. Known Place request ownership

The owner-isolation fix is implemented on PR #3 and its current-head
regression suite passes. The API now writes a UUID-to-`owner_uid` mapping
before dispatch, distinguishes `generic` from `paper_reproduction`, and
checks that mapping before generic status, result, bundle and author-exact
status lookups. Unknown IDs and another user's IDs receive the same 404; the
GitHub/Drive lookup is not called on that path. Dispatch is fail-closed if the
mapping cannot be persisted.

The additive migration
`20261106171458_known_place_request_ownership.sql` is applied to the Tokyo
target. The table has RLS enabled, no browser grants or policy, service-role
SELECT/INSERT/UPDATE only, and 0 rows. Snapshot Regression Tests passed 19/19,
including the promoted API regression suite, and the history alignment
contract was updated to 12 migrations. However, PR #3 is still Draft/Open and
the Production API remains on the old `c14e1e5` deployment. The fix is not
Production-live until PR review/merge, an API deploy, and authenticated
cross-account runtime verification.

### 3. End-to-end acceptance

Still pending: authenticated Firebase Admin + Supabase read verification,
GitHub token scope proof, Drive artifact retrieval, API Production deployment
of the owner-isolation code after merge, live cross-account owner verification,
per-engine credential-free mock dispatch/callback tests, private result
retrieval, controlled positive science pilots, independent science review and
rollback rehearsal.

## Safety invariants

- Keep `DISPLACEMENT_ACTIONS_ENABLED=false` and
  `RIVERSHIFT_ACTIONS_ENABLED=false`.
- Keep repository workflow gates closed. Do not enable a gate simply to test
  credentials or a workflow.
- Never re-dispatch the two expired-preflight `processing_jobs` rows.
- Do not alter the original Dynamic/Backend Production routing, Production
  database, source repositories or rollback assets as part of this checkpoint.
- A READY deployment, passing static CI or a successful login does not by
  itself constitute a scientific pilot or Production cutover.

