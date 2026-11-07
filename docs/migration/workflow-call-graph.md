# SARGuardian reusable workflow call graph

**Source audit run:** [41966952548](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41966952548)  
**Parsed source variants:** 82 (7 Dynamic main + 35 backend main + 40 Known Place PR #85)  
**Call edges:** 20 total — 8 external reusable workflow calls and 12 local reusable workflow calls.  
**Distinct call targets:** 16.

## 1. Dynamic main callers

| Caller workflow | Job | Reusable workflow target | Ref type | Migration handling |
|---|---|---|---|---|
| `known-place-analysis.yml` | `analyze-known-place` | backend `know-place-aoi-analysis.yml` | Immutable SHA `5edf41a61d5b10b0f3d4bd8f67619d512cb1c204` | Exact pin is an ancestor of the imported Known Place PR #85 head; keep the target code revision explicit |
| `known-place-paper-reproduction.yml` | `author-exact-p05023-replay` | backend `know-place-author-exact-replay.yml` | Immutable SHA `d847b0461a2fec1bdf2abcce0a6b1d2f9dddabc9` | Preserve exact replay contract and explicit consent; do not switch to generic AOI |
| `sarguardian-aoi-wkt-dashboard.yml` | `process-products` | local `sarguardian-aoi-product-worker.yml` | Same repository/commit | Promote the reusable worker and caller together, preserve artifacts and inputs |
| `sarguardian-displacement.yml` | `process-dynamic-aoi` | local `sarguardian-aoi-wkt-dashboard.yml` | Same repository/commit | Dynamic wrapper has a distinct dispatch input contract; do not substitute backend inputs |

## 2. Backend main callers

| Caller workflow | Job | Reusable workflow target | Ref type | Migration handling |
|---|---|---|---|---|
| `know-place-aoi-dispatcher.yml` | `known-place-aoi-analysis` | backend `know-place-aoi-analysis.yml` | Immutable SHA `0e0611c12913044787ee84a39fa60a81d30ae516` | Preserve this stable current dispatcher lineage separately from Dynamic's 5edf pin |
| `know-place-paper-reproduction-dispatcher.yml` | `author-exact-p05023-replay` | backend `know-place-author-exact-replay.yml` | Immutable SHA `d847b0461a2fec1bdf2abcce0a6b1d2f9dddabc9` | Preserve author-exact launcher, P05023 identity, and raw-data cleanup gates |
| `sarguardian-aoi-wkt-dashboard.yml` | `process-products` | local `sarguardian-aoi-product-worker.yml` | Same repository/commit | Keep worker contract tied to backend main dashboard version until callers are switched together |
| `sarguardian-aoi-wkt-dashboard.yml` | `retry-products` | local `sarguardian-aoi-product-worker.yml` | Same repository/commit | Retry wave must receive only failed product IDs |
| `sarguardian-aoi-wkt-dispatcher.yml` | `run-isolated-aoi-pipeline` | backend `sarguardian-aoi-wkt-dashboard.yml` | Mutable branch `main` | Legacy/manual dispatcher path; record its payload before any deprecation or root promotion |
| `sarguardian-streaming-batch.yml` | `process-one` | local `sarguardian-product-worker.yml` | Same repository/commit | Preserve separate streaming worker; do not merge it with AOI product worker by filename |
| `sarguardian-streaming-batch.yml` | `retry-products` | local `sarguardian-product-worker.yml` | Same repository/commit | Keep retry-plan/preassembly/artifact contracts intact |

## 3. Known Place PR #85 branch callers

| Caller workflow | Job | Reusable workflow target | Ref type | Migration handling |
|---|---|---|---|---|
| `know-place-author-exact-consent-bridge.yml` | `acquire-analyze-retain-author-exact` | local `know-place-author-exact-replay.yml` | Same feature-branch commit | Consent bridge stays inactive/manual; never trigger raw acquisition on documentation/UI push |
| `know-place-generic-aoi-consent-bridge.yml` | `run-generic-aoi` | local `know-place-aoi-analysis.yml` | Same feature-branch commit | Consent bridge stays inactive/manual; preserve two-polygon behavior |
| `sarguardian-aoi-wkt-dashboard.yml` | `process-products` | local `sarguardian-aoi-product-worker.yml` | Same feature-branch commit | This is the PR #85 variant, not backend main or Dynamic variant |
| `sarguardian-aoi-wkt-dashboard.yml` | `retry-products` | local `sarguardian-aoi-product-worker.yml` | Same feature-branch commit | Preserve retry-only-failed semantics |
| `sarguardian-aoi-wkt-dispatcher.yml` | `author_exact_p05023` | backend `know-place-author-exact-replay.yml` | Mutable branch `feat/know-place-analysis` | Branch head observed as `bd7a59c54ddae7c19fd88896e877c3a530b43d9e`; before activation choose and pin the exact intended workflow commit |
| `sarguardian-aoi-wkt-dispatcher.yml` | `generic_aoi_date` | backend `know-place-aoi-analysis.yml` | Mutable branch `feat/know-place-analysis` | Same branch-ref risk; preserve the two-polygon inputs and output contract |
| `sarguardian-aoi-wkt-dispatcher.yml` | `render_author_dashboard` | backend `know-place-author-dashboard.yml` | Mutable branch `feat/know-place-analysis` | Pin exact renderer revision and verify retained artifact identity |
| `sarguardian-streaming-batch.yml` | `process-one` | local `sarguardian-product-worker.yml` | Same feature-branch commit | Keep separate streaming worker lineage |
| `sarguardian-streaming-batch.yml` | `retry-products` | local `sarguardian-product-worker.yml` | Same feature-branch commit | Preserve retry plan and preassembly checks |

## 4. Edge disposition summary

| Call type | Count | Risk / required action |
|---|---:|---|
| Local reusable workflow calls | 12 | When promoting, move caller and callee together and verify same-repository path resolution |
| External reusable calls pinned to full SHA | 4 | Preserve exact source revision and record provenance |
| External reusable calls to mutable branches | 4 | One uses backend `main`; three use `feat/know-place-analysis`. Review caller and payload, then replace branch ref with a reviewed full SHA only during approved workflow promotion |
| **Total edges** | **20** | |

The static contract analyzer deduplicates call-target strings and reports 16 distinct reusable references; the dependency parser reports all 20 individual caller/job edges. These are different counts, not conflicting audits.

## 5. Checkout refs that are not fixed at parse time

The 141 external checkout steps include three runtime-supplied refs:
- backend dashboard workflow: `needs.manifest.outputs.orchestration_sha`;
- Known Place generic AOI: `inputs.backend_science_ref`;
- Known Place author-exact replay: `inputs.backend_code_ref`.

These values must be validated as full 40-character commit IDs, tied to approved source repositories, and recorded in the run manifest. The author-exact replay currently receives the separate `b825df798ea4cb9874aa10dd01174d2a8ef73cba` code pin. Do not silently substitute PR #85 head, backend main, or current NISAR main.

## 6. Promotion sequence

1. Retain all source variants and this graph as immutable evidence.
2. Choose the canonical caller/callee version for each engine using the active API dispatch contract and source tests.
3. Promote a caller and all its reusable callees atomically to root workflows, changing only approved paths and immutable refs.
4. Set explicit least-privilege permissions on every root caller/callee; keep Production secrets inaccessible to PR code.
5. Validate input names, external checkout SHA validation, artifact names, callback ordering, retries, and cleanup with mock dispatches.
6. Keep original backend dispatch targets active until the Monorepo route has passed a no-double-dispatch pilot and rollback rehearsal.

No root production workflow was enabled by creating this call graph.
