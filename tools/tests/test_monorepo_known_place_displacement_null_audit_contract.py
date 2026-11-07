from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "know-place-displacement-null-audit.yml"
ENGINE = ROOT / "engines" / "known-place" / "tools" / "know_place" / "displacement_null_archive_reconstruction.py"


def test_displacement_null_audit_is_manual_gated_hash_checked_and_caveated():
    text = WORKFLOW.read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "push" not in workflow.get("on", {})
    assert workflow["permissions"]["contents"] == "read"
    assert workflow["jobs"]["reproduce-published-table"]["needs"] == "preflight"
    assert workflow["jobs"]["reproduce-published-table"]["defaults"]["run"]["working-directory"] == "engines/known-place"
    assert "MONOREPO_KNOWN_PLACE_DISPLACEMENT_NULL_AUDIT_ENABLED" in text
    assert '!= "true"' in text
    assert "https://zenodo.org/api/records/22730419" in text
    assert "bhotekoshi2026_nisar_data-and-code_CC-BY-4.0.zip" in text
    assert "183389034" in text
    assert "002c2ba173a03693431b79578ca28d6b11e1ec00423d7533e82198871576c5e3" in text
    assert "python -m tools.know_place.displacement_null_archive_reconstruction" in text
    assert "NOT_PRESENT_IN_REVIEWED_ZENODO_ARCHIVE" in text
    assert "ORIGINAL_GENERATOR_AND_DRAW_SEQUENCE_IDENTITY=UNVERIFIED" in text
    assert "HAZARD_DETECTION_STATUS=NOT_EVALUATED" in text
    assert "RAW_HDF5_READ_OR_DOWNLOADED=NO" in text
    assert "secrets." not in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text
    assert "actions/upload-artifact@v4" not in text
    assert ENGINE.is_file()
