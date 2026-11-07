from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "find-displacements-reassemble-existing.yml"


def test_reassembly_is_manual_gated_and_uses_only_monorepo_artifacts():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow = yaml.load(workflow_text, Loader=yaml.BaseLoader)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}

    inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    assert set(inputs) == {"checkpoint_run_id", "product_run_id"}
    assert inputs["checkpoint_run_id"]["required"] == "true"
    assert inputs["product_run_id"]["required"] == "true"
    assert "default" not in inputs["checkpoint_run_id"]
    assert "default" not in inputs["product_run_id"]

    assert workflow["permissions"]["contents"] == "read"
    assert workflow["permissions"]["actions"] == "read"
    assert workflow["jobs"]["reassemble"]["needs"] == "preflight"
    assert "MONOREPO_FIND_DISPLACEMENT_REASSEMBLY_ENABLED" in workflow_text
    assert '!= "true"' in workflow_text

    assert "migration/source-snapshots/backend-pins/d9e67" in workflow_text
    assert "d9e67df7d800032c37d23f74df44c98e3ab655f7" in workflow_text
    assert "ab547ecc82bcc4d6ccef545a59852536c2beacc6" in workflow_text
    assert "git archive" in workflow_text
    assert "repository: moshiour0/SARGuardian-backend" not in workflow_text
    assert "repository: moshiour0/SARGuardian" not in workflow_text
    assert "sarguardian-backend-api.vercel.app" not in workflow_text

    for name in (
        "sarguardian-stream-run-manifest",
        "sarguardian-granule-*",
        "sarguardian-cleanup-*",
    ):
        assert name in workflow_text
    assert "inputs.checkpoint_run_id" in workflow_text
    assert "inputs.product_run_id" in workflow_text

    assert "secrets.GOOGLE_DRIVE_OAUTH_CLIENT_JSON" in workflow_text
    assert "secrets.GOOGLE_DRIVE_REFRESH_TOKEN" in workflow_text
    assert "secrets.GOOGLE_DRIVE_PARENT_FOLDER_ID" in workflow_text
    assert "EARTHDATA_TOKEN" not in workflow_text
    assert "download_nisar_product.py" not in workflow_text

    assert "len(products) != 33" in workflow_text
    assert '{"GUNW": 15, "GOFF": 18}' in workflow_text
    assert "REASSEMBLY_SCIENCE_COMMIT_DOES_NOT_MATCH_EXACT_BASELINE_PIN" in workflow_text
    assert "aggregate_streamed_outputs.py" in workflow_text
    assert '|| "$report_status" != "PASS"' in workflow_text
    assert "if: steps.aggregate_results.outputs.status == 'PASS' && steps.aggregate_results.outputs.script_exit == '0'" in workflow_text
    assert "drive_resumable_upload.py" in workflow_text
