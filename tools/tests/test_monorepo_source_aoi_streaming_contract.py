from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
STREAM = ROOT / ".github" / "workflows" / "sarguardian-streaming-batch.yml"
WORKER = ROOT / ".github" / "workflows" / "sarguardian-product-worker.yml"


def _load(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    value = yaml.load(text, Loader=yaml.BaseLoader)
    assert isinstance(value, dict)
    return value, text


def test_source_aoi_streaming_batch_is_local_manual_and_fail_closed():
    workflow, text = _load(STREAM)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "push" not in workflow.get("on", {})
    assert "MONOREPO_DISPLACEMENT_STREAMING_ENABLED" in text
    assert '!= "true"' in text

    jobs = workflow["jobs"]
    assert jobs["manifest"]["needs"] == "preflight"
    assert jobs["process-one"]["uses"] == "./.github/workflows/sarguardian-product-worker.yml"
    assert jobs["retry-products"]["uses"] == "./.github/workflows/sarguardian-product-worker.yml"
    assert jobs["retry-plan"]["needs"] == ["manifest", "process-one"]
    assert jobs["preassembly-verify"]["needs"] == ["manifest", "process-one", "retry-plan", "retry-products"]
    assert jobs["aggregate"]["needs"] == ["manifest", "process-one", "retry-plan", "retry-products", "preassembly-verify"]
    assert "always()" in jobs["retry-plan"]["if"]
    assert "always()" in jobs["aggregate"]["if"]
    assert "needs.preassembly-verify.result == 'success'" in jobs["aggregate"]["if"]

    for caller in ("process-one", "retry-products"):
        secrets = jobs[caller].get("secrets", {})
        assert set(secrets) == {
            "EARTHDATA_USERNAME", "EARTHDATA_PASSWORD", "EARTHDATA_TOKEN",
            "GOOGLE_DRIVE_OAUTH_CLIENT_JSON", "GOOGLE_DRIVE_REFRESH_TOKEN",
            "GOOGLE_DRIVE_PARENT_FOLDER_ID",
        }

    assert "ab547ecc82bcc4d6ccef545a59852536c2beacc6" in text
    assert 'git -C "$GITHUB_WORKSPACE" archive' in text
    assert "repository: moshiour0/SARGuardian" not in text
    assert "repository: moshiour0/SARGuardian-backend" not in text
    assert "secrets: inherit" not in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text
    assert "actions/download-artifact@v4" not in text
    assert "actions/upload-artifact@v4" not in text
    assert "max-parallel: 1" in text
    assert "validation-pilot" in text and "full-source-baseline" in text
    assert "resume_from_run_id" in text
    assert "product_retry_gate.py plan-retries" in text
    assert "product_retry_gate.py verify" in text
    assert "BATCH_EQUIVALENCE_STATUS" in text


def test_source_aoi_product_worker_uses_exact_local_sources_and_narrow_secrets():
    workflow, text = _load(WORKER)
    trigger = workflow.get("on", {})
    assert set(trigger) == {"workflow_call"}
    inputs = trigger["workflow_call"]["inputs"]
    assert set(inputs) == {
        "product_id", "granule_name", "product_type", "maturity",
        "expected_source_bytes", "retention_profile", "execution_label",
    }
    assert set(trigger["workflow_call"]["secrets"]) == {
        "EARTHDATA_USERNAME", "EARTHDATA_PASSWORD", "EARTHDATA_TOKEN",
        "GOOGLE_DRIVE_OAUTH_CLIENT_JSON", "GOOGLE_DRIVE_REFRESH_TOKEN",
        "GOOGLE_DRIVE_PARENT_FOLDER_ID",
    }
    assert "continue-on-error" in text
    assert "AOI_NAME: source" in text
    assert "SCIENCE_COMMIT: ab547ecc82bcc4d6ccef545a59852536c2beacc6" in text
    assert 'git -C "$GITHUB_WORKSPACE" archive' in text
    assert "repository: moshiour0/SARGuardian" not in text
    assert "repository: moshiour0/SARGuardian-backend" not in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text
    assert "actions/download-artifact@v4" not in text
    assert "actions/upload-artifact@v4" not in text
    assert "download_nisar_product.py" in text
    assert "drive_resumable_upload.py" in text
    assert "Delete local raw/archive only after successful remote retention" in text
    assert "if: success()" in text
