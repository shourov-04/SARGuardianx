# Dynamic/backend source path collision report

**Compared source refs:**  
- Dynamic `dd64b7adc90594f1d7f316b352e39fbac2013cb6`  
- Backend `97d849454918b1425ac41bb70e7a32d11cfd3833`

## Summary

| Measure | Count |
|---|---:|
| Dynamic tracked files | 185 |
| Backend tracked files | 244 |
| Paths present in both repositories | 24 |
| Same path and identical Git blob | 5 |
| Same path but different Git blob | 19 |

This is direct evidence that copying both repositories into one root with an ordinary directory overlay would silently overwrite source files. The existing snapshots are correctly isolated under separate prefixes.

## Exact identical blobs (5)

These paths are byte-identical at the compared refs:

| Shared path | Git blob SHA | Decision |
|---|---|---|
| `tools/measure_target_from_raster.py` | `9937cf7e263da36ad3741f77321e4f9e6b866588` | Candidate for a shared utility only after import/call-site tests |
| `tools/sarguardian_hdf5_archive.py` | `d056aa86c3341eed92a6f39b515d418d610efc00` | Candidate for shared archive package after retention contract review |
| `tools/tests/test_measure_target_from_raster.py` | `0826b61915d56c578a7ae3b09c383c239db40d4a` | Keep one canonical test when the module destination is chosen |
| `tools/validate_product_aoi.py` | `97b9be365df3a5876f8a2499a955f340782a3f15` | Candidate for shared utility after consumer tracing |
| `tools/verify_reader_equivalence.py` | `56fc6b98b4b3cdb83225ae6239cfbf008c17d26a` | Candidate for shared utility after reader compatibility tests |

Identical Git blobs prove content equality, not identical runtime usage or deployment ownership.

## Divergent same-path files (19)

| Shared path | Dynamic blob SHA | Backend blob SHA | Resolution constraint |
|---|---|---|---|
| `.github/workflows/sarguardian-aoi-product-worker.yml` | `656d105a9b1543f7fac20db199babb81cba844a7` | `15dc032db32a568dfb6acc5777b54332364d084b` | Compare reusable workflow inputs, source checkout, artifact and callback contracts; choose one canonical workflow only after caller mapping |
| `.github/workflows/sarguardian-aoi-wkt-dashboard.yml` | `ed74c64295de18dd6310a43f323baca4d6923f34` | `eabdc43e0e0b05fccd532647bbddde2216694e64` | Not interchangeable by name; trace which repo owns dispatch, status callback, retry, and dashboard build |
| `README.md` | `0185c09c5da6496563fbab1a2621e70f9d9145f6` | `9507cf88389ce2cb4a6807d992caf8cc8e068376` | Replace with a single monorepo README; retain source docs in snapshot |
| `docs/SCIENTIFIC_REGRESSION_GUARD.md` | `0caa35edbe1ea2700fcf2da668a77a6411419f27` | `c5e90ff397c45592750dd940356236f834328b25` | Reconcile the two guard documents; do not discard requirements from either |
| `tools/aggregate_aoi_run.py` | `547dc2345b365f9c7ebfcfeccf326f3b5f739f97` | `c6606dc5d2f5ef81f5422aba2636a4eb6b28f17b` | Different dashboard/orchestration implementations; inspect caller graph and tests before choosing the Dynamic-facing entry point |
| `tools/discover_aoi_products.py` | `4a037ba3b80c47972fc531d90ebf32c6332f709e` | `dafe7b6cd6eb62c4c77d033044751c670577d583` | Compare catalogue pagination, product identity, retries, and callers |
| `tools/download_nisar_product.py` | `d54a06f33faa584c8c4503722d475c52ebcf757e` | `307d84c874d480b76a77070abae9390a7b6546b6` | Compare authentication, download resume, verification, and caller expectations |
| `tools/drive_resumable_upload.py` | `e17e750f944e1365861bcceecb55452fb13a00fe` | `84a6b32c39d456644fe6af1a6d803b26de12b27b` | Compare resumable upload receipt, folder resolution, and retry semantics |
| `tools/plan_aoi_retries.py` | `ed26719e9c9791df6f1f50946004f9d47dab2392` | `3d607faa81fac17970adbe627332afbbd674d2f7` | Do not merge retry logic until tests prove identical failed-only and batch contracts |
| `tools/prepare_aoi_drive_folders.py` | `391effb299fa7c844123303b0e0cafb935205c` | `5cc8c37514bfd38b330fffa47a27f7171f8bea0b` | Resolve Drive folder semantics against the established parent-folder variable and upload callers |
| `tools/requirements-retention.txt` | `d8232c44c58a6f4d5ee3fa9daeb73a4ebde3ed80` | `f86daa08bb8ea461b9746260df8e025b83f553bf` | Reconcile dependency constraints, Python versions, and worker environment lock |
| `tools/run_export_science_diagnostics.py` | `f2ec9da4284c66409e366663f58f5a49dfb89ae7` | `51b8720b8038a761a629fe7b7a9c80ee9b388ffc` | Preserve science input/output schemas and withholding semantics |
| `tools/tests/test_aggregate_aoi_run.py` | `4558818fdbc7c897ba1b0cb050a11e21a9bec3d0` | `5701d8806101ac664760544631879fb1f45f338f` | Keep both test histories until canonical module and fixture parity are proven |
| `tools/tests/test_discover_aoi_products.py` | `640abb2f3a45242a29f849e38a9f7add41f0ec4a` | `188358c3bae815ec5b9b88a22e2d1c938576a38d` | Keep broader tests; differences may capture different discovery contracts |
| `tools/tests/test_plan_aoi_retries.py` | `54d7f9c241d210a4de913836b95b47b167cd7dd9` | `6ee6a74ed9344f1df3dad91954444bb8c3042c6f` | Preserve retry edge cases from both |
| `tools/tests/test_run_export_science_diagnostics.py` | `43cab196eecb0893afc28953631a0340cb4aaea6` | `d735e798b92948cbf73e16ae70794857a651637f` | Preserve both science diagnostic contract suites |
| `tools/tests/test_validate_aoi_derived_outputs.py` | `a57cba1f211e66eb1fc43fa0161320d063e3582b` | `2180022367497ab43ec811955c9b2f4707849b77` | Preserve the stricter output/manifest validation cases from both |
| `tools/validate_aoi_derived_outputs.py` | `f201de1428cba9d153f0387d6ae225d9d5aea255` | `974e75e6e79978a9e18d1ddec0a1d3bf734d2953` | Compare completeness rules, identity checks, and failure handling before consolidating |
| `tools/write_no_valid_pixel_stats.py` | `6caff2ead5f44f265f23c65da69ea6fa538776d7` | `9af30123da000d577a500005363f2ba7632bd4b0` | Compare denominator, missing-data, and output schema semantics |

## Promotion decision

1. Keep both complete source snapshots immutable.
2. Move the Dynamic API's own AOI-facing adapters with the API, not by replacing them with backend command-line tools.
3. Keep backend processing tools in their engine/worker package until callers and tests are mapped.
4. For the five identical helpers, share only after path/import and worker environment tests pass.
5. For the 19 divergent paths, preserve both variants in versioned/source namespaces until a reviewed canonicalisation decision has test evidence.
6. Do not copy either source `.github/workflows/` over the other. The two named AOI workflow duplicates have different blob SHAs and caller graphs.

No source files have been overwritten in the monorepo; all remain isolated in their original snapshot prefixes.
