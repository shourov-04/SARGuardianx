# SARGuardian monorepo migration plan

**Plan date:** 2026-11-05  
**Execution state:** ten source snapshots preserved (nine commit-backed histories plus the divergent Known Place author-exact code tree); app and engine paths promoted. The latest 15-job source/promoted parity run, migration metadata validation, and full-history secret scan all pass. The RiverShift workflow candidate is statically validated but remains inactive. Production cutover remains blocked.

## Executive decision

Use a **preserve-first, staged monorepo migration**. Do not concatenate source roots or merge the APIs in one step. Source snapshots remain immutable; promoted paths are exact copies that will be refactored only after call graphs, build roots, and workflow contracts are verified.

## Phase 0 — protect and verify inputs

- [x] Verify target repository exists and connected GitHub integration has push/admin access.
- [x] Record current default-branch SHAs for Dynamic, backend, and NISAR science sources.
- [x] Record Known Place feature-branch base and open PR #85 separately from backend main.
- [x] Import nine commit-backed source trees and retain their source commit history.
- [x] Preserve the divergent Known Place author-exact `backend_code_ref` (`b825df…`) as an additional exact 277-path tree snapshot.
- [x] Inventory all 42 Dynamic/backend-main workflow files with source blob SHAs, triggers, jobs, checkout repositories/pins, and credential-risk notes.
- [x] Record the Known Place PR #85 workflow delta: 15 added workflows, 8 modified same-path workflows, and 10 backend-main-only workflows.
- [x] Parse all 82 workflow variants and inventory permissions, action pins, secret references, external checkouts, artifacts, retries, reusable calls, and triggers; see `docs/migration/workflow-contract-audit.md`.
- [ ] Complete exhaustive branch/tag inventory beyond the selected immutable refs.
- [x] Record existing Vercel frontend/API project IDs, verified domains, latest production SHAs, and environment variable names (without decrypting secrets); exact project Root Directory still requires team settings access.
- [x] Verify active Supabase project identity, public table/RLS status, security advisor, and remote migration history without changing schema; retention policy review remains pending.
- [ ] Trace calls to the old backend `app/` service and determine if it is still used.

## Phase 1 — safe monorepo foundation

- [x] Add README, engineering/scientific guardrails, architecture boundaries, contribution rules, source-pin manifest, and staged migration plan.
- [x] Add secrets-free metadata validation and isolated source/promoted regression CI.
- [ ] Add CODEOWNERS and verify branch protection/required checks.
- [ ] Complete configuration-name mapping before creating environment templates.
- [x] Run Gitleaks across the full reachable Git history using a checksum-verified binary; 20 synthetic test-only findings were reviewed and scoped to exact fingerprints.
- [x] Validate that the Gitleaks exception file has exactly 20 unique test-file fingerprints and no directory/rule-wide exclusions.

## Phase 2 — immutable imports and source integrity

- [x] Import nine commit-backed snapshots plus one divergent exact tree snapshot under `migration/source-snapshots/` (1,685 tracked paths).
- [x] Preserve source commit histories through Git parent relationships.
- [x] Promote Supabase CLI config and seven local migration files under `infrastructure/supabase/` as exact blob copies; no remote DDL was run.
- [x] Compare every imported snapshot path, file mode, object type, and Git blob SHA.
- [x] Preserve divergent historical worker checkouts (Dynamic API, backend reassembly, legacy Sagormodak science fork) separately rather than overlaying them.
- [x] Record 24 Dynamic/backend same-path collisions, including 19 different-content files.
- [x] Keep all original source repositories unchanged.

## Phase 3 — application and engine path promotion

- [x] Promote Dynamic `Frontend/` to `apps/web/`; build, lint, and 155 tests pass at the promoted path.
- [x] Promote Dynamic active `Backend/` to `apps/api/`; 215 API tests and the Google Maps adapter contract pass from the promoted path.
- [x] Retain Dynamic root tools under `apps/tools/` and its workflow compatibility mirror under `apps/.github/workflows/`; these mirrors are inactive.
- [x] Promote Find Displacements dashboard/tools to `engines/find-displacements/`; 104 dashboard/worker-tools tests pass.
- [x] Promote the Known Place PR #85 source tree to `engines/known-place/`; 318 tests pass.
- [x] Promote RiverShift GCOV code to `engines/river-shift/`; 259 tests pass.
- [x] Promote current NISAR science source to `science/nisar-core/`; 180 tests pass.
- [x] Verify exact blob identity for promoted directories, workflow/dependency compatibility fixtures, and the Supabase migration subtree.
- [ ] Decide the long-term package boundary for duplicated utilities; do not deduplicate by filename.
- [ ] Decide whether the older SQLAlchemy/session-oriented backend `app/` is retained under a `legacy/` namespace or retired after caller tracing.

**Important:** engine-local `.github/workflows/` directories are inactive fixtures preserving existing tests' source-relative workflow paths. GitHub Actions only activates root `.github/workflows/`.

## Static workflow audit result

The automated contract audit parsed 82 workflow variants with zero YAML parse errors. It found 25 workflow instances with implicit/default job permissions, 432 tag-based action references, 58 secret-using workflow instances, 41 external-checkout instances across four repositories, 16 reusable workflow-call references, 189 artifact steps, and 23 workflows with retry markers. These are review counts across all source variants, not proof of production execution. See `docs/migration/workflow-contract-audit.md`.

