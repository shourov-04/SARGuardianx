from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "sarguardian-extended-science.yml"


def test_extended_science_uses_only_verified_monorepo_derived_bundle():
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    assert set(inputs) == {"source_run_id"}
    assert inputs["source_run_id"]["required"] == "true"
    assert "default" not in inputs["source_run_id"]

    assert workflow["permissions"]["contents"] == "read"
    assert workflow["permissions"]["actions"] == "read"
    assert workflow["jobs"]["extended-science"]["needs"] == "preflight"
    assert workflow["jobs"]["extended-science"]["defaults"]["run"]["working-directory"] == "migration/source-snapshots/backend-main"
    assert "MONOREPO_EXTENDED_SCIENCE_ENABLED" in text
    assert '!= "true"' in text

    for required in (
        "SCIENCE_SOURCE_RUN_NOT_FROM_THIS_MONOREPO",
        "SCIENCE_SOURCE_HEAD_REPOSITORY_NOT_MONOREPO",
        "SCIENCE_SOURCE_BRANCH_MISMATCH",
        "SCIENCE_SOURCE_RUN_MUST_BE_MANUALLY_DISPATCHED",
        "SCIENCE_SOURCE_RUN_NOT_MONOREPO_STREAMING_BATCH",
        "SCIENCE_SOURCE_RUN_NOT_SUCCESSFUL",
        "SCIENCE_SOURCE_AGGREGATE_ARTIFACT_MISSING_OR_EXPIRED",
    ):
        assert required in text

    assert "ab547ecc82bcc4d6ccef545a59852536c2beacc6" in text
    assert 'git -C "$GITHUB_WORKSPACE" archive "$SCIENCE_COMMIT"' in text
    assert "sarguardian-streaming-run-" in text
    assert "actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333" in text
    assert "run_extended_science.py" in text
    assert "--source-bundle" in text
    assert "--science-root" in text
    assert "EARTHDATA" not in text
    assert "download_nisar_product.py" not in text
    assert "raw_hdf5_extracted" not in text
    assert "secrets.GOOGLE_DRIVE_OAUTH_CLIENT_JSON" in text
    assert "secrets.GOOGLE_DRIVE_REFRESH_TOKEN" in text
    assert "secrets.GOOGLE_DRIVE_PARENT_FOLDER_ID" in text
    assert "drive_resumable_upload.py" in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text
