# SARGuardian — NASA Space Apps 2026 score-sheet evidence matrix

**Challenge:** Dancing with the SARs  
**Category:** Earth Science  
**Product:** SARGuardian — Earth in Sight  
**Source score sheet:** Project Library file "Score Sheet.md" (local judges' rubric; maximum 118 before the +5% women-participation bonus).

This is the submission evidence register, not a promise of marks. Every claim below must be supported by the linked implementation, source record or test/run evidence. A software test proves a software contract; it does not by itself prove geophysical accuracy.

## Scoring criteria and evidence

| Criterion | Points | Product evidence to show | Evidence source | Public wording guard |
|---|---:|---|---|---|
| Impact | 1–20 | Four entry workflows spanning slope displacement, glacier-terrain displacement screening, focused known-place research and river change; demonstrate a real AOI/date workflow and one traceable regional case. | apps/web/src/data/engineData.ts; RiverShift Judge Brief and Run #36 evidence; source-linked case study documents. | Say the platform can screen different surface-change questions where compatible NISAR products exist. Do not imply equal coverage, accuracy or validated impact for every region. |
| Creativity | 1–20 | Target-free AOI discovery; two-polygon Measurement/Reference Known Place design; separate GCOV water/change screening; map search, observed-date playback and independent context overlays. | Promoted apps/web and engines; Known Place PR #85 source pin; RiverShift Judge Guide. | Describe what each workflow actually does. Do not call a UI category a separate scientific engine unless it has its own processing path. |
| Validity | 1–20 | Exact source commits, product provenance, checksums, pixel-support gates, compatibility checks, overlap QA, regression tests, reproducible run reports and explicit independent-reference states. | docs/migration/source-pins.json; docs/scientific-validation/; engine test suites; RiverShift Run #36 replay evidence. | Distinguish code tests, internal QA, reproducibility and independent physical validation. Never turn NO_MATCH_NO_SCORE into a zero score or a passing accuracy claim. |
| Relevance | 1–20 | NISAR L-band products are measurement sources: GUNW phase, GOFF offsets and GCOV covariance/water screening are handled as distinct measurement families. | science/nisar-core; engines/find-displacements; engines/known-place; engines/river-shift. | Identify the exact product and measured quantity for each workflow. Do not imply the basemap or ancillary layer is a NISAR measurement. |
| Presentation | 1–20 | A single guided application, global AOI map, clear workflow entry points, source dates, readable change layers, playback on observed dates and judge-facing evidence guide. | apps/web; docs/submission; RiverShift Judge Brief/Guide. | Tell a concise story: Earth changes → NISAR observes → SARGuardian screens → provenance and uncertainty support interpretation. |
| Teamwork | 1–5 | Actual team roles, contributions, collaboration evidence and team-member attribution. | Official team/project page and approved contributor records. | Do not invent roles, names, contributions or participation. Confirm team details with the team before submission. |
| User experience | 1–5 | First-use flow: select a workflow, search/draw AOI, choose dates, discover eligible products, process/review results, inspect evidence. Mobile and desktop usability. | apps/web; browser/keyboard/mobile QA records. | Do not award ourselves “anyone can use it” until independent first-time-user tests are recorded. |
| NASA data usage | 1–5 | NISAR products are central inputs; ASF DAAC/NASA CMR provide discovery/access; other sources are explicitly labelled as context or independent reference. | Product manifests, workflow source, source registry, RiverShift guide. | Name NASA–ISRO NISAR correctly and distinguish NASA/ASF product inputs from Sentinel-1, optical, OSM, gauge and basemap context. |
| Challenge category identified | 0 or 1 | Earth Science and Dancing with the SARs are named on the submission page. | Project page. | Use the official challenge and category names. |
| Repository access | 0 or 1 | Public GitHub source link opens without authentication and contains license, setup, data/provenance and reproducible instructions. | Monorepo repository visibility and README. | Current Monorepo is private. Do not claim public/open repository access until the final secret/data/license audit is complete and repository visibility is deliberately changed. |
| Project page complete | 0 or 1 | Official NASA Space Apps project page is completed, submitted and includes team, challenge, summary, links, sources and media. | Official project page. | Do not mark complete until the official page reports successful submission. |

## Required scientific distinctions

### Landslide / Find Displacements
- Find Displacements is target-free AOI-wide candidate discovery; it does not require the user to name a target point first.
- GOFF offset diagnostics and GUNW LOS phase diagnostics remain separate measurement families.
- Pairwise LOS is not cumulative or three-dimensional displacement.
- Structural/provenance PASS is not independent geophysical validation.
- An anomaly is a candidate for investigation, not automatically a landslide.

### Glacier Movement / collapse context
- The current promoted category is named **Glacier Movement** and routes through the shared AOI-wide displacement workflow.
- It is not a separate glacier-collapse physics model or an automatic avalanche detector.
- Use glacier-collapse/ice–rock-avalanche language only for a specific study where the event context, acquisition geometry, measured quantity and supporting evidence are documented. Keep the UI wording at Glacier Movement unless a separately validated collapse workflow is promoted.

### Known Place Analysis
- Generic two-polygon analysis and author-exact research reproduction are separate paths.
- The measurement polygon and reference polygon have distinct roles; the reference polygon is not automatically proven stable.
- Preserve the exact author-selected NISAR product revision and acquisition configuration for paper reproduction. Do not substitute a different CRID/product revision.
- A benchmark reproduction is not automatically a universal calibration or independent ground truth.

### River Shift
- NISAR L-band GCOV is the primary measurement input; the selected exact products, acquisition dates, compatibility and valid raster support determine eligibility.
- The map shows screening candidates, not automatically field-confirmed erosion, deposition, damage, sediment volume or flood causality.
- Run #36's independent OPERA DSWx-S1 reference review returned **NO_MATCH_NO_SCORE / PROVISIONAL** when no eligible temporally matched reference was found.
- OPERA DSWx-S1 is a cross-sensor SAR-derived reference, not field truth. RTC-S1 backscatter inventory is not a water mask and cannot generate WTR agreement scores.
- Playback is across actual acquisition dates, not interpolation or forecast.

## AI-judge discoverability requirements

The final public root README should make the following obvious without requiring a judge to infer it from code:

1. Official challenge and category.
2. What SARGuardian does, and who can use it.
3. Four workflow entry points with accurate scope descriptions.
4. Which NISAR product powers each workflow and what quantity it measures.
5. A short “try it” path for each workflow.
6. At least one real, reproducible case with exact acquisition dates, source product IDs and downloadable evidence.
7. Separate software-test, internal-QA and independent-validation statements.
8. Known limitations beside the specific result they qualify.
9. Installation, environment setup, test commands, license, data terms and public source references.
10. A demo video/screenshots and a concise technical architecture diagram.

A judge should be able to locate the evidence by searching for stable headings such as “Challenge Fit”, “NISAR Data”, “How to Reproduce”, “Validation”, “Known Limitations”, “Workflow Evidence” and “Sources”.

## Submission blockers — do not misreport as complete

- Monorepo visibility is currently **private**; repository-access scoring requires public access or another openly accessible source link.
- Public release requires full secret-history review, removal/retention review of private data/artifacts, license review and confirmation that no credential or personal information is committed.
- The official project page's final submission state and all team member details must be confirmed by the team.
- Teamwork and women-participation bonus cannot be inferred from code or repository metadata.
- Mobile and first-time-user UX must be demonstrated with recorded human testing, not inferred from a successful build.
- A full independent geophysical validation claim is prohibited unless its own source, date, spatial support, labeling protocol and metrics pass the stated gates.

## Release language

Use capability-first, evidence-bounded language. Prefer:

> “SARGuardian brings several NISAR-powered surface-change workflows into one interactive platform. Users can explore eligible AOIs, review observations and candidate changes, and trace each result to its source products and quality checks.”

Avoid unsupported phrases such as “AI predicts disasters”, “detects every landslide worldwide”, “field-verified damage”, “centimetre-accurate glacier collapse alerts” or “fully validated global accuracy”.
