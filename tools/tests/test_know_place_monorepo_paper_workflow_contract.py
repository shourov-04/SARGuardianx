from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / ".github" / "workflows" / "know-place-paper-reproduction-dispatcher.yml"
REPLAY = ROOT / ".github" / "workflows" / "know-place-author-exact-replay.yml"


def test_author_exact_dispatcher_calls_only_the_local_monorepo_reusable_workflow():
    text = DISPATCHER.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "uses: ./.github/workflows/know-place-author-exact-replay.yml" in text
    assert "moshiour0/SARGuardian-backend/.github/workflows" not in text
    assert "GOOGLE_DRIVE_PARENT_FOLDER_ID" in text
    assert "GOOGLE_DRIVE_FOLDER_ID" not in text


def test_author_exact_dispatcher_preserves_the_distinct_historical_code_pin():
    text = DISPATCHER.read_text(encoding="utf-8")
    assert 'backend_code_ref: "b825df798ea4cb9874aa10dd01174d2a8ef73cba"' in text
    assert "consent_marker: ${{ inputs.consent_marker }}" in text
    assert "bridge_authorized: false" in text


def test_author_exact_replay_is_manual_or_reusable_and_fail_closed():
    text = REPLAY.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "workflow_call:" in text
    assert "\n  push:" not in text
    assert "[run-know-place]" in text
    assert "RAW_DOWNLOAD_CONSENT=PASS" in text
    assert "steps.credentials.outputs.secrets_ready == 'true'" in text


def test_author_exact_replay_uses_only_monorepo_preserved_science_and_code_pins():
    text = REPLAY.read_text(encoding="utf-8")
    assert "Check out the Monorepo source snapshots" in text
    assert "migration/source-snapshots/backend-pins/b825df" in text
    assert "migration/source-snapshots/nisar-pins/10639a9" in text
    assert '--science-root "$SCIENCE_SOURCE_ROOT"' in text
    assert "repository: moshiour0/SARGuardian-backend" not in text
    assert "repository: moshiour0/SARGuardian" not in text
    assert text.count("working-directory: migration/source-snapshots/backend-pins/b825df") == 5
    assert '"$BACKEND_SOURCE_ROOT/tools/drive_resumable_upload.py"' in text


def test_author_exact_replay_binds_source_and_orchestrator_commits_separately():
    text = REPLAY.read_text(encoding="utf-8")
    assert 'EXPECTED_BACKEND_CODE_REF="b825df798ea4cb9874aa10dd01174d2a8ef73cba"' in text
    assert 'default: "b825df798ea4cb9874aa10dd01174d2a8ef73cba"' in text
    assert "BACKEND_CODE_REF:" in text
    assert 'data["repository_commit"] = backend_sha' in text
    assert 'data["orchestrator_commit"] = orchestrator_sha' in text
    assert "AUTHOR_EXACT_SOURCE_LINEAGE_VERIFICATION_FAILED" in text


def test_author_exact_replay_has_immutable_external_action_pins():
    text = REPLAY.read_text(encoding="utf-8")
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in text
    assert "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0" in text
    assert "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9" in text
    assert "@v4" not in text and "@v5" not in text
