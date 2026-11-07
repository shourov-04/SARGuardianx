# Known Place PR #85 workflow delta

**Compared refs**
- Feature branch / PR base: `moshiour0/SARGuardian-backend@bd7a59c54ddae7c19fd88896e877c3a530b43d9`
- PR #85 head: `moshiour0/SARGuardian-backend@bfde7dde8ada92a03054cd8dbad8daa7a5c119f8`
- Backend main comparison: `moshiour0/SARGuardian-backend@97d849454918b1425ac41bb70e7a32d11cfd3833`

## PR #85 head versus backend main

| Relationship | Count |
|---|---:|
| Workflow files in PR #85 head | 40 |
| Workflow files in backend main | 35 |
| PR #85-only workflows | 15 |
| Same-path workflows with different content | 8 |
| Same-path, identical workflows | 17 |
| Backend-main-only workflows absent from PR #85 branch | 10 |

These counts are path/blob comparisons. They do not imply every workflow in the feature branch should be activated.

## 15 PR #85-only workflows

| Path | SHA at PR #85 head |
|---|---|
| `.github/workflows/know-place-analysis-reanalysis.yml` | `see immutable PR #85 snapshot` |
| `.github/workflows/know-place-analysis-run.yml` | `see immutable PR #85 snapshot` |
| `.github/workflows/know-place-analysis-validation.yml` | `c2b2888bc1c87c2a78936345c76242a69bc817ff` |
| `.github/workflows/know-place-aoi-analysis.yml` | `deb45457be51fa7921a7a4967ba6d97b5be15a68` |
| `.github/workflows/know-place-author-dashboard.yml` | `see immutable PR #85 snapshot` |
| `.github/workflows/know-place-author-exact-consent-bridge.yml` | `c6e0cc8c72d658eaaacde3b80df8fb34606311b9` |
| `.github/workflows/know-place-author-exact-replay.yml` | `0b425fd118ca39aefbf9f61c7eb8efcb9d313f75` |
| `.github/workflows/know-place-author-map-render.yml` | `see immutable PR #85 snapshot` |
| `.github/workflows/know-place-dem-source-acquisition.yml` | `see immutable PR #85 snapshot` |
| `.github/workflows/know-place-displacement-null-audit.yml` | `see immutable PR #85 snapshot` |
| `.github/workflows/know-place-generic-aoi-consent-bridge.yml` | `5b149a4e4267c15eefb7000b952030c473e8eb45` |
| `.github/workflows/know-place-generic-aoi-drive-retry.yml` | `see immutable PR #85 snapshot` |
| `.github/workflows/know-place-generic-map-browser-smoke.yml` | `see immutable PR #85 snapshot` |
| `.github/workflows/know-place-retained-crown-audit.yml` | `see immutable PR #85 snapshot` |
| `.github/workflows/know-place-terrain-datum-sensitivity.yml` | `see immutable PR #85 snapshot` |

The full file/blob manifest is the PR #85 source tree under `migration/source-snapshots/backend-known-place-pr85/.github/workflows/`. The table highlights the new Know Place-specific workflow surface; SHA values not repeated above remain verifiable from the immutable snapshot and its source commit.

## Eight same-path, changed-content workflows

| Path | PR #85 head SHA | Migration implication |
|---|---|---|
| `dashboard-assets-test.yml` | `[PR snapshot]` | Keep branch-specific asset/test contract; compare dependencies and output assets |
| `sarguardian-aoi-code-validation.yml` | `[PR snapshot]` | Compare Python/science pins and static/parser test scope |
| `sarguardian-aoi-product-worker.yml` | `[PR snapshot]` | Compare reusable inputs, science checkout, output/retention contract |
| `sarguardian-aoi-wkt-dashboard.yml` | `[PR snapshot]` | Compare Dynamic callback/API, job barriers, retries, final status |
| `sarguardian-aoi-wkt-dispatcher.yml` | `[PR snapshot]` | Compare dispatch payload, token permissions, and duplicate-run protection |
| `sarguardian-product-worker.yml` | `[PR snapshot]` | Compare reusable-worker role and caller list |
| `sarguardian-retention-ci.yml` | `e02ca99b48a640a0636326aed3308ee6219120d8` | Compare retention fixtures and pinned-science regression |
| `sarguardian-streaming-batch.yml` | `[PR snapshot]` | Compare batch/retry/assemble and artifact/receipt semantics |

Exact PR-head blob SHAs for all eight are available through the immutable PR #85 snapshot tree. Do not promote one version based on workflow filename alone.

## Seventeen unchanged workflows

The following paths have identical content in PR #85 head and backend main:
- `earthdata-auth-test.yml`
- `earthdata-token-smoke-test.yml`
- `nisar-discovery-test.yml`
- `nisar-goff-timeseries-test.yml`
- `nisar-gunw-earthaccess-discovery-test.yml`
- `nisar-gunw-earthaccess-read-test.yml`
- `nisar-gunw-science-test.yml`
- `nisar-gunw-timeseries-test.yml`
- `nisar-multi-granule-storage-test.yml`
- `nisar-single-download-test.yml`
- `retention-archive-tests.yml`
- `runner-test.yml`
- `sarguardian-aoi-live-discovery-check.yml`
- `sarguardian-live-validation.yml`
- `sarguardian-reassemble-existing.yml`
- `sarguardian-retention-pilot.yml`
- `sarguardian-science-worker.yml`

## Ten backend-main-only workflows

These are absent from the PR #85 feature branch and must not be lost when the Known Place tree is promoted:
- `dashboard-real-artifact-smoke.yml`
- `know-place-aoi-dispatcher.yml`
- `know-place-paper-reproduction-dispatcher.yml`
- `river-shift-gcov-process.yml`
- `river-shift-independent-reference-validation.yml`
- `river-shift-opera-dswx-s1-retained-replay.yml`
- `river-shift-run36-retrospective-replay.yml`
- `river-shift-sentinel2-retained-replay.yml`
- `river-shift-tests.yml`
- `sarguardian-extended-science.yml`

This is why the Known Place PR snapshot and backend main snapshot must coexist as separate provenance sources. The engine promotion kept the PR #85 package while Find Displacements and RiverShift were promoted separately from backend main.

## Activation and migration rule

- These workflows are archived within the Known Place source snapshot.
- Engine-local workflow copies in this repository are test fixtures, not active GitHub Actions.
- Review credential use, caller graph, external source checkouts, environment names, Drive writes, callback destinations, retention, and trigger scope for every workflow before any selected file is moved into root `.github/workflows/`.
- Keep author-exact and consent bridge workflows manual/gated; never allow an ordinary monorepo documentation push to initiate external-data acquisition or raw-product retention.
