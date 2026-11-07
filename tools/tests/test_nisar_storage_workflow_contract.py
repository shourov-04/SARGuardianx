from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SINGLE = ROOT / ".github" / "workflows" / "nisar-single-download-test.yml"
MULTI = ROOT / ".github" / "workflows" / "nisar-multi-granule-storage-test.yml"


def _load(path: Path):
    text = path.read_text(encoding="utf-8")
    return yaml.load(text, Loader=yaml.BaseLoader), text


def test_single_download_is_manual_gated_and_cleans_raw_product():
    workflow, text = _load(SINGLE)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert workflow["jobs"]["download-test"]["needs"] == "preflight"
    assert "MONOREPO_NISAR_STORAGE_TESTS_ENABLED" in text
    assert '!= "true"' in text
    assert "earthaccess.download(" in text
    assert "shutil.rmtree(temp_dir)" in text
    assert "Cleanup verification failed safely." in text
    assert "NISAR_DOWNLOAD_CLEANUP_SUCCESS" in text
    assert "GOOGLE_DRIVE_PARENT_FOLDER_ID" not in text
    assert "drive_resumable_upload.py" not in text
    assert "actions/setup-python@v5" not in text


def test_multi_granule_storage_is_separately_gated_at_15_gb_and_cleans_raw_data():
    workflow, text = _load(MULTI)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert workflow["jobs"]["storage-test"]["needs"] == "preflight"
    assert "MONOREPO_NISAR_MULTI_GRANULE_STORAGE_TESTS_ENABLED" in text
    assert '!= "true"' in text
    assert "TARGET_BYTES = 15 * 1024 ** 3" in text
    assert "LOW_DISK_BYTES = 2 * 1024 ** 3" in text
    assert "MAX_GRANULES = 8" in text
    assert "earthaccess.download(" in text
    assert "shutil.rmtree(temp_dir)" in text
    assert "NISAR_MULTI_GRANULE_CLEANUP_SUCCESS" in text
    assert "GOOGLE_DRIVE_PARENT_FOLDER_ID" not in text
    assert "drive_resumable_upload.py" not in text
    assert "actions/setup-python@v5" not in text
