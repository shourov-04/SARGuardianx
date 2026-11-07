from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
READ = ROOT / ".github" / "workflows" / "nisar-gunw-earthaccess-read-test.yml"
SCIENCE = ROOT / ".github" / "workflows" / "nisar-gunw-science-test.yml"


def _load(path: Path):
    text = path.read_text(encoding="utf-8")
    return yaml.load(text, Loader=yaml.BaseLoader), text


def _validate(path: Path, job_name: str, required_marker: str, cleanup_failure_marker: str):
    workflow, text = _load(path)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert workflow["permissions"]["contents"] == "read"
    assert workflow["jobs"][job_name]["needs"] == "preflight"
    assert "MONOREPO_NISAR_PRODUCT_TESTS_ENABLED" in text
    assert '!= "true"' in text
    assert "77cc9646cfa46d3aff3669d351912f984cf67aa3" in text
    assert "os.environ.get(\"SCIENCE_COMMIT\", \"\")" in text
    assert "rev-parse" not in text
    assert 'git -C "$GITHUB_WORKSPACE" cat-file -e "$SCIENCE_COMMIT^{commit}"' in text
    assert 'git -C "$GITHUB_WORKSPACE" archive "$SCIENCE_COMMIT"' in text
    assert "repository: Sagormodak/SARGuardian" not in text
    assert "repository: moshiour0/SARGuardian" not in text
    assert "repository: moshiour0/SARGuardian-backend" not in text
    assert "secrets.EARTHDATA_USERNAME" in text
    assert "secrets.EARTHDATA_PASSWORD" in text
    assert required_marker in text
    assert "NISAR_GUNW_RAW_CLEANUP_SUCCESS" in text
    assert cleanup_failure_marker in text
    assert "drive_resumable_upload.py" not in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text


def test_gunw_earthaccess_read_test_is_gated_and_exact_pin():
    _validate(READ, "read-gunw", "earthaccess.download(", "NISAR_GUNW_EARTHACCESS_RAW_CLEANUP_FAILED")


def test_gunw_science_feasibility_test_is_gated_and_exact_pin():
    _validate(SCIENCE, "gunw-science-test", "asf_search.download_url(", "NISAR_GUNW_RAW_CLEANUP_FAILED")