## Phase 4 — central workflow migration

The audited baseline has 42 workflow YAML files: 7 in Dynamic and 35 in backend main. The Known Place PR #85 feature branch contains 40 workflow YAMLs: 15 branch-specific additions, 8 changed same-path files, 17 unchanged files, and 10 backend-main-only files absent from that branch.

Before moving any operational workflow into root `.github/workflows/`, record:
- trigger types, branch/path filters, dispatch inputs, and reusable workflow callers;
- job graph, dependencies, concurrency, matrix, environments, and permissions;
- each external checkout repository/ref/path and immutable source pin;
- artifact names, retention, upload/download relationships, and Drive/Supabase writes;
- secrets/variables by name only;
- callbacks, callback signatures, expected sequence/terminal states;
- retry behavior, cleanup, and failure propagation;
- disposition: CI regression, operational dispatcher/worker, credentialed/live integration, retained replay/validation, legacy, or retirement candidate.

**Duplicate-run rule:** original repository workflows remain authoritative while the monorepo copies are inactive or mock-only. Do not permit one request to dispatch both old and new production workers.

**RiverShift constraint:** preserve the 20-job GCOV graph: prepare, four sequential batch/status barriers, up to three retry waves, and assemble. Keep batches of 15 where configured; retry only failed products; never re-download successful products; preserve callback/artifact/Drive receipt order; fail the outer workflow if a required inner stage fails.

**Known Place constraint:** use PR #85 for the engine implementation and two-polygon research behavior, but reconcile current backend-main/Dynamic dispatchers against the active API contract. The PR feature branch does not contain later backend-main RiverShift/dispatcher workflows.

**Exit condition:** every workflow version has a reviewed disposition; selected root workflows pass isolated tests; duplicate-dispatch prevention and rollback are demonstrated.

**RiverShift candidate status:** `migration/workflow-candidates/river-shift-gcov-process.yml` now passes exact source-transformation validation and all promoted RiverShift regression tests. It is intentionally not in root `.github/workflows/`; 20-job operational mock/dry-run, secret mapping, and dispatch cutover checks remain outstanding.

## Phase 5 — infrastructure, operational validation, and cutover

- [ ] Verify Vercel project IDs, roots, build settings, output settings, function limits, environment scopes, production branch, and aliases.
- [x] Confirm active Supabase project identity, four public tables, RLS enablement, owner policies, security advisor, and seven remote migrations by read-only query.
- [x] Promote the local Supabase config and SQL migration files into `infrastructure/supabase/` with exact source blob identity.
- [ ] Verify Supabase retention/cleanup policy and reconcile remote migration version/name drift with local filenames without applying migrations. See `docs/migration/supabase-migration-lineage.md`.
- [x] Record current Vercel environment variable names and worker dispatch destinations without decrypting or copying secret values; final target Preview variable mapping remains pending.
- [ ] Deploy a Preview only; test authentication, map search/AOI drawing, dashboard/archive, all engine pages, and result retrieval.
- [ ] Exercise API dispatch/callback signatures, sequence ordering, retry behavior, terminal failure, Drive receipts, and retention with mocks.
- [ ] Compare canonical source and promoted output fixtures/manifests; path-level code identity is already verified, but real-output parity remains pending.
- [ ] Run an isolated real-data pilot only after mock, security, and scientific fixture gates pass.
- [ ] Compare pilot output to source baselines and independent validation evidence.
- [ ] Rehearse rollback to the existing production deployment and original dispatchers.
- [ ] Obtain explicit approval before production Vercel aliases, callback destinations, or worker dispatch ownership changes.

## Current CI acceptance baseline

Latest complete source/promoted-path CI: [41967622599](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41967622599), 16/16 jobs passed:
- source snapshot tests: 1,463 passed, 1 skipped;
- promoted-path tests: 1,231 passed;
- total: 2,694 passing test executions, 1 skipped;
- exact source blob/history checks: 1,685 snapshot entries plus promoted paths, fixtures, and Supabase migration mappings;
- workflow dependency graph: 82 variants, 135 jobs, 20 reusable edges, 141 external checkouts;
- RiverShift workflow candidate contract validator: PASS (20-job graph, path rewrite, immutable Node 24 action pins, artifact/retry/callback/retention checks);
- full-history Gitleaks scan: [41964029586](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41964029586), PASS with zero unreviewed findings.

See `docs/migration/validation-baseline.md` and `docs/migration/readiness-and-remaining-work.md`.

## Mandatory production cutover gates

- Source integrity: PASS
- Snapshot and promoted-path regression parity: PASS
- Workflow inventory: PASS (42 baseline files + 40 PR #85 branch variants catalogued)
- Workflow security/caller/disposition review: IN PROGRESS
- Workflow permissions/caller/callback/retry parity: PENDING
- API live contract/auth/CORS: PENDING Preview
- Supabase identity/schema/RLS/security advisor: PASS (read-only)
- Supabase migration-history alignment and retention policy: PENDING
- Historical Git secret scan: PASS (zero unreviewed findings)
- Workflow static contract parse: PASS (82 variants, zero YAML errors); runtime permission/caller/dispatch dry-run: PENDING
- Runtime secret/permission mapping: PENDING
- Vercel Preview/routing: PENDING
- Scientific real-output parity and independent validation: PENDING
- Rollback rehearsal: PENDING

A repository merge is not a production cutover.
