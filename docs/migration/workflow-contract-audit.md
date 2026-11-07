# Workflow contract and security audit

**Audit run:** [Snapshot Regression Tests 41966952548](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41966952548)  
**Auditor:** `tools/audit_workflow_contracts.py`  
**Source refs:**
- Dynamic main `dd64b7adc90594f1d7f316b352e39fbac2013cb6`
- Backend main `97d849454918b1425ac41bb70e7a32d11cfd3833`
- Known Place PR #85 head `bfde7dde8ada92a03054cd8dbad8daa7a5c119f8`

## Coverage

The audit parsed 82 workflow-file instances with **zero YAML parse errors**:

| Source tree | Workflow versions |
|---|---:|
| Dynamic main | 7 |
| Backend main | 35 |
| Known Place PR #85 head | 40 |
| **Total** | **82** |

The PR #85 feature tree intentionally contributes its own 40 workflow variants. The count does not mean there are 82 unique workflow filenames; 17 PR #85 workflows have exactly the same path and blob as backend main, while 8 others differ and 15 are feature-branch additions.

## Trigger and integration inventory

| Measure | Workflow-instance count |
|---|---:|
| `workflow_dispatch` | 61 |
| `push` | 30 |
| `pull_request` | 12 |
| `workflow_call` | 11 |
| References to reusable workflow calls | 16 |
| Workflow instances referencing secrets | 58 |
| Workflow instances checking out external repositories | 41 |
| Workflow instances with retry-related markers | 23 |
| Workflow instances containing `continue-on-error` | 5 |
| Artifact upload/download steps | 189 |

Trigger counts are not additive: one workflow can declare multiple events. The external checkout repositories observed are:
- `moshiour0/SARGuardian`
- `moshiour0/SARGuardian-backend`
- `moshiour0/SARGuardian_Dynamic`
- `Sagormodak/SARGuardian`

The legacy `Sagormodak/SARGuardian` checkout is an explicit provenance/ownership review item. Do not silently retarget it to `moshiour0/SARGuardian`.

## Reusable workflow call graph

The dedicated workflow dependency parser now enumerates **20 caller/job edges**:
- 12 local reusable workflow calls;
- 8 external reusable workflow calls;
- 16 distinct call-target strings after deduplication.

The 20-edge list is in [workflow-call-graph.md](workflow-call-graph.md). It identifies:
- Dynamic Known Place generic and author-exact calls;
- backend-main Known Place dispatchers;
- Dynamic/backend/PR #85 variants of the AOI dashboard and reusable product workers;
- the separate streaming worker;
- the PR #85 consent bridges and feature-branch dispatcher calls.

Four of the eight external reusable calls use mutable refs: one `@main` dashboard dispatcher and three `@feat/know-place-analysis` calls. Before promotion, replace each with an intentionally selected and verified immutable SHA, preserving the current API dispatch contract. The remaining four external reusable calls are full-SHA pinned.

The same parser reports 141 external checkout steps. Three use runtime-selected refs rather than static SHAs: the Dynamic dashboard orchestration SHA output, Known Place `backend_science_ref`, and author-exact `backend_code_ref`. These must be validated as 40-character commit IDs and constrained to the expected repository/source ownership before any operational root workflow is activated.

## Permission review

There are 55 workflow instances with a top-level `permissions` block. The analyzer identified 25 workflow instances with at least one job that has neither job-level nor top-level explicit permissions. Several are inherited duplicates in the Known Place PR #85 tree.

Affected workflow instances:

- Dynamic main: `sarguardian-aoi-product-worker.yml`.
- Backend main: `earthdata-auth-test.yml`, `nisar-discovery-test.yml`, `nisar-goff-timeseries-test.yml`, `nisar-gunw-earthaccess-discovery-test.yml`, `nisar-gunw-earthaccess-read-test.yml`, `nisar-gunw-science-test.yml`, `nisar-gunw-timeseries-test.yml`, `nisar-multi-granule-storage-test.yml`, `nisar-single-download-test.yml`, `runner-test.yml`, `sarguardian-aoi-product-worker.yml`, `sarguardian-product-worker.yml`.
- Known Place PR #85: the same 12 inherited/changed workflow names above, including `sarguardian-aoi-product-worker.yml` and `sarguardian-product-worker.yml`.

The source workflows are snapshots and were not changed by this audit. Any workflow promoted to root must declare explicit least-privilege permissions at top-level and/or per job. Do not assume the repository's current default token permissions are appropriately restricted.

## Action pinning

The 432 unpinned action-reference occurrences break down as follows:

| Action reference | Occurrences |
|---|---:|
| `actions/checkout@v4` | 141 |
| `actions/download-artifact@v4` | 111 |
| `actions/setup-python@v5` | 79 |
| `actions/upload-artifact@v4` | 78 |
| `mamba-org/setup-micromamba@v3` | 22 |
| `actions/setup-node@v4` | 1 |
| **Total** | **432** |

