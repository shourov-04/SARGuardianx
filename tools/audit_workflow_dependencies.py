#!/usr/bin/env python3
"""Audit source workflow YAML, job graphs, reusable calls, checkouts and secret names."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required: python -m pip install pyyaml") from exc

ROOT = Path(__file__).resolve().parents[1]
SETS = {
    "dynamic-main": ROOT / "migration/source-snapshots/dynamic/.github/workflows",
    "backend-main": ROOT / "migration/source-snapshots/backend-main/.github/workflows",
    "known-place-pr85": ROOT / "migration/source-snapshots/backend-known-place-pr85/.github/workflows",
}
EXPECTED_COUNTS = {
    "dynamic-main": 7,
    "backend-main": 35,
    "known-place-pr85": 40,
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REUSABLE_RE = re.compile(
    r"^(?P<repo>[^/]+/[^/]+)/\.github/workflows/(?P<path>[^@]+)@(?P<ref>.+)$"
) 
LOCAL_RE = re.compile(r"^\./\.github/workflows/(?P<path>[^@]+)$")
SECRET_RE = re.compile(r"\$\{\{\s*secrets\.([A-Za-z_][A-Za-z0-9_]*)")
VAR_RE = re.compile(r"\$\{\{\s*vars\.([A-Za-z_][A-Za-z0-9_]*)")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    return [str(value)]


def main() -> int:
    totals: dict[str, int] = {}
    all_workflows: list[dict[str, Any]] = []
    global_call_edges: list[dict[str, str]] = []
    global_checkouts: list[dict[str, str]] = []
    all_secret_names: set[str] = set()
    all_var_names: set[str] = set()
    total_jobs = 0
    push_replay_candidates: list[str] = []
    failures: list[str] = []

    for label, folder in SETS.items():
        if not folder.is_dir():
            fail(f"Missing workflow directory: {folder}")
        paths = sorted(
            p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in {".yml", ".yaml"}
        )
        totals[label] = len(paths)
        expected = EXPECTED_COUNTS[label]
        if len(paths) != expected:
            failures.append(
                f"{label}: expected {expected} workflow files, found {len(paths)}"
            )

        for path in paths:
            rel = str(path.relative_to(ROOT))
            raw = path.read_text(encoding="utf-8")
            try:
                document = yaml.load(raw, Loader=yaml.BaseLoader)
            except yaml.YAMLError as exc:
                failures.append(f"{rel}: YAML parse error: {type(exc).__name__}")
                continue

            if not isinstance(document, dict):
                failures.append(f"{rel}: top-level YAML must be a mapping")
                continue
            triggers_value = document.get("on", document.get(True))
            triggers = (
                sorted(triggers_value.keys())
                if isinstance(triggers_value, dict)
                else normalize_list(triggers_value)
            )
            jobs = document.get("jobs")
            if not isinstance(jobs, dict) or not jobs:
                failures.append(f"{rel}: missing or empty jobs mapping")
                continue

            job_names = set(jobs)
            job_count = len(jobs)
            total_jobs += job_count
            workflow_calls: list[str] = []
            checkouts: list[dict[str, str]] = []
            artifact_uploads: list[dict[str, str]] = []
            artifact_downloads: list[dict[str, str]] = []
            permissions = document.get("permissions")
            env_names = set()
            secret_names = set(SECRET_RE.findall(raw))
            var_names = set(VAR_RE.findall(raw))
            all_secret_names.update(secret_names)
            all_var_names.update(var_names)
            if "push" in triggers and any(x in path.name.lower() for x in ("replay", "retained", "consent", "drive-retry")):
                push_replay_candidates.append(rel)

            for job_name, job in jobs.items():
                if not isinstance(job, dict):
                    failures.append(f"{rel}: job {job_name} is not a mapping")
                    continue
                needs = set(normalize_list(job.get("needs")))
                unresolved = sorted(needs - job_names)
                if unresolved:
                    failures.append(
                        f"{rel}: job {job_name} needs unknown jobs: {', '.join(unresolved)}"
                    )
                for key in (job.get("env") or {}):
                    env_names.add(str(key))

                # Reusable workflows are declared on a job's top-level "uses",
                # not inside steps. Record external and local calls separately.
                job_uses = str(job.get("uses") or "")
                match = REUSABLE_RE.match(job_uses)
                if match:
                    edge = {
                        "source": rel,
                        "job": str(job_name),
                        "call_kind": "external_reusable_workflow",
                        "target_repo": match.group("repo"),
                        "target_workflow": match.group("path"),
                        "target_ref": match.group("ref"),
                    }
                    workflow_calls.append(
                        f"{edge['target_repo']}/{edge['target_workflow']}@{edge['target_ref']}"
                    )
                    global_call_edges.append(edge)
                else:
                    local_match = LOCAL_RE.match(job_uses)
                    if local_match:
                        edge = {
                            "source": rel,
                            "job": str(job_name),
                            "call_kind": "local_reusable_workflow",
                            "target_repo": "<same-repository>",
                            "target_workflow": local_match.group("path"),
                            "target_ref": "<same-commit>",
                        }
                        workflow_calls.append(
                            f"./.github/workflows/{edge['target_workflow']}@<same-commit>"
                        )
                        global_call_edges.append(edge)

                for step in job.get("steps") or []:
                    if not isinstance(step, dict):
                        continue
                    uses = str(step.get("uses") or "")
                    step_with = step.get("with") if isinstance(step.get("with"), dict) else {}
                    if uses == "actions/checkout" or uses.startswith("actions/checkout@"):
                        checkouts.append({
                            "job": str(job_name),
                            "uses": uses,
                            "repository": str(step_with.get("repository") or "<current-repository>"),
                            "ref": str(step_with.get("ref") or "<implicit-event-sha>"),
                            "path": str(step_with.get("path") or "."),
                        })
                    match = REUSABLE_RE.match(uses)
                    if match:
                        edge = {
                            "source": rel,
                            "job": str(job_name),
                            "target_repo": match.group("repo"),
                            "target_workflow": match.group("path"),
                            "target_ref": match.group("ref"),
                        }
                        workflow_calls.append(
                            f"{edge['target_repo']}/{edge['target_workflow']}@{edge['target_ref']}"
                        )
                        global_call_edges.append(edge)
                    lower = uses.lower()
                    artifact_name = str(step_with.get("name") or step_with.get("artifact") or "<default>")
                    if "upload-artifact" in lower:
                        artifact_uploads.append({
                            "job": str(job_name),
                            "name": artifact_name,
                            "retention_days": str(step_with.get("retention-days") or "<default>"),
                        })
                    if "download-artifact" in lower:
                        artifact_downloads.append({
                            "job": str(job_name),
                            "name": artifact_name,
                        })

                for key in (job.get("env") or {}):
                    env_names.add(str(key))
                if job.get("permissions") and permissions is None:
                    # Job-level permissions are intentionally recorded as job-level.
                    pass

            global_checkouts.extend({"source": rel, **x} for x in checkouts)
            all_workflows.append({
                "source_set": label,
                "path": rel,
                "name": str(document.get("name") or path.stem),
                "triggers": triggers,
                "job_count": job_count,
                "job_names": sorted(str(x) for x in job_names),
                "workflow_calls": workflow_calls,
                "checkouts": checkouts,
                "uploads": artifact_uploads,
                "downloads": artifact_downloads,
                "secret_names": sorted(secret_names),
                "variable_names": sorted(var_names),
                "permissions_declared": permissions is not None,
                "concurrency_declared": "concurrency" in document,
            })

    if failures:
        for item in failures:
            print(item, file=sys.stderr)
        raise SystemExit(1)

    summary = {
        "source_workflow_counts": totals,
        "total_workflows": len(all_workflows),
        "total_jobs": total_jobs,
        "reusable_workflow_calls": len(global_call_edges),
        "reusable_calls_by_kind": dict(Counter(x["call_kind"] for x in global_call_edges)),
        "external_checkout_steps": len(global_checkouts),
        "secret_variable_names": sorted(all_secret_names),
        "repository_variable_names": sorted(all_var_names),
        "push_replay_candidates": sorted(push_replay_candidates),
        "workflows": all_workflows,
        "reusable_workflow_edges": global_call_edges,
        "external_checkouts": global_checkouts,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(
        "WORKFLOW_DEPENDENCY_AUDIT_PASS "
        f"workflows={len(all_workflows)} jobs={total_jobs} "
        f"reusable_calls={len(global_call_edges)} external_checkouts={len(global_checkouts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
