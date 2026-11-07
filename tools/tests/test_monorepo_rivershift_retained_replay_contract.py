from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = {
    "opera": ROOT / ".github" / "workflows" / "river-shift-opera-dswx-s1-retained-replay.yml",
    "run36": ROOT / ".github" / "workflows" / "river-shift-run36-retrospective-replay.yml",
    "sentinel2": ROOT / ".github" / "workflows" / "river-shift-sentinel2-retained-replay.yml",
}
HELPER = ROOT / "engines" / "river-shift" / "tools" / "river_shift" / "verify_monorepo_source_run.py"
RUN36_WRAPPER = ROOT / "engines" / "river-shift" / "tools" / "river_shift" / "replay_retained_run36_monorepo.py"
CANONICAL_RUN36 = ROOT / "engines" / "river-shift" / "tools" / "river_shift" / "replay_retained_run36.py"
PREVIEW_API_HOST = "sar-guardi-git-ed4bd9-moshiour-rahman-sarkers-projects-2cebe363.vercel.app"


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    return workflow, text


def check_common(workflow: dict, text: str, gate: str, job: str):
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "push:" not in text
    assert "MONOREPO_RIVERSHIFT_" in text
    assert gate in text
    assert '!= "true"' in text
    assert workflow["permissions"]["contents"] == "read"
    assert workflow["permissions"]["actions"] == "read"
    assert workflow["jobs"][job]["needs"] == "preflight"
    assert "verify_monorepo_source_run.py" in text
    assert "rivershift-prepared-" in text
    assert "github.token" in text
    assert "repository: moshiour0/SARGuardian-backend" not in text
    assert "sarguardian-backend-api.vercel.app" not in text
    assert "actions/checkout@v4" not in text
    assert "actions/download-artifact@v4" not in text
    assert "actions/upload-artifact@v4" not in text
    assert "mamba-org/setup-micromamba@v3" not in text


def test_monorepo_source_run_verifier_is_strict_and_artifact_scoped():
    text = HELPER.read_text(encoding="utf-8")
    assert "moshiour0/sarguardian-monorepo" in text
    assert "SOURCE_RUN_NOT_FROM_THIS_MONOREPO" in text
    assert "SOURCE_RUN_HEAD_REPOSITORY_NOT_MONOREPO" in text
    assert "SOURCE_RUN_BRANCH_MISMATCH" in text
    assert "SOURCE_RUN_MUST_BE_MANUALLY_DISPATCHED" in text
    assert "SOURCE_RUN_NOT_MONOREPO_RIVERSHIFT_GCOV_WORKFLOW" in text
    assert "SOURCE_RUN_NOT_SUCCESSFUL" in text
    assert "rivershift-prepared-" in text
    assert 'startswith("rivershift-product-")' in text
    assert "SOURCE_PREPARED_ARTIFACT_MISSING_OR_EXPIRED" in text
    assert "SOURCE_PRODUCT_COG_ARTIFACTS_MISSING_OR_EXPIRED" in text
    assert "EXPIRED" in text or 'get("expired") is False' in text
    assert "GITHUB_API_ARTIFACT_LIST" not in text or "ARTIFACT_LIST" in text


def test_opera_retained_replay_is_gated_preview_only_and_preserves_review_status():
    workflow, text = load(WORKFLOWS["opera"])
    check_common(workflow, text, "MONOREPO_RIVERSHIFT_OPERA_REPLAY_ENABLED", "reference")
    inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    assert set(inputs) == {
        "source_run_id", "source_job_id", "api_base_url",
        "maximum_date_offset_days", "discovery_window_days",
        "minimum_common_support_fraction",
    }
    assert inputs["source_run_id"]["required"] == "true"
    assert inputs["source_job_id"]["required"] == "true"
    assert inputs["api_base_url"]["default"] == f"https://{PREVIEW_API_HOST}"
    assert "API_BASE_URL_MUST_BE_THE_MONOREPO_PREVIEW_API" in text
    assert "run_opera_dswx_s1_reference.py" in text
    assert "METRICS_COMPUTED_REVIEW_REQUIRED" in text
    assert "PROVISIONAL_REVIEW_REQUIRED" in text
    assert "not field truth" in text
    assert "does not validate erosion" in text
    assert "secrets.EARTHDATA_TOKEN" in text
    assert "secrets.RIVERSHIFT_CALLBACK_SECRET" in text
    assert "secrets.GOOGLE_DRIVE_PARENT_FOLDER_ID" in text
    job_env = workflow["jobs"]["reference"].get("env", {})
    assert "GOOGLE_DRIVE_OAUTH_CLIENT_JSON" not in job_env
    replay = next(step for step in workflow["jobs"]["reference"]["steps"] if step.get("name") == "Run OPERA DSWx-S1 independent SAR cross-check")
    assert "GOOGLE_DRIVE_OAUTH_CLIENT_JSON" in replay["env"]