These counts include duplicated workflow variants and therefore are not 432 unique action names. A version tag is a moving reference; it is not an immutable SHA pin.

The Monorepo's own root validation workflows use immutable SHA pins for checkout, setup-python, and setup-node. When an operational source workflow is promoted, pin each third-party action to a verified immutable commit and record the action release/commit provenance. Do not rewrite the archival source snapshots.

## Highest-risk processing workflows

### RiverShift GCOV worker

Backend-main `river-shift-gcov-process.yml` has:
- 75 unpinned action-reference occurrences;
- 38 artifact upload/download steps;
- ASF/Earthdata, Drive, and callback secret references;
- manual `workflow_dispatch` trigger;
- retry and failure-continuation markers.

This is the 20-job processing graph: prepare, four sequential batch/status barriers, up to three failed-only retry waves, final assemble. Any promotion must retain the graph and retry-only-failed-product semantics. A `continue-on-error` stage must not result in an outer green conclusion when a required processing stage failed.

### Guarded Monorepo root port

The validated candidate has now been copied to `.github/workflows/river-shift-gcov-process.yml` with one explicit preflight job (21 root jobs total). The 20-job source candidate remains unchanged under `migration/workflow-candidates/`.

- Root workflow trigger is `workflow_dispatch` only; no push or pull-request trigger.
- The new preflight job reads only the repository variable `MONOREPO_RIVERSHIFT_PROCESSING_ENABLED`. Unless it equals the literal string `true`, it fails before checkout, credentials, Earthdata, Drive, callback or any processing step.
- The prepare job requires successful preflight; all batch/status/retry/assemble jobs remain dependent on prepare and keep the original order and conditions.
- The Monorepo API still defaults to the existing Backend repository/workflow/ref. The root workflow is not the active dispatch target and the opt-in variable must remain unset until the API routing, secrets, callback, artifact, retention, mock and rollback gates pass.
- The workflow validator now compares the root YAML against the validated candidate and allows only the extra credential-free preflight gate and `prepare.needs: preflight`. It checks that the root gate is fail-closed and contains no secret references or third-party actions.

A YAML/CI pass and a mock dispatch/skip test are still required for the root port. The initial static candidate test alone is not proof of the root workflow's runtime behavior.

### Find Displacements AOI workflow

Three variants exist:
- Dynamic main `sarguardian-aoi-wkt-dashboard.yml`: 18 unpinned action references, 9 artifact steps, Dynamic + science + backend checkouts.
- Backend main `sarguardian-aoi-wkt-dashboard.yml`: 23 unpinned action references, 10 artifact steps, Dynamic + science + backend checkouts.
- Known Place PR #85 branch version: 15 unpinned action references, 8 artifact steps.

They are not interchangeable. Compare callers, payload inputs, science pins, artifact names, and callbacks before choosing one canonical root workflow.

### Streaming and reassembly

- Backend-main `sarguardian-streaming-batch.yml`: 30 unpinned action references, 20 artifact steps, retries and pre-assembly verification.
- `sarguardian-reassemble-existing.yml`: 10 unpinned action references, 7 artifact steps; manual recovery path.
- `sarguardian-aoi-product-worker.yml` and `sarguardian-product-worker.yml` are different reusable workers; compare their input/output and retention contracts rather than merging by name.

## Push-trigger safety

The source workflow register separately identifies three backend-main retained RiverShift replay workflows with `push` triggers:
- `river-shift-opera-dswx-s1-retained-replay.yml`
- `river-shift-run36-retrospective-replay.yml`
- `river-shift-sentinel2-retained-replay.yml`

The Known Place PR #85 feature tree adds several credentialed `push`-trigger workflows, including author-exact acquisition/replay, consent bridges, map rendering, DEM acquisition, and Drive retry. These must remain inactive or be converted to an explicit manual/isolated trigger after the behavior has been reviewed. A monorepo docs or UI push must never unexpectedly start raw-data acquisition, external replay, or Drive upload.

## Disposition rules

1. Original source workflows remain authoritative while migration is in progress.
2. No source workflow copy is activated at root by bulk copy.
3. New root workflows must use explicit permissions, immutable action pins, precise path/branch triggers, least-privilege cross-repo tokens, and redacted logs.
4. Every external checkout must identify repository, ref, checkout path, and whether the ref is immutable.
5. Every callback must retain endpoint, signature, request ID, ordering, and terminal status semantics.
6. Every artifact must retain name, upload/download pairing, content identity, retention period, and cleanup rules.
7. Reusable workflow callers must be enumerated; updating a called workflow without all callers is unsafe.
8. Preserve the existing production dispatch destinations until the new root workflow contract passes dry-run/mock parity and explicit cutover is approved.

## Audit limitations

This is a static YAML/contract inventory. It does not prove that a workflow is currently called in production, that its referenced external repository/ref is still reachable, or that its runtime artifact/secret behavior is correct. Those require call-graph tracing and workflow-run evidence, documented before activation.
