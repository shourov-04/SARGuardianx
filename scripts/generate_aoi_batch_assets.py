"""Generate the composite product action and bounded batch/recovery workflows."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT
RUNTIME = TARGET

SCIENCE_COMMIT = "006d4cd1485cf80e509eaf8717c12e9c6390ac09"
SCIENCE_ROOT = "migration/source-snapshots/nisar-pins/006d4cd"
ENGINE_ROOT = "engines/find-displacements"

ACTION_INPUTS = {
    "aoi_wkt": {"required": True},
    "product_id": {"required": True},
    "granule_name": {"required": True},
    "product_type": {"required": True},
    "maturity": {"required": True},
    "expected_source_bytes": {"required": True},
    "retention_profile": {"required": True},
    "execution_label": {"required": True},
    "job_id": {"required": False, "default": ""},
    "target_latitude": {"required": False, "default": ""},
    "target_longitude": {"required": False, "default": ""},
}


def expression(value: str) -> str:
    return "${{ " + value + " }}"


def generate_action() -> None:
    source = RUNTIME / ".github/workflows/sarguardian-aoi-product-worker.yml"
    document = yaml.safe_load(source.read_text(encoding="utf-8"))
    steps = document["jobs"]["process"]["steps"]
    start = next(index for index, step in enumerate(steps) if step.get("name") == "Download first-attempt evidence for retry identity checks")
    product_steps = []
    drive_job_id_injections = 0
    for source_step in steps[start:]:
        step = dict(source_step)
        # Composite action metadata does not accept the workflow-only timeout key.
        # The enclosing reusable job already has GitHub's 360-minute hard limit.
        step.pop("timeout-minutes", None)
        run = step.get("run")
        if isinstance(run, str):
            run = run.replace(
                "python engines/find-displacements/tools/drive_resumable_upload.py",
                "python apps/dynamic/tools/drive_resumable_upload.py",
            )
            inline_marker = '--version-tag "$DRIVE_VERSION_TAG" --files'
            inline_replacement = (
                '--version-tag "$DRIVE_VERSION_TAG" \\\n'
                '  --job-id "$DRIVE_JOB_ID" --files'
            )
            line_marker = '--version-tag "$DRIVE_VERSION_TAG" \\\n'
            line_replacement = line_marker + '  --job-id "$DRIVE_JOB_ID" \\\n'
            drive_job_id_injections += run.count(inline_marker) + run.count(line_marker)
            step["run"] = run.replace(line_marker, line_replacement).replace(
                inline_marker, inline_replacement
            )
        product_steps.append(step)
    if drive_job_id_injections != 3:
        raise RuntimeError(
            f"expected three Drive job-id injection points, got {drive_job_id_injections}"
        )
    init = {
        "name": "Initialize isolated product attempt",
        "shell": "bash",
        "env": {
            "ACTION_PRODUCT_ID": expression("inputs.product_id"),
            "ACTION_GRANULE_NAME": expression("inputs.granule_name"),
            "ACTION_PRODUCT_TYPE": expression("inputs.product_type"),
            "ACTION_MATURITY": expression("inputs.maturity"),
            "ACTION_EXPECTED_SOURCE_BYTES": expression("inputs.expected_source_bytes"),
            "ACTION_RETENTION_PROFILE": expression("inputs.retention_profile"),
            "ACTION_EXECUTION_LABEL": expression("inputs.execution_label"),
            "ACTION_JOB_ID": expression("inputs.job_id"),
            "ACTION_TARGET_LATITUDE": expression("inputs.target_latitude"),
            "ACTION_TARGET_LONGITUDE": expression("inputs.target_longitude"),
        },
        "run": """set -euo pipefail
if [[ ! "$ACTION_PRODUCT_ID" =~ ^(GUNW|GOFF)-[0-9]{3}$ ]]; then
  echo "ERROR=INVALID_BATCH_PRODUCT_ID" >&2
  exit 2
