# Migration and promoted-path validation baseline

**Latest complete source/promoted-path run:** [GitHub Actions run 41967622599](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41967622599)  
**Validated commit:** `107e17c3a05330e1675736cd1cdf4f1f1092ec01`  
**Result:** **16/16 jobs passed**.  
**Latest historical secret scan:** [run 41967622669](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41967622669) — PASS, zero unreviewed Gitleaks findings.  
**Latest migration metadata validation:** [run 41964029595](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41964029595) — PASS.  
**Source snapshot scope:** 10 snapshots, 1,685 tracked source paths.  
**Promoted scope:** `apps/web`, `apps/api`, Find Displacements, Known Place, RiverShift GCOV, and NISAR science.

## Test results

Source-snapshot regression and promoted-path regression are intentionally separate, so the same test suite can be verified at its original source location and its new Monorepo location.

| Validation group | Result | Evidence |
|---|---|---:|
| Dynamic frontend snapshot | PASS | 155 tests; 20 test files; build and lint pass |
| Dynamic active API snapshot | PASS | 215 tests; Google Maps adapter contract pass |
| Backend workers + Find Displacements snapshot | PASS | 336 passed, 1 skipped |
| Known Place PR #85 snapshot | PASS | 318 tests |
| RiverShift GCOV snapshot | PASS | 259 tests |
| NISAR science snapshot | PASS | 180 tests |
| Promoted `apps/web` | PASS | 155 tests; build and lint pass |
| Promoted `apps/api` | PASS | 215 tests |
| Promoted Find Displacements | PASS | 104 dashboard/worker-tools tests |
| Promoted Known Place | PASS | 318 tests |
| Promoted RiverShift | PASS | 259 tests |
| Promoted NISAR science | PASS | 180 tests |
| Source workflow contract audit | PASS | 82 workflow variants parsed; zero YAML parse errors |
| RiverShift candidate contract validator | PASS | exact source transformation, YAML parse, 20-job graph, 15-product matrices, artifact/retry/callback/retention assertions |
| Workflow dependency parser | PASS | 82 YAML workflow variants, 135 jobs, 20 reusable call edges, 141 external checkout steps |
| Exact Git source/promoted integrity | PASS | 1,685 source entries plus promoted app/engine/workflow/Supabase mappings |

**Snapshot-path executions:** 1,463 passed, 1 skipped.  
**Promoted-path executions:** 1,231 passed.  
**Combined:** **2,694 passing test executions, 1 skipped**. This is an execution count, not a unique test-case count, because suites are run at both the immutable source location and the promoted location.

All 15 jobs completed successfully in run 41964029591. No source science algorithm was altered to obtain a green result.

## Exact source integrity

The integrity job used a full-history checkout and compared Git object identity rather than decoded/re-encoded file contents.

| Immutable source snapshot | Tracked paths |
|---|---:|
| Dynamic main | 185 |
| Backend main | 244 |
| Known Place PR #85 head | 277 |
| NISAR science main | 110 |
| NISAR historical pin 10639 | 133 |
| NISAR historical pin 006d | 135 |
| Dynamic historical callback API pin db6472 | 130 |
| Backend historical reassembly pin d9e67 | 86 |
| Legacy Sagormodak NISAR fork pin 77cc964 | 108 |
| Known Place author-exact backend code tree pin b825df | 277 |
| **Total** | **1,685** |

For each commit-backed source tree, the validator compared every tracked path, file mode, Git object type, and blob SHA. The divergent Known Place author-exact code ref `b825df798ea4cb9874aa10dd01174d2a8ef73cba` is not an ancestor of PR #85; its exact 277-entry tree is compared using the recorded source tree SHA `3c77b2d52474364020acebeb4338b5babe7ff4ec`.

The validator also checks exact Git object identity for the promoted Dynamic frontend/API/tools/workflow compatibility paths, Known Place engine, NISAR source, Find Displacements dashboard/tools and workflow fixtures, and RiverShift engine/workflow fixtures. It confirms:
- Known Place feature base `bd7a59c54ddae7c19fd88896e877c3a530b43d9e` is an ancestor of imported PR #85 head `bfde7dde8ada92a03054cd8dbad8daa7a5c119f8`.
- NISAR historical pin `ab547ecc82bcc4d6ccef545a59852536c2beacc6` is an ancestor of current NISAR main `9fcb543ef28a7f6fe70a379aed9cfe3e43e277ec`.
- The extra author-exact `b825df` tree is preserved separately rather than being silently substituted with PR #85 code.

