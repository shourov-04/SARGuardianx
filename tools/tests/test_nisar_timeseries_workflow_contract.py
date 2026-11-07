from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
GUNW = ROOT / ".github" / "workflows" / "nisar-gunw-timeseries-test.yml"
GOFF = ROOT / ".github" / "workflows" / "nisar-goff-timeseries-test.yml"
GOFF_DRIVE_UPLOADER = ROOT / "migration" / "source-snapshots" / "backend-main" / "scripts" / "upload_goff_result_to_drive.py"


def _load(path: Path):
    text = path.read_text(encoding="utf-8")
    return yaml.load(text, Loader=yaml.BaseLoader), text


def _base(path: Path, job: str):
    workflow, text = _load(path)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert workflow["permissions"]["contents"] == "read"
    assert workflow["jobs"][job]["needs"] == "preflight"
    assert "MONOREPO_NISAR_PRODUCT_TESTS_ENABLED" in text
    assert '!= "true"' in text
    assert "77cc9646cfa46d3aff3669d351912f984cf67aa3" in text
    assert 'git -C "$GITHUB_WORKSPACE" cat-file -e "$SCIENCE_COMMIT^{commit}"' in text
    assert 'git -C "$GITHUB_WORKSPACE" archive "$SCIENCE_COMMIT"' in text
    assert 'os.environ.get("SCIENCE_COMMIT", "")' in text
    assert "rev-parse" not in text
    assert "repository: Sagormodak/SARGuardian" not in text
    assert "repository: moshiour0/SARGuardian" not in text
    assert "repository: moshiour0/SARGuardian-backend" not in text
    assert "secrets.EARTHDATA_USERNAME" in text
    assert "secrets.EARTHDATA_PASSWORD" in text
    assert "RAW_CLEANUP_FAILED" in text or "RAW_CLEANUP_SUCCESS" in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text
    return workflow, text


def test_gunw_time_series_keeps_three_sequential_pairs_and_raw_cleanup():
    workflow, text = _base(GUNW, "gunw-timeseries")
    assert "GUNW_DOWNLOAD_PROGRESS: {download_index}/3" in text
    assert "zip(chain, pairs)" in text
    assert "read_gunw(" in text
    assert "NISAR_GUNW_TIMESERIES_RAW_CLEANUP_SUCCESS" in text
    assert "NISAR_GUNW_TIMESERIES_RAW_CLEANUP_FAILED" in text
    assert "drive_resumable_upload.py" not in text


def test_goff_candidate4_time_series_retains_drive_output_with_local_uploader():
    workflow, text = _base(GOFF, "goff-timeseries")
    assert "read_goff(" in text
    assert "candidate-4" in text.lower()
    assert "scripts/upload_goff_result_to_drive.py" in text
    assert str(GOFF_DRIVE_UPLOADER).replace(str(ROOT) + "/", "") in str(GOFF_DRIVE_UPLOADER)
    assert "secrets.GOOGLE_DRIVE_OAUTH_CLIENT_JSON" in text
    assert "secrets.GOOGLE_DRIVE_REFRESH_TOKEN" in text
    assert "secrets.GOOGLE_DRIVE_PARENT_FOLDER_ID" in text
    assert "actions/upload-artifact@" in text
    assert "raw_cleanup_success" in text
