#!/usr/bin/env python3
"""Validate that every imported source GitHub Actions workflow has a reviewed disposition."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "migration" / "workflow-dispositions.json"
ALLOWED_DISPOSITIONS = {
    "root-present-contract-review-required",
    "feature-variant-contract-review-required",
    "renamed-root-port-contract-review",
    "ci-consolidated-parity-review",
    "ci-test-port-required",
    "manual-benchmark-disposition-required",
    "manual-live-workflow-port-required",
    "legacy-callback-source-review-required",
    "split-ci-live-contract-review",
    "manual-research-port-required",
    "author-exact-research-disposition-required",
    "archive-inactive-consent-bridge",
    "manual-renderer-port-required",
    "drive-retry-port-review-required",
    "api-dispatch-replacement-contract-review",
    "archive-confirmed-inactive",
}


def git_blob_sha(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + bytes([0])
    return hashlib.sha1(header + data).hexdigest()


def fail(message: str) -> None:
    print(f"WORKFLOW_DISPOSITION_ERROR={message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sources = manifest["sources"]
    entries = manifest["workflow_instances"]
    if len(entries) != 82:
        fail(f"expected 82 source workflow instances, got {len(entries)}")

    entry_keys = [(item["source_id"], item["workflow_name"]) for item in entries]
    if len(entry_keys) != len(set(entry_keys)):
        fail("duplicate (source_id, workflow_name) disposition entry")

    seen_source_ids = set()
    for source in sources:
        source_id = source["id"]
        seen_source_ids.add(source_id)
        directory = ROOT / source["snapshot_workflow_directory"]
        if not directory.is_dir():
            fail(f"missing source snapshot workflow directory: {directory}")

        expected = {
            item["workflow_name"]: item
            for item in entries
            if item["source_id"] == source_id
        }
        actual_paths = sorted(
            path for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
        )
        actual_names = {path.name for path in actual_paths}
        if actual_names != set(expected):
            missing = sorted(actual_names - set(expected))
            extra = sorted(set(expected) - actual_names)
            fail(f"{source_id} coverage mismatch; unclassified={missing}; missing_source_files={extra}")

        if len(actual_paths) != source["expected_workflow_count"]:
            fail(
                f"{source_id} expected {source['expected_workflow_count']} files, "
                f"found {len(actual_paths)}"
            )

        for path in actual_paths:
            item = expected[path.name]
            actual_sha = git_blob_sha(path.read_bytes())
            if actual_sha != item["source_blob_sha"]:
                fail(
                    f"{source_id}/{path.name} blob mismatch: "
                    f"expected {item['source_blob_sha']}, got {actual_sha}"
                )
            disposition = item["disposition"]
            if disposition not in ALLOWED_DISPOSITIONS:
                fail(f"unknown disposition {disposition!r} for {source_id}/{path.name}")
            if not item.get("note", "").strip():
                fail(f"missing rationale for {source_id}/{path.name}")
            for target in item.get("root_workflows", []):
                target_path = ROOT / target
                if not target_path.is_file():
                    fail(f"declared root target does not exist: {target}")

    if seen_source_ids != {"dynamic-main", "backend-main", "backend-known-place-pr85"}:
        fail(f"unexpected source inventory groups: {sorted(seen_source_ids)}")

    # These two source workflows are intentionally archival-only: no root
    # workflow or live API route may activate their obsolete/high-impact paths.
    for item in entries:
        if item["workflow_name"] in {"runner-test.yml", "sarguardian-science-worker.yml"}:
            if item["disposition"] != "archive-confirmed-inactive" or item.get("root_workflows"):
                fail(f"legacy workflow must remain explicitly archived: {item['source_id']}/{item['workflow_name']}")

    root_dir = ROOT / ".github" / "workflows"
    root_count = sum(
        1 for path in root_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    )
    if root_count != manifest["expected_root_workflow_count"]:
        fail(
            f"root workflow inventory changed: expected "
            f"{manifest['expected_root_workflow_count']}, got {root_count}; "
            "update the disposition matrix before adding/removing root workflows"
        )

    mapped = {
        target
        for item in entries
        for target in item.get("root_workflows", [])
    }
    counts = Counter(item["disposition"] for item in entries)
    print(
        "WORKFLOW_DISPOSITION_COVERAGE=PASS "
        f"source_instances={len(entries)} "
        f"dynamic={manifest['sources'][0]['expected_workflow_count']} "
        f"backend={manifest['sources'][1]['expected_workflow_count']} "
        f"known_place_pr85={manifest['sources'][2]['expected_workflow_count']} "
        f"root_workflows={root_count} "
        f"root_targets={len(mapped)}"
    )
    for status, count in sorted(counts.items()):
        print(f"WORKFLOW_DISPOSITION_COUNT {status}={count}")
    print("NOTE=coverage_and_blob_identity_only; semantic_parity_and_live_processing_are_separate_gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
