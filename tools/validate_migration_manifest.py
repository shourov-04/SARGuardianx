#!/usr/bin/env python3
"""Validate the source provenance manifest without external dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "migration" / "source-pins.json"
EXPECTED_REPOSITORIES = {
    "moshiour0/SARGuardian_Dynamic",
    "moshiour0/SARGuardian-backend",
    "moshiour0/SARGuardian",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_sha(value: Any, location: str) -> None:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        fail(f"{location} must be a 40-character lowercase Git SHA")


def main() -> int:
    if not MANIFEST.is_file():
        fail(f"Missing manifest: {MANIFEST}")

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Manifest is not valid readable JSON: {exc}")

    if data.get("manifest_version") != 1:
        fail("Unsupported or missing manifest_version")
    if data.get("target_repository") != "moshiour0/SARGuardian-Monorepo":
        fail("target_repository does not match this monorepo")

    sources = data.get("source_repositories")
    if not isinstance(sources, list):
        fail("source_repositories must be a list")

    repositories = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            fail(f"source_repositories[{index}] must be an object")
        repository = source.get("repository")
        if not isinstance(repository, str):
            fail(f"source_repositories[{index}].repository is missing")
        repositories.add(repository)
        require_sha(source.get("audited_commit"), f"{repository}.audited_commit")
        if source.get("import_status") not in {"not_imported", "imported", "verified"}:
            fail(f"{repository}.import_status has an unsupported value")

    if repositories != EXPECTED_REPOSITORIES:
        fail(
            "source repository set mismatch; expected "
            + ", ".join(sorted(EXPECTED_REPOSITORIES))
        )

    extra_refs = data.get("additional_immutable_refs", [])
    if not isinstance(extra_refs, list):
        fail("additional_immutable_refs must be a list")
    for index, item in enumerate(extra_refs):
        if not isinstance(item, dict):
            fail(f"additional_immutable_refs[{index}] must be an object")
        require_sha(item.get("commit"), f"additional_immutable_refs[{index}].commit")

    print(
        "Migration manifest valid: "
        f"{len(sources)} source repositories, {len(extra_refs)} immutable refs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
