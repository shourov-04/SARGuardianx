from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "know-place-dem-source-acquisition.yml"


def test_dem_source_acquisition_is_manual_gated_and_hashes_all_16_tiles():
    text = WORKFLOW.read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "push" not in workflow.get("on", {})
    assert workflow["permissions"]["contents"] == "read"
    assert workflow["jobs"]["acquire-and-hash-dem"]["needs"] == "preflight"
    assert "MONOREPO_KNOWN_PLACE_DEM_ACQUISITION_ENABLED" in text
    assert '!= "true"' in text
    assert "range(27, 31)" in text
    assert "range(83, 87)" in text
    assert "EXPECTED_16_TILES_GOT" in text
    assert "hashlib.sha256()" in text
    assert "rasterio.open(path)" in text
    assert "EXPECTED_16_PROFILE_CHECKS_GOT" in text
    assert "UNVERIFIED_CURRENT_PUBLIC_MIRROR_COPY" in text
    assert "no vertical transformation" in text
    assert "raw_nisar_goff_downloaded" in text
    assert "HAZARD_DETECTION_STATUS=NOT_EVALUATED" in text
    assert "Copernicus DEM GLO-90 free-use terms apply" in text
    assert "secrets." not in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text
    assert "actions/upload-artifact@v4" not in text
