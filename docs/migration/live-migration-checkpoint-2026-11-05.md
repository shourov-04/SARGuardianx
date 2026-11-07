# SARGuardian Monorepo — live migration checkpoint

**Audit date:** 2026-11-05  
**Target branch:** `migration/source-snapshot-import`  
**Current documentation branch head:** `151f59854705351d34f234c4c78595ffe7d31a60` (checkpoint/readiness/README documentation commits only)  
**Last code-bearing integration commit:** `1bcc0648e01794496ec08375e3f245aaadaaf2cf` — [fail-closed Find Displacements dispatcher](https://github.com/moshiour0/SARGuardian-Monorepo/commit/1bcc0648e01794496ec08375e3f245aaadaaf2cf)

This checkpoint supersedes earlier “latest head” references in the readiness report. It is a source, branch and integration audit; it does not authorize production cutover.

## 1. Current source-of-truth pins

The selected source baselines remain:

| Source | Selected immutable revision | Selected responsibility |
|---|---|---|
| [SARGuardian_Dynamic](https://github.com/moshiour0/SARGuardian_Dynamic/commit/dd64b7adc90594f1d7f316b352e39fbac2013cb6) | `dd64b7adc90594f1d7f316b352e39fbac2013cb6` | React/Vite app, active Firebase/Supabase FastAPI API, job persistence and callbacks |
| [SARGuardian-backend](https://github.com/moshiour0/SARGuardian-backend/commit/97d849454918b1425ac41bb70e7a32d11cfd3833) | `97d849454918b1425ac41bb70e7a32d11cfd3833` | Processing workers, RiverShift GCOV engine, Find Displacements orchestration and Actions |
| [SARGuardian science](https://github.com/moshiour0/SARGuardian/commit/9fcb543ef28a7f6fe70a379aed9cfe3e43e277ec) | `9fcb543ef28a7f6fe70a379aed9cfe3e43e277ec` | Canonical NISAR science source baseline |

The exact snapshots and promoted-path copies are already in the Monorepo. Ten immutable source snapshots preserve **1,685 tracked paths**. The import includes the Known Place PR #85 feature lineage, the separate author-exact backend code pin, both historical NISAR pins, the Dynamic historical callback API, backend historical reassembly tools and the explicitly identified legacy fork. Do not flatten these revisions into one undifferentiated source tree.

### Historical runtime pins that must remain explicit

- Find Displacements' current AOI worker checks out NISAR science revision `006d4cd1485cf80e509eaf8717c12e9c6390ac09`. The Monorepo preserves that full commit history and the worker verifies the exact checkout SHA. It must not be silently changed to the canonical science-main package.
- The backend Known Place author-exact dispatcher supplies `b825df798ea4cb9874aa10dd01174d2a8ef73cba` as its separate code pin. It is a sibling revision, not the PR #85 engine head. Its exact tree is preserved separately. Keep the P05023 replay bound to its author-exact code and product identity.
- The Known Place generic engine is promoted from backend PR #85 head `bfde7dde8ada92a03054cd8dbad8daa7a5c119f8`; this preserves the feature branch's two-polygon lineage. Backend main alone is not a substitute.

## 2. Open source-PR disposition

The selected source is the latest integrated `main` snapshot, not whichever feature branch has the most recent-looking name. Open PRs are reviewed as deltas; they are not wholesale merge instructions.

| Source PR | Current disposition | Migration decision |
|---|---|---|
| Dynamic [#86](https://github.com/moshiour0/SARGuardian_Dynamic/pull/86), global homepage positioning | Open; four commits ahead and two behind Dynamic main in the observed comparison. Changes the RiverShift card to `RESEARCH PREVIEW`, adjusts CTA/description and frontend README/tests. | Keep pending as a small product-copy decision. Do not replace the promoted Dynamic-main snapshot with this stale branch. Decide the meaning of card availability vs scientific review state before a targeted port. |
| Dynamic [#75](https://github.com/moshiour0/SARGuardian_Dynamic/pull/75), event-observation offset display | Open; its event timing concept is already represented in the current main page via `event_observation_timing` and the shared display helper. | Do not cherry-pick the stale page file wholesale. Verify any remaining wording difference against the current main page before a minimal patch. |
| Dynamic [#76](https://github.com/moshiour0/SARGuardian_Dynamic/pull/76), OPERA cross-check copy | Open; the targeted branch changes the validation explainer in RiverShiftPage. Current main already shows `NO_SCORE` when eligible independent water metrics are absent, but does not contain the PR's explicit ±3-day / 80%-common-support copy in that section. | Keep as a targeted UX/documentation candidate; review its thresholds against the backend validator contract before porting. Do not cherry-pick the entire stale branch. |
| Backend [#135](https://github.com/moshiour0/SARGuardian-backend/pull/135), event-observation timing | Open; current backend main already includes `event_observation_timing` and the first-post-event acquisition gap in its result summary. | Treat the code intent as already present in selected backend main; no duplicate cherry-pick. Confirm through the backend's merged Run #150 lineage. |
| Backend [#134](https://github.com/moshiour0/SARGuardian-backend/pull/134), validation API origin | Open; current independent-reference workflow defaults to `https://sarguardian-backend-api.vercel.app`, not the frontend domain. | Treat the corrected API origin as present in selected backend main; no duplicate cherry-pick. |
| Backend [#85](https://github.com/moshiour0/SARGuardian-backend/pull/85), Known Place independent polygons | Open/draft against `feat/know-place-analysis`, not backend main. | Its exact head is the promoted Known Place source. Preserve its lineage and do not merge it into backend main as a migration shortcut. |
| Science [#12](https://github.com/moshiour0/SARGuardian/pull/12), exact GUNW acquisition-network grouping | Open; one-commit code delta to `pixel_stack.py`, adding frame/subswath/bandwidth/polarization/CRID network identity and stricter grid checks. The same promoted runtime file blob is present in the preserved `006d4cd` worker pin. | Keep the canonical science-main package unchanged for now; preserve the pinned runtime behavior. Run the complete NISAR and promoted Find Displacements suites before any canonical science-main promotion. |
| Science [#8](https://github.com/moshiour0/SARGuardian/pull/8), regression guards | Open; large feature/audit branch. | Historical evidence and candidate tests only. Do not overlay the entire branch on canonical science main. |
| Science [#9](https://github.com/moshiour0/SARGuardian/pull/9), per-script audit docs | Open; documentation-only branch in the observed comparison. | Keep the audit as a separate reviewable documentation contribution; it must not change the pinned runtime source. |
| Science [#5](https://github.com/moshiour0/SARGuardian/pull/5), raw Target 4/9 investigation | Open/draft and includes large science/audit deltas. | Preserve the report/evidence separately. Do not use its diagnostics to relax pixel masks or thresholds without an independent scientific decision. |

### RiverShift source-lineage checks

The current Dynamic main contains the searchable AOI map flow and current result page. Backend main contains the actual GCOV worker, actual post-event acquisition-gap metadata, full-resolution candidate-mask overlap audit and retained evidence logic. The current RiverShift UI keeps observed water, new-water candidates and persistent land/water candidates distinct, and the validation panel returns `NO_SCORE` without eligible independent-reference metrics.

The later OPERA DSWx-S1 / Run #36 replay and RTC-S1 inventory branches are preserved as evidence-only source snapshots. They are not active production workflows. A retained replay, a checksum match, internal overlap QA or a passing test is not field truth. Run #36 remains `PROVISIONAL / NO_MATCH_NO_SCORE` where no eligible temporally matched reference exists.

## 3. Promoted code and root workflow boundary

The promoted layout is:

- `apps/web`: React/Vite user interface.
- `apps/api`: active Dynamic FastAPI API, including Firebase/Supabase job state and callback handlers.
- `engines/find-displacements`: target-free AOI workflow and diagnostics.
- `engines/known-place`: separate two-polygon and author-exact research engine.
- `engines/river-shift`: independent GCOV worker and test suite.
- `science/nisar-core`: canonical science-main source, separate from immutable historical runtime pins.
- `migration/source-snapshots/` and `migration/source-branch-snapshots/`: immutable provenance, not runtime search paths.

Selected root workflow entrypoints are gated:

| Root workflow | Function | Safety state |
|---|---|---|
| `.github/workflows/sarguardian-aoi-wkt-dashboard.yml` | Find Displacements dispatcher | `MONOREPO_DISPLACEMENT_ACTIONS_ENABLED=true` required before downstream checkout/credentials |
| `.github/workflows/sarguardian-aoi-dashboard-engine.yml` | Find Displacements reusable dashboard engine | Called only through the gated dispatcher; preserves exact `006d4cd` science pin |
| `.github/workflows/know-place-aoi-dispatcher.yml` | Known Place generic two-polygon dispatcher | Credential-free preflight; raw work additionally gated by user consent and `MONOREPO_KNOWN_PLACE_ACTIONS_ENABLED=true` |
| `.github/workflows/know-place-aoi-analysis.yml` | Known Place reusable engine | Explicitly mapped worker secrets; catalog-only dry-run path |
| `.github/workflows/river-shift-gcov-process.yml` | RiverShift 15-product-batch GCOV processor | Credential-free preflight; requires `MONOREPO_RIVERSHIFT_PROCESSING_ENABLED=true` |

The source workflows remain unchanged in their snapshots. Retained replays, manual data-download checks and independent-reference workflows have not been activated as production dispatchers. Do not bulk-copy all source workflows into root `.github/workflows/`.

## 4. Dispatch and secret configuration — no cutover

The promoted API preserves compatibility defaults to the existing repositories:

- Find Displacements and Known Place Actions remain disabled by default; Known Place generic and author-exact destinations remain configurable independently and default to backend dispatchers.
- RiverShift `RIVERSHIFT_ACTIONS_ENABLED` defaults to `false`; its repository/workflow/ref are configurable and currently default to `moshiour0/SARGuardian-backend` / `river-shift-gcov-process.yml` / `main`.
- The Monorepo API must not be pointed at the root workflow merely because that workflow exists. First prove the payload, signed callback URL/secret, status sequence, artifact names, retention receipts, retry behavior and duplicate-dispatch prevention against a non-production route.

Secret *names* are part of the contract; values must be set separately in the target environment and must never be copied into Git. Relevant contracts include `GITHUB_ACTIONS_TOKEN`, `DISPLACEMENT_CALLBACK_SECRET`, the separate Known Place destination variables, `RIVERSHIFT_GITHUB_ACTIONS_TOKEN`, `RIVERSHIFT_CALLBACK_SECRET`, `EARTHDATA_TOKEN` (or the approved username/password fallback), `GOOGLE_DRIVE_OAUTH_CLIENT_JSON`, `GOOGLE_DRIVE_REFRESH_TOKEN` and `GOOGLE_DRIVE_PARENT_FOLDER_ID`. No secret value is present in this report.

## 5. Current CI and deployment blockers

### GitHub Actions

The latest workflow runs triggered by current PR head `151f59854705351d34f234c4c78595ffe7d31a60` (documentation-only commits after code-bearing commit `1bcc0648e01794496ec08375e3f245aaadaaf2cf`) were:

| Run | Workflow | Observed outcome |
|---|---|---|
| [41996716079](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41996716079) | Snapshot Regression Tests | All 17 regression jobs completed as failure with `steps=null` |
| [41996716004](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41996716004) | Migration Metadata Validation | The provenance job failed with `steps=null` |
| [41996715986](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41996715986) | Historical Secret Scan | The Gitleaks job failed with `steps=null` |

Earlier code-head runs 41990721765/786/757 were also retried through GitHub's failed-job rerun operation and reproduced the same pre-step state. The current documentation-head runs 41996716079/004/986 then failed in the same way without a runner step. No runner logs or artifacts were available. Therefore:

- This is **not evidence of Python/TypeScript/test assertion failures**, because none of those steps started.
- It is also **not a passing validation**. Current-head regression, metadata and full-history secret-scan gates remain unresolved.
- The exact account/repository cause is not established. Do not attribute it to plan limits, permissions or a GitHub outage without account-level evidence.

Historical green runs remain useful for the revisions they actually tested: [41980756059](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41980756059) completed 17/17 before the latest source-branch archive and follow-up commits. It must not be used as the current-head green signal.

### Vercel

The Monorepo's Web and API Preview projects were created with separate roots (`apps/web` and `apps/api`) and had earlier READY Preview deployments. Newer PR checks for both projects now return the Vercel build-rate-limit URL. The earlier Preview deployments are consequently stale relative to the current migration head. This is a hosting build quota blocker, not evidence that the latest source compiled or failed to compile.

Do not repoint existing Production projects or aliases. The current Monorepo Preview remains isolated; API processing dispatch flags must remain disabled until staging smoke tests pass.

### Supabase

The local Supabase config and seven migration files are promoted. Remote migration history does not yet reconcile cleanly with local version prefixes/names. Perform read-only history reconciliation and retention/RLS review before any future `db push`. No remote schema change has been applied.

## 6. Release gate and next sequence

The Monorepo is **source-consolidated and code-promoted, but not production-ready**.

1. Restore a functioning GitHub Actions runner path and obtain a successful current-head regression, metadata and full-history secret-scan run. Do not use a workflow with `steps=null` as validation.
2. Complete the RiverShift 20-job mock/dry-run: all four 15-product batch barriers, artifact absence/mismatch, failed-only retry waves, callback ordering, Drive receipt checks and final non-green failure propagation.
3. Run mock dispatch/HMAC callback/status-polling round trips for Find Displacements, Known Place and RiverShift. Prove exactly one repository receives each dispatch.
4. Resolve the Vercel build quota, redeploy current code to Preview and test non-production auth, Supabase job persistence, map/search, API origin and signed callbacks. Keep all real processing flags off.
5. Reconcile Supabase migration history read-only. Do not reapply an existing migration.
6. Run one isolated, source-checked pilot per engine, compare outputs/manifests and obtain independent scientific review appropriate to each result.
7. Rehearse rollback to the original Dynamic/Backend routes. Cut over one engine at a time only after the user explicitly approves the production change.

**Never promote a structural/provenance PASS to scientific validation.** An anomaly remains a candidate; pairwise LOS is not cumulative or 3-D motion; actual-date playback is not interpolation or forecasting; `NOT MEASURED` is not zero.


### GitHub runner-allocation evidence — deeper REST metadata check

A direct read of GitHub's Actions REST run and job payload for Snapshot Regression Tests run 41997989469 confirms:
- all 17 jobs were created with label `ubuntu-24.04`;
- every failed job has `runner_id=0`, blank `runner_name`, `runner_group_id=0`, blank `runner_group_name`;
- `steps=[]` in GitHub REST (the connector renders this as `steps=null`);
- jobs completed 2–12 seconds after creation, with no runner assignment;
- the workflow run itself started and completed in roughly 13 seconds.

This is stronger evidence that the failure occurs **before hosted-runner allocation**, not inside Python, Node, package installation, workflow shell steps or scientific tests. It still does not identify the reason. The GitHub connector did not expose repository Actions-permission/billing settings or the job's internal startup message, so do not assume the cause is plan quota, disabled Actions, billing or GitHub service incident. The owner needs to inspect the repository's Actions settings and account billing/usage (and confirm GitHub-hosted runner availability) in GitHub UI/support. Keep the migration validation gate blocked until a fresh run receives a nonzero runner ID and executes its steps.


### Minimal hosted-runner diagnostic — 2026-11-05 09:10 UTC

To separate workflow contents from runner allocation, a temporary-safe diagnostic workflow was added at `.github/workflows/runner-allocation-diagnostic.yml`. It has a single `ubuntu-latest` job, `contents: read` permission, no checkout, no external actions, no secrets, no deployment, and only prints runner ID/name/OS plus `uname` and UTC date.

The branch push successfully triggered:
- [Runner Allocation Diagnostic run 42000147699](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42000147699)
- [Snapshot Regression Tests run 42000148149](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42000148149)
- [Historical Secret Scan run 42000147708](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42000147708)

The minimal diagnostic job itself failed in approximately one second with `runner_id=0`, blank `runner_name`, `runner_group_id=0`, blank `runner_group_name` and an empty `steps` array. Its logs endpoint returned no payload. GitHub's failed-job rerun succeeded in submitting attempt 2, but that attempt also failed in roughly two seconds with `runner_id=0`, blank runner name and no steps (job `127153275793`). The snapshot regression run on the same commit again had 17/17 jobs fail before runner assignment; the full-history secret scan did the same.

This is a direct isolation test: the symptom reproduces without checkout, action pinning, Python, Node, dependencies, custom runner labels or secrets. Workflow YAML parsing and event triggering worked well enough to create a job. It does not identify whether the underlying cause is an account/usage restriction or a GitHub hosted-runner provisioning issue.

### External corroboration and account checks

GitHub Community reports show the same public metadata signature in unrelated private repositories:
- [Discussion #210692 — ubuntu-latest job fails before runner starts, 20 Oct 2026](https://github.com/orgs/community/discussions/210692): a minimal ubuntu-latest job failed with runner_id 0, blank runner name and no steps; the report also reproduced across two repositories.
- [Discussion #211408 — runner_id 0 and BlobNotFound, 27 Oct 2026](https://github.com/orgs/community/discussions/211408): fresh private-repository runs failed before steps; reruns reproduced the same result.
- [Discussion #205948 — fresh runner_id 0 failures, 27 Aug 2026](https://github.com/orgs/community/discussions/205948): similar reports after a previously resolved Actions incident.

These are community reports, not proof that the same underlying incident affects this account. GitHub Status history shows no Nov 5 Actions incident; Nov 4 incidents were marked resolved. Therefore a broad active Actions outage is not confirmed.

The repository metadata API confirms the owner has repository admin permission, but the connected GitHub tool cannot read account/repository Actions enablement, hosted-runner usage budgets, billing restrictions or GitHub-controlled account suspension state. Before treating the runner failure as a code blocker, the repository owner should inspect:
1. Repository `Settings → Actions → General`: confirm Actions are enabled, the allowed-actions policy permits required pinned actions, and there is no repository-level restriction.
2. Personal account `Settings → Billing and licensing → Usage` (menu labels may vary): review Actions included usage, additional spending/budget caps, payment status and any account-level suspension notice.
3. If Actions says it is disabled for the account/repository by GitHub, follow GitHub's notice and contact GitHub Support; GitHub documents that some platform-controlled disabled states cannot be restored by changing repository settings. See [Managing GitHub Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository) and [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

Keep the diagnostic workflow: it is credential-free and can be manually dispatched after runner access is restored. Do not rerun the 17-job regression matrix repeatedly until a minimal diagnostic run allocates a nonzero runner and reaches its first step.


## Latest RiverShift API code/test commit validation — 2026-11-05

RiverShift-only API configuration validation was added to reject malformed GitHub repository owner/name, unsafe workflow filenames/path traversal and invalid refs. New tests cover four unsafe target variants and accept a slash-delimited migration branch. Four additional API status-polling tests cover missing signed callback, completed GitHub failure, dispatch timeout and terminal signed-success preservation. The latest code-bearing test commit is 70c780d2bee11dc2a821040b4d10209ac519affa; subsequent commits only update migration documentation.

Latest Actions on that code head:
- Runner Allocation Diagnostic 42002234943 completed failure after about 43 seconds, still runner_id=0, blank runner name, and zero steps.
- Snapshot Regression Tests 42002235091: 17 jobs, with a subset failing before runner assignment while the rest remained queued at the latest sample; all observed jobs had zero steps.
- Migration Metadata Validation 42002235044 and Historical Secret Scan 42002234981 completed failure before any runner step.

The newly added API/config tests therefore remain unexecuted. Do not mark CI green based on queued jobs.
