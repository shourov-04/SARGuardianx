#!/usr/bin/env python3
"""Fail-closed structural contract checks for the Monorepo live-retention port."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "sarguardian-live-validation.yml"
EXPECTED_SCIENCE_COMMIT = "ab547ecc82bcc4d6ccef545a59852536c2beacc6"
EXPECTED_TOOL_BLOBS = {
    "download_nisar_product.py": "307d84c874d480b76a77070abae9390a7b6546b6",
    "drive_resumable_upload.py": "84a6b32c39d456644fe6af1a6d803b26de12b27b",
    "validate_product_aoi.py": "97b9be365df3a5876f8a2499a955f340782a3f15",
    "sarguardian_hdf5_archive.py": "d056aa86c3341eed92a6f39b515d418d610efc00",
    "verify_reader_equivalence.py": "56fc6b98b4b3cdb83225ae6239cfbf008c17d26a",
    "aggregate_streamed_outputs.py": "6211b0565323ff4d044658162654ce629ab2b29b",
    "time_window.py": "e8473d0ed03aeba9ba53679d8648df60723e6d46",
    "requirements-retention.txt": "f86daa08bb8ea461b9746260df8e025b83f553bf",
}

EXPECTED_GRANULES = {
    ("GUNW", "NISAR_L2_PR_GUNW_026_048_D_074_028_4000_SH_20260723T125813_20260723T125848_20260816T125812_20260816T125846_P05023_N_F_J_001"),
    ("GOFF", "NISAR_L2_PR_GOFF_026_048_D_074_028_4000_SH_20260723T125813_20260723T125848_20260816T125812_20260816T125846_P05023_N_F_J_001"),
}


def fail(message: str) -> None:
    print(f"LIVE_RETENTION_WORKFLOW_ERROR={message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not WORKFLOW.is_file():
        fail(f"missing workflow: {WORKFLOW}")

    raw = WORKFLOW.read_text(encoding="utf-8")
    try:
        workflow = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        fail(f"invalid YAML: {exc}")

    if not isinstance(workflow, dict):
        fail("workflow YAML root must be a mapping")
    events = workflow.get("on", workflow.get(True))
    if not isinstance(events, dict) or set(events) != {"workflow_dispatch"}:
        fail("live retention must remain workflow_dispatch-only")
    dispatch = events.get("workflow_dispatch")
    inputs = dispatch.get("inputs") if isinstance(dispatch, dict) else {}
    consent = inputs.get("confirm_live_retention") if isinstance(inputs, dict) else None
    if not isinstance(consent, dict) or consent.get("required") is not True or consent.get("type") != "boolean":
        fail("required boolean confirm_live_retention input is missing")

    permissions = workflow.get("permissions")
    if permissions != {"contents": "read"}:
        fail(f"unexpected token permissions: {permissions}")

    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict) or set(jobs) != {"preflight", "validate-retention"}:
        fail("expected only preflight and validate-retention jobs")
    preflight = jobs["preflight"]
    if not isinstance(preflight, dict) or not isinstance(preflight.get("steps"), list):
        fail("credential-free preflight steps are missing")
    preflight_steps = preflight["steps"]
    preflight_runs = "\n".join(
        step.get("run", "")
        for step in preflight_steps
        if isinstance(step, dict) and isinstance(step.get("run", ""), str)
    )
    preflight_env = json.dumps(preflight_steps, sort_keys=True)
    if "MONOREPO_SARGUARDIAN_LIVE_VALIDATION_ENABLED" not in preflight_env:
        fail("repository opt-in gate is missing")
    if "inputs.confirm_live_retention" not in preflight_env or "secrets." in preflight_env:
        fail("per-run consent must be checked before the processing job receives secrets")
    if preflight_runs.count('!= "true"') < 2:
        fail("both repository opt-in and per-run consent must fail closed unless literally true")

    processing = jobs["validate-retention"]
    if processing.get("needs") != "preflight":
        fail("processing must depend on successful credential-free preflight")
    strategy = processing.get("strategy", {})
    if strategy.get("fail-fast") is not False or strategy.get("max-parallel") != 1:
        fail("GUNW and GOFF retention jobs must run sequentially without matrix fail-fast")
    matrix = strategy.get("matrix", {}).get("include")
    observed = {
        (row.get("product_type"), row.get("granule_name"))
        for row in matrix or []
        if isinstance(row, dict)
    }
    if observed != EXPECTED_GRANULES:
        fail("fixed P05023 GUNW/GOFF products changed without a reviewed source update")

    encoded = json.dumps(processing, sort_keys=True)
    if EXPECTED_SCIENCE_COMMIT not in encoded:
        fail("exact ab547 science pin is missing")
    checkout_steps = [
        step for step in processing.get("steps", [])
        if isinstance(step, dict) and str(step.get("uses", "")).startswith("actions/checkout@")
    ]
    if not any(step.get("with", {}).get("fetch-depth") == 0 for step in checkout_steps):
        fail("the root checkout must fetch full Git history before materializing the historical science commit")
    if "git worktree add --detach" not in encoded:
        fail("historical source must be materialized from the Monorepo's full Git history")
    if "engines/find-displacements/tools" not in encoded:
        fail("retention worker must use the promoted Monorepo tool package")

    source_tools = ROOT / "migration" / "source-snapshots" / "backend-main" / "tools"
    promoted_tools = ROOT / "engines" / "find-displacements" / "tools"
    for name, expected_blob in EXPECTED_TOOL_BLOBS.items():
        source_path = source_tools / name
        promoted_path = promoted_tools / name
        if not source_path.is_file() or not promoted_path.is_file():
            fail(f"retention tool source/promoted path is missing: {name}")
        for label, path in (("source", source_path), ("promoted", promoted_path)):
            data = path.read_bytes()
            actual_blob = hashlib.sha1(
                b"blob " + str(len(data)).encode("ascii") + bytes([0]) + data
            ).hexdigest()
            if actual_blob != expected_blob:
                fail(f"{label} retention tool Git blob changed: {name}; expected {expected_blob}, got {actual_blob}")

    history_check = subprocess.run(
        ["git", "cat-file", "-e", f"{EXPECTED_SCIENCE_COMMIT}^{{commit}}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if history_check.returncode != 0:
        fail(f"exact pinned science commit is unavailable in Monorepo Git history: {EXPECTED_SCIENCE_COMMIT}")
    if "DRIVE_ARCHIVE_VERIFICATION=PASS" not in encoded:
        fail("remote Drive archive receipt verification is missing")
    if "AUTOMATIC_RAW_DELETION=DISABLED" not in encoded:
        fail("non-destructive raw-retention boundary is missing")
    if "RENDER_CALLBACK_URL" in raw or "WORKER_CALLBACK_SECRET" in raw:
        fail("legacy callback secrets do not belong in this independent retention workflow")

    uses = re.findall(r"uses:\s*([^\s]+)", raw)
    for reference in uses:
        if "@" not in reference or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}", reference):
            fail(f"third-party action is not pinned to a full commit SHA: {reference}")
    if re.search(r"repository:\s*moshiour0/SARGuardian|repository:\s*Sagormodak/SARGuardian", raw):
        fail("workflow must not check out an external science repository")

    print(
        "LIVE_RETENTION_WORKFLOW_CONTRACT=PASS "
        "products=GUNW,GOFF "
        f"science_commit={EXPECTED_SCIENCE_COMMIT} "
        "manual_only=true repository_gate=true per_run_consent=true "
        "drive_receipts=true automatic_raw_deletion=false "
        f"exact_tool_blobs={len(EXPECTED_TOOL_BLOBS)}/{len(EXPECTED_TOOL_BLOBS)} "
        "historical_git_object=PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
