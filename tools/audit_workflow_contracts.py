#!/usr/bin/env python3
"""Build a secrets-safe structural inventory of all source workflow variants."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ("dynamic-main", "migration/source-snapshots/dynamic/.github/workflows"),
    ("backend-main", "migration/source-snapshots/backend-main/.github/workflows"),
    ("known-place-pr85", "migration/source-snapshots/backend-known-place-pr85/.github/workflows"),
)
WORKFLOW_SUFFIXES = {".yml", ".yaml"}
SECRET_RE = re.compile(r"\$\{\{\s*secrets\.([A-Za-z_][A-Za-z0-9_]*)")
VAR_RE = re.compile(r"\$\{\{\s*vars\.([A-Za-z_][A-Za-z0-9_]*)")
URL_RE = re.compile(r"https?://[^\s'\"\)]+", re.IGNORECASE)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def run_git_blob(path: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def flatten_strings(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str):
                found.append(key)
            found.extend(flatten_strings(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(flatten_strings(item))
    return found


def mapping_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def normalize_permissions(value: Any) -> dict[str, str]:
    if isinstance(value, str):
        return {"__all__": value}
    permissions = mapping_or_empty(value)
    return {str(key): str(item) for key, item in sorted(permissions.items())}


def audit_workflow(source: str, path: Path) -> dict[str, Any]:
    relative = path.relative_to(ROOT).as_posix()
    raw = path.read_text(encoding="utf-8")
    try:
        document = yaml.load(raw, Loader=yaml.BaseLoader)
    except yaml.YAMLError as exc:
        return {
            "source": source,
            "path": relative,
            "blob_sha": run_git_blob(relative),
            "parse": "error",
            "parse_error_type": type(exc).__name__,
        }

    if not isinstance(document, dict):
        return {
            "source": source,
            "path": relative,
            "blob_sha": run_git_blob(relative),
            "parse": "error",
            "parse_error_type": "top_level_not_mapping",
        }

    events = mapping_or_empty(document.get("on"))
    jobs = mapping_or_empty(document.get("jobs"))
    top_permissions = normalize_permissions(document.get("permissions"))
    job_rows = []
    step_uses: list[dict[str, Any]] = []
    reusable_calls: list[str] = []
    checkout_rows: list[dict[str, Any]] = []
    artifact_rows: list[dict[str, Any]] = []
    job_permissions: dict[str, dict[str, str]] = {}
    undeclared_job_permissions: list[str] = []
    continuable_jobs: list[str] = []
    job_workdirs: dict[str, str] = {}

    all_strings = flatten_strings(document)
    secret_names = sorted({m.group(1) for value in all_strings for m in SECRET_RE.finditer(value)})
    variable_names = sorted({m.group(1) for value in all_strings for m in VAR_RE.finditer(value)})
    text_for_flags = "\n".join(all_strings)

    for job_id, job_value in jobs.items():
        job = mapping_or_empty(job_value)
        permissions = normalize_permissions(job.get("permissions"))
        job_permissions[str(job_id)] = permissions
        if not permissions and not top_permissions:
            undeclared_job_permissions.append(str(job_id))
        if "continue-on-error" in job:
            continuable_jobs.append(str(job_id))
        defaults = mapping_or_empty(job.get("defaults"))
        run_defaults = mapping_or_empty(defaults.get("run"))
        if run_defaults.get("working-directory"):
            job_workdirs[str(job_id)] = str(run_defaults["working-directory"])

        needs = job.get("needs", [])
        if isinstance(needs, str):
            needs = [needs]
        elif not isinstance(needs, list):
            needs = []

        if job.get("uses"):
            reusable_calls.append(str(job.get("uses")))

        steps = job.get("steps", [])
        if not isinstance(steps, list):
            steps = []

        for step_index, step_value in enumerate(steps, start=1):
            step = mapping_or_empty(step_value)
            uses = step.get("uses")
            if uses:
                uses = str(uses)
                item = {
                    "job": str(job_id),
                    "step": step_index,
                    "uses": uses,
                    "pinned_sha": bool(re.search(r"@[0-9a-f]{40}$", uses)),
                }
                step_uses.append(item)
                if ".github/workflows/" in uses:
                    reusable_calls.append(uses)
            with_values = mapping_or_empty(step.get("with"))
            action_name = str(uses or "")
            if action_name.startswith("actions/checkout@") or "/checkout@" in action_name:
                checkout_rows.append({
                    "job": str(job_id),
                    "step": step_index,
                    "action": action_name,
                    "repository": with_values.get("repository"),
                    "ref": with_values.get("ref"),
                    "path": with_values.get("path"),
                    "fetch_depth": with_values.get("fetch-depth"),
                    "persist_credentials": with_values.get("persist-credentials"),
                })
            if action_name.startswith("actions/upload-artifact@") or action_name.startswith("actions/download-artifact@"):
                artifact_rows.append({
                    "job": str(job_id),
                    "step": step_index,
                    "action": action_name,
                    "name": with_values.get("name"),
                    "path": with_values.get("path"),
                    "pattern": with_values.get("pattern"),
                    "retention_days": with_values.get("retention-days"),
                    "merge_multiple": with_values.get("merge-multiple"),
                })

        job_rows.append({
            "id": str(job_id),
            "needs": [str(x) for x in needs],
            "uses": str(job.get("uses")) if job.get("uses") else None,
            "permissions": permissions,
            "continue_on_error": str(job.get("continue-on-error")) if "continue-on-error" in job else None,
            "timeout_minutes": str(job.get("timeout-minutes")) if "timeout-minutes" in job else None,
            "environment": str(mapping_or_empty(job.get("environment")).get("name") or job.get("environment") or ""),
        })

    on_workflow_call = mapping_or_empty(events.get("workflow_call"))
    on_dispatch = mapping_or_empty(events.get("workflow_dispatch"))
    trigger_names = sorted(str(key) for key in events.keys())
    external_checkout_repos = sorted({
        str(row["repository"]) for row in checkout_rows if row.get("repository")
    })
    actions_unpinned = [
        item for item in step_uses
        if "@" in item["uses"] and not item["pinned_sha"]
    ]
    callback_context = sorted({
        token for token in flatten_strings(document)
        if any(word in token.lower() for word in ("callback", "public_api_url", "artifact_url", "drive"))
    })
    callback_identifiers = sorted({
        token for token in (secret_names + variable_names)
        if any(word in token.lower() for word in ("callback", "drive", "api_url", "github_actions"))
    })
    urls = sorted({url.rstrip(",;") for value in all_strings for url in URL_RE.findall(value)})
    retry_markers = sorted({
        word for word in ("retry", "max_attempts", "retry_count", "continue-on-error", "fail-fast")
        if word in text_for_flags.lower()
    })

    return {
        "source": source,
        "path": relative,
        "blob_sha": run_git_blob(relative),
        "parse": "ok",
        "triggers": trigger_names,
        "workflow_dispatch_inputs": sorted(mapping_or_empty(on_dispatch.get("inputs")).keys()),
        "workflow_call_inputs": sorted(mapping_or_empty(on_workflow_call.get("inputs")).keys()),
        "workflow_call_secrets": sorted(mapping_or_empty(on_workflow_call.get("secrets")).keys()),
        "top_permissions": top_permissions,
        "undeclared_job_permissions": undeclared_job_permissions,
        "job_permissions": job_permissions,
        "jobs": job_rows,
        "external_checkout_repositories": external_checkout_repos,
        "checkouts": checkout_rows,
        "reusable_workflow_calls": sorted(set(reusable_calls)),
        "actions": step_uses,
        "unpinned_action_count": len(actions_unpinned),
        "unpinned_actions": actions_unpinned,
        "artifact_steps": artifact_rows,
        "secret_names": secret_names,
        "variable_names": variable_names,
        "callback_and_drive_identifiers": callback_identifiers,
        "callback_related_context_tokens": callback_context,
        "literal_urls": urls,
        "retry_markers": retry_markers,
        "continuable_jobs": sorted(set(continuable_jobs)),
        "job_working_directories": job_workdirs,
        "workflow_concurrency": document.get("concurrency"),
        "workflow_defaults": document.get("defaults"),
        "environment_names": sorted({
            str(mapping_or_empty(job).get("environment", {}).get("name"))
            for job in jobs.values()
            if isinstance(mapping_or_empty(job).get("environment"), dict)
            and mapping_or_empty(job).get("environment", {}).get("name")
        }),
    }


def main() -> int:
    records: list[dict[str, Any]] = []
    for source, prefix in SOURCES:
        root = ROOT / prefix
        if not root.is_dir():
            raise SystemExit(f"Missing workflow snapshot directory: {prefix}")
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in WORKFLOW_SUFFIXES:
                records.append(audit_workflow(source, path))

    summary = {
        "workflow_instances": len(records),
        "parse_errors": sum(item.get("parse") != "ok" for item in records),
        "by_source": {
            source: sum(item["source"] == source for item in records)
            for source, _ in SOURCES
        },
        "trigger_counts": {},
        "workflow_call_count": 0,
        "manual_dispatch_count": 0,
        "push_trigger_count": 0,
        "pull_request_trigger_count": 0,
        "top_permission_declared": 0,
        "workflows_with_undeclared_job_permissions": 0,
        "workflow_instances_with_secrets": 0,
        "workflow_instances_with_external_checkout": 0,
        "external_checkout_repositories": sorted({
            repo for item in records for repo in item.get("external_checkout_repositories", [])
        }),
        "unpinned_action_references": sum(item.get("unpinned_action_count", 0) for item in records),
        "artifacts_steps": sum(len(item.get("artifact_steps", [])) for item in records),
        "reusable_workflow_calls": sum(len(item.get("reusable_workflow_calls", [])) for item in records),
        "workflows_with_retry_markers": sum(bool(item.get("retry_markers")) for item in records),
        "workflows_with_continue_on_error": sum(bool(item.get("continuable_jobs")) for item in records),
    }

    for item in records:
        if item.get("parse") != "ok":
            continue
        for trigger in item.get("triggers", []):
            summary["trigger_counts"][trigger] = summary["trigger_counts"].get(trigger, 0) + 1
        summary["workflow_call_count"] += "workflow_call" in item.get("triggers", [])
        summary["manual_dispatch_count"] += "workflow_dispatch" in item.get("triggers", [])
        summary["push_trigger_count"] += "push" in item.get("triggers", [])
        summary["pull_request_trigger_count"] += "pull_request" in item.get("triggers", [])
        summary["top_permission_declared"] += bool(item.get("top_permissions"))
        summary["workflows_with_undeclared_job_permissions"] += bool(item.get("undeclared_job_permissions"))
        summary["workflow_instances_with_secrets"] += bool(item.get("secret_names"))
        summary["workflow_instances_with_external_checkout"] += bool(item.get("external_checkout_repositories"))

    result = {
        "audit_version": 1,
        "source_refs": {
            "dynamic-main": "dd64b7adc90594f1d7f316b352e39fbac2013cb6",
            "backend-main": "97d849454918b1425ac41bb70e7a32d11cfd3833",
            "known-place-pr85": "bfde7dde8ada92a03054cd8dbad8daa7a5c119f8",
        },
        "summary": summary,
        "workflows": records,
    }

    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))

    print("WORKFLOW_REVIEW_QUEUE_BEGIN")
    for item in records:
        if item.get("parse") != "ok":
            print(f"PARSE_ERROR source={item['source']} path={item['path']}")
            continue
        risks = []
        if item.get("undeclared_job_permissions"):
            risks.append("implicit_permissions=" + ",".join(item["undeclared_job_permissions"]))
        if item.get("unpinned_action_count"):
            risks.append("unpinned_actions=" + str(item["unpinned_action_count"]))
        if item.get("secret_names"):
            risks.append("secret_names=" + ",".join(item["secret_names"]))
        if item.get("external_checkout_repositories"):
            risks.append("external_checkouts=" + ",".join(item["external_checkout_repositories"]))
        if item.get("reusable_workflow_calls"):
            risks.append("reusable_calls=" + str(len(item["reusable_workflow_calls"])))
        if item.get("artifact_steps"):
            risks.append("artifact_steps=" + str(len(item["artifact_steps"])))
        if item.get("retry_markers"):
            risks.append("retry_markers=" + ",".join(item["retry_markers"]))
        if risks:
            print(
                f"REVIEW source={item['source']} path={item['path']} "
                f"triggers={','.join(item['triggers']) or 'none'} "
                + " ".join(risks)
            )

    print("REUSABLE_WORKFLOW_CALL_GRAPH_BEGIN")
    for item in records:
        for called in item.get("reusable_workflow_calls", []):
            print(
                f"REUSABLE_CALL source={item['source']} "
                f"caller={item['path']} uses={called}"
            )
    print("EXTERNAL_CHECKOUT_REF_GRAPH_BEGIN")
    for item in records:
        for checkout in item.get("checkouts", []):
            repository = checkout.get("repository")
            if repository:
                ref = str(checkout.get("ref") or "default-branch")
                immutable = bool(SHA_RE.fullmatch(ref))
                print(
                    f"EXTERNAL_CHECKOUT source={item['source']} "
                    f"workflow={item['path']} repository={repository} "
                    f"ref={ref} immutable_ref={str(immutable).lower()} "
                    f"checkout_path={checkout.get('path') or 'workspace-root'}"
                )

    action_refs: dict[str, int] = {}
    for item in records:
        for action in item.get("unpinned_actions", []):
            action_refs[action["uses"]] = action_refs.get(action["uses"], 0) + 1
    print("UNPINNED_ACTION_REFERENCE_FREQUENCY_BEGIN")
    for action, count in sorted(action_refs.items(), key=lambda pair: (-pair[1], pair[0])):
        print(f"UNPINNED_ACTION_REF count={count} uses={action}")
    print("WORKFLOW_REVIEW_QUEUE_END")
    print("WORKFLOW_CONTRACT_AUDIT_PASS" if summary["parse_errors"] == 0 else "WORKFLOW_CONTRACT_AUDIT_PARSE_FAILURE")
    return 0 if summary["parse_errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
