# SARGuardian Monorepo

A controlled consolidation of SARGuardian's web application, active API, independent processing engines, NISAR science source, and GitHub Actions workflows.

> **Migration status: source import and first code promotion are complete on an isolated migration branch.** The original repositories remain authoritative and unchanged. No production deployment, secret transfer, live processing, or workflow cutover has been performed.

## Source systems

| Source | Responsibility | Audited baseline |
|---|---|---|
| [SARGuardian_Dynamic](https://github.com/moshiour0/SARGuardian_Dynamic) | React/Vite web app, active Firebase-authenticated FastAPI API, Supabase job persistence, deployment adapters | `dd64b7adc90594f1d7f316b352e39fbac2013cb6` |
| [SARGuardian-backend](https://github.com/moshiour0/SARGuardian-backend) | Scientific processing workers, RiverShift GCOV engine, Find Displacements diagnostics, reusable Actions workflows | `97d849454918b1425ac41bb70e7a32d11cfd3833` |
| [SARGuardian](https://github.com/moshiour0/SARGuardian) | NISAR science source used by pinned processing workflows | Current main at audit: `9fcb543ef28a7f6fe70a379aed9cfe3e43e277ec` |

The exact source trees have been imported under `migration/source-snapshots/` with their source commit histories preserved. See the [source-pin manifest](docs/migration/source-pins.json) and [source import report](docs/migration/source-import-report.md).

## Engine boundaries

- **Find Displacements:** target-free AOI-wide candidate discovery. GOFF offsets and GUNW LOS diagnostics remain separate measurement families.
- **Known Place Analysis:** a current API-connected generic two-polygon workflow pinned to Backend's active reusable workflow/source revision 0e0611c12913044787ee84a39fa60a81d30ae516; the original feat/know-place-analysis branch was not merged into Backend main and PR #85 remains Draft/Open. Its PR #85 lineage is preserved separately. Author-exact P05023 replay remains a distinct manual-consent-gated path.
- **River Shift:** an independent NISAR GCOV engine with ASF acquisition discovery, processing, overlap diagnostics, transects, and external validation.
- **Glacier Movement:** currently a product/category route into the shared Find Displacements engine, not a separately proven processing engine.

## Active runtime scope (evidence-based)

The migration preserves all **82 historical source workflow instances** without activating them indiscriminately. The current API application graph contains two primary processing paths—**Find Displacements** and the generic two-polygon **Known Place Analysis** workflow—and two separately gated paths: **RiverShift GCOV** and author-exact **P05023** reproduction.

- **Find Displacements:** target-free AOI discovery and the separate GOFF/GUNW diagnostics remain isolated. Backend run [42097077601](https://github.com/moshiour0/SARGuardian-backend/actions/runs/42097077601) completed its processing chain, recovered one failed GUNW product through a failed-only retry, assembled the dashboard and reported a terminal callback. A Monorepo live pilot is still pending.
- **Known Place Analysis:** the generic dispatcher uses Backend main's active reusable workflow/source pin `0e0611c12913044787ee84a39fa60a81d30ae516`; successful Backend runs [41533701551](https://github.com/moshiour0/SARGuardian-backend/actions/runs/41533701551) and [41533582770](https://github.com/moshiour0/SARGuardian-backend/actions/runs/41533582770) retained result artifacts. Its Monorepo dispatcher and engine are imported and tested, but the Monorepo dispatch gate remains off. The separate PR #85 research lineage is preserved; it was not merged into Backend main.
- **RiverShift:** it remains an independent NISAR GCOV engine, not part of Landslide/Find Displacements. The prior run [42089984247](https://github.com/moshiour0/SARGuardian-backend/actions/runs/42089984247) matched 14/14 catalogue granules but stopped safely at `EVENT_WINDOW_NOT_BRACKETED`; a positive-case Monorepo pilot is still required.
- **Author-exact P05023:** kept separate and manual-consent-gated. The prior run [41423614257](https://github.com/moshiour0/SARGuardian-backend/actions/runs/41423614257) did not pass source-manifest completeness, so it is not a complete successful reproduction.
- **Glacier Movement:** currently a product/category route into the shared Find Displacements engine, not a separately promoted processing engine.

The [active runtime scope and run evidence](docs/migration/active-runtime-scope-2026-11-06.md) records the source/workflow pins and gates. Historic diagnostics, alternate forks and unused worker variants remain preserved for provenance, not automatically activated.

## Migration principles

1. Preserve the original repositories and immutable source SHAs until the monorepo passes acceptance.
2. Import source snapshots with provenance before refactoring or relocating code.
3. Keep the active Dynamic API distinct from the older backend `app/` service until a usage and contract review proves consolidation safe.
4. Preserve all workflow triggers, permissions, artifacts, callbacks, retries, and retention behaviour.
5. Never copy secret values into Git. Build an explicit secret-name mapping and configure target secrets separately.
6. Validate in an isolated migration branch and Preview environment before any production cutover.
7. No engine algorithm or scientific status semantics may change as a side effect of repository consolidation.

## Current target layout

```text
apps/
  web/                 # React/Vite frontend, promoted and tested
  api/                 # active Firebase/Supabase API, promoted and tested
  tools/               # Dynamic API compatibility helpers
engines/
  find-displacements/  # AOI-wide candidate discovery and diagnostics
  known-place/         # PR #85 research implementation
  river-shift/         # independent GCOV engine
science/
  nisar-core/          # current NISAR science source
migration/
  source-snapshots/    # immutable source trees and historical pins
.github/workflows/     # only reviewed central workflows become active here
docs/
  architecture/
  migration/
  scientific-validation/
```

Source snapshots remain immutable, and promoted paths are exact copies. Original source paths remain available until deployment, workflow parity, and security/cutover checks complete. Nested `.github/workflows/` directories beneath `apps/`, `engines/`, and `migration/source-snapshots/` are inactive compatibility/archive paths; GitHub Actions only executes workflow files from the repository-root `.github/workflows/`.

## Current verified migration state — 2026-11-06

Verified source/workflow head: `9bd6858b7ea4e2500a531634e4a96f2d2288bf09`. The later branch commits through `9312ec5` are documentation-only.

- [Snapshot Regression Tests 42187445481](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445481): **19/19 jobs passed**.
- [Backend Source Snapshot Regression 42187445413](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445413): **2/2 jobs passed**, including the Known Place PR #85 source suite.
- Migration Metadata [42187445630](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445630), Historical Secret Scan [42187445962](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445962), Runner Diagnostic [42187445578](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445578), Retention Archive [42187445646](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445646), Dashboard Assets [42187445703](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187445703), and AOI Dual-Pin Validation [42187446475](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/42187446475): all successful.

### Vercel Preview

The Web project (`apps/web`) and API project (`apps/api`) are separate Hobby/Free-plan projects linked to this repository. Latest inspected deployments are READY and Preview-only (`target=null`), with SSO protection and no Production aliases. The code-bearing commit deployed is `c246f3b16a5b7320ab97250f202847b9f4d5c8c2`; the diff from that commit to the current code head only changes docs/security validators, not Web/API runtime files. Web stable Preview root returned HTTP 200, and API stable Preview `/health` returned HTTP 200.

Preview is not functionally complete: Web currently has only `VITE_SARGUARDIAN_API_URL`. It still needs `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_STORAGE_BUCKET`, `VITE_FIREBASE_MESSAGING_SENDER_ID`, `VITE_FIREBASE_APP_ID`, optional `VITE_FIREBASE_MEASUREMENT_ID`, and `VITE_GOOGLE_MAPS_API_KEY`. These are browser-visible client configuration, not server secrets. Scope them to Preview/this branch and restrict the Maps key's HTTP referrers to the Monorepo Preview domain.

API Preview has the Tokyo Supabase URL, CORS, callback bases and all four workflow destination names/refs. It lacks `SUPABASE_SERVICE_ROLE_KEY` (new key for the Monorepo project), `FIREBASE_SERVICE_ACCOUNT_JSON`, `GITHUB_ACTIONS_TOKEN`, `DISPLACEMENT_CALLBACK_SECRET`, `RIVERSHIFT_CALLBACK_SECRET`, and Google Drive result-read OAuth credentials. No Production credential was copied; the Vercel connector did not reveal the old project's sensitive values.

### Supabase Preview database

The Free Tokyo Supabase project `SARGuardian-Monorepo` (`qbmhpdprvxssqinnommz`) is `ACTIVE_HEALTHY`, with four empty RLS-enabled app tables and zero Security Advisor lints. The nine local migration filenames match the nine live remote version/name records in `migration/supabase-history-alignment.json`; CI verifies every path, version, name and Git blob SHA. The two Monorepo forward migrations are accounted for, including the applied default-privilege hardening migration and a successful transactional privilege probe. No `db push`, history repair, replay or reset was run. Dynamic Production Supabase remains a separate project and lineage.

## Current readiness

- [x] Source snapshots preserve 1,685 tracked paths and original commit ancestry.
- [x] Dynamic Web/API, Find Displacements, current generic Known Place pin, RiverShift GCOV and NISAR science paths are promoted separately.
- [x] Active product scope is limited to 5 primary workflows (Find Displacements + generic Known Place), 3 gated feature workflows (RiverShift + author-exact P05023), and 7 migration CI workflows; all 82 historical source variants remain preserved.
- [x] Current source/workflow CI passed: Snapshot Regression 19/19, Backend Source Snapshot Regression 2/2, metadata, secret scan, runner, retention, dashboard asset and AOI dual-pin checks.
- [x] Web/API Preview builds are READY and Preview-only; root and health probes returned HTTP 200. Existing Production aliases were not changed.
- [x] Supabase Tokyo project is active with four RLS-enabled tables; all nine local migration versions/names and blob hashes match the connected remote inventory/manifest.
- [ ] Configure Web Preview Firebase client config and Google Maps key, with HTTP-referrer restriction.
- [ ] Configure API Preview's new Supabase service key, Firebase Admin, GitHub dispatch token, callback HMAC values and Drive result-read OAuth.
- [ ] Configure Monorepo Actions Secrets: Earthdata, Google Drive OAuth/refresh token/parent folder ID, and matching callback HMAC secrets.
- [ ] Complete authenticated login, owner-scoped Supabase persistence/readback, mock dispatch, callback/status correlation, artifact access, and controlled Find Displacements + Known Place pilots.
- [ ] Keep RiverShift gated until an eligible event date produces a successful positive-case GCOV pilot; keep author-exact P05023 separately consent-gated until source manifest, science, Drive and cleanup all pass.
- [ ] Review Web dependency advisories/bundle size, licensing, science validity and rollback. Merge PR #1 then PR #2 only after acceptance and explicit owner approval.

**Release boundary:** PR #1 and PR #2 remain Draft/Open and unmerged. Monorepo `main` is still the bootstrap state. Existing Dynamic + Backend Production, Production Vercel aliases, callbacks, dispatch targets and Supabase remain authoritative and unchanged.
