#!/usr/bin/env python3
"""Enforce the evidence-based SARGuardian active runtime call graph and source pins."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = ROOT / "migration" / "active-runtime-scope.json"
KNOWN_PLACE_PIN_PATH = ROOT / "migration" / "active-runtime-pins" / "known-place-generic-0e061.json"


def fail(message: str) -> None:
    print(f"ACTIVE_RUNTIME_SCOPE_ERROR={message}", file=sys.stderr)
    raise SystemExit(1)


def require_file(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"required runtime file is missing: {relative}")
    return path.read_text(encoding="utf-8")


def require_contains(relative: str, *needles: str) -> str:
    content = require_file(relative)
    for needle in needles:
        if needle not in content:
            fail(f"{relative} is missing required contract marker: {needle}")
    return content


def git_blob_sha(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\x00"
    return hashlib.sha1(header + data).hexdigest()


def validate_known_place_active_pin() -> None:
    try:
        manifest = json.loads(KNOWN_PLACE_PIN_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read active Known Place source-pin manifest: {exc}")
    if manifest.get("source_repository") != "moshiour0/SARGuardian-backend":
        fail("unexpected Known Place source repository")
    if manifest.get("source_workflow_commit") != "0e0611c12913044787ee84a39fa60a81d30ae516":
        fail("generic Known Place source pin must remain the exact active Backend runtime revision")
    if manifest.get("source_dispatcher_blob") != "90b254a68dae6c8449edeacf4ea205743ee89380":
        fail("generic Known Place Backend main dispatcher blob pin changed")
    if manifest.get("source_reusable_workflow_blob") != "844cdeefd2d78c74c623a4d910f9b6091789d79b":
        fail("generic Known Place reusable workflow blob pin changed")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != 10:
        fail("expected ten exact current-runtime Known Place overlays")
    seen: set[str] = set()
    for row in files:
        source = row.get("source_path")
        destination = row.get("destination_path")
        source_sha = row.get("source_blob_sha")
        if not isinstance(source, str) or not source or not isinstance(destination, str) or not destination.startswith("engines/known-place/") or destination in seen or not isinstance(source_sha, str) or len(source_sha) != 40:
            fail(f"invalid Known Place active-pin row: {row!r}")
        seen.add(destination)
        target = ROOT / destination
        if not target.is_file():
            fail(f"active Known Place overlay file is missing: {destination}")
        actual = git_blob_sha(target.read_bytes())
        if actual != source_sha:
            fail(f"active Known Place source blob mismatch: {destination}; expected={source_sha}; actual={actual}")
    expected = {
        "engines/known-place/tools/know_place/aoi_request.py": "8fcfdf635994ceb6093160931f21ae6cf0f986de",
        "engines/known-place/tools/know_place/aoi_runner.py": "9364b94d6629c67e44f007a0e2634824aa7e1f9f",
        "engines/known-place/tools/know_place/geometry.py": "25292440fd94426882a8c51b00b186b162de429a",
        "engines/known-place/tools/know_place/series.py": "f1b67c9255706b8e10ad4e2e280e80640490b405",
        "engines/known-place/tools/know_place/upload_bundle_to_drive.py": "ef721ee9e1d1b388927866054883440f95e1f2f6",
        "engines/known-place/tools/tests/test_know_place_aoi_runner.py": "1a48c7258d97ec4b98dd81d67cc425a73b02f8d8",
        "engines/known-place/tools/tests/test_know_place_geometry.py": "17d7b56cdb47af6d774c58d8abc9b33903be7144",
        "engines/known-place/tools/tests/test_know_place_series.py": "22acef6e41822e4b7f23d2902f467015e4a69099",
        "engines/known-place/tools/tests/test_know_place_upload_bundle.py": "88bc0c613b05023658555f605104a2570266d7ba",
        "engines/known-place/app/storage/drive_client.py": "64aef9f7e3b6c4eee63d2ad9e21565be2ebed2a2",
    }
    observed = {row["destination_path"]: row["source_blob_sha"] for row in files}
    if observed != expected:
        fail("Known Place active source-pin manifest differs from the reviewed ten-file overlay")
    print("KNOWN_PLACE_ACTIVE_PIN_BLOB_PARITY=PASS source=0e0611c files=10")


def main() -> int:
    scope = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))
    if scope.get("schema_version") != 1:
        fail("unsupported active runtime scope schema")
    paths = scope.get("runtime_paths")
    if not isinstance(paths, list) or len(paths) != 4:
        fail("expected four separately classified API feature paths")

    expected_primary = {
        ".github/workflows/sarguardian-aoi-wkt-dashboard.yml",
        ".github/workflows/sarguardian-aoi-dashboard-engine.yml",
        ".github/workflows/sarguardian-aoi-product-worker.yml",
        ".github/workflows/know-place-aoi-dispatcher.yml",
        ".github/workflows/know-place-aoi-analysis.yml",
    }
    expected_gated = {
        ".github/workflows/river-shift-gcov-process.yml",
        ".github/workflows/know-place-paper-reproduction-dispatcher.yml",
        ".github/workflows/know-place-author-exact-replay.yml",
    }
    primary = set(scope.get("runtime_workflow_allowlist", []))
    gated = set(scope.get("gated_feature_workflow_allowlist", []))
    preserved = set(scope.get("preserved_disabled_feature_workflow_allowlist", []))
    if primary != expected_primary:
        fail("primary runtime allowlist must contain Find Displacements and current generic Known Place call graphs")
    if gated != expected_gated:
        fail("gated features must contain RiverShift and the separate author-exact P05023 call graph")
    if preserved:
        fail("connected API workflows must not be silently placed in a preserved/unused bucket")
    all_feature = primary | gated
    if len(primary) + len(gated) != len(all_feature):
        fail("primary and gated workflow allowlists must be disjoint")

    expected_ci = {
        ".github/workflows/snapshot-regression-tests.yml",
        ".github/workflows/backend-source-regression-tests.yml",
        ".github/workflows/migration-metadata.yml",
        ".github/workflows/historical-secret-scan.yml",
        ".github/workflows/retention-archive-tests.yml",
        ".github/workflows/dashboard-assets-test.yml",
        ".github/workflows/sarguardian-aoi-code-validation.yml",
    }
    ci = set(scope.get("migration_ci_allowlist", []))
    if ci != expected_ci or ci & all_feature:
        fail("migration CI allowlist is invalid or overlaps product workflows")
    for path in all_feature | ci:
        require_file(path)

    require_contains("apps/api/app/main.py",
        '@app.post("/api/displacement-jobs"', "include_router(river_shift_jobs_router)",
        '@app.post("/api/known-place-analysis"', '@app.post("/api/known-place-paper-reproduction"')
    require_file("apps/web/package.json")
    require_file("apps/api/app/persistence.py")

    require_contains(".github/workflows/sarguardian-aoi-wkt-dashboard.yml",
        "workflow_dispatch:", "MONOREPO_DISPLACEMENT_ACTIONS_ENABLED",
        "uses: ./.github/workflows/sarguardian-aoi-dashboard-engine.yml")
    require_contains(".github/workflows/sarguardian-aoi-dashboard-engine.yml",
        "uses: ./.github/workflows/sarguardian-aoi-product-worker.yml", "max-parallel: 15",
        "migration/source-snapshots/nisar-pins/006d4cd")
    require_contains(".github/workflows/sarguardian-aoi-product-worker.yml",
        "006d4cd1485cf80e509eaf8717c12e9c6390ac09", "GOOGLE_DRIVE_PARENT_FOLDER_ID")

    require_contains("apps/api/app/config.py",
        '_flag(values, "DISPLACEMENT_ACTIONS_ENABLED", False)',
        "KNOWN_PLACE_GITHUB_ACTIONS_REPOSITORY", "KNOWN_PLACE_GITHUB_ACTIONS_WORKFLOW",
        "KNOWN_PLACE_GITHUB_ACTIONS_REF")
    require_contains("apps/api/app/known_place.py",
        "known_place_github_actions_repository", "dispatch_known_place_analysis",
        "scope_aoi_wkt", "reference_wkt")
    require_contains(".github/workflows/know-place-aoi-dispatcher.yml",
        "workflow_dispatch:", "MONOREPO_KNOWN_PLACE_ENABLED",
        "uses: ./.github/workflows/know-place-aoi-analysis.yml")
    require_contains(".github/workflows/know-place-aoi-analysis.yml",
        "KNOWN_PLACE_BACKEND_RUNTIME_PIN=0e0611c12913044787ee84a39fa60a81d30ae516",
        "9364b94d6629c67e44f007a0e2634824aa7e1f9f")
    validate_known_place_active_pin()

    require_contains(".github/workflows/river-shift-gcov-process.yml",
        "MONOREPO_RIVERSHIFT_PROCESSING_ENABLED", "max-parallel: 15", "retry_status:",
        "event_date:", "analysis_mode:")
    require_contains("engines/river-shift/tools/river_shift/batched_gcov_job.py",
        "GOOGLE_DRIVE_PARENT_FOLDER_ID")

    require_contains(".github/workflows/know-place-paper-reproduction-dispatcher.yml",
        "uses: ./.github/workflows/know-place-author-exact-replay.yml",
        "b825df798ea4cb9874aa10dd01174d2a8ef73cba", "[run-know-place]")
    require_contains(".github/workflows/know-place-author-exact-replay.yml",
        "MONOREPO_KNOWN_PLACE_PAPER_REPRODUCTION_ENABLED",
        "b825df798ea4cb9874aa10dd01174d2a8ef73cba", "[run-know-place]")

    config = require_contains("apps/api/app/config.py",
        '_flag(values, "DISPLACEMENT_ACTIONS_ENABLED", False)',
        '_flag(values, "RIVERSHIFT_ACTIONS_ENABLED", False)')
    if "DISPLACEMENT_ACTIONS_ENABLED=true" in config or "RIVERSHIFT_ACTIONS_ENABLED=true" in config:
        fail("API runtime defaults must remain fail-closed")

    disposition = json.loads((ROOT / "migration" / "workflow-dispositions.json").read_text(encoding="utf-8"))
    instances = disposition.get("workflow_instances", [])
    if len(instances) != 82:
        fail("all 82 source workflow instances must remain preserved as provenance")
    counts = {item["id"]: item["expected_workflow_count"] for item in disposition.get("sources", [])}
    if counts != {"dynamic-main": 7, "backend-main": 35, "backend-known-place-pr85": 40}:
        fail(f"unexpected source workflow provenance counts: {counts}")

    evidence = scope.get("evidence", {})
    fd = evidence.get("find_displacements", {})
    if not (fd.get("conclusion") == "success" and fd.get("jobs_total") == 20
            and fd.get("jobs_success") == 19 and fd.get("jobs_failed_initial_attempt") == 1
            and fd.get("retry_conclusion") == "success"
            and fd.get("final_dashboard_conclusion") == "success"
            and fd.get("terminal_callback_conclusion") == "success"):
        fail("Find Displacements primary runtime evidence is incomplete or inconsistent")
    rs = evidence.get("river_shift", {})
    if not (rs.get("error_code") == "EVENT_WINDOW_NOT_BRACKETED"
            and rs.get("catalogue_exact_matches") == 14
            and rs.get("product_batches_started") is False):
        fail("RiverShift evidence must retain the observed fail-closed eligibility distinction")
    kp = evidence.get("known_place", {})
    dispatch = kp.get("dispatch_query_first_page", {})
    if not (kp.get("generic_backend_science_ref") == "0e0611c12913044787ee84a39fa60a81d30ae516"
            and kp.get("two_polygon_pr_state") == "open"
            and kp.get("two_polygon_pr_draft") is True
            and kp.get("two_polygon_pr_merged") is False
            and dispatch.get("records_returned") == 100
            and dispatch.get("generic_dispatches") == 16
            and dispatch.get("generic_success") == 8
            and dispatch.get("generic_failure") == 7
            and dispatch.get("author_exact_dispatches") == 1
            and dispatch.get("author_exact_failure") == 1):
        fail("Known Place active-run evidence or unmerged feature-branch lineage is stale/inconsistent")
    author = kp.get("author_exact", {})
    if not (author.get("last_run_id") == 41423614257
            and author.get("conclusion") == "failure"
            and author.get("cleanup_error") == "SOURCE_MANIFEST_STATUS_NOT_COMPLETE"):
        fail("Author-Exact P05023 must remain gated until a complete successful replay is evidenced")

    print("ACTIVE_RUNTIME_SCOPE=PASS "
          f"primary_runtime_workflows={len(primary)} gated_feature_workflows={len(gated)} "
          f"migration_ci_workflows={len(ci)} api_feature_paths={len(paths)} "
          f"source_workflow_instances={len(instances)}")
    print("PRIMARY_RUNTIME=find-displacements,known-place-generic")
    print("GATED_FEATURES=river-shift,known-place-author-exact-p05023")
    print("NOTE=source_snapshot_provenance_does_not_activate_unused_workflows_or_claim_production_cutover")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
