from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / ".github" / "workflows" / "earthdata-auth-test.yml"
TOKEN = ROOT / ".github" / "workflows" / "earthdata-token-smoke-test.yml"


def _load(path: Path):
    text = path.read_text(encoding="utf-8")
    return yaml.load(text, Loader=yaml.BaseLoader), text


def test_earthdata_username_password_auth_diagnostic_is_manual_and_no_download():
    workflow, text = _load(AUTH)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "MONOREPO_EARTHDATA_DIAGNOSTICS_ENABLED" in text
    assert '!= "true"' in text
    assert "secrets.EARTHDATA_USERNAME" in text
    assert "secrets.EARTHDATA_PASSWORD" in text
    assert "EARTHDATA_TOKEN" not in text
    assert "download_nisar_product.py" not in text
    assert "drive_resumable_upload.py" not in text
    assert "Catalogue search: not performed" in text


def test_earthdata_token_probe_diagnostic_is_local_and_no_download():
    workflow, text = _load(TOKEN)
    assert set(workflow.get("on", {})) == {"workflow_dispatch"}
    assert "MONOREPO_EARTHDATA_DIAGNOSTICS_ENABLED" in text
    assert '!= "true"' in text
    assert "secrets.EARTHDATA_TOKEN" in text
    assert "ab547ecc82bcc4d6ccef545a59852536c2beacc6" in text
    assert 'git -C "$GITHUB_WORKSPACE" archive' in text
    assert "repository: moshiour0/SARGuardian" not in text
    assert "repository: moshiour0/SARGuardian-backend" not in text
    assert "--probe-only" in text
    assert "RAW_DOWNLOAD_PERFORMED=no" in text
    assert "drive_resumable_upload.py" not in text
    assert "GOOGLE_DRIVE_PARENT_FOLDER_ID" not in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text
