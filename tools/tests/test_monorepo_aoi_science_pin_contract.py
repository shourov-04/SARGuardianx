"""Regression checks for the active reusable AOI workflow's science revision binding."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
ENGINE_WORKFLOW = ROOT / ".github" / "workflows" / "sarguardian-aoi-dashboard-engine.yml"
PRODUCT_WORKER = ROOT / ".github" / "workflows" / "sarguardian-aoi-product-worker.yml"
DISCOVERY_TOOL = ROOT / "engines" / "find-displacements" / "tools" / "discover_aoi_products.py"
SCIENCE_ROOT = ROOT / "migration" / "source-snapshots" / "nisar-pins" / "006d4cd"
EXPECTED_SCIENCE_COMMIT = "006d4cd1485cf80e509eaf8717c12e9c6390ac09"


def test_reusable_workflow_exports_one_immutable_science_pin_to_all_jobs() -> None:
    workflow = yaml.load(ENGINE_WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    assert workflow["env"]["SCIENCE_COMMIT"] == EXPECTED_SCIENCE_COMMIT
    assert (SCIENCE_ROOT / "README.md").is_file()
    assert (SCIENCE_ROOT / "requirements.txt").is_file()

    workflow_text = ENGINE_WORKFLOW.read_text(encoding="utf-8")
    assert workflow_text.count('echo "SCIENCE_REVISION_VERIFIED=$SCIENCE_COMMIT"') == 2
    assert workflow_text.count("SCIENCE_REVISION_STORAGE=IMMUTABLE_MONOREPO_SNAPSHOT") == 2


def test_reusable_workflow_pin_matches_worker_and_discovery_tool_pins() -> None:
    worker = PRODUCT_WORKER.read_text(encoding="utf-8")
    discovery = DISCOVERY_TOOL.read_text(encoding="utf-8")

    assert f"SCIENCE_COMMIT: {EXPECTED_SCIENCE_COMMIT}" in worker
    assert f'SCIENCE_COMMIT = "{EXPECTED_SCIENCE_COMMIT}"' in discovery



def test_discovery_and_dashboard_use_separate_pinned_git_checkout_for_provenance() -> None:
    workflow = yaml.load(ENGINE_WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    text = ENGINE_WORKFLOW.read_text(encoding="utf-8")

    manifest_steps = workflow["jobs"]["manifest"]["steps"]
    dashboard_steps = workflow["jobs"]["dashboard"]["steps"]

    def pinned_checkout(steps: list[dict]) -> dict:
        matches = [
            step for step in steps
            if step.get("uses", "").startswith("actions/checkout@")
            and step.get("with", {}).get("repository") == "moshiour0/SARGuardian"
        ]
        assert len(matches) == 1
        checkout = matches[0]["with"]
        assert checkout["ref"] == EXPECTED_SCIENCE_COMMIT
        assert checkout["path"] == "science-source"
        assert checkout["persist-credentials"] == "false"
        return matches[0]

    pinned_checkout(manifest_steps)
    pinned_checkout(dashboard_steps)

    assert text.count("git -C science-source rev-parse HEAD") == 2
    assert text.count('echo "SCIENCE_GIT_CHECKOUT_VERIFIED=$actual"') == 2
    assert text.count('--science-root "$PWD/science-source"') == 2
    assert text.count("-r science-source/requirements.txt") == 2
    assert 'science_root = "$GITHUB_WORKSPACE/migration/source-snapshots/nisar-pins/006d4cd"' not in text
