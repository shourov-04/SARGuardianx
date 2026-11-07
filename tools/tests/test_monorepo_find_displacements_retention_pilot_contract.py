from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "find-displacements-retention-pilot.yml"


def test_retention_pilot_is_manual_gated_pinned_and_non_destructive():
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "push" not in workflow.get("on", {})
    assert "MONOREPO_DISPLACEMENT_RETENTION_PILOT_ENABLED" in text
    assert '!= "true"' in text
    assert workflow["jobs"]["retain-one-granule"]["needs"] == "preflight"
    assert "ab547ecc82bcc4d6ccef545a59852536c2beacc6" in text
    assert 'git -C "$GITHUB_WORKSPACE" archive' in text
    assert "repository: moshiour0/SARGuardian" not in text
    assert "sarguardian-backend-api.vercel.app" not in text

    assert "EARTHDATA_USERNAME" in text
    assert "EARTHDATA_PASSWORD" in text
    assert "EARTHDATA_TOKEN" in text
    assert "GOOGLE_DRIVE_OAUTH_CLIENT_JSON" in text
    assert "GOOGLE_DRIVE_REFRESH_TOKEN" in text
    assert "GOOGLE_DRIVE_PARENT_FOLDER_ID" in text
    assert "download_nisar_product.py" in text
    assert "validate_product_aoi.py" in text
    assert "sarguardian_hdf5_archive.py" in text
    assert "verify_reader_equivalence.py" in text
    assert "drive_resumable_upload.py" in text
    assert "AUTOMATIC_RAW_DELETION=DISABLED" in text
    assert "rm -f" not in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text
    assert "actions/upload-artifact@v4" not in text