fi
product_root="$RUNNER_TEMP/sarguardian-stream/$ACTION_PRODUCT_ID"
prior_root="$RUNNER_TEMP/sarguardian-stream/prior-attempt/granule"
if [[ "$ACTION_EXECUTION_LABEL" != "initial" ]]; then
  case "$product_root" in "$RUNNER_TEMP"/sarguardian-stream/*) rm -rf -- "$product_root" ;; *) exit 2 ;; esac
  case "$prior_root" in "$RUNNER_TEMP"/sarguardian-stream/*) rm -rf -- "$prior_root" ;; *) exit 2 ;; esac
fi
{
  printf 'PRODUCT_ID=%s\n' "$ACTION_PRODUCT_ID"
  printf 'GRANULE_NAME=%s\n' "$ACTION_GRANULE_NAME"
  printf 'PRODUCT_TYPE=%s\n' "$ACTION_PRODUCT_TYPE"
  printf 'MATURITY=%s\n' "$ACTION_MATURITY"
  printf 'EXPECTED_SOURCE_BYTES=%s\n' "$ACTION_EXPECTED_SOURCE_BYTES"
  printf 'RETENTION_PROFILE=%s\n' "$ACTION_RETENTION_PROFILE"
  printf 'PRODUCT_EXECUTION_LABEL=%s\n' "$ACTION_EXECUTION_LABEL"
  printf 'DRIVE_JOB_ID=%s\n' "$ACTION_JOB_ID"
  printf 'TARGET_LATITUDE=%s\n' "$ACTION_TARGET_LATITUDE"
  printf 'TARGET_LONGITUDE=%s\n' "$ACTION_TARGET_LONGITUDE"
  printf 'DRIVE_VERSION_TAG=%s-%s-%s\n' "$GITHUB_RUN_ID" "$GITHUB_RUN_ATTEMPT" "$ACTION_EXECUTION_LABEL"
} >> "$GITHUB_ENV"
""",
    }
    action = {
        "name": "Process one SARGuardian AOI product",
        "description": "Run one isolated product attempt inside a balanced batch runner.",
        "inputs": ACTION_INPUTS,
        "runs": {"using": "composite", "steps": [init, *product_steps]},
    }
    destination = TARGET / ".github/actions/process-aoi-product/action.yml"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        "# Generated from sarguardian-aoi-product-worker.yml.\n"
        + yaml.safe_dump(action, sort_keys=False, width=160),
        encoding="utf-8",
        newline="\n",
    )


def workflow_inputs(batch_name: str, count_name: str) -> dict:
    return {
        batch_name: {"required": True, "type": "string"},
        count_name: {"required": True, "type": "number"},
        "aoi_wkt": {"required": True, "type": "string"},
        "orchestration_sha": {"required": True, "type": "string"},
        "retention_profile": {"required": True, "type": "string"},
        "job_id": {"required": False, "type": "string", "default": ""},
        "target_latitude": {"required": False, "type": "string", "default": ""},
        "target_longitude": {"required": False, "type": "string", "default": ""},
    }


def setup_steps() -> list[dict]:
    return [
        {"name": "Checkout orchestration code", "uses": "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1", "with": {"repository": expression("github.repository"), "ref": expression("inputs.orchestration_sha")}},
        {"name": "Verify orchestration revision", "shell": "bash", "run": "set -euo pipefail\ntest \"$(git rev-parse HEAD)\" = \"$AOI_ORCHESTRATION_SHA\"\n"},
        {"name": "Verify immutable NISAR source snapshot", "shell": "bash", "run": f"set -euo pipefail\ntest -s {SCIENCE_ROOT}/README.md\ntest -s {SCIENCE_ROOT}/requirements.txt\ntest -s {SCIENCE_ROOT}/src/gunw_reader.py\ntest -s {SCIENCE_ROOT}/src/goff_reader.py\ntest -s {SCIENCE_ROOT}/src/local_floor.py\necho \"SCIENCE_REVISION_VERIFIED=$SCIENCE_COMMIT\"\n"},
        {"name": "Set up Python", "uses": "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0", "with": {"python-version": "3.13", "check-latest": False}},
        {"name": "Install pinned science and retention dependencies once per runner", "shell": "bash", "run": f"set -euo pipefail\npython -m pip install --disable-pip-version-check --no-cache-dir --retries 5 --timeout 45 -r {SCIENCE_ROOT}/requirements.txt\npython -m pip install --disable-pip-version-check --no-cache-dir --retries 5 --timeout 45 -r {ENGINE_ROOT}/tools/requirements-retention.txt\n"},
    ]


def job_env() -> dict:
    return {
        "PYTHONUNBUFFERED": "1",
        "AOI_NAME": "custom",
        "SARGUARDIAN_AOI_WKT": expression("inputs.aoi_wkt"),
        "AOI_ORCHESTRATION_SHA": expression("inputs.orchestration_sha"),
        "AOI_ORCHESTRATION_BRANCH": "main",
        "SCIENCE_COMMIT": SCIENCE_COMMIT,
        "EARTHDATA_USERNAME": expression("secrets.EARTHDATA_USERNAME"),
        "EARTHDATA_PASSWORD": expression("secrets.EARTHDATA_PASSWORD"),
        "EARTHDATA_TOKEN": expression("secrets.EARTHDATA_TOKEN"),
        "GOOGLE_DRIVE_OAUTH_CLIENT_JSON": expression("secrets.GOOGLE_DRIVE_OAUTH_CLIENT_JSON"),
        "GOOGLE_DRIVE_REFRESH_TOKEN": expression("secrets.GOOGLE_DRIVE_REFRESH_TOKEN"),
        "GOOGLE_DRIVE_PARENT_FOLDER_ID": expression("secrets.GOOGLE_DRIVE_PARENT_FOLDER_ID || secrets.GOOGLE_DRIVE_FOLDER_ID"),
    }


def action_step(index: int, json_input: str, label: str, step_id: str, retry_if: str | None = None) -> dict:
    row = f"fromJSON(inputs.{json_input})[{index}]"
    condition = retry_if or f"{row}.present"
    return {
        "name": f"Product slot {index + 1:03d} - {label}",
        "id": step_id,
        "if": expression(condition),
        "continue-on-error": True,
        "uses": "./.github/actions/process-aoi-product",
        "with": {
            "aoi_wkt": expression("inputs.aoi_wkt"),
            "product_id": expression(f"{row}.id"),
            "granule_name": expression(f"{row}.granule_name"),
            "product_type": expression(f"{row}.product_type"),
            "maturity": expression(f"{row}.maturity"),
            "expected_source_bytes": expression(f"{row}.expected_source_bytes"),
            "retention_profile": expression("inputs.retention_profile"),
            "execution_label": label,
            "job_id": expression("inputs.job_id"),
            "target_latitude": expression("inputs.target_latitude"),
            "target_longitude": expression("inputs.target_longitude"),
        },
    }


def write_workflow(path: Path, name: str, inputs: dict, steps: list[dict], timeout: int) -> None:
    document = {
        "name": name,
        "on": {"workflow_call": {"inputs": inputs}},
        "jobs": {
            "process": {
                "name": name,
                "runs-on": "ubuntu-24.04",
                "timeout-minutes": timeout,
                "env": job_env(),
                "steps": [*setup_steps(), *steps],
            }
        },
    }
    path.write_text(
        "# Generated by generate_aoi_batch_assets.py.\n"
        + yaml.safe_dump(document, sort_keys=False, width=180),
        encoding="utf-8",
        newline="\n",
    )


def generate_workflows() -> None:
    primary_steps: list[dict] = []
    for index in range(20):
        first_id = f"slot_{index + 1:02d}_attempt_1"
        primary_steps.append(action_step(index, "batch_json", "initial", first_id))
        primary_steps.append(action_step(index, "batch_json", "primary-retry", f"slot_{index + 1:02d}_attempt_2", f"steps.{first_id}.outcome == 'failure'"))
    write_workflow(
        TARGET / ".github/workflows/sarguardian-aoi-batch-worker.yml",
        "SARGuardian primary AOI batch runner",
        workflow_inputs("batch_json", "product_count"),
        primary_steps,
        360,
    )


def normalize_dashboard_encoding() -> None:
    """Replace one legacy non-UTF-8 display label while preserving workflow text."""
    path = TARGET / ".github/workflows/sarguardian-aoi-wkt-dashboard.yml"
    lines = path.read_bytes().decode("utf-8", errors="replace").splitlines()
    for index, line in enumerate(lines):
        if line.startswith("    name: Process AOI product"):
            lines[index] = "    name: Primary runner ${{ matrix.batch_id }} (${{ matrix.product_count }} products)"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    recovery_steps = [action_step(index, "recovery_json", "recovery-final", f"recovery_{index + 1:03d}") for index in range(200)]
    write_workflow(
        TARGET / ".github/workflows/sarguardian-aoi-recovery-worker.yml",
        "SARGuardian final AOI recovery runner",
        workflow_inputs("recovery_json", "retry_count"),
        recovery_steps,
        360,
    )


if __name__ == "__main__":
    generate_action()
    generate_workflows()
    normalize_dashboard_encoding()
