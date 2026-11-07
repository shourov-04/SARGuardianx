from __future__ import annotations

import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPOSITORY_ROOT / ".github" / "workflows" / "river-shift-gcov-process.yml"


def _job_block(workflow: str, job_name: str, next_job: str) -> str:
    start_marker = f"  {job_name}:"
    end_marker = f"  {next_job}:"
    start = workflow.find(start_marker)
    end = workflow.find(end_marker, start + len(start_marker))
    assert start >= 0, f"Missing Monorepo RiverShift job: {job_name}"
    assert end > start, f"Missing next job after Monorepo RiverShift job: {job_name}"
    return workflow[start:end]


def test_root_workflow_has_preflight_and_all_twenty_processing_jobs():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    jobs_section = workflow.split("\njobs:\n", 1)[1]
    job_names = re.findall(r"^  ([A-Za-z0-9_-]+):\s*$", jobs_section, re.MULTILINE)
    expected = {
        "preflight", "prepare",
        "batch_1", "batch_1_status",
        "batch_2", "batch_2_status",
        "batch_3", "batch_3_status",
        "batch_4", "batch_4_status",
        "retry_prepare", "retry_dispatch", "retry",
        "retry_prepare_2", "retry_dispatch_2", "retry_2",
        "retry_prepare_3", "retry_dispatch_3", "retry_3",
        "retry_status", "assemble",
    }

    assert len(job_names) == 21
    assert set(job_names) == expected
    assert "permissions:\n  contents: read\n" in workflow
    assert "actions: write" not in workflow
    assert "needs: preflight" in _job_block(workflow, "prepare", "batch_1")


def test_preflight_is_fail_closed_and_does_not_receive_worker_secrets():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    preflight = _job_block(workflow, "preflight", "prepare")

    assert "MONOREPO_RIVERSHIFT_PROCESSING_ENABLED" in preflight
    assert 'if [[ "$MONOREPO_PROCESSING_ENABLED" != "true" ]]' in preflight
    assert "secrets." not in preflight


def test_four_first_attempt_batches_are_sequential_and_status_gated():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    batches = [
        ("batch_1", "batch_1_status", "needs: prepare",
         "batch_1_status", "needs: [prepare, batch_1]"),
        ("batch_2", "batch_2_status", "needs: [prepare, batch_1_status]",
         "batch_2_status", "needs: [prepare, batch_1_status, batch_2]"),
        ("batch_3", "batch_3_status", "needs: [prepare, batch_2_status]",
         "batch_3_status", "needs: [prepare, batch_2_status, batch_3]"),
        ("batch_4", "batch_4_status", "needs: [prepare, batch_3_status]",
         "batch_4_status", "needs: [prepare, batch_3_status, batch_4]"),
    ]
    next_for_status = {
        "batch_1_status": "batch_2",
        "batch_2_status": "batch_3",
        "batch_3_status": "batch_4",
        "batch_4_status": "retry_prepare",
    }

    for batch, status, batch_needs, _status_name, status_needs in batches:
        block = _job_block(workflow, batch, status)
        status_block = _job_block(workflow, status, next_for_status[status])
        assert batch_needs in block
        assert "max-parallel: 15" in block
        assert "continue-on-error: true" not in block
        assert "run: python -u engines/river-shift/tools/river_shift/batched_gcov_job.py" in block
        assert status_needs in status_block
        assert "if: always()" in status_block

    for batch_name, previous_status in (
        ("batch_2", "batch_1_status"),
        ("batch_3", "batch_2_status"),
        ("batch_4", "batch_3_status"),
    ):
        block = _job_block(workflow, batch_name, f"{batch_name}_status")
        assert f"needs.{previous_status}.result == 'success'" in block


