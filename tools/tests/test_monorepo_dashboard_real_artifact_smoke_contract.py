from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "dashboard-real-artifact-smoke.yml"


def test_retained_dashboard_smoke_is_manual_and_monorepo_run_scoped():
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "push" not in workflow.get("on", {})
    inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    assert set(inputs) == {"source_run_id"}
    assert inputs["source_run_id"]["required"] == "true"
    assert "default" not in inputs["source_run_id"]

    assert workflow["permissions"]["contents"] == "read"
    assert workflow["permissions"]["actions"] == "read"
    assert workflow["jobs"]["rebuild"]["needs"] == "preflight"
    assert workflow["jobs"]["rebuild"]["defaults"]["run"]["working-directory"] == "migration/source-snapshots/backend-main"
    assert "MONOREPO_DASHBOARD_REAL_ARTIFACT_SMOKE_ENABLED" in text
    assert '!= "true"' in text

    for required in (
        "SOURCE_RUN_NOT_FROM_THIS_MONOREPO",
        "SOURCE_RUN_HEAD_REPOSITORY_NOT_MONOREPO",
        "SOURCE_RUN_NOT_FROM_EXPECTED_PREVIEW_BRANCH",
        "SOURCE_RUN_NOT_SUCCESSFUL",
        "SOURCE_RUN_WORKFLOW_NOT_AN_APPROVED_AOI_ENTRYPOINT",
        'if run.get("path") != ".github/workflows/sarguardian-aoi-wkt-dashboard.yml":',
        "run_attempt",
    ):
        assert required in text

    assert "sarguardian-aoi-dashboard-" in text
    assert 'if run.get("path") != ".github/workflows/sarguardian-aoi-wkt-dashboard.yml":' in text
    assert ".github/workflows/sarguardian-aoi-wkt-dispatcher.yml" not in text
    assert 'output.write(f"run_id={run_id}\\n")' in text
    assert 'output.write(f"run_attempt={attempt}\\n")' in text
    assert "steps.source.outputs.run_attempt" in text
    assert ".github/workflows/sarguardian-aoi-wkt-dispatcher.yml" not in text
    assert "actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333" in text
    assert "006d4cd1485cf80e509eaf8717c12e9c6390ac09" in text
    assert 'git -C "$GITHUB_WORKSPACE" archive "$SCIENCE_COMMIT"' in text
    assert "repository: moshiour0/SARGuardian" not in text
    assert "repository: moshiour0/SARGuardian-backend" not in text
    assert "40998521651" not in text
    assert "NO_RAW_REPLAY=true" in text
    assert "raw_hdf5_replayed" in text
    assert "WITHHELD_NO_COMPATIBLE_REPEATED_NETWORK" in text
    assert "NOT TESTABLE, not NO DETECTION" in text
    assert 'int(extended.get("candidate_features", 0)) == 2208' in text
    assert "gunw_tiffs[@]" in text
    assert 'test "$before" = "$after"' in text
    assert 'output.write(f"run_id={run_id}\\\\n")' not in text

    job = workflow["jobs"]["rebuild"]
    assert "GOOGLE_DRIVE_OAUTH_CLIENT_JSON" not in str(job.get("env", {}))
    drive_step = next(step for step in job["steps"] if step.get("name") == "Upload refreshed dashboard bundle and audit receipts to private Drive")
    assert set(drive_step["env"]) == {
        "GOOGLE_DRIVE_OAUTH_CLIENT_JSON",
        "GOOGLE_DRIVE_REFRESH_TOKEN",
        "GOOGLE_DRIVE_PARENT_FOLDER_ID",
        "RUN_ID_SAFE",
    }
    assert "drive_resumable_upload.py" in text
    assert "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9" in text
