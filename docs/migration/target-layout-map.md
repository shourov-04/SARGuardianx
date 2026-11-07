# Source-to-target layout map

**Status:** first code-promotion pass committed; runtime parity jobs are in progress. The original immutable snapshots remain intact.

## Application layer

| Source snapshot | Promoted destination | Status / notes |
|---|---|---|
| `migration/source-snapshots/dynamic/Frontend/` | `apps/web/` | Promoted as an exact copy; frontend build, lint and tests pass from this path. Vercel project root is not changed yet. |
| `migration/source-snapshots/dynamic/Backend/` | `apps/api/` | Promoted as an exact copy; the 215-test API suite passes from this path. Live Firebase/Supabase/CORS/callback environment checks remain pending. |
| Dynamic root `tools/` | `apps/tools/` | Test/runtime compatibility helpers required by original API tests. Not yet deduplicated with backend tools. |
| Dynamic `.github/workflows/` | `apps/.github/workflows/` | Inactive path compatibility fixtures; GitHub does not activate workflows below `apps/`. |
| Backend main `app/` | Not promoted | Separate SQLAlchemy/session-oriented service; caller and deployment audit required before choosing `legacy/backend-api/` or retirement. |

## Engine and science layer

| Source snapshot | Promoted destination | Status / notes |
|---|---|---|
| Backend main `dashboard/` plus non-RiverShift `tools/` | `engines/find-displacements/` | Exact copies; includes seven inactive workflow compatibility fixtures and requirement files. These mirror backend-root workflow files that original tests read by relative path; the Known Place dispatchers remain contract fixtures only. Keeps target-free AOI discovery, candidate-local floors, gated GUNW pixel diagnostics, and GOFF diagnostics separate. |
| Backend Known Place PR #85 head | `engines/known-place/` | Entire PR-head snapshot exact-copied; preserves the feature-branch ancestor, author-exact P05023 workflow and two-polygon implementation. |
| Backend main `tools/river_shift/` | `engines/river-shift/tools/river_shift/` | Exact copy of 74 tracked paths; keeps the original source-relative package/test path. Two inactive workflow fixtures are under the engine root. |
| NISAR science main | `science/nisar-core/` | Whole current science tree exact-copied. Historical non-ancestor pins remain in distinct snapshot directories. |
| Divergent worker checkouts | `migration/source-snapshots/*-pins/` | Immutable, provenance-only source snapshots; not silently overlaid into current engine code. |
 
Detailed counts and decisions are in [engine-promotion-report.md](engine-promotion-report.md).

## Workflow layer

Active workflows are only those in repository-root `.github/workflows/`. Current root workflows are:
- `migration-metadata.yml`
- `snapshot-regression-tests.yml`

The following nested locations are inactive copies/fixtures, not active workflows:
- `migration/source-snapshots/**/.github/workflows/`
- `apps/.github/workflows/`
- `engines/find-displacements/.github/workflows/`
- `engines/known-place/.github/workflows/`
- `engines/river-shift/.github/workflows/`
- `science/nisar-core/.github/workflows/`

The active root `.github/workflows/` should receive only workflows that pass the 42-file workflow register. For each selected workflow, preserve trigger filters, job graph, permissions, cross-repository checkout, artifacts, callback, retry, retention, and rollback semantics. Never bulk-copy all source workflow files.

## Verified collision result

Dynamic and backend main share 24 exact source paths: 5 paths have identical Git blobs and 19 have different blobs. The full source SHA comparison and resolution constraints are in [path-collision-report.md](path-collision-report.md). Do not overlay both source tool trees into one common root.

## Promotion verification

The validator compares path, Git file mode, object type, and blob SHA for each source and destination mapping. Any missing, extra, or changed entry in the promoted directories fails CI. See [source-import-report.md](source-import-report.md) and [validation-baseline.md](validation-baseline.md).

## Remaining dependency and deployment checks

- Trace backend root `app/` callers and workflow references.
- Identify shared utilities by import and call graph, not filename.
- Decide whether `apps/tools/` should become a versioned shared library or remain an API compatibility package; do not merge divergent backend versions.
- Verify Vercel root paths, static assets, Python function config, environment scopes and aliases before preview deployment.
- Keep production dispatch/callback endpoints and Supabase schema unchanged until isolated API and engine tests, security checks and rollback rehearsal pass.