**Integrity result:** `ALL_SNAPSHOT_BLOB_INTEGRITY_PASS total_entries=1685`. The same run also reported `PROMOTED_PATH_BLOB_INTEGRITY_PASS Supabase configuration and migration promotion: 8 entries`.

## RiverShift Monorepo workflow candidate

An inactive candidate now exists at `migration/workflow-candidates/river-shift-gcov-process.yml`. The validator reconstructs the candidate from the original backend-main workflow using only the seven documented engine-path/action-pin transformations, compares the entire candidate text, parses both YAML documents, and verifies the same 20 job IDs and core artifact/retry/callback/Drive contracts.

Run 41964029591 includes:
- `RIVERSHIFT_MONOREPO_WORKFLOW_CANDIDATE_PASS`;
- 20 checkout action pins, 8 upload-artifact pins, 30 download-artifact pins, and 17 micromamba pins;
- Node 24 action runtimes;
- unchanged 15-product batch sizing, retry-only-failed waves, root-relative artifact directories, callback sequencing, and retention settings.

**The candidate remains inactive.** It is not under root `.github/workflows/`, and the active Dynamic API still dispatches RiverShift to `moshiour0/SARGuardian-backend@main`. Static/CI parity does not replace a 20-job operational dry-run or authorize production workflow cutover.

## Historical secret scan

The checksum-verified Gitleaks full-history scan [41964029586](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41964029586) completed successfully:
- full reachable history scanned;
- unreviewed finding count: **0**;
- 20 exact synthetic test-fixture fingerprints remain narrowly allowlisted;
- no raw secret report artifact retained.

This is evidence that no unreviewed Gitleaks finding remains in the scanned Monorepo history; it is not proof about credentials that may have been copied outside this repository.

## Live infrastructure cross-check

Read-only Vercel inventory confirmed that the frontend and API Production deployments still run commit `42d977b5abd186866ac0d78454239563eebb18d2`, while current Dynamic main is `dd64b7adc90594f1d7f316b352e39fbac2013cb6` (one commit ahead). The API also has a READY Preview from feature branch `feat/rivershift-map-place-search-20261105`, commit `c5ff0c1273ddf75d9e7ea270a039e2ca5f9723e9`; that deployment is not Production. Exact Vercel Root Directory settings were not exposed by the read-only project metadata. See [live Vercel inventory](../operations/live-vercel-inventory.md).

Read-only Supabase inventory confirmed the active `SARGuardian_Dynamic` project, four public RLS-enabled tables, owner-read policies, zero security-advisor lints, and seven remote migration records. A performance-advisor recheck flagged an unindexed foreign key and four RLS init-plan warnings; live policy expressions were already in scalar-subquery form, and no DDL was applied. Two remote RiverShift migration versions/names differ from local filenames; reconcile history before any future migration. See [live Supabase inventory](../operations/live-supabase-inventory.md).

## What this validation establishes

- All 10 source snapshots are exact across 1,685 tracked paths.
- Promoted application and engine directories are exact copies of their recorded source trees/subtrees or approved documented workflow fixtures.
- Source and promoted frontend/API/engine regression suites pass at both path locations.
- The RiverShift Monorepo candidate's YAML, job graph, source transformations, action pins, and key artifact/retry/callback/retention contracts pass static validation.
- Historical secret scanning has zero unreviewed findings.

## What this validation does not establish

- Production Vercel root/domain and environment configuration is ready to switch.
- Firebase, Supabase, Google Drive, ASF credentials, callback secrets, or GitHub token permissions are configured in the target deployment.
- The RiverShift candidate has completed an isolated 20-job operational dry-run with mock callbacks/artifacts.
- All original workflows are ready to move into root `.github/workflows/`; permissions, callers, artifacts, retention, callbacks, duplicate-dispatch prevention, and rollback still need runtime verification.
- Real-data output parity or independent geophysical validation has passed.
- A production cutover or rollback rehearsal has been performed.

A passing CI migration baseline is necessary, not sufficient, for production cutover.