def test_retry_waves_are_fresh_runner_limited_and_assembled_after_reconciliation():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    waves = [
        ("retry_prepare", "retry_dispatch", "retry", "retry_prepare_2"),
        ("retry_prepare_2", "retry_dispatch_2", "retry_2", "retry_prepare_3"),
        ("retry_prepare_3", "retry_dispatch_3", "retry_3", "retry_status"),
    ]

    for prepare_name, dispatch_name, worker_name, next_name in waves:
        prepare = _job_block(workflow, prepare_name, dispatch_name)
        dispatch = _job_block(workflow, dispatch_name, worker_name)
        worker = _job_block(workflow, worker_name, next_name)
        assert "RIVERSHIFT_RETRY_ATTEMPT:" in prepare
        assert "validate_retry_matrix.py" in dispatch
        assert "RIVERSHIFT_EXPECTED_RETRY_ATTEMPT:" in dispatch
        assert "max-parallel: 15" in worker
        assert "!cancelled()" in worker
        assert "continue-on-error: true" not in worker
        assert "run: python -u engines/river-shift/tools/river_shift/batched_gcov_job.py" in worker

    retry_status = _job_block(workflow, "retry_status", "assemble")
    for name in (
        "retry_dispatch", "retry_dispatch_2", "retry_dispatch_3",
        "retry_prepare_2", "retry_prepare_3", "retry_2", "retry_3",
    ):
        assert name in retry_status
    assert "if: always()" in retry_status
    assert "RIVERSHIFT_RETRY_DISPATCH_STATUSES:" in retry_status
    assert "RIVERSHIFT_RETRY_PREPARE_STATUSES:" in retry_status
    assert "RIVERSHIFT_RETRY_COUNTS:" in retry_status
    assert "needs.retry_status.result == 'success'" in workflow[workflow.find("  assemble:"):]


def test_google_drive_and_callback_credentials_are_least_scoped():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    prepare = _job_block(workflow, "prepare", "batch_1")
    product = _job_block(workflow, "batch_1", "batch_1_status")
    status = _job_block(workflow, "batch_1_status", "batch_2")
    assemble = workflow[workflow.find("  assemble:"):]

    required_in_prepare_and_assemble = (
        "RIVERSHIFT_CALLBACK_SECRET",
        "EARTHDATA_TOKEN",
        "EARTHDATA_USERNAME",
        "EARTHDATA_PASSWORD",
        "GOOGLE_DRIVE_OAUTH_CLIENT_JSON",
        "GOOGLE_DRIVE_REFRESH_TOKEN",
        "GOOGLE_DRIVE_PARENT_FOLDER_ID",
    )
    for name in required_in_prepare_and_assemble:
        assert f"secrets.{name}" in prepare
        assert f"secrets.{name}" in assemble

    for name in ("EARTHDATA_TOKEN", "EARTHDATA_USERNAME", "EARTHDATA_PASSWORD"):
        assert f"secrets.{name}" in product
    for name in (
        "RIVERSHIFT_CALLBACK_SECRET",
        "GOOGLE_DRIVE_OAUTH_CLIENT_JSON",
        "GOOGLE_DRIVE_REFRESH_TOKEN",
        "GOOGLE_DRIVE_PARENT_FOLDER_ID",
    ):
        assert f"secrets.{name}" not in product

    assert "secrets.RIVERSHIFT_CALLBACK_SECRET" in status
    assert "secrets.EARTHDATA_TOKEN" not in status
    assert "secrets.GOOGLE_DRIVE_OAUTH_CLIENT_JSON" not in status


def test_independent_reference_validation_is_manual_local_and_separately_gated():
    workflow_path = REPOSITORY_ROOT / ".github" / "workflows" / "river-shift-independent-reference-validation.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    trigger_section = workflow.split("\njobs:\n", 1)[0]

    assert "workflow_dispatch:" in trigger_section
    assert "\n  push:" not in trigger_section
    assert "MONOREPO_RIVERSHIFT_REFERENCE_VALIDATION_ENABLED" in workflow
    assert '!= "true"' in workflow
    assert "engines/river-shift/tools/river_shift/validate_independent_reference.py" in workflow
    assert "repository: moshiour0/SARGuardian-backend" not in workflow
    assert "sarguardian-backend-api.vercel.app" not in workflow
    assert "RIVERSHIFT_VALIDATION_API_BASE_URL: ${{ inputs.api_base_url }}" in workflow
    assert "secrets.RIVERSHIFT_CALLBACK_SECRET" in workflow
    assert "secrets.GOOGLE_DRIVE_PARENT_FOLDER_ID" in workflow
    assert "MONOREPO_RIVERSHIFT_PROCESSING_ENABLED" not in workflow
