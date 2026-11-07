from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
GCOV = ROOT / ".github" / "workflows" / "nisar-discovery-test.yml"
GUNW = ROOT / ".github" / "workflows" / "nisar-gunw-earthaccess-discovery-test.yml"


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    return yaml.load(text, Loader=yaml.BaseLoader), text


def test_gcov_discovery_is_manual_gated_and_catalogue_only():
    workflow, text = load(GCOV)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "MONOREPO_NISAR_DIAGNOSTICS_ENABLED" in text
    assert '!= "true"' in text
    assert 'short_name="NISAR_L2_GCOV_PROVISIONAL_V1"' in text
    assert "earthaccess.login(strategy=" in text
    assert "earthaccess.search_data(" in text
    assert "earthaccess.download" not in text
    assert "download_nisar_product.py" not in text
    assert "drive_resumable_upload.py" not in text
    assert "GOOGLE_DRIVE_PARENT_FOLDER_ID" not in text


def test_gunw_discovery_uses_exact_legacy_pin_without_download():
    workflow, text = load(GUNW)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "MONOREPO_NISAR_DIAGNOSTICS_ENABLED" in text
    assert '!= "true"' in text
    assert "77cc9646cfa46d3aff3669d351912f984cf67aa3" in text
    assert 'git -C "$GITHUB_WORKSPACE" archive "$SCIENCE_COMMIT"' in text
    assert 'git -C "$GITHUB_WORKSPACE" cat-file -e "$SCIENCE_COMMIT^{commit}"' in text
    assert 'gunw_reader.AOIS["source"]' in text
    assert 'short_name="NISAR_L2_GUNW_PROVISIONAL_V1"' in text
    assert "earthaccess.search_data(" in text
    assert "earthaccess.download" not in text
    assert "repository: Sagormodak/SARGuardian" not in text
    assert "repository: moshiour0/SARGuardian" not in text
    assert "repository: moshiour0/SARGuardian-backend" not in text
    assert "GOOGLE_DRIVE_PARENT_FOLDER_ID" not in text
