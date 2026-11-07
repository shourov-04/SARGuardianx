#!/usr/bin/env python3
"""Fail-closed contract check between the Known Place API and Monorepo workflows."""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
API_PATH = ROOT / "apps" / "api" / "app" / "known_place.py"
DISPATCHER_PATH = ROOT / ".github" / "workflows" / "know-place-aoi-dispatcher.yml"
REUSABLE_PATH = ROOT / ".github" / "workflows" / "know-place-aoi-analysis.yml"
UPLOAD_ARTIFACT_SHA = "cf430e030ddbb5b0abf93d22962f4752f3646cd9"


def fail(message: str) -> None:
    raise RuntimeError(message)


def expression(value: str) -> str:
    return "$" + "{{ " + value + " }}"


def read_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    except (OSError, yaml.YAMLError) as exc:
        fail(f"Cannot parse {path.relative_to(ROOT)}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a YAML mapping.")
    return value


def mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be a mapping.")
    return value


def api_dispatch_input_names() -> set[str]:
    try:
        tree = ast.parse(API_PATH.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        fail(f"Cannot parse the API Known Place adapter: {exc}")

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != "dispatch_known_place_analysis":
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.Assign):
                continue
            if not any(isinstance(target, ast.Name) and target.id == "inputs" for target in child.targets):
                continue
            if not isinstance(child.value, ast.Dict):
                fail("Known Place API dispatch input payload must remain a literal dictionary.")
            names: set[str] = set()
            for key in child.value.keys:
                if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                    fail("Known Place API dispatch inputs must use literal string keys.")
                names.add(key.value)
            return names
    fail("Could not find the Known Place API dispatch input dictionary.")
    return set()


def validate_author_exact_reproduction_gate() -> None:
    """Require a repository-level opt-in and exact consent before P05023 raw acquisition."""
    worker_path = ROOT / ".github" / "workflows" / "know-place-author-exact-replay.yml"
    paper_dispatcher_path = ROOT / ".github" / "workflows" / "know-place-paper-reproduction-dispatcher.yml"
    worker = read_yaml(worker_path)
    dispatcher = read_yaml(paper_dispatcher_path)

    events = mapping(worker.get("on"), "author-exact worker events")
    if set(events) != {"workflow_dispatch", "workflow_call"}:
        fail("Author-exact worker must remain manual/reusable only.")
    dispatch = mapping(events["workflow_dispatch"], "author-exact workflow_dispatch")
    call = mapping(events["workflow_call"], "author-exact workflow_call")
    if "consent_marker" not in mapping(dispatch.get("inputs"), "author-exact dispatch inputs"):
        fail("Author-exact manual entry point must require the consent marker input.")
    if "consent_marker" not in mapping(call.get("inputs"), "author-exact call inputs"):
        fail("Author-exact reusable call must accept the consent marker.")

    jobs = mapping(worker.get("jobs"), "author-exact worker jobs")
    if set(jobs) != {"trigger-gate", "acquire-analyze-retain"}:
        fail("Author-exact worker job graph changed.")
    gate = mapping(jobs["trigger-gate"], "author-exact trigger gate")
    steps = gate.get("steps")
    if not isinstance(steps, list) or len(steps) != 1:
        fail("Author-exact trigger gate must have one credential-free step.")
    step = mapping(steps[0], "author-exact trigger gate step")
    if "uses" in step or "secrets." in str(gate):
        fail("Author-exact trigger gate must not use external actions or receive secrets.")
    env = mapping(step.get("env"), "author-exact trigger gate env")
    if env.get("PAPER_REPRODUCTION_ENABLED") != expression("vars.MONOREPO_KNOWN_PLACE_PAPER_REPRODUCTION_ENABLED"):
        fail("Author-exact worker must read its own repository-level opt-in Variable.")
    if env.get("MANUAL_CONSENT_MARKER") != expression("inputs.consent_marker || ''"):
        fail("Author-exact worker must inspect the explicit consent marker.")
    run = str(step.get("run", ""))
    for marker in (
        'if [[ "$PAPER_REPRODUCTION_ENABLED" != "true" ]]',
        'if [[ "$MANUAL_CONSENT_MARKER" != "[run-know-place]" ]]',
        "exit 1",
        'echo "RAW_SOURCE_DOWNLOADS=0"',
    ):
        if marker not in run:
            fail(f"Author-exact preflight is missing fail-closed marker: {marker}")

    processing = mapping(jobs["acquire-analyze-retain"], "author-exact processing job")
    if processing.get("needs") != "trigger-gate":
        fail("Author-exact acquisition must depend on the repository/consent gate.")
    processing_condition = str(processing.get("if", "")).strip()
    expected_condition = "needs.trigger-gate.outputs.run_author_exact == 'true'"
    if processing_condition not in {expected_condition, expression(expected_condition)}:
        fail("Author-exact acquisition must require successful gate output.")
    if not mapping(processing.get("env"), "author-exact processing env").get("EARTHDATA_TOKEN"):
        fail("Author-exact worker must keep Earthdata credentials in the gated processing job.")

    dispatcher_jobs = mapping(dispatcher.get("jobs"), "paper dispatcher jobs")
    dispatcher_job = mapping(dispatcher_jobs.get("author-exact-p05023-replay"), "paper dispatcher reusable call")
    if dispatcher_job.get("uses") != "./.github/workflows/know-place-author-exact-replay.yml":
        fail("Paper dispatcher must call the gated Monorepo-local author-exact worker.")
    forwarded = mapping(dispatcher_job.get("with"), "paper dispatcher inputs")
    if forwarded.get("consent_marker") != expression("inputs.consent_marker"):
        fail("Paper dispatcher must forward the exact user consent marker unchanged.")
    if forwarded.get("bridge_authorized") != "false":
        fail("Paper dispatcher must not claim a consent-bridge authorization.")
    print("KNOWN_PLACE_AUTHOR_EXACT_REPOSITORY_AND_CONSENT_GATE_PASS")


