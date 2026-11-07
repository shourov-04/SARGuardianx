from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "know-place-generic-map-browser-smoke.yml"


def test_generic_map_browser_smoke_is_manual_and_synthetic_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "push" not in workflow.get("on", {})
    assert workflow["permissions"]["contents"] == "read"
    job = workflow["jobs"]["generic-aoi-synthetic-browser"]
    assert job["defaults"]["run"]["working-directory"] == "engines/known-place"
    assert job["runs-on"] == "ubuntu-24.04"
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in text
    assert "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1" in text
    assert "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9" in text
    assert "playwright@1.56.1" in text
    assert "tools/tests/fixtures/generic_aoi_map_report.json" in text
    assert "from tools.know_place.interactive_map import write_interactive_map" in text
    assert "GENERIC_AOI_FIXTURE_ONLY=PASS" in text
    assert "measurement_claim" in text
    assert "NOT_EVALUATED" in text
    assert "raw_hdf5_read_or_downloaded:false" in text
    assert "RAW_HDF5_MEMBERS=0" in text
    assert "engines/known-place/artifacts/generic-aoi-browser/**" in text
    assert "GOOGLE_DRIVE" not in text
    assert "EARTHDATA" not in text
    assert "secrets." not in text
    assert "repository: " not in text
