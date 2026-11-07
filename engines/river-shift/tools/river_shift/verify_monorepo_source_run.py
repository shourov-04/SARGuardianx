#!/usr/bin/env python3
"""Verify a retained RiverShift source run belongs to this Monorepo Preview branch."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from uuid import UUID


def get_json(url: str, token: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            value = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GITHUB_API_HTTP_{exc.code}") from None
    if not isinstance(value, dict):
        raise RuntimeError("GITHUB_API_RESPONSE_NOT_OBJECT")
    return value


def verify(
    *,
    source_run_id: str,
    source_job_id: str,
    expected_branch: str,
    require_products: bool,
    token: str,
) -> dict:
    if not re.fullmatch(r"[1-9][0-9]{5,19}", source_run_id):
        raise ValueError("SOURCE_RUN_ID_INVALID")
    try:
        canonical_job_id = str(UUID(source_job_id))
    except (ValueError, AttributeError):
        raise ValueError("SOURCE_JOB_ID_INVALID_UUID") from None

    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if repo.lower() != "moshiour0/sarguardian-monorepo":
        raise ValueError("CURRENT_REPOSITORY_IS_NOT_SARGUARDIAN_MONOREPO")
    api = f"https://api.github.com/repos/{repo}"
    run = get_json(f"{api}/actions/runs/{source_run_id}", token)

    if run.get("repository", {}).get("full_name", "").lower() != repo.lower():
        raise ValueError("SOURCE_RUN_NOT_FROM_THIS_MONOREPO")
    if run.get("head_repository", {}).get("full_name", "").lower() != repo.lower():
        raise ValueError("SOURCE_RUN_HEAD_REPOSITORY_NOT_MONOREPO")
    if run.get("head_branch") != expected_branch:
        raise ValueError("SOURCE_RUN_BRANCH_MISMATCH")
    if run.get("event") != "workflow_dispatch":
        raise ValueError("SOURCE_RUN_MUST_BE_MANUALLY_DISPATCHED")
    if run.get("path") != ".github/workflows/river-shift-gcov-process.yml":
        raise ValueError("SOURCE_RUN_NOT_MONOREPO_RIVERSHIFT_GCOV_WORKFLOW")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        raise ValueError("SOURCE_RUN_NOT_SUCCESSFUL")

    attempt = run.get("run_attempt")
    run_number = run.get("run_number")
    if not isinstance(attempt, int) or attempt < 1:
        raise ValueError("SOURCE_RUN_ATTEMPT_INVALID")
    if not isinstance(run_number, int) or run_number < 1:
        raise ValueError("SOURCE_RUN_NUMBER_INVALID")

    artifact_rows = []
    page = 1
    while page <= 20:
        payload = get_json(
            f"{api}/actions/runs/{source_run_id}/artifacts?per_page=100&page={page}",
            token,
        )
        rows = payload.get("artifacts")
        if not isinstance(rows, list):
            raise ValueError("SOURCE_RUN_ARTIFACT_LIST_INVALID")
        artifact_rows.extend(row for row in rows if isinstance(row, dict))
        if len(rows) < 100:
            break
        page += 1
    else:
        raise ValueError("SOURCE_RUN_ARTIFACT_PAGINATION_LIMIT_EXCEEDED")

    prepared_name = f"rivershift-prepared-{canonical_job_id}"
    prepared = next(
        (
            item for item in artifact_rows
            if item.get("name") == prepared_name
            and item.get("expired") is False
            and int(item.get("size_in_bytes", 0)) > 0
        ),
        None,
    )
    if prepared is None:
        raise ValueError("SOURCE_PREPARED_ARTIFACT_MISSING_OR_EXPIRED")

    products = sorted(
        item.get("name", "")
        for item in artifact_rows
        if item.get("name", "").startswith("rivershift-product-")
        and item.get("expired") is False
        and int(item.get("size_in_bytes", 0)) > 0
    )
    if require_products and not products:
        raise ValueError("SOURCE_PRODUCT_COG_ARTIFACTS_MISSING_OR_EXPIRED")

    result = {
        "repository": repo,
        "source_run_id": source_run_id,
        "source_run_number": run_number,
        "source_run_attempt": attempt,
        "source_run_head_sha": run.get("head_sha"),
        "source_run_branch": expected_branch,
        "source_run_workflow": run.get("path"),
        "source_job_id": canonical_job_id,
        "prepared_artifact_name": prepared_name,
        "product_artifact_names": products,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--source-job-id", required=True)
    parser.add_argument("--expected-branch", required=True)
    parser.add_argument("--require-products", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        print("RIVERSHIFT_SOURCE_RUN_CHECK=FAIL reason=GH_TOKEN_MISSING", flush=True)
        return 2
    try:
        result = verify(
            source_run_id=args.source_run_id,
            source_job_id=args.source_job_id,
            expected_branch=args.expected_branch,
            require_products=args.require_products,
            token=token,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a", encoding="utf-8") as stream:
                stream.write(f"run_id={result['source_run_id']}\n")
                stream.write(f"run_number={result['source_run_number']}\n")
                stream.write(f"run_attempt={result['source_run_attempt']}\n")
                stream.write(f"prepared_artifact={result['prepared_artifact_name']}\n")
                stream.write("product_artifact_count=" + str(len(result["product_artifact_names"])) + "\n")
        print("RIVERSHIFT_MONOREPO_SOURCE_RUN_VERIFICATION=PASS", flush=True)
        print(f"RIVERSHIFT_SOURCE_RUN_ID={result['source_run_id']}", flush=True)
        print(f"RIVERSHIFT_SOURCE_RUN_NUMBER={result['source_run_number']}", flush=True)
        print(f"RIVERSHIFT_SOURCE_RUN_ATTEMPT={result['source_run_attempt']}", flush=True)
        print(f"RIVERSHIFT_SOURCE_PREPARED_ARTIFACT={result['prepared_artifact_name']}", flush=True)
        print(f"RIVERSHIFT_SOURCE_PRODUCT_ARTIFACT_COUNT={len(result['product_artifact_names'])}", flush=True)
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"RIVERSHIFT_SOURCE_RUN_VERIFICATION=FAIL reason={type(exc).__name__}:{exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