def main() -> int:
    api_inputs = api_dispatch_input_names()
    dispatcher = read_yaml(DISPATCHER_PATH)
    reusable = read_yaml(REUSABLE_PATH)

    dispatcher_events = mapping(dispatcher.get("on"), "dispatcher on")
    if set(dispatcher_events) != {"workflow_dispatch"}:
        fail("Monorepo Known Place dispatcher must be manual-only (workflow_dispatch only).")
    reusable_events = mapping(reusable.get("on"), "reusable workflow on")
    if set(reusable_events) != {"workflow_call"}:
        fail("Monorepo Known Place engine file must remain reusable-only (workflow_call only).")

    dispatch_inputs = mapping(
        mapping(dispatcher_events["workflow_dispatch"], "workflow_dispatch")["inputs"],
        "workflow_dispatch inputs",
    )
    call_inputs = mapping(
        mapping(reusable_events["workflow_call"], "workflow_call")["inputs"],
        "workflow_call inputs",
    )

    if set(dispatch_inputs) != api_inputs:
        fail(
            "Workflow-dispatch inputs differ from the API request payload: "
            f"api_only={sorted(api_inputs - set(dispatch_inputs))}; "
            f"workflow_only={sorted(set(dispatch_inputs) - api_inputs)}"
        )
    expected_call_inputs = api_inputs - {"request_id"}
    if set(call_inputs) != expected_call_inputs:
        fail(
            "Reusable workflow inputs differ from API fields after the run-correlation UUID: "
            f"expected={sorted(expected_call_inputs)}; actual={sorted(call_inputs)}"
        )

    request_id = mapping(dispatch_inputs["request_id"], "request_id")
    if request_id.get("required") != "true":
        fail("The dispatcher must require the API-generated request_id.")
    if dispatcher.get("run-name") != f"Known Place Analysis {expression('inputs.request_id')}":
        fail("Dispatcher run-name must exactly match the API's Known Place status correlation title.")

    dispatcher_permissions = mapping(dispatcher.get("permissions"), "dispatcher permissions")
    if dispatcher_permissions != {"contents": "read"}:
        fail("Dispatcher permissions must remain contents: read only.")

    jobs = mapping(dispatcher.get("jobs"), "dispatcher jobs")
    if set(jobs) != {"known-place-preflight", "known-place-aoi-analysis"}:
        fail("Dispatcher must contain exactly the guarded preflight and reusable analysis jobs.")
    dispatch_preflight = mapping(jobs["known-place-preflight"], "dispatcher preflight job")
    preflight_steps = dispatch_preflight.get("steps")
    if not isinstance(preflight_steps, list) or len(preflight_steps) != 1:
        fail("Dispatcher must have one credential-free preflight step.")
    dispatch_gate = preflight_steps[0]
    if not isinstance(dispatch_gate, dict) or "uses" in dispatch_gate:
        fail("Dispatcher preflight must not invoke an external action.")
    dispatch_gate_env = mapping(dispatch_gate.get("env"), "dispatcher preflight env")
    if (
        dispatch_gate_env.get("MONOREPO_KNOWN_PLACE_ENABLED") != expression("vars.MONOREPO_KNOWN_PLACE_ACTIONS_ENABLED")
        or dispatch_gate_env.get("EXECUTE_DOWNLOADS") != expression("inputs.execute_downloads")
    ):
        fail("Dispatcher preflight must read the repository opt-in and requested execution mode.")
    dispatch_gate_run = str(dispatch_gate.get("run", ""))
    for marker in ('if [[ "$EXECUTE_DOWNLOADS" == "true" ]]', '!= "true"', "RAW_SOURCE_DOWNLOADS=DISABLED", "DRIVE_UPLOAD=DISABLED"):
        if marker not in dispatch_gate_run:
            fail("Dispatcher preflight must fail closed for raw downloads while allowing catalog-only dry runs.")
    if "secrets." in str(dispatch_preflight):
        fail("Dispatcher preflight must not receive credentials.")

    analyze = mapping(jobs["known-place-aoi-analysis"], "dispatcher analyze job")
    if analyze.get("needs") != "known-place-preflight":
        fail("Dispatcher analysis job must depend on its fail-closed preflight.")
    if analyze.get("uses") != "./.github/workflows/know-place-aoi-analysis.yml":
        fail("Dispatcher must call the Monorepo-local Known Place reusable workflow.")
    forwarded = mapping(analyze.get("with"), "dispatcher workflow-call inputs")
    if set(forwarded) != set(call_inputs):
        fail(
            "Dispatcher does not forward the complete reusable workflow input contract: "
            f"missing={sorted(set(call_inputs) - set(forwarded))}; "
            f"extra={sorted(set(forwarded) - set(call_inputs))}"
        )
    for name in call_inputs:
        expected = expression(f"inputs.{name}")
        if forwarded[name] != expected:
            fail(f"Dispatcher input {name!r} must pass through unchanged as {expected!r}.")

    expected_secrets = {
        "EARTHDATA_TOKEN",
        "EARTHDATA_USERNAME",
        "EARTHDATA_PASSWORD",
        "GOOGLE_DRIVE_OAUTH_CLIENT_JSON",
        "GOOGLE_DRIVE_REFRESH_TOKEN",
        "GOOGLE_DRIVE_PARENT_FOLDER_ID",
    }
    declared_secrets = mapping(mapping(reusable_events["workflow_call"], "workflow_call").get("secrets"), "workflow_call secrets")
    if set(declared_secrets) != expected_secrets:
        fail("Reusable workflow secret contract does not match the six scoped worker secrets.")
    forwarded_secrets = mapping(analyze.get("secrets"), "dispatcher secret forwarding")
    if set(forwarded_secrets) != expected_secrets:
        fail("Dispatcher must forward exactly the six worker secrets, not inherit the repository-wide secret set.")
    for name in expected_secrets:
        if forwarded_secrets[name] != expression("secrets." + name):
            fail(f"Dispatcher worker secret {name!r} must be mapped explicitly.")

    for name in ("aoi_wkt", "start_date", "end_date"):
        if mapping(dispatch_inputs[name], name).get("required") != "true":
            fail(f"Dispatcher must require {name}.")
    for name in ("execute_downloads", "consent_marker"):
        input_spec = mapping(dispatch_inputs[name], name)
        reusable_spec = mapping(call_inputs[name], f"workflow_call.{name}")
        safe_default = "false" if name == "execute_downloads" else ""
        if input_spec.get("default") != safe_default:
            fail(f"Dispatcher {name} default is not the safe opt-in value.")
        if reusable_spec.get("default") != safe_default:
            fail(f"Reusable workflow {name} default is not the safe opt-in value.")

    reusable_permissions = mapping(reusable.get("permissions"), "reusable permissions")
    if reusable_permissions != {"contents": "read"}:
        fail("Reusable workflow permissions must remain contents: read only.")
    reusable_jobs = mapping(reusable.get("jobs"), "reusable jobs")
    preflight = mapping(reusable_jobs.get("preflight"), "preflight job")
    preflight_steps = preflight.get("steps")
    if not isinstance(preflight_steps, list):
        fail("Reusable workflow preflight must have explicit steps.")
    preflight_text = "\n".join(str(step.get("run", "")) for step in preflight_steps if isinstance(step, dict))
    preflight_env = "\n".join(
        f"{name}={value}"
        for step in preflight_steps
        if isinstance(step, dict)
        for name, value in mapping(step.get("env", {}), "preflight step env").items()
    )
    if (
        "MONOREPO_KNOWN_PLACE_ACTIONS_ENABLED" not in preflight_env
        or "EXECUTE_DOWNLOADS" not in preflight_env
        or 'if [[ "$EXECUTE_DOWNLOADS" == "true" ]]' not in preflight_text
        or '!= "true"' not in preflight_text
        or "RAW_SOURCE_DOWNLOADS=DISABLED" not in preflight_text
        or "DRIVE_UPLOAD=DISABLED" not in preflight_text
    ):
        fail("Reusable workflow must allow catalog-only dry runs while gating every raw download on explicit repository opt-in.")

    analysis_job = mapping(reusable_jobs.get("analyze-aoi"), "analyze-aoi job")
    steps = analysis_job.get("steps")
    if not isinstance(steps, list):
        fail("Known Place analyze-aoi job must define steps.")
    download_preflight = next(
        (step for step in steps if isinstance(step, dict) and step.get("name") == "Preflight all required credentials before any raw source download"),
        None,
    )
    if download_preflight is None or download_preflight.get("if") != expression("inputs.execute_downloads"):
        fail("Raw source credentials must be preflighted only on explicit execute_downloads=true.")
    download_run = str(download_preflight.get("run", ""))
    for token in ("[run-know-place]", "EARTHDATA", "GOOGLE_DRIVE_PARENT_FOLDER_ID"):
        if token not in download_run:
            fail(f"Raw-download preflight is missing {token}.")
    dry_run = next(
        (step for step in steps if isinstance(step, dict) and step.get("name") == "Catalog-only dry run (no product downloads)"),
        None,
    )
    if dry_run is None or dry_run.get("if") != expression("!inputs.execute_downloads"):
        fail("Catalog-only dry run must remain the default path.")
    upload = next(
        (step for step in steps if isinstance(step, dict) and step.get("name") == "Preserve report, dashboard, maps and Drive receipt as workflow artifacts"),
        None,
    )
    if upload is None:
        fail("The workflow must preserve a retrievable API result artifact.")
    if upload.get("uses") != f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}":
        fail("Result artifact upload must remain pinned to the reviewed immutable action SHA.")
    download_step = next(
        (step for step in steps if isinstance(step, dict) and step.get("name") == "Download exact selected GOFF granules and compute measurements"),
        None,
    )
    if download_step is None or download_step.get("if") != expression("inputs.execute_downloads"):
        fail("Raw GOFF download must be impossible on catalog-only dry runs.")
    drive_step = next(
        (step for step in steps if isinstance(step, dict) and step.get("name") == "Upload and byte-verify the derived result bundle in central Drive"),
        None,
    )
    if drive_step is None or drive_step.get("if") != expression("inputs.execute_downloads && success()"):
        fail("Drive upload must happen only after an explicit raw-download opt-in and successful processing.")
    drive_env = mapping(drive_step.get("env"), "Drive upload step env")
    if drive_env.get("GOOGLE_DRIVE_PARENT_FOLDER_ID") != expression("secrets.GOOGLE_DRIVE_PARENT_FOLDER_ID"):
        fail("Known Place Drive upload must use the configured parent-folder secret in the upload step scope.")
    if steps.index(download_preflight) >= steps.index(download_step):
        fail("Earthdata/Drive credential preflight must precede the first source-data download.")
    artifact_name = mapping(upload.get("with"), "artifact upload with").get("name")
    expected_artifact_name = (
        "know-place-aoi-" + expression("github.run_id") + "-" + expression("github.run_attempt")
    )
    if artifact_name != expected_artifact_name:
        fail("Workflow artifact name must match the API's know-place-aoi-{run_id}- result lookup prefix.")

    validate_author_exact_reproduction_gate()
    print("KNOWN_PLACE_API_INPUT_CONTRACT_PASS")
    print("KNOWN_PLACE_DISPATCH_STATUS_CORRELATION_PASS")
    print("KNOWN_PLACE_REUSABLE_FORWARDING_PASS")
    print("KNOWN_PLACE_RAW_DOWNLOAD_CONSENT_GATE_PASS")
    print("KNOWN_PLACE_ARTIFACT_AND_DRIVE_CONTRACT_PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