def test_run36_replay_uses_new_monorepo_source_run_and_six_checked_cogs():
    workflow, text = load(WORKFLOWS["run36"])
    check_common(workflow, text, "MONOREPO_RIVERSHIFT_RUN36_REPLAY_ENABLED", "replay")
    inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    assert set(inputs) == {"source_run_id", "source_job_id"}
    assert "41803576163" not in text
    assert "4e6e4071-fb9d-4e20-a331-867f3f2bd88f" not in text
    assert "pattern: rivershift-product-b01-*" in text
    assert "replay_retained_run36_monorepo.py" in text
    assert "--source-run-number" in text
    assert "--source-job-id" in text

    wrapper = RUN36_WRAPPER.read_text(encoding="utf-8")
    assert "exactly six distinct retained GCOV granules" in wrapper
    assert "original.ORIGINAL_METRICS" in wrapper
    assert "historical_reference" in wrapper
    assert "moshiour0/SARGuardian-Monorepo" in wrapper
    assert "EXACT_AREA_REPRODUCTION" in wrapper
    assert "original.replay(" in wrapper

    canonical = CANONICAL_RUN36.read_text(encoding="utf-8")
    assert "SOURCE_RUN_ID = 41803576163" in canonical
    assert "SOURCE_RUN_NUMBER = 36" in canonical
    assert "SOURCE_JOB_ID = \"4e6e4071-fb9d-4e20-a331-867f3f2bd88f\"" in canonical


def test_sentinel2_replay_binds_source_run_and_uses_every_cog_batch():
    workflow, text = load(WORKFLOWS["sentinel2"])
    check_common(workflow, text, "MONOREPO_RIVERSHIFT_SENTINEL2_REPLAY_ENABLED", "cross-sensor")
    inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    assert set(inputs) == {
        "source_run_id", "source_job_id", "api_base_url", "observation_date",
        "max_day_offset", "max_cloud_cover", "mndwi_threshold", "minimum_common_support",
    }
    assert inputs["source_run_id"]["required"] == "true"
    assert inputs["source_job_id"]["required"] == "true"
    assert inputs["observation_date"]["required"] == "true"
    assert inputs["api_base_url"]["default"] == f"https://{PREVIEW_API_HOST}"
    assert "API_BASE_URL_MUST_BE_THE_MONOREPO_PREVIEW_API" in text
    assert "pattern: rivershift-product-*" in text
    assert "source_workflow_run_id" in text
    assert "original_prepared_sha256" in text
    assert "original_manifest_mutated" in text
    assert "replay_sentinel2_from_retained_run.py" in text
    assert "publish_sentinel2_references.py" in text
    assert "sarguardian-backend-api.vercel.app" not in text
    assert "METRICS_COMPUTED_REVIEW_REQUIRED" in text
    assert "SENTINEL2_REFERENCE_METRICS_OR_REVIEW_GATE_FAILED" in text
    assert "not ground truth" in text.lower()
    assert "secrets.GOOGLE_DRIVE_OAUTH_CLIENT_JSON" in text
    assert "secrets.RIVERSHIFT_CALLBACK_SECRET" in text
    assert "GOOGLE_DRIVE_OAUTH_CLIENT_JSON" not in str(workflow["jobs"]["cross-sensor"].get("env", {}))
