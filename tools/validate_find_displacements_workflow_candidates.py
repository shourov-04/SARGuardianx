#!/usr/bin/env python3
"""Validate inactive Find Displacements workflow candidates against exact sources."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "migration/source-snapshots/backend-main/.github/workflows"
CANDIDATE_DIR = ROOT / "migration/workflow-candidates/find-displacements"
DASH_SOURCE = SOURCE_DIR / "sarguardian-aoi-wkt-dashboard.yml"
WORKER_SOURCE = SOURCE_DIR / "sarguardian-aoi-product-worker.yml"
DASH_CANDIDATE = CANDIDATE_DIR / "sarguardian-aoi-wkt-dashboard.yml"
WORKER_CANDIDATE = CANDIDATE_DIR / "sarguardian-aoi-product-worker.yml"
API_SOURCE = ROOT / "apps/api/app/displacements.py"

PIN_REPLACEMENTS = (
    (
        "actions/checkout@v4",
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
    ),
    (
        "actions/setup-python@v5",
        "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7.1.0",
    ),
    (
        "actions/upload-artifact@v4",
        "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2",
    ),
    (
        "actions/download-artifact@v4",
        "actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333 # v8.0.2",
    ),
)

DASH_REPLACEMENTS = PIN_REPLACEMENTS + (
    (
        "repository: moshiour0/SARGuardian_Dynamic",
        "repository: moshiour0/SARGuardian-Monorepo",
    ),
    (
        "repository: moshiour0/SARGuardian-backend",
        "repository: moshiour0/SARGuardian-Monorepo",
    ),
    (
        "repository: moshiour0/SARGuardian\n",
        "repository: moshiour0/SARGuardian-Monorepo\n",
    ),
    (
        "workflow-support/tools/",
        "workflow-support/engines/find-displacements/tools/",
    ),
    (
        "dashboard-source/tools/",
        "dashboard-source/engines/find-displacements/tools/",
    ),
    (
        "tools/requirements-retention.txt",
        "engines/find-displacements/tools/requirements-retention.txt",
    ),
    (
        "python tools/",
        "python engines/find-displacements/tools/",
    ),
)

WORKER_REPLACEMENTS = PIN_REPLACEMENTS + (
    (
        "repository: moshiour0/SARGuardian\n",
        "repository: moshiour0/SARGuardian-Monorepo\n",
    ),
    (
        "tools/requirements-retention.txt",
        "engines/find-displacements/tools/requirements-retention.txt",
    ),
    (
        "python tools/",
        "python engines/find-displacements/tools/",
    ),
)

EXPECTED_PINS = {
    "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1": 10,
    "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0": 3,
    "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9": 3,
    "actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333": 7,
}
EXPECTED_WORKER_PINS = {
    "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1": 2,
    "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0": 1,
    "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9": 4,
    "actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333": 1,
}

def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def transform(source: str, replacements: tuple[tuple[str, str], ...], label: str) -> str:
    result = source
    for old, new in replacements:
        count = result.count(old)
        if count == 0:
            fail(f"{label}: expected source token missing: {old!r}")
        result = result.replace(old, new)
    return result


def load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    except (OSError, yaml.YAMLError) as exc:
        fail(f"{label}: YAML parse failed: {type(exc).__name__}")
    if not isinstance(value, dict) or not isinstance(value.get("jobs"), dict):
        fail(f"{label}: expected workflow/job mapping")
    return value


def job_ids(doc: dict[str, Any]) -> list[str]:
    return list(doc["jobs"].keys())


def normalize_needs(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value]
    if value is None:
        return []
    return [str(value)]


def compare_job_graph(source: dict[str, Any], candidate: dict[str, Any], label: str) -> None:
    if job_ids(source) != job_ids(candidate):
        fail(f"{label}: job identifiers/order changed")
    for job_id in job_ids(source):
        old = source["jobs"][job_id]
        new = candidate["jobs"][job_id]
        if normalize_needs(old.get("needs")) != normalize_needs(new.get("needs")):
            fail(f"{label}: needs graph changed in job {job_id}")
        if old.get("if") != new.get("if"):
            fail(f"{label}: job condition changed in {job_id}")
        if old.get("strategy") != new.get("strategy"):
            fail(f"{label}: strategy/matrix changed in {job_id}")
        if old.get("with") != new.get("with"):
            fail(f"{label}: reusable worker input mapping changed in {job_id}")


def validate_action_pins(text: str, expected: dict[str, int], label: str) -> None:
    for action, count in expected.items():
        actual = text.count(action)
        if actual != count:
            fail(f"{label}: expected {count} occurrences of {action}, got {actual}")
    if re.search(r"(?m)^\s*uses:\s*[^\s]+@v\d", text):
        fail(f"{label}: unpinned version-tag action remains")
    # A workflow call to a local reusable workflow is not a third-party action.
    external_uses = re.findall(r"(?m)^\s*uses:\s*([^\s]+)", text)
    allowed_non_action = {
        "./.github/workflows/sarguardian-aoi-product-worker.yml",
    }
    for item in external_uses:
        if item.startswith("./"):
            if item not in allowed_non_action:
                fail(f"{label}: unexpected local workflow reference {item}")


def validate_inputs(dashboard: dict[str, Any]) -> None:
    dispatch = dashboard.get("on", {}).get("workflow_dispatch", {}).get("inputs", {})
    call = dashboard.get("on", {}).get("workflow_call", {}).get("inputs", {})
    required = {
        "aoi_wkt", "start_date", "end_date", "date_filter_mode",
        "run_profile", "retention_profile", "job_id", "callback_url",
        "request_fingerprint", "place_name", "place_latitude",
        "place_longitude", "target_latitude", "target_longitude",
    }
    missing_dispatch = sorted(required - set(dispatch))
    missing_call = sorted(required - set(call))
    if missing_dispatch or missing_call:
        fail(
            "dashboard input contract incomplete: "
            f"dispatch_missing={missing_dispatch}; call_missing={missing_call}"
        )
    api = API_SOURCE.read_text(encoding="utf-8")
    for key in ("date_filter_mode", "run_profile", "retention_profile", "request_fingerprint"):
        if f'"{key}"' not in api:
            fail(f"API dispatcher input mapping is missing {key}")


def validate_tool_paths(text: str, label: str) -> None:
    # Match only a root-relative command/reference. The old substring check also
    # matched the valid promoted path under engines/find-displacements/tools/.
    legacy_root_command = re.search(r"(?m)^\s*python\s+tools/", text)
    legacy_root_requirements = re.search(
        r"(?m)^\s*(?:-r\s+)?tools/requirements-retention\.txt(?:\s|$)",
        text,
    )
    if legacy_root_command or legacy_root_requirements:
        fail(f"{label}: old root tools path remains")
    refs = re.findall(
        r"(?:python\s+| -r\s+|environment-file:\s*)([A-Za-z0-9_./-]*engines/find-displacements/tools/[A-Za-z0-9_./-]+)",
        text,
    )
    for relative in refs:
        # Some workflow steps check out the same Monorepo into a runner-local
        # subdirectory. Validate the referenced repository path from the
        # Monorepo root, not a runner workspace prefix.
        repo_relative = relative
        for checkout_prefix in ("workflow-support/", "dashboard-source/"):
            if repo_relative.startswith(checkout_prefix):
                repo_relative = repo_relative[len(checkout_prefix):]
                break
        candidate = ROOT / repo_relative
        if not candidate.is_file():
            fail(
                f"{label}: promoted tool path does not exist in the Monorepo: "
                f"{relative} (repository path: {repo_relative})"
            )
    if label == "dashboard" and "dashboard-source/engines/find-displacements/tools/aggregate_aoi_run.py" not in text:
        fail(f"{label}: dashboard aggregator is not mapped to promoted engine")


def main() -> int:
    source_dashboard_text = DASH_SOURCE.read_text(encoding="utf-8")
    source_worker_text = WORKER_SOURCE.read_text(encoding="utf-8")
    dashboard_text = DASH_CANDIDATE.read_text(encoding="utf-8")
    worker_text = WORKER_CANDIDATE.read_text(encoding="utf-8")

    expected_dashboard = transform(source_dashboard_text, DASH_REPLACEMENTS, "dashboard")
    expected_worker = transform(source_worker_text, WORKER_REPLACEMENTS, "worker")
    if dashboard_text != expected_dashboard:
        fail("dashboard candidate contains changes beyond the reviewed path/repository/action pin mapping")
    if worker_text != expected_worker:
        fail("worker candidate contains changes beyond the reviewed path/repository/action pin mapping")

    source_dashboard = load_yaml(DASH_SOURCE, "source dashboard")
    candidate_dashboard = load_yaml(DASH_CANDIDATE, "candidate dashboard")
    source_worker = load_yaml(WORKER_SOURCE, "source worker")
    candidate_worker = load_yaml(WORKER_CANDIDATE, "candidate worker")

    compare_job_graph(source_dashboard, candidate_dashboard, "dashboard")
    compare_job_graph(source_worker, candidate_worker, "worker")
    validate_inputs(candidate_dashboard)
    validate_action_pins(dashboard_text, EXPECTED_PINS, "dashboard")
    validate_action_pins(worker_text, EXPECTED_WORKER_PINS, "worker")
    validate_tool_paths(dashboard_text, "dashboard")
    validate_tool_paths(worker_text, "worker")

    dashboard_repo_values = re.findall(r"(?m)^\s*repository:\s*(\S+)", dashboard_text)
    worker_repo_values = re.findall(r"(?m)^\s*repository:\s*(\S+)", worker_text)
    allowed_repo = "moshiour0/SARGuardian-Monorepo"
    if any(value != allowed_repo for value in dashboard_repo_values + worker_repo_values):
        fail("candidate still checks out an external repository")
    if "moshiour0/SARGuardian-backend" in dashboard_text + worker_text:
        fail("candidate retains old backend checkout owner")
    if "moshiour0/SARGuardian_Dynamic" in dashboard_text + worker_text:
        fail("candidate retains old Dynamic checkout owner")

    # The dashboard and worker must be promoted as one reusable workflow pair.
    for job_id in ("process-products", "retry-products"):
        job = candidate_dashboard["jobs"].get(job_id, {})
        if job.get("uses") != "./.github/workflows/sarguardian-aoi-product-worker.yml":
            fail(f"dashboard {job_id} does not call the Monorepo local worker")
    if "workflow_call" not in candidate_worker.get("on", {}):
        fail("product worker is not reusable via workflow_call")

    print("FIND_DISPLACEMENTS_MONOREPO_CANDIDATE_PASS")
    print(f"FIND_DISPLACEMENTS_DASHBOARD_JOBS={len(job_ids(candidate_dashboard))}")
    print(f"FIND_DISPLACEMENTS_WORKER_JOBS={len(job_ids(candidate_worker))}")
    print(f"FIND_DISPLACEMENTS_DASHBOARD_ACTION_PINS={sum(EXPECTED_PINS.values())}")
    print(f"FIND_DISPLACEMENTS_WORKER_ACTION_PINS={sum(EXPECTED_WORKER_PINS.values())}")
    print("FIND_DISPLACEMENTS_INPUT_WORKER_ARTIFACT_CALLBACK_RETRY_GRAPH=UNCHANGED")
    print("FIND_DISPLACEMENTS_CANDIDATE_STATUS=INACTIVE_CANDIDATE_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
