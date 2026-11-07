# Evidence-based active runtime scope — 2026-11-06

**Purpose:** identify the currently application-linked SARGuardian dispatch paths and the exact source revisions they execute. This is not authorization for Production cutover.

## Corrected decision

Do not activate all 82 historical workflow instances. Keep their source snapshots and dispositions for provenance, but promote only the workflows currently connected to Dynamic's API and proven dispatch history.

| Tier | Workflow files | Evidence | Monorepo decision |
|---|---|---|---|
| **Primary, currently proven application runtime** | Find Displacements dispatcher → dashboard engine → product worker; generic Known Place dispatcher → two-polygon reusable workflow | Find Displacements run [42097077601](https://github.com/moshiour0/SARGuardian-backend/actions/runs/42097077601) succeeded after a failed-only GUNW retry, dashboard assembly and terminal callback. Generic Known Place runs [41533701551](https://github.com/moshiour0/SARGuardian-backend/actions/runs/41533701551) and [41533582770](https://github.com/moshiour0/SARGuardian-backend/actions/runs/41533582770) succeeded and produced workflow artifacts. | Keep the 5-file primary call graph in Monorepo. The generic Known Place engine is pinned to its actual current Backend runtime commit 0e0611c12913044787ee84a39fa60a81d30ae516, not just the older PR #85 head. |
| **Connected but gated feature paths** | RiverShift GCOV workflow; author-exact P05023 dispatcher → replay workflow | RiverShift run [42089984247](https://github.com/moshiour0/SARGuardian-backend/actions/runs/42089984247) matched 14/14 catalogue granules but correctly stopped before products at EVENT_WINDOW_NOT_BRACKETED. Author-exact run [41423614257](https://github.com/moshiour0/SARGuardian-backend/actions/runs/41423614257) passed its consent gate and uploaded its derived bundle/receipt, but source-manifest completeness failed and post-delete cleanup was blocked. | Preserve both call graphs, but keep their processing gates false until a successful positive-case pilot satisfies the scientific and retention acceptance criteria. |
| **Migration CI** | Seven test/security/metadata workflows listed in migration/active-runtime-scope.json | Snapshot, source regression, metadata, secret-scan, retention, dashboard and AOI code checks. | Keep as CI only; they are not user-job processing workflows. |

## Known Place branch/merge lineage — verified

- Backend branch feat/know-place-analysis currently points to bd7a59c54ddae7c19fd88896e877c3a530b43d9e.
- Backend main is 97d849454918b1425ac41bb70e7a32d11cfd3833.
- PR [#85](https://github.com/moshiour0/SARGuardian-backend/pull/85), the independent two-polygon implementation, is still **Draft/Open**, not merged. Its base is feat/know-place-analysis; its head is bfde7dde8ada92a03054cd8dbad8daa7a5c119f8.
- This does **not** mean Known Place is absent from current main. Backend main has a generic dispatcher whose reusable workflow and backend_science_ref both pin 0e0611c12913044787ee84a39fa60a81d30ae516. The pin is 78 commits ahead of the current feature-branch pointer and 32 commits ahead of the PR #85 head.
- PR [#86](https://github.com/moshiour0/SARGuardian-backend/pull/86) merged into main as 50af9e5413db5f797c4f2866bc4685be84a9fcef, but its scope was only the GOFF-candidate-to-suggested-measurement-polygon handoff. It did not merge PR #85's generic two-polygon engine.
- Backend main's author-exact dispatcher separately calls reusable workflow pin d847b0461a2fec1bdf2abcce0a6b1d2f9dddabc9 and passes Backend code pin b825df798ea4cb9874aa10dd01174d2a8ef73cba.

Therefore, the Monorepo retains PR #85's complete immutable branch snapshot for its research lineage, while the ten runtime/test files that differ from current production generic pin 0e0611c are explicitly overlaid into engines/known-place. The exact source blob hashes are recorded in migration/active-runtime-pins/known-place-generic-0e061.json. The source-snapshot verifier excludes only these ten deliberate overlays from PR #85 directory parity; the active-pin validator checks each destination blob against the 0e061 manifest.

## Workflow call graphs in Monorepo

| Feature | API surface | Root workflow chain | State |
|---|---|---|---|
| Find Displacements | apps/api/app/displacements.py | sarguardian-aoi-wkt-dashboard.yml → sarguardian-aoi-dashboard-engine.yml → sarguardian-aoi-product-worker.yml | Primary runtime |
| Known Place generic two-polygon | apps/api/app/known_place.py | know-place-aoi-dispatcher.yml → know-place-aoi-analysis.yml | Primary runtime; exact active source pin 0e061 copied and hash-checked |
| RiverShift NISAR GCOV | apps/api/app/river_shift_jobs.py | river-shift-gcov-process.yml | Gated pending positive-case pilot |
| Known Place author-exact P05023 | apps/api/app/known_place.py | know-place-paper-reproduction-dispatcher.yml → know-place-author-exact-replay.yml | Gated pending complete successful replay |

Generic Known Place and author-exact remain separate request schemas, workflow pins, artifact paths and safety gates. The author-exact path requires exact [run-know-place] consent and the fixed P05023 source identity; do not merge it into the generic polygon workflow.

## What remains outside the runtime call graph

Do not turn standalone catalogue probes, manual renderer workflows, historical branch bridges, one-off validation runs, alternate legacy worker variants, or unrelated failed experiments into automatic user-job dependencies. Their source versions remain in immutable source snapshots and the 82-entry workflow disposition register. A source archive is not a deployment dependency.

## Cutover acceptance gates

- Store Firebase, Supabase, GitHub dispatch, callback-signing and Drive-read credentials only in the API server's private environment; keep every value outside Git and browser bundles.
- Monorepo Actions secrets: Earthdata access, Drive OAuth client/refresh token and GOOGLE_DRIVE_PARENT_FOLDER_ID. Never expose these in apps/web or VITE_*.
- Authenticated Preview login, owner-scoped Supabase persistence/readback, dispatch correlation, status polling, signed callbacks, terminal failure propagation and artifact access.
- A successful isolated Find Displacements run using Monorepo workflow files and exact science pin.
- A successful generic Known Place catalog-only check and positive two-polygon measurement pilot using exact 0e061 files.
- A scientifically eligible, positive-case RiverShift GCOV pilot.
- A complete author-exact P05023 replay only if that feature is included in the release; require all five exact source hashes, author metric tables, Drive byte verification and raw cleanup receipt.
- Read-only Supabase migration-history verification; independent science review; dependency/licensing review; rollback rehearsal.
- Explicit owner approval before merging to the production default branch or changing any Production Vercel/API/DB target.

## Safety boundary

All Monorepo processing switches remain false. Existing Dynamic Production, Backend Actions, Production callback URLs, Production Vercel aliases and the original Supabase project remain unchanged.

Machine-readable counterpart: migration/active-runtime-scope.json.
