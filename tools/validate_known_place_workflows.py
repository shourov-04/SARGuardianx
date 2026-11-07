#!/usr/bin/env python3
"""Validate the guarded, Monorepo-local Known Place workflow contract."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "engines/known-place/.github/workflows/know-place-aoi-analysis.yml"
CANDIDATE = ROOT / "migration/workflow-candidates/known-place/know-place-aoi-analysis.yml"
ANALYSIS = ROOT / ".github/workflows/know-place-aoi-analysis.yml"
DISPATCHER = ROOT / ".github/workflows/know-place-aoi-dispatcher.yml"
API = ROOT / "apps/api/app/known_place.py"

EXPECTED_API_INPUTS = {
    "request_id",
    "aoi_wkt",
    "scope_aoi_wkt",
    "start_date",
    "end_date",
    "hazard_mode",
    "analysis_mode",
    "polarization",
    "track",
    "direction",
    "coherence_neighbours",
    "allowed_release_ids",
    "reference_wkt",
    "candidate_context_json",
    "geometry_height_m",
    "execute_downloads",
    "consent_marker",
}
EXPECTED_SECRETS = {
    "EARTHDATA_TOKEN",
    "EARTHDATA_USERNAME",
    "EARTHDATA_PASSWORD",
    "GOOGLE_DRIVE_OAUTH_CLIENT_JSON",
    "GOOGLE_DRIVE_REFRESH_TOKEN",
    "GOOGLE_DRIVE_PARENT_FOLDER_ID",
}
CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"
MICROMAMBA_SHA = "f457c30a868e4760d3a6fcea5f25dc655b8edf39"
UPLOAD_SHA = "cf430e030ddbb5b0abf93d22962f4752f3646cd9"
RUNNER_BLOB = "9364b94d6629c67e44f007a0e2634824aa7e1f9f"
REQUIREMENTS_BLOB = "81b3d7724fb9f8c6721104b1327aed746f520848"


def read_yaml(path: Path) -> tuple[str, dict]:
    raw = path.read_text(encoding="utf-8")
    document = yaml.safe_load(raw)
    if not isinstance(document, dict):
        raise SystemExit(f"ERROR=KNOWN_PLACE_YAML_INVALID path={path.relative_to(ROOT)}")
    return raw, document


def event_map(document: dict) -> dict:
    # PyYAML's YAML 1.1 resolver can parse the key `on` as boolean True.
    events = document.get("on", document.get(True))
    if not isinstance(events, dict):
        raise SystemExit("ERROR=KNOWN_PLACE_WORKFLOW_TRIGGER_MISSING")
    return events


def gate_is_closed(job: dict, raw_workflow: str, label: str) -> None:
    if not isinstance(job, dict):
        raise SystemExit(f"ERROR={label}_PREFLIGHT_JOB_MISSING")
    steps = job.get("steps")
    if not isinstance(steps, list) or len(steps) != 1:
        raise SystemExit(f"ERROR={label}_PREFLIGHT_MUST_HAVE_ONE_STEP")
    step = steps[0]
    if not isinstance(step, dict) or "uses" in step:
        raise SystemExit(f"ERROR={label}_PREFLIGHT_MUST_NOT_USE_EXTERNAL_ACTIONS")
    env = step.get("env", {})
    if not isinstance(env, dict) or env.get("MONOREPO_KNOWN_PLACE_ENABLED") != "$" + "{{ vars.MONOREPO_KNOWN_PLACE_ACTIONS_ENABLED }}":
        raise SystemExit(f"ERROR={label}_PREFLIGHT_VARIABLE_MISSING")
    if env.get("EXECUTE_DOWNLOADS") != "$" + "{{ inputs.execute_downloads }}":
        raise SystemExit(f"ERROR={label}_PREFLIGHT_DOWNLOAD_MODE_MISSING")
    run = step.get("run", "")
    required_markers = (
        'if [[ "$EXECUTE_DOWNLOADS" == "true" ]]',
        '!= "true"',
        "exit 1",
        "RAW_SOURCE_DOWNLOADS=DISABLED",
        "DRIVE_UPLOAD=DISABLED",
    )
    if any(marker not in run for marker in required_markers):
        raise SystemExit(f"ERROR={label}_PREFLIGHT_DOES_NOT_SEPARATE_DRY_RUN_FROM_RAW_DOWNLOADS")
    if "secrets." in str(job):
        raise SystemExit(f"ERROR={label}_PREFLIGHT_MUST_NOT_RECEIVE_SECRETS")
    if "MONOREPO_KNOWN_PLACE_ACTIONS_ENABLED" not in raw_workflow:
        raise SystemExit(f"ERROR={label}_PREFLIGHT_VARIABLE_NOT_IN_WORKFLOW")


def find_step(steps: list, name: str) -> dict:
    matches = [step for step in steps if isinstance(step, dict) and step.get("name") == name]
    if len(matches) != 1:
        raise SystemExit(f"ERROR=KNOWN_PLACE_STEP_COUNT_CHANGED name={name} count={len(matches)}")
    return matches[0]


def main() -> int:
    source_text, _ = read_yaml(SOURCE)
    candidate_text, _ = read_yaml(CANDIDATE)
    if candidate_text != source_text:
        raise SystemExit("ERROR=KNOWN_PLACE_PR85_CANDIDATE_NOT_EXACT_SOURCE_COPY")

    analysis_text, analysis_doc = read_yaml(ANALYSIS)
    dispatcher_text, dispatcher_doc = read_yaml(DISPATCHER)
    analysis_events = event_map(analysis_doc)
    dispatcher_events = event_map(dispatcher_doc)
    if set(analysis_events) != {"workflow_call"}:
        raise SystemExit("ERROR=KNOWN_PLACE_ANALYSIS_MUST_BE_REUSABLE_ONLY")
    if set(dispatcher_events) != {"workflow_dispatch"}:
        raise SystemExit("ERROR=KNOWN_PLACE_DISPATCHER_MUST_BE_MANUAL_ONLY")

    call = analysis_events["workflow_call"]
    if not isinstance(call, dict):
        raise SystemExit("ERROR=KNOWN_PLACE_WORKFLOW_CALL_MISSING")
    call_inputs = call.get("inputs", {})
    if not isinstance(call_inputs, dict):
        raise SystemExit("ERROR=KNOWN_PLACE_WORKFLOW_CALL_INPUTS_MISSING")
    if set(call_inputs) != EXPECTED_API_INPUTS - {"request_id"}:
        raise SystemExit(f"ERROR=KNOWN_PLACE_CALL_INPUT_CONTRACT_CHANGED fields={sorted(call_inputs)}")
    if call_inputs["execute_downloads"].get("type") != "boolean" or call_inputs["execute_downloads"].get("default") is not False:
        raise SystemExit("ERROR=KNOWN_PLACE_DOWNLOADS_MUST_DEFAULT_FALSE")
    if call_inputs["consent_marker"].get("default") != "":
        raise SystemExit("ERROR=KNOWN_PLACE_CONSENT_MUST_DEFAULT_EMPTY")

    dispatcher_inputs = dispatcher_events["workflow_dispatch"].get("inputs", {})
    if set(dispatcher_inputs) != EXPECTED_API_INPUTS:
        raise SystemExit(f"ERROR=KNOWN_PLACE_API_INPUT_CONTRACT_CHANGED fields={sorted(dispatcher_inputs)}")
    if dispatcher_inputs["execute_downloads"].get("default") is not False:
        raise SystemExit("ERROR=KNOWN_PLACE_DISPATCH_DOWNLOADS_MUST_DEFAULT_FALSE")
    if dispatcher_inputs["consent_marker"].get("default") != "":
        raise SystemExit("ERROR=KNOWN_PLACE_DISPATCH_CONSENT_MUST_DEFAULT_EMPTY")

    api_text = API.read_text(encoding="utf-8")
    for field in EXPECTED_API_INPUTS:
        if f'"{field}"' not in api_text:
            raise SystemExit(f"ERROR=KNOWN_PLACE_API_FIELD_NOT_FOUND field={field}")

    run_name = dispatcher_doc.get("run-name", "")
    if "Known Place Analysis" not in run_name or ("$" + "{{ inputs.request_id }}") not in run_name:
        raise SystemExit("ERROR=KNOWN_PLACE_RUN_NAME_MUST_CORRELATE_REQUEST_ID")

    dispatcher_jobs = dispatcher_doc.get("jobs", {})
    if not isinstance(dispatcher_jobs, dict) or set(dispatcher_jobs) != {"known-place-preflight", "known-place-aoi-analysis"}:
        raise SystemExit("ERROR=KNOWN_PLACE_DISPATCHER_JOB_GRAPH_CHANGED")
    gate_is_closed(dispatcher_jobs["known-place-preflight"], dispatcher_text, "KNOWN_PLACE_DISPATCHER")
    dispatcher_analysis = dispatcher_jobs["known-place-aoi-analysis"]
    if dispatcher_analysis.get("needs") != "known-place-preflight":
        raise SystemExit("ERROR=KNOWN_PLACE_DISPATCHER_ANALYSIS_NOT_GATED")
    if dispatcher_analysis.get("uses") != "./.github/workflows/know-place-aoi-analysis.yml":
        raise SystemExit("ERROR=KNOWN_PLACE_DISPATCHER_MUST_CALL_LOCAL_REUSABLE_WORKFLOW")
    with_inputs = dispatcher_analysis.get("with", {})
    if set(with_inputs) != EXPECTED_API_INPUTS - {"request_id"}:
        raise SystemExit("ERROR=KNOWN_PLACE_DISPATCHER_INPUT_FORWARDING_CHANGED")
    for field, value in with_inputs.items():
        if value != "$" + "{{ inputs." + field + " }}":
            raise SystemExit(f"ERROR=KNOWN_PLACE_DISPATCHER_INPUT_NOT_FORWARDED field={field}")
    secret_map = dispatcher_analysis.get("secrets", {})
    if set(secret_map) != EXPECTED_SECRETS:
        raise SystemExit("ERROR=KNOWN_PLACE_DISPATCHER_SECRET_MAP_CHANGED")
    for secret in EXPECTED_SECRETS:
        if secret_map[secret] != "$" + "{{ secrets." + secret + " }}":
            raise SystemExit(f"ERROR=KNOWN_PLACE_DISPATCHER_SECRET_MAPPING_CHANGED secret={secret}")

    analysis_jobs = analysis_doc.get("jobs", {})
    if not isinstance(analysis_jobs, dict) or set(analysis_jobs) != {"preflight", "analyze-aoi"}:
        raise SystemExit("ERROR=KNOWN_PLACE_ANALYSIS_JOB_GRAPH_CHANGED")
    gate_is_closed(analysis_jobs["preflight"], analysis_text, "KNOWN_PLACE_ANALYSIS")
    analysis_job = analysis_jobs["analyze-aoi"]
    if analysis_job.get("needs") != "preflight":
        raise SystemExit("ERROR=KNOWN_PLACE_ANALYSIS_JOB_NOT_GATED")
    job_env = analysis_job.get("env", {})
    if any(key in job_env for key in EXPECTED_SECRETS):
        raise SystemExit("ERROR=KNOWN_PLACE_JOB_LEVEL_SECRETS_NOT_ALLOWED")
    if "engines/known-place/know-place-aoi-output" not in str(job_env.get("OUTPUT_ROOT", "")):
        raise SystemExit("ERROR=KNOWN_PLACE_OUTPUT_ROOT_NOT_MONOREPO_SCOPED")

    steps = analysis_job.get("steps", [])
    checkout = find_step(steps, "Checkout Monorepo at the exact caller commit")
    if checkout.get("uses") != f"actions/checkout@{CHECKOUT_SHA}" or checkout.get("with", {}).get("ref") != "$" + "{{ github.sha }}":
        raise SystemExit("ERROR=KNOWN_PLACE_CHECKOUT_NOT_PINNED_TO_CALLER_SHA")
    identity = find_step(steps, "Verify Monorepo and promoted Known Place engine identity")
    identity_run = identity.get("run", "")
    for marker in (RUNNER_BLOB, REQUIREMENTS_BLOB):
        if marker not in identity_run:
            raise SystemExit(f"ERROR=KNOWN_PLACE_ENGINE_BLOB_PIN_MISSING sha={marker}")
    setup = find_step(steps, "Set up pinned Python 3.13 runtime")
    if setup.get("uses") != f"mamba-org/setup-micromamba@{MICROMAMBA_SHA}":
        raise SystemExit("ERROR=KNOWN_PLACE_MICROMAMBA_ACTION_NOT_PINNED")
    if setup.get("with", {}).get("create-args") != "python=3.13 pip":
        raise SystemExit("ERROR=KNOWN_PLACE_PYTHON_RUNTIME_NOT_313")

    install = find_step(steps, "Install versioned Known Place runtime from the Monorepo engine")
    request = find_step(steps, "Write normalized request input without shell interpolation")
    catalog = find_step(steps, "Catalog-only dry run (no product downloads)")
    download = find_step(steps, "Download exact selected GOFF granules and compute measurements")
    drive = find_step(steps, "Upload and byte-verify the derived result bundle in central Drive")
    for step in (install, request, catalog, download, drive):
        if step.get("working-directory") != "engines/known-place":
            raise SystemExit(f"ERROR=KNOWN_PLACE_ENGINE_WORKING_DIRECTORY_CHANGED step={step.get('name')}")
    for step in (install, request, catalog, download, drive):
        if step.get("shell") != "micromamba-shell {0}":
            raise SystemExit(f"ERROR=KNOWN_PLACE_PYTHON_STEP_SHELL_CHANGED step={step.get('name')}")
    if catalog.get("env") or "secrets." in str(catalog):
        raise SystemExit("ERROR=KNOWN_PLACE_CATALOG_ONLY_STEP_MUST_BE_CREDENTIAL_FREE")
    if set(download.get("env", {})) != {"EARTHDATA_TOKEN", "EARTHDATA_USERNAME", "EARTHDATA_PASSWORD"}:
        raise SystemExit("ERROR=KNOWN_PLACE_EARTHDATA_SECRET_SCOPE_CHANGED")
    if set(drive.get("env", {})) != {"BUNDLE_FOLDER_NAME", "GOOGLE_DRIVE_OAUTH_CLIENT_JSON", "GOOGLE_DRIVE_REFRESH_TOKEN", "GOOGLE_DRIVE_PARENT_FOLDER_ID"}:
        raise SystemExit("ERROR=KNOWN_PLACE_DRIVE_SECRET_SCOPE_CHANGED")
    credential_preflight = find_step(steps, "Preflight all required credentials before any raw source download")
    if credential_preflight.get("if") != ("$" + "{{ inputs.execute_downloads }}"):
        raise SystemExit("ERROR=KNOWN_PLACE_CREDENTIAL_PREFLIGHT_NOT_DOWNLOAD_GATED")
    if "[run-know-place]" not in credential_preflight.get("run", ""):
        raise SystemExit("ERROR=KNOWN_PLACE_RAW_DOWNLOAD_CONSENT_MARKER_CHANGED")
    if not {"EARTHDATA_TOKEN", "EARTHDATA_USERNAME", "EARTHDATA_PASSWORD", "GOOGLE_DRIVE_OAUTH_CLIENT_JSON", "GOOGLE_DRIVE_REFRESH_TOKEN", "GOOGLE_DRIVE_PARENT_FOLDER_ID"}.issubset(credential_preflight.get("env", {})):
        raise SystemExit("ERROR=KNOWN_PLACE_CREDENTIAL_PREFLIGHT_SCOPE_INCOMPLETE")

    artifact = find_step(steps, "Preserve report, dashboard, maps and Drive receipt as workflow artifacts")
    if artifact.get("uses") != f"actions/upload-artifact@{UPLOAD_SHA}":
        raise SystemExit("ERROR=KNOWN_PLACE_ARTIFACT_ACTION_NOT_PINNED")
    artifact_path = artifact.get("with", {}).get("path", "")
    for required_path in (
        "engines/known-place/monorepo-engine-source.txt",
        "engines/known-place/know-place-request.json",
        "engines/known-place/know-place-aoi-output/**",
    ):
        if required_path not in artifact_path:
            raise SystemExit(f"ERROR=KNOWN_PLACE_ARTIFACT_PATH_MISSING path={required_path}")

    for raw, label in ((analysis_text, "ANALYSIS"), (dispatcher_text, "DISPATCHER")):
        if "moshiour0/SARGuardian-backend" in raw or "backend_science_ref" in raw or "BACKEND_SCIENCE_REF" in raw:
            raise SystemExit(f"ERROR=KNOWN_PLACE_{label}_STILL_CHECKS_OUT_BACKEND")
        if re.search(r"(?m)^\s*uses:\s+[^\s]+@v\d", raw):
            raise SystemExit(f"ERROR=KNOWN_PLACE_{label}_HAS_UNPINNED_TAG_ACTION")

    print("KNOWN_PLACE_PR85_SOURCE_CANDIDATE_EXACT_PASS")
    print("KNOWN_PLACE_API_INPUT_CONTRACT_PASS")
    print("KNOWN_PLACE_REQUEST_ID_STATUS_CORRELATION_PASS")
    print("KNOWN_PLACE_MONOREPO_ENGINE_BLOB_PINS_PASS")
    print("KNOWN_PLACE_LOCAL_REUSABLE_WORKFLOW_PASS")
    print("KNOWN_PLACE_EXPLICIT_OPT_IN_GATES_PASS")
    print("KNOWN_PLACE_EXPLICIT_DOWNLOAD_CONSENT_PASS")
    print("KNOWN_PLACE_CREDENTIAL_SCOPE_PASS")
    print("KNOWN_PLACE_PINNED_ACTIONS_AND_ARTIFACT_PATHS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
