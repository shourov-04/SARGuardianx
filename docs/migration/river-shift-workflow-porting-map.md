# RiverShift GCOV workflow porting map

**Source workflow:** `migration/source-snapshots/backend-main/.github/workflows/river-shift-gcov-process.yml`  
**Candidate:** `migration/workflow-candidates/river-shift-gcov-process.yml`  
**Activation status:** inactive candidate only; it is not in root `.github/workflows/` and is not dispatched by the live API.

## Workflow graph preserved

The candidate retains all 20 source job IDs and their original `needs` / `if` expressions:
- `prepare`;
- four independent product matrices `batch_1`–`batch_4`, each with `max-parallel: 15`;
- four sequential `batch_N_status` reconciliation barriers;
- three failed-only retry preparation, validation, and execution waves;
- `retry_status`;
- `assemble`.

The candidate is generated from the backend-main source workflow with only seven reviewed substitutions. `tools/validate_workflow_candidates.py` reconstructs that transformation, compares the entire candidate text, parses both YAML documents, and asserts the 20-job graph, all seven 15-runner limits, action pin counts, and core artifact/retry/callback/Drive contracts.

## Path changes

The source workflow assumes the repository root contains `tools/river_shift/`. In the Monorepo the engine is at `engines/river-shift/tools/river_shift/`.

| Source path or command | Candidate path or command |
|---|---|
| `tools/river_shift/environment.yml` | `engines/river-shift/tools/river_shift/environment.yml` |
| `python -u tools/river_shift/batched_gcov_job.py` | `python -u engines/river-shift/tools/river_shift/batched_gcov_job.py` |
| `python -u tools/river_shift/validate_retry_matrix.py` | `python -u engines/river-shift/tools/river_shift/validate_retry_matrix.py` |

No job-level `working-directory` is added. This is deliberate: the worker reads and writes root-relative `prepared/`, `product-output/`, `batch-results/`, `product-artifacts/`, `retry-product-artifacts/`, and `retry-plan/` folders, and Actions artifact upload/download paths remain relative to `GITHUB_WORKSPACE`. The engine's own `process_gcov_job.py` derives the helper-script CWD from `Path(__file__).resolve().parent`, so child scripts resolve beside the promoted GCOV code without changing the outer workspace root.

## Action pins and runtimes

The source uses tag references to action versions that may execute on the retired Node 20 runtime. The candidate pins the reviewed Node 24 action commits:

| Action | Version | Immutable SHA | Occurrences |
|---|---|---|---:|
| `actions/checkout` | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` | 20 |
| `actions/upload-artifact` | v7.0.2 | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` | 8 |
| `actions/download-artifact` | v8.0.2 | `9000827ccba6bdab643e8b6fd33ac0654aef8333` | 30 |
| `mamba-org/setup-micromamba` | v3 | `f457c30a868e4760d3a6fcea5f25dc655b8edf39` | 17 |

Each SHA was resolved from the corresponding upstream tag, and the referenced `action.yml` was inspected to confirm `node24`. The artifact action versions preserve the candidate's `pattern`, `merge-multiple`, `retention-days`, `compression-level`, and `if-no-files-found` inputs.

## Semantics deliberately not changed

- Original workflow_dispatch input names, defaults, choices, and requiredness.
- Job IDs, dependency edges, branch/status gates, concurrency key, and no-cancel behavior.
- 15-product batch sizing and per-product runner isolation.
- Failed-only retry queue, three fresh-runner waves, and backoff behavior.
- Artifact names, workspace-relative artifact directories, retention days, upload/download pattern pairing, and retry receipt reconciliation.
- Callback order, callback sequence propagation, request fingerprint, and terminal state handling.
- Earthdata authentication, Drive folder parent variable name, private result publication, checksum receipt, and cleanup behavior.
- The source workflow remains the source-of-truth fixture; no engine science code was modified.

## Promotion gates still outstanding

**Static and unit validation:** PASS in [CI run 41964029591](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41964029591). The exact transformation validator passed, and the promoted RiverShift engine suite passed 259 tests. The candidate still remains inactive.

Before this candidate can enter root `.github/workflows/`:
1. Add an isolated dry-run/mock test for all 20 jobs, including batch barriers, missing artifacts, failed-only retry waves, callback sequence, Drive receipt mismatch, and terminal failure propagation.
2. Review the top-level `contents: read` permission and any additional token scope; do not broaden it by default.
3. Verify all secrets/variables by name in the target repository without transferring values.
4. Test a non-production workflow_dispatch in an isolated branch and ensure one run cannot trigger old and new processing simultaneously.
5. Keep the API dispatch destination at `moshiour0/SARGuardian-backend@main` until explicit cutover approval.

A candidate CI PASS is not permission to enable the workflow or move live processing.
