from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "dashboard-assets-test.yml"


def test_dashboard_asset_builder_workflow_is_offline_and_snapshot_scoped():
    text = WORKFLOW.read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    triggers = workflow.get("on", {})
    assert set(triggers) == {"workflow_dispatch", "pull_request"}
    assert "push" not in triggers

    paths = triggers["pull_request"]["paths"]
    assert "migration/source-snapshots/backend-main/dashboard/**" in paths
    assert "migration/source-snapshots/backend-main/tools/aggregate_aoi_run.py" in paths

    job = workflow["jobs"]["dashboard-assets"]
    assert job["runs-on"] == "ubuntu-24.04"
    assert job["defaults"]["run"]["working-directory"] == "migration/source-snapshots/backend-main"

    assert "dashboard/assets/prepare_web_assets.py" in text
    assert "dashboard.tests.test_prepare_web_assets" in text
    assert "node --check" in text
    assert "DASHBOARD_WORKFLOW_YAML_PASS" in text
    assert "GOOGLE_DRIVE" not in text
    assert "EARTHDATA" not in text
    assert "repository: " not in text
    assert "actions/checkout@v4" not in text
    assert "actions/setup-python@v5" not in text
