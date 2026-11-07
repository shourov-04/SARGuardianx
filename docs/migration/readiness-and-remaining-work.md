# SARGuardian Monorepo readiness and remaining work

> **Latest checkpoint:** this file is a historical timeline. For the current
> deployment, Supabase, security and release-gate state, read
> [latest-release-checkpoint-2026-11-06.md](latest-release-checkpoint-2026-11-06.md).
> Later verified state in that checkpoint supersedes older sections below.
>
**Last updated:** 2026-11-06  
**Working branch:** `security/private-actions-artifact-guard` (Draft PR #3; not merged)  
**Current production state:** unchanged; original Dynamic app/API and backend Actions remain authoritative.

## Production job data — non-destructive metadata mirror completed

The isolated Tokyo Monorepo target contains an 80-row metadata-only mirror of the
original Production inventory (3 preflights, 2 processing jobs, 51 Displacement
jobs, 24 RiverShift jobs). The original source rows were not updated or deleted;
no raw NISAR binaries were copied. The new `known_place_requests` owner-mapping
table is separate from that mirror and currently has 0 rows. Two historical
`processing_jobs` remain queued with expired linked preflights and must never be
re-dispatched. See [the target schema and history](supabase-target.md) and
[the data migration plan](supabase-production-data-migration-plan.md).

## Prior complete migration verification before current Known Place pin overlay — 2026-11-06

- Previous code/workflow head `8454a15fe2e014afa1297e2c03faff132734e998`: [Snapshot Regression Tests 42182301730](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42182301730) passed **19/19** before the latest active Known Place source-pin correction. The current correction has its own new CI runs and must pass separately before this branch is marked green.
- Additional same-head checks: Backend source snapshot suites 2/2 passed, Migration Metadata Validation passed, Historical Secret Scan passed, Runner Allocation Diagnostic passed, Retention Archive Regression passed, Dashboard asset tests passed, and dual-pin AOI validation passed.
- Docs/readiness-only head `16d1ac1866d2df66443badb40b645cb844afd018` follows that code head and is running its own final PR checks. Do not call the docs-only head fully green until its own Snapshot Regression finishes.
- Monorepo Supabase local migration directory now contains nine files whose 14-digit filename prefixes and suffix names match the nine live migration records returned by the Monorepo project inventory. Seven imported SQL blobs are still byte-identical to their immutable Dynamic source-snapshot files; the two forward migration blobs are unchanged. CI checks every path and blob SHA. No remote migration record, schema, table or data was changed by this filename alignment.
- The existing Dynamic Production Supabase project has a separate lineage and is not covered by the Monorepo nine-record alignment manifest. Keep its reconciliation separate.
- PR #2 remains Draft/unmerged. Existing Dynamic/Backend Production routing, Vercel Production aliases and Production Supabase are unchanged.


## 2026-11-06 active migration scope decision — evidence-based product paths

The migration does **not** activate all 82 historic workflow instances. Their source snapshots remain preserved, but the current Dynamic application call graph contains two active application paths and two independently gated features.

| Tier | Workflow count | Contents | Evidence / acceptance |
|---|---:|---|---|
| **Primary application runtime** | 5 | Find Displacements dispatcher → dashboard engine → product worker; generic Known Place dispatcher → generic two-polygon analysis engine | Find Displacements run [42097077601](https://github.com/moshiour0/SARGuardian-backend/actions/runs/42097077601) completed, recovered GUNW-002 via failed-only retry, assembled dashboard and reported terminal callback. Generic Known Place Backend-main dispatch page returned 16 runs: 8 success, 7 failure, 1 cancelled; successful runs [41533701551](https://github.com/moshiour0/SARGuardian-backend/actions/runs/41533701551) and [41533582770](https://github.com/moshiour0/SARGuardian-backend/actions/runs/41533582770) retained result artifacts at exact generic reusable workflow pin 0e0611c. |
| **Connected gated feature paths** | 3 | RiverShift GCOV; author-exact P05023 dispatcher and reusable replay | RiverShift run [42089984247](https://github.com/moshiour0/SARGuardian-backend/actions/runs/42089984247) matched 14/14 granules but stopped safely at EVENT_WINDOW_NOT_BRACKETED. Author-exact run [41423614257](https://github.com/moshiour0/SARGuardian-backend/actions/runs/41423614257) passed consent and Drive derived-bundle receipt, but source-manifest completeness failed and raw cleanup was blocked. |
| **Migration CI** | 7 | Snapshot/source regression, metadata, secret scan, retention, dashboard assets and AOI code validation | Validation-only; not product runtime dependencies. |

The Known Place generic engine now uses the active Backend main workflow/source pin 0e0611c12913044787ee84a39fa60a81d30ae516. The Monorepo PR #85 research snapshot remains preserved, but PR #85 itself is still Draft/Open on feat/know-place-analysis and was not merged to Backend main. The detailed lineage and exact 10-file source overlay are recorded in [active runtime scope](active-runtime-scope-2026-11-06.md) and migration/active-runtime-pins/known-place-generic-0e061.json.

### What this scope decision changes

- The current application cutover graph contains only Find Displacements and generic Known Place.
- RiverShift remains connected to the API but dispatch stays false until a scientifically eligible event window completes a positive-case GCOV pilot.
- Author-exact P05023 remains a separate manual-consent path with fixed workflow/code pins; its gate stays false until a complete source-manifest, science, Drive and cleanup acceptance passes.
- Historical diagnostics, one-off renderer jobs, alternate forks and unused worker variants remain archived/provenance-only; they are not user-job runtime dependencies.
- Keep all 82 source workflow instances preserved in the inventory and immutable snapshots. This is provenance completeness, not a requirement to activate all of them.
- Existing Dynamic Production, Backend workflow targets, callbacks, Vercel Production aliases and Production Supabase remain unchanged.

### Remaining completion gates

1. Pass current-head Snapshot Regression, Backend Source Snapshot Regression, Historical Secret Scan and all independent CI checks after the Known Place pin correction.
2. Configure Monorepo-only API Preview credentials (Firebase Admin, Supabase service role, GitHub dispatch, callback HMAC and Drive result-read OAuth) and Monorepo Actions Secrets (Earthdata and Drive OAuth/parent folder). Do not commit or paste secret values.
3. Verify authenticated Preview login, owner-scoped Supabase persistence/readback, API → workflow request correlation, status polling, signed callbacks, terminal failure propagation and artifact access.
4. Run a catalog-only Known Place Preview, then a controlled positive two-polygon measurement pilot against the exact 0e061 pin; confirm Drive receipt and API artifact access.
5. Run Find Displacements in Monorepo with an isolated/mock dispatch then a controlled real-data pilot; verify product retries, dashboard output, Drive receipts and terminal callback.
6. Complete a positive-case RiverShift run with a genuinely bracketed event date; verify 15-product batch barriers, failed-only retries, output, Drive receipt and signed callback.
7. Keep Author-Exact P05023 manual-consent-gated until the full source-manifest and scientific validation succeeds and raw cleanup is independently verified.
8. Confirm the nine Monorepo Supabase migration filename/version/name pairs using an authenticated read-only CLI v3 listing if available; no db push, repair, replay or reset is justified because the connected inventory already matches the local alignment manifest. Keep original Dynamic Production lineage separate.
9. Review Web advisories/bundle size, licensing, science validity and rollback; then merge PRs in sequence. Production cutover requires explicit owner approval.

**Superseded status:** this section predates the current `9bd6858` CI and Preview verification. The authoritative current checkpoint is recorded in the latest live reconciliation section below.


> **Current-head verification — 2026-11-06, code/workflow head `f6f48462a3546bccfe551549c931c87523d35fa8`:**
> - [Snapshot Regression Tests 42176353725](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42176353725): **19/19 jobs passed** on this exact head. This includes the API's Monorepo-only 13-query owner-scope guard and the new Supabase future-object default-privilege SQL contract, as well as Web, Dynamic API/frontend, Find Displacements, Known Place, RiverShift, NISAR, workflow inventory and source blob-integrity jobs.
> - [Backend Source Snapshot Regression 42176353744](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42176353744): immutable source suites passed — Backend main **595 passed, 1 skipped**; Known Place PR #85 **563 passed, 1 skipped**.
> - [Migration Metadata Validation 42176353822](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42176353822), [Historical Secret Scan 42176353743](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42176353743), [Runner Allocation Diagnostic 42176353508](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42176353508), [Retention Archive Regression 42176353747](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42176353747), [dual-pin AOI validation 42176353609](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42176353609) and [Dashboard asset builder 42176353425](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42176353425): all successful.
> - Workflow inventory: **82/82** source workflow instances (Dynamic 7, Backend main 35, Known Place PR #85 40), **42** Monorepo root workflow files, **39** mapped root destinations; four legacy variants are archive-only. Contract-equivalence review and safe promotion are still separate from static inventory completeness.
> - The P05023 structural gate validates exact source object `ab547ecc82bcc4d6ccef545a59852536c2beacc6`, manual-only launch, explicit consent gates, distinct GUNW+GOFF inputs, Drive receipt and no automatic raw deletion. It has not been live-dispatched.
> - Monorepo Preview Vercel API [deployment HJtpYcp](https://vercel.com/moshiour-rahman-sarkers-projects-2cebe363/sar-guardian-monorepo-api/HJtpYcpCWypvTsMVBwQDnv4RrNb7) is READY on this code head, Preview-only (`target=null`); `/health` returned HTTP 200. Web Preview [deployment 2U6HvM](https://vercel.com/moshiour-rahman-sarkers-projects-2cebe363/sar-guardian-monorepo-web/2U6HvMTE9sqTU6DM2VaZgBV4PhB4) is READY on the immediately prior code/test head. Neither has a Production alias.
> - The Free Tokyo Supabase target `qbmhpdprvxssqinnommz` is ACTIVE_HEALTHY at `https://qbmhpdprvxssqinnommz.supabase.co`. It has four empty RLS-enabled app tables and zero Security Advisor findings. Nine migration rows exist. The local `infrastructure/supabase/migrations/` filenames are now keyed to the nine exact remote version/name pairs in `migration/supabase-history-alignment.json`; the seven imported SQL blobs remain exact source copies. A final authenticated CLI v3 `migration list --remote` check remains, and no remote repair or DDL replay has been done.
> - Forward migration `20261106064055_20261106100000_public_default_privileges_hardening.sql` was applied to the Monorepo Preview DB. Future public tables/sequences created by `postgres` no longer inherit anon/authenticated grants; future functions also lose browser EXECUTE plus PostgreSQL's global default PUBLIC EXECUTE. `service_role` defaults remain intact. A transactional post-apply probe verified the table, sequence and function privileges and rolled back all probe objects. Supabase-managed `supabase_admin` defaults are untouched because the connected `postgres` role cannot assume that provider role.
> - API Preview has all four Monorepo workflow destination names/refs, callback base URLs, CORS and fail-closed API flags. It still lacks `SUPABASE_SERVICE_ROLE_KEY`, Firebase Admin JSON, GitHub PAT, HMAC callback secrets and Drive OAuth values. Authenticated login, persisted job writes, signed callbacks and private Drive retrieval are not yet runtime-tested.
> - All original Dynamic Production Web/API projects, Backend workflow destinations and Dynamic Production Supabase remain unchanged. No real NISAR downloads, RiverShift GCOV execution, Drive uploads or Production cutover were performed. Public Monorepo visibility is explicitly authorized; secret values remain outside Git history.

> **RiverShift root-workflow contract update — 2026-11-06, commit `3caf888764f9726773879b55463c17c111ae53a4`:**
> - The promoted engine's original `test_workflow_retry_contract.py` was restored byte-for-byte to its Backend source blob `200658f9889116bbdf2edb0753dfc7121985b827`; immutable source snapshot paths were not changed.
> - A new Monorepo-only test, `tools/tests/test_monorepo_rivershift_workflow_contract.py`, is run by the promoted RiverShift regression job. It checks the root workflow's 21 jobs (fail-closed preflight + 20 processing jobs), sequential 15-product batch barriers, retry-wave validation, final reconciliation dependency, read-only workflow permission and least-scope Earthdata/Drive/callback secrets.
> - The root workflow test was added to `snapshot-regression-tests.yml`. [Snapshot Regression Tests 42113191409](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42113191409) completed **17/17 jobs successfully**, including the new RiverShift root-workflow contract and the archived OPERA/RTC regression checks. [Historical Secret Scan 42113191759](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42113191759), [Migration Metadata Validation 42113191408](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42113191408), and [Runner Allocation Diagnostic 42113191766](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42113191766) also passed.
> - This verifies the workflow definition and test contracts, **not** an actual 20-job processing execution. The processing gate remains disabled; no ASF/Earthdata download, Google Drive upload, signed callback round-trip or live RiverShift result was generated.
> - The latest Vercel Web/API Preview deployments remain the `84be793` docs-head builds, both `READY`. Commits after that build only changed tests/workflow definitions; no frontend/API runtime code or Production routing changed.


> **Supabase retention update (2026-11-06):** a new canonical forward migration `20261105205909_catalog_preflight_retention.sql` was applied successfully to the active `SARGuardian_Dynamic` project. It enables `pg_cron 1.6.4`, adds one daily 03:20 UTC cleanup job owned by `postgres`, and purges only catalogue preflight snapshots more than seven days past expiry and not referenced by `processing_jobs`. The immutable guard remains in place for normal writes; the purge function is SECURITY DEFINER, has an empty search_path, and is not executable by browser roles or API `service_role`. A synthetic transactional test passed. All three existing expired preflight rows remain untouched because none has passed the grace period; two are FK-referenced by queued jobs. No other job history, Drive/GitHub artifact, raw data, or scientific result is auto-purged. The seven older migration-history identities still have version/name drift and were not repaired. The new migration is excluded by one exact relative path from the immutable Supabase snapshot comparison; all other imported paths remain byte-checked.

> **Codespaces promoted-path validation update (2026-11-06; migration branch head `87f1595d397809a24b0969b069a1ac182786d408`):** the owner ran the promoted-path validation locally in isolated persistent Conda/npm environments. Results: active API **226 passed** plus the Node Google Maps adapter contract; Find Displacements **104 passed**; Known Place **318 passed** using the CI glob `tools/tests/test_know_place_*.py` and `tools/know_place` compile; RiverShift **259 passed** (Python 3.13.18, GDAL 3.13.3, Rasterio 1.5.2; 186 warnings); NISAR Science Core **180 passed** from the pinned requirements (15 warnings); Web **155 passed across 20 test files**, with `npm ci`, `npm run build`, and `npm run lint` passing on Node 20.20.2/npm 10.8.2. Total: **1,242 promoted-path test executions passed**. The Web build reports a 558.46 kB minified JS chunk; dependency audit advisories were not individually reviewed. No real NISAR downloads, processing, Drive writes, or workflow dispatches were performed.
>
> The current-head Known Place API/workflow contract validator now passes after correcting its environment-map lookup and Drive secret scope assertions. `validate_migration_manifest.py` passes (3 source repositories, 14 immutable refs). `verify_source_snapshots.py` passes with **1,685** source entries, five RiverShift source-branch archive files, promoted blob/mode/type checks, and both ancestry checks. The working tree was clean after these checks. That runner-allocation observation was historical and has since been superseded by successful current-head GitHub Actions runs and a fresh full-history secret scan; see the 2026-11-06 verification block above.
>
> A read-only inventory of the ten root workflows found their third-party `uses:` references pinned to full 40-character commit SHAs; references to local reusable workflows (`./.github/workflows/...`) are same-commit local calls, not third-party action tags. The 432 unpinned references in the archival audit are source workflow variants and must not be rewritten inside immutable snapshots. Continue reviewing only workflows selected for root activation.

> **Historical PR-head validation update (2026-11-05; superseded by the 2026-11-06 current-head verification above):** the current documentation branch head is `151f59854705351d34f234c4c78595ffe7d31a60`, following code-bearing commit `1bcc0648e01794496ec08375e3f245aaadaaf2cf`. New current-head runs [41996716079](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41996716079), [41996716004](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41996716004), and [41996715986](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41996715986) again failed before runner steps (`steps=null`); the prior 419907 runs and their failed-job reruns behaved the same way. The exact cause remains unknown. See the [live migration checkpoint](live-migration-checkpoint-2026-11-05.md).


> **Historical live checkpoint update (2026-11-05; superseded by the 2026-11-06 current-head verification above):** this report's earlier CI references predate Monorepo head [`1bcc0648e01794496ec08375e3f245aaadaaf2cf`](https://github.com/moshiour0/SARGuardian-Monorepo/commit/1bcc0648e01794496ec08375e3f245aaadaaf2cf). Its latest regression, metadata and full-history secret-scan runs (41990721765, 41990721786, 41990721757) all failed before any runner step; failed-job reruns reproduced `steps=null`. This is not a test assertion failure, but it is not a green validation. See the [live migration checkpoint](live-migration-checkpoint-2026-11-05.md) for current source-PR dispositions, root-workflow gates, rerun evidence and exact remaining cutover conditions. That checkpoint supersedes stale “latest head” identifiers below.

## Executive status

**Source snapshots and audited core app/engine promotions are in place. All inventoried source workflows have explicit dispositions, but contract-equivalence review, runtime credential setup and Production cutover are not complete.**

The Monorepo now contains:
- 10 immutable source snapshots: **1,685 tracked paths** with source commit ancestry and exact Git object identity preserved;
- promoted app/API paths: `apps/web`, `apps/api`, and Dynamic compatibility support paths;
- separate promoted engines: Find Displacements, Known Place PR #85, RiverShift GCOV, and NISAR science;
- Supabase config and seven SQL migration files under `infrastructure/supabase/`;
- static workflow inventory, reusable workflow call graph, source pin inventory, and workflow migration/cutover documentation.

Latest full code/test baseline and follow-up execution:
- [GitHub Actions run 41980756059](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41980756059): **17/17 jobs passed** for the promoted application/engine code and the Known Place configurable-routing changes.
- The later source-branch archive gate was added to `tools/verify_source_snapshots.py`. It pins five OPERA/Run #36 source files against `migration/source-branch-snapshots/rivershift-validation-pins.json`; the archive is evidence-only and does not activate those workflows.
- Later source-archive gate and Known Place workflow-contract edits are not yet validated by a successful current-head run. Runs [41983005054](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41983005054), [41983005055](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41983005055), [41983005107](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41983005107), and latest runs [41989627071](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41989627071), [41989626966](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41989626966), [41989627000](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41989627000) all concluded `failure` before runner steps. Latest run 41989627000 created all 17 regression jobs, but each had `steps=null`; metadata/secret-scan jobs likewise had no steps/logs. A rerun of the latest three runs reproduced the same state. This is **not evidence of a code/test assertion failure**, but it is not a passing validation either. A successful current-head source/archive integrity run and full-history secret scan are still required.
- At the time checked, [GitHub Status](https://www.githubstatus.com/) reported all systems operational; the [incident history](https://www.githubstatus.com/history) lists the November 4 Actions incident as resolved. The repository-level pre-job failure remains unexplained; do not attribute it to billing, permissions, or a platform outage without account-specific evidence.
- 1,463 source-snapshot test executions passed, 1 skipped.
- 1,231 promoted-path test executions passed.
- **2,694 passing executions, 1 skipped**. This is an execution count because source and promoted paths intentionally run the same suites twice; it is not a count of unique test cases.
- Exact Git blob/mode/type checks passed for all 1,685 core source snapshot paths and the promoted code/config/workflow compatibility mappings. Additional OPERA/Run #36 validation files are archived separately under migration/source-branch-snapshots/ with source blob hashes; they are not active workflows.
- Full-history Gitleaks scan [41967281531](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41967281531): PASS for the earlier imported history. Latest full-history scan [41989626966](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41989626966) did not start its job step, including after rerun; the new archive, science audit and migration documentation have **not yet received a successful fresh scan**.
- Workflow dependency parser: 82 workflow variants, 135 jobs, 20 reusable call edges (12 local and 8 external), and 141 external checkout steps.

## Completed

| Area | Status | Evidence |
|---|---|---|
| Source preservation | PASS | 10 source snapshots, 1,685 paths, source SHAs/history retained |
| Dynamic frontend/API promotion | PASS | 155 frontend tests; 215 API tests; frontend build/lint pass |
| Find Displacements promotion | PASS | 104 promoted dashboard/worker tests; original GOFF/GUNW separation unchanged |
| Known Place promotion | PASS (source/code baseline) | PR #85 engine lineage and separate author-exact P05023 pin; 318 engine tests pass on the historical baseline. API workflow destinations are independently configurable. One canonical two-job root dispatcher plus one `workflow_call` engine workflow are present; duplicate dispatcher removed. Two contract validators cover source identity/permissions/opt-in and API field/status/artifact/scoped-secret mapping. Latest current-head CI is unresolved pre-run failure, not green. |
| RiverShift GCOV promotion | PASS | 259 tests pass; independent GCOV boundary retained |
| NISAR science promotion | PASS | 180 tests pass; historical worker pins separately preserved |
| Supabase source migration files | PASS | config + seven migration files exact-copy promoted |
| Workflow syntax/static inventory | PASS | 82 YAML variants parse with zero YAML errors; 20 reusable call edges enumerated |
| Secret scan | PASS | Full reachable history scanned; 20 exact synthetic test-fixture fingerprints are narrowly allowlisted |
| Production config discovery | PASS | Existing Production Vercel projects and active Supabase state inspected read-only; no production changes |

## Remaining critical work

### 1. Operational GitHub Actions centralization — IN PROGRESS

The source workflows are inventoried, but most are still archival snapshots. They have **not** been bulk-copied into root `.github/workflows/`.

The static audit found:
- 432 unpinned action-reference occurrences across the 82 source workflow variants (including duplicated branch variants);
- 25 workflow variants where at least one job has neither job-level nor top-level explicit permissions;
- 8 external reusable workflow call edges, of which 4 still use mutable branch refs;
- 141 external checkout steps, with three workflow inputs/outputs supplying the ref dynamically.

The next work is to choose only the required production/CI workflows, pin every external action and source checkout, define least-privilege permissions, and preserve caller/input/artifact/callback/retry/retention semantics. The source snapshots will remain unchanged.

**RiverShift:** the validated 20-job candidate now has a guarded 21-job root port at .github/workflows/river-shift-gcov-process.yml. It is workflow_dispatch-only; the credential-free preflight fails closed unless MONOREPO_RIVERSHIFT_PROCESSING_ENABLED=true. The API still defaults to the old Backend workflow and Preview dispatch is disabled. Still required: a 20-job operational mock/dry-run covering all four 15-product batch barriers, missing/failed artifacts, failed-only retry waves, callback ordering, Drive receipt mismatch, and final failure propagation.

**Known Place:** the canonical API entrypoint is `.github/workflows/know-place-aoi-dispatcher.yml`; it uses a request-ID run name, a credential-free preflight and explicit mapping of exactly six worker secrets into the local reusable workflow `.github/workflows/know-place-aoi-analysis.yml`. The reusable engine allows catalog-only dry runs with raw downloads and Drive upload off; raw downloads require both explicit user consent and `MONOREPO_KNOWN_PLACE_ACTIONS_ENABLED=true`. The duplicate `know-place-aoi-monorepo-dispatcher.yml` was removed. API production defaults still target the existing Backend dispatcher; no production route was changed. Current-head CI has not yet executed these validators successfully.

### 2. Vercel Monorepo Preview — INITIAL BUILDS READY; LATEST BUILD BLOCKED BY HOSTING QUOTA

Two new Vercel projects are now Git-linked to `moshiour0/SARGuardian-Monorepo` with separate roots:
- Web: project `sar-guardian-monorepo-web`, root `apps/web`.
- API: project `sar-guardian-monorepo-api`, root `apps/api`.

The isolated Preview deployments both reached READY with `target=null` (Preview, not Production):
- Web deployment [`dpl_GMUhm39paoZgMfqyxzPSDBqaVMKe`](https://vercel.com/moshiour-rahman-sarkers-projects-2cebe363/sar-guardian-monorepo-web) uses commit `cb23414a069f3bd0c0ad466b1a581d5e26038e64`; stable branch alias: `sar-guardi-git-90a645-moshiour-rahman-sarkers-projects-2cebe363.vercel.app`.
- API deployment [`dpl_F5m1ZnpYktLNHiQ5p7WD1kHDm6Tf`](https://vercel.com/moshiour-rahman-sarkers-projects-2cebe363/sar-guardian-monorepo-api) uses commit `f2cca2b57ccd40ad93ff1ab41a5b862f41833b51`; stable branch alias: `sar-guardi-git-ed4bd9-moshiour-rahman-sarkers-projects-2cebe363.vercel.app`.

The Web RiverShift page and API config/main blobs match the current branch. The deployed API `known_place.py` is one six-line correction behind current source: its workflow URL variable references were corrected from `workflow_PAGE` to `workflow_page` after that deployment. The current source is corrected, but Known Place dispatch/status must not be treated as tested on this Preview until the API is redeployed. Preview-only API URL/CORS values are configured; Find Displacements and RiverShift dispatch are explicitly disabled. No Production credentials, Supabase service-role key, Firebase Admin credential, GitHub token, Drive OAuth or callback secret were copied to Preview.

Vercel's Git integration has since rejected newer deployments with `api-deployments-free-per-day` (`more than 100`), shown in its PR bot comment. This is a hosting deployment quota blocker, not a reported TypeScript/Python build failure. The current Preview projects remain SSO-protected and behind the latest source commit; the API also needs the six-line Known Place URL-reference correction deployed. Full login, staging persistence, live map key/Places API, private Drive result retrieval and real processing are not yet validated on Monorepo Preview.

Do not repoint either existing Production project. Keep Preview dispatch disabled until staging auth/database and callback contracts are ready.

### 3. Supabase migration-history and retention reconciliation — PARTIAL

The new Monorepo Supabase target and existing Dynamic Production Supabase are separate. The Monorepo's nine local migration filenames now match the nine remote version/name rows in `migration/supabase-history-alignment.json`; the seven imported SQL blobs remain byte-identical to immutable Dynamic source files, and the two forward migrations retain reviewed SHA-1 blob identities. CI verifies that mapping. A final authenticated CLI v3 `supabase migration list --remote` confirmation is still required; no remote history repair, old DDL replay, `db push` or reset has been performed. The existing Dynamic Production project has its own eight-row historical lineage and must be reconciled separately against its original local files before any future database push. Its history must not be conflated with the Monorepo target. Retention for processing/displacement/RiverShift jobs and Drive/GitHub artifacts remains undefined and is intentionally not auto-purged. `postgres` defaults are hardened for future app objects; Supabase-managed `supabase_admin` defaults remain outside the current permission scope.

### 4. End-to-end integration and production cutover — NOT STARTED

Still required:
- mock API dispatch and signed callback round trips for Find Displacements, Known Place, and RiverShift;
- verify request IDs, HMAC signatures, callback order, status polling, cancellation, failure propagation, Drive receipt, and retention behavior;
- compare canonical source/promoted output fixtures and manifests;
- run one isolated real-data pilot per engine and independently review outputs;
- rehearse rollback to existing Vercel deployment and original backend workflow targets;
- obtain explicit production cutover approval before changing repository/ref values, callback destinations, domains, or aliases.

## Current completion sequence

1. Configure Preview-only Web client variables and API/Actions credentials listed in the current checkpoint. Generate a new Supabase API secret for `qbmhpdprvxssqinnommz`; do not reuse the old Dynamic project's service key.
2. Add matching callback HMAC values to both API Preview and Monorepo Actions Secrets. Add Earthdata and Google Drive OAuth/parent-folder secrets only to the Monorepo repository's Actions secrets.
3. Verify Firebase login, owner-scoped Supabase writes/reads, mock dispatch, request/run correlation, signed callback sequencing, failure propagation and private Drive artifact reads.
4. Run controlled Find Displacements and generic Known Place pilots at the same exact source/runtime pins. Keep RiverShift and author-exact P05023 gated until their separate scientific/retention acceptance is complete.
5. Perform final science, dependency/licensing and rollback review. Merge PR #1 then PR #2 in sequence; switch Production only after explicit owner approval.

**Supabase history note:** the nine Monorepo filename/version/name/blob mappings already match the connected remote project inventory and CI contract. An authenticated CLI v3 `migration list --remote` check remains optional if a CLI-authenticated environment is available. This does not justify a migration repair, replay or `db push`. Existing Dynamic Production has its own separate history and must remain untouched during this Monorepo work.

## Updated Preview and database verification — 2026-11-05

- Web and API Monorepo Vercel builds are independently verified as READY Preview deployments; Web ran TypeScript + Vite build, API compiled Python functions and uploaded outputs. These deployments came from documentation-only commits after the last code-bearing integration commit. They are Preview only and SSO-protected.
- The Preview environment audit is fail-closed: no Firebase config or Google Maps key in Web; no Supabase credentials, service-account credentials, GitHub/Earthdata/Drive tokens or callback secret in API. Both live processing flags are explicitly false. Thus Preview builds successfully, but auth, Maps, live data persistence and processing callbacks have not been runtime-validated.
- Vercel Preview runtime-log queries returned no records in the last 30 minutes; no route smoke test is claimed. See the live Vercel inventory (../operations/live-vercel-inventory.md).
- Historical Dynamic Production read-only Supabase verification confirms its four job tables and RiverShift schema contract. That seven-row observation belongs to the 2026-11-05 historical checkpoint, not the current Monorepo target. The Monorepo target now has nine remote records and nine local deployment filenames aligned by remote version/name; imported SQL blobs remain byte-identical and CI verifies the map. No remote DDL or migration-history repair was run.
- Supabase CLI v3 is now default and changes remote targeting: use --remote for any future remote list/push operation; never run db push until migration versions/names are reconciled. See Supabase migration lineage (supabase-migration-lineage.md) and the official v2→v3 migration guide (https://supabase.com/docs/guides/local-development/cli/migrating-to-v3).
- Web build warnings remain: one 560.16 kB JS chunk and npm audit summary of 19 advisories (10 moderate, 7 high, 2 critical); exact advisories must be reviewed before public release. Do not blindly run npm audit fix --force.


## Historical RiverShift validation update — 2026-11-05 (superseded by current-head CI pass)

The API now validates RiverShift workflow repository, filename and ref formats at production startup. New tests were added for invalid targets, valid branch refs and GitHub run-status fallback (missing callback, failed run, start timeout, terminal success preservation). At that time, the tests had not executed because runner diagnostic 42002234943 and snapshot run 42002235091 failed or queued before runner allocation. This observation is historical; current-head RiverShift worker/API regression jobs passed in Snapshot Regression Tests 42108970979. See the [RiverShift integration review](river-shift-integration-review-2026-11-05.md) for the remaining end-to-end dry-run gates.

The earlier API Preview redeploy request was rejected by Vercel with HTTP 402, but this is superseded: the current API Preview is now `READY` for commit `96bcdee42b5b6871f5638dd3e41161cccc966130`.


## Current API, workflow and Supabase acceptance status — 2026-11-06 (bdc110f)

### GitHub workflow consolidation

The complete source workflow inventory is accounted for: 82 source instances from Dynamic main, Backend main and Known Place PR #85; 42 root workflow files; 39 distinct root workflow destinations. The audit is a **disposition register**, not a claim that every source variant has been activated or proven contract-equivalent. Contract-review categories remain open in `migration/workflow-dispositions.json`; four legacy instances are explicitly archive-only.

The API's four processing destinations are documented in `docs/migration/api-dispatch-cutover-map.md`. Find Displacements uses the dashboard workflow schema, generic Known Place remains distinct from author-exact P05023, and RiverShift remains an independent GCOV engine. Production-compatible defaults are retained in source; the Vercel Preview points to Monorepo workflows on the migration branch. All API and repository processing switches remain false.

### Supabase Monorepo target

The Free Tokyo project is active and has the expected four empty RLS-enabled tables. The Monorepo's nine local migration filenames are now aligned to the nine observed remote version/name rows, with byte-identical imported SQL blobs and pinned Monorepo-only forward migrations. Do not run `db push`, migration repair, replay or reset until authenticated CLI v3 confirms the full local/remote timestamp alignment. The existing Dynamic Production project retains its separate historical migration lineage. The existing `SARGuardian_Dynamic` Production project has its own separate migration lineage; do not conflate its rows with this new target.

The first direct ACL inspection found broad defaults for future objects. A forward hardening migration is now applied for future application objects created by `postgres`, and a transactional post-apply probe verified no browser-role table/sequence/function privileges while preserving `service_role`. Supabase-managed `supabase_admin` defaults are unchanged and remain a future review boundary; the connected `postgres` role cannot assume that provider role. The `processing_jobs.preflight_id` FK also lacks a covering index; consider a separate index migration only after query-plan/expected-volume review.

### Preview readiness and blocking inputs

The API Preview is READY at the current API code commit. The Web Preview is READY on the immediately preceding docs-only commit. Both are SSO-protected, Preview-only and have no Production alias.

The API Preview environment has the Tokyo `SUPABASE_URL`, callback base URLs and all four workflow destination names/refs. It intentionally lacks the server-side Supabase service key, Firebase Admin JSON, GitHub PAT, callback HMAC secrets and Drive OAuth values. Do not put any of these in the Web project or commit them. The Supabase service key must be created in the Dashboard as a named API secret and added only to Vercel API Preview. Firebase Admin, GitHub dispatch and Drive result-read credentials need to be added in their respective server-side/Actions secret stores before runtime acceptance.

**Remaining acceptance gates:** authenticated Preview health/auth/map/persistence smoke; mock dispatch and HMAC callback/status-polling round trips for all engines; Drive receipt read/write verification; one explicit dry-run or isolated real-data pilot per engine; default-privilege and FK-index review; migration-history reconciliation; independent science review; rollback rehearsal; explicit owner approval before merge or Production cutover.


## Known Place active-runtime lineage correction — 2026-11-06

A targeted Backend main workflow-history and commit-pin audit corrected the earlier scope note in this file. The earlier “no Known Place dispatch in the latest 100 runs” statement was based on a general all-event run page and was wrong for the user-facing dispatch path. Filtering the Backend Actions history by event=workflow_dispatch and branch=main returned 115 total records; the first 100 contained 16 generic Known Place dispatches (8 success, 7 failure, 1 cancelled) and one author-exact dispatch (failure).

The generic Backend main dispatcher calls its reusable analysis workflow and science code at 0e0611c12913044787ee84a39fa60a81d30ae516. The two most recent successful generic runs in that result page were 41533701551 and 41533582770, both retaining result artifacts. PR #85 is still Draft/Open on feat/know-place-analysis; it was not merged to Backend main. PR #86 merged only the GOFF candidate handoff. The actual current generic runtime pin is 78 commits ahead of the current feature-branch pointer and 32 commits ahead of PR #85 head. Monorepo now carries an exact 10-file runtime/test overlay from that current pin, recorded in migration/active-runtime-pins/known-place-generic-0e061.json.

The author-exact paper dispatcher separately uses reusable workflow pin d847b0461a2fec1bdf2abcce0a6b1d2f9dddabc9 and Backend code pin b825df798ea4cb9874aa10dd01174d2a8ef73cba. Its observed run 41423614257 did not complete: consent and initial Drive retention passed, but source-manifest completeness failed and post-delete cleanup was blocked. Keep author-exact gated and do not describe it as successfully reproduced.

The primary cutover register now includes Find Displacements and generic Known Place. RiverShift remains gated pending positive-case GCOV. Author-exact P05023 remains a separately gated manual-consent path. All Monorepo API and repository processing flags remain false pending Preview credentials, authenticated persistence/callback checks and pilot acceptance.


## Latest live reconciliation — 2026-11-06, branch head 9bd6858

**Verified head:** `9bd6858b7ea4e2500a531634e4a96f2d2288bf09` on `migration/source-snapshot-import`.

### Current CI state
- Snapshot Regression Tests [42187445481](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445481): **19/19 jobs passed**.
- Backend Source Snapshot Regression [42187445413](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445413): Backend main and Known Place PR #85 source suites both passed.
- Historical Secret Scan [42187445962](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445962): **success** on this exact head after the reviewed 21-entry allowlist update.
- Migration Metadata Validation [42187445630](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445630), Runner Allocation Diagnostic [42187445578](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445578), Dashboard Asset tests [42187445703](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445703), Retention Archive Regression [42187445646](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445646), and dual-pin AOI validation [42187446475](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187446475): all **success**.
- This is source/build/static-contract CI evidence. It is not a live processing pilot or Production cutover.

### Current hosting and database state
- Monorepo Web and API Vercel projects are separate, SSO-protected, Preview-only projects (`live=false`, latest deployment `target=null`). The latest READY deployments inspected are on commit `c246f3b16a5b7320ab97250f202847b9f4d5c8c2`, not the current docs/security head. GitHub's Vercel checks for `9bd6858` point to the Free-plan build-rate-limit page; no current-head Vercel build was created. Older READY Preview builds are not evidence of an authenticated end-to-end runtime.
- The dedicated Tokyo Supabase project `qbmhpdprvxssqinnommz` is `ACTIVE_HEALTHY`, PostgreSQL 17.11, with nine recorded migrations. Four app tables exist, all RLS-enabled and all empty. No user/job/result data has been migrated. Security Advisor and Health Advisor return zero findings. Performance Advisor currently reports one unindexed FK, four RLS-policy initialization-plan warnings and eight unused-index notices; the latter are expected to be low-confidence while all tables remain empty.
- The existing `SARGuardian_Dynamic` Supabase Production project and original Dynamic/Backend Production routing remain separate and unchanged.

### Operational blockers that remain
- API Preview still lacks the server-only Supabase service-role key, Firebase Admin credential, GitHub Actions dispatch token, callback HMAC secrets and Google Drive read OAuth. Monorepo Actions still need owner-configured Earthdata/Drive OAuth, Drive parent-folder ID and matching callback secrets. Values must be added directly to the appropriate provider secret stores, never committed or pasted into chat.
- Web Preview currently has only `VITE_SARGUARDIAN_API_URL`; Firebase browser configuration and a Maps key are not present in the branch-specific environment inventory.
- Required Web Preview client variables from `apps/web/.env.example` / `apps/web/src/firebase.ts`: `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_STORAGE_BUCKET`, `VITE_FIREBASE_MESSAGING_SENDER_ID`, `VITE_FIREBASE_APP_ID`, optional `VITE_FIREBASE_MEASUREMENT_ID`, and `VITE_GOOGLE_MAPS_API_KEY`. These values are public browser configuration; scope them to Preview and restrict Maps HTTP referrers to the Monorepo Preview domain. Existing Dynamic Vercel values are marked sensitive and were not exposed by the connected read interface, so no guessed values were added.
- All Monorepo processing flags and root workflow gates remain fail-closed. No Monorepo live worker dispatch, real NISAR download, private Drive upload or signed callback round-trip has been performed.
- Find Displacements needs a controlled Monorepo pilot; generic Known Place needs a catalog-only Preview check and a positive two-polygon pilot; RiverShift needs a genuinely bracketed event-date positive GCOV run; author-exact P05023 remains manual-consent-gated until source manifest, science, Drive receipt and cleanup all pass.
- Reconcile the nine Monorepo local/remote migration identities using the authenticated CLI v3 read-only listing if available. Do not run `db push`, reset or replay. Review the processing_jobs FK index and four RLS policy performance notices against actual query patterns before changing schema.
- Review Web npm advisories and the large JS bundle, licensing/redistribution rights, independent science validation, rollback and final cutover controls.

### Pull request and release state
- PR #1 (foundation) is **Draft/Open**, base `main`, head `migration/bootstrap-and-provenance`.
- PR #2 (source import/promotion) is **Draft/Open**, base `migration/bootstrap-and-provenance`, head `migration/source-snapshot-import`.
- Default branch `main` remains at the initial bootstrap commit; the imported source and promoted code are not yet merged into `main`.
- No Production aliases, production dispatch targets, source repositories or Dynamic Production database were changed. Merge and Production promotion remain separate approval gates.

