from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / ".github" / "workflows" / "sarguardian-aoi-dashboard-engine.yml"
WORKER = ROOT / ".github" / "workflows" / "sarguardian-aoi-product-worker.yml"
PIN = "migration/source-snapshots/nisar-pins/006d4cd"
SCIENCE_COMMIT = "006d4cd1485cf80e509eaf8717c12e9c6390ac09"


def test_find_displacements_callback_uses_the_promoted_monorepo_api_adapter():
    text = ENGINE.read_text(encoding="utf-8")
    assert '"$GITHUB_WORKSPACE/apps/api"' in text
    assert "science_adapter.dynamic_callback" in text
    assert "dynamic-api/Backend" not in text
    assert "db6472e1c304e21242f1ab1dfd671ccb21ba5697" not in text


def test_find_displacements_engine_preserves_snapshot_and_pins_git_provenance_source():
    text = ENGINE.read_text(encoding="utf-8")
    assert f"{PIN}/requirements.txt" in text
    assert f"{PIN}/README.md" in text
    assert f"$GITHUB_WORKSPACE/{PIN}" in text
    # The source snapshot remains the immutable worker input and is verified
    # by the migration snapshot contract. Git-based diagnostics require a
    # real checkout, not a nested directory inside the Monorepo's .git tree.
    assert text.count("repository: moshiour0/SARGuardian\n") == 2
    assert text.count(f"ref: {SCIENCE_COMMIT}") == 2
    assert text.count("path: science-source") == 2
    assert text.count('--science-root "$PWD/science-source"') == 2
    assert text.count("git -C science-source rev-parse HEAD") == 2


def test_find_displacements_product_worker_has_no_external_science_checkout():
    text = WORKER.read_text(encoding="utf-8")
    assert f"{PIN}/requirements.txt" in text
    assert f"$GITHUB_WORKSPACE/{PIN}" in text
    for module in ("gunw_reader.py", "goff_reader.py", "local_floor.py"):
        assert f'python "$GITHUB_WORKSPACE/{PIN}/src/{module}"' in text
    assert "science-source" not in text
    assert f"ref: {SCIENCE_COMMIT}" not in text
    assert "path: science-source" not in text
    assert "GOOGLE_DRIVE_PARENT_FOLDER_ID" in text
    assert "GOOGLE_DRIVE_FOLDER_ID" not in text


def test_find_displacements_engine_and_worker_are_local_root_workflows():
    engine = ENGINE.read_text(encoding="utf-8")
    worker = WORKER.read_text(encoding="utf-8")
    assert "uses: ./.github/workflows/sarguardian-aoi-product-worker.yml" in engine
    assert "actions/checkout@" in engine and "actions/checkout@" in worker
    assert "GOOGLE_DRIVE_PARENT_FOLDER_ID" in engine
    assert "GOOGLE_DRIVE_PARENT_FOLDER_ID" in worker
    assert "GOOGLE_DRIVE_FOLDER_ID" not in engine + worker
