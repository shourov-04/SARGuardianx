#!/usr/bin/env python3
"""Compare imported monorepo snapshot entries with their exact source Git trees."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Snapshot:
    label: str
    source_sha: str
    destination_prefix: str
    source_tree_sha: str | None = None


SNAPSHOTS = (
    Snapshot(
        "Dynamic main",
        "dd64b7adc90594f1d7f316b352e39fbac2013cb6",
        "migration/source-snapshots/dynamic",
    ),
    Snapshot(
        "Backend main",
        "97d849454918b1425ac41bb70e7a32d11cfd3833",
        "migration/source-snapshots/backend-main",
    ),
    Snapshot(
        "Known Place PR #85 head",
        "bfde7dde8ada92a03054cd8dbad8daa7a5c119f8",
        "migration/source-snapshots/backend-known-place-pr85",
    ),
    Snapshot(
        "NISAR science main",
        "9fcb543ef28a7f6fe70a379aed9cfe3e43e277ec",
        "migration/source-snapshots/nisar-science",
    ),
    Snapshot(
        "NISAR historical pin 10639",
        "10639a916c9829850775410b3ed7de62e527770d",
        "migration/source-snapshots/nisar-pins/10639a9",
    ),
    Snapshot(
        "NISAR historical pin 006d",
        "006d4cd1485cf80e509eaf8717c12e9c6390ac09",
        "migration/source-snapshots/nisar-pins/006d4cd",
    ),
    Snapshot(
        "Dynamic historical callback API pin db6472",
        "db6472e1c304e21242f1ab1dfd671ccb21ba5697",
        "migration/source-snapshots/dynamic-pins/db6472",
    ),
    Snapshot(
        "Backend historical reassembly pin d9e67",
        "d9e67df7d800032c37d23f74df44c98e3ab655f7",
        "migration/source-snapshots/backend-pins/d9e67",
    ),
    Snapshot(
        "Legacy Sagormodak science pin 77cc964",
        "77cc9646cfa46d3aff3669d351912f984cf67aa3",
        "migration/source-snapshots/legacy-fork/77cc964",
    ),
    Snapshot(
        "Known Place author-exact backend code pin b825df",
        "b825df798ea4cb9874aa10dd01174d2a8ef73cba",
        "migration/source-snapshots/backend-pins/b825df",
        "3c77b2d52474364020acebeb4338b5babe7ff4ec",
    ),
)

ANCESTOR_CHECKS = (
    (
        "Known Place feature branch base",
        "bd7a59c54ddae7c19fd88896e877c3a530b43d9e",
        "bfde7dde8ada92a03054cd8dbad8daa7a5c119f8",
    ),
    (
        "Historical extended-science pin",
        "ab547ecc82bcc4d6ccef545a59852536c2beacc6",
        "9fcb543ef28a7f6fe70a379aed9cfe3e43e277ec",
    ),
)


def git(*args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {message}")
    return completed.stdout


def tree_entries(revision: str) -> dict[str, tuple[str, str, str]]:
    """Return path -> (mode, object type, object SHA), preserving raw path names."""
    raw = git("ls-tree", "-r", "-z", "--full-tree", revision)
    result: dict[str, tuple[str, str, str]] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, path_bytes = record.split(b"\t", 1)
            mode, object_type, object_sha = metadata.decode("ascii").split(" ")
            path = path_bytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError(f"Cannot parse git ls-tree record: {exc}") from exc
        result[path] = (mode, object_type, object_sha)
    return result


def check_ancestor(label: str, ancestor: str, descendant: str) -> None:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if result.returncode == 1:
        raise RuntimeError(
            f"{label} is not preserved as an ancestor: {ancestor} -> {descendant}"
        )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Cannot verify {label}: {message}")
    print(f"ANCESTRY_PASS {label}: {ancestor} -> {descendant}")



def load_promotion_overrides() -> dict[str, dict[str, str]]:
    """Load hash-pinned, path-preserving edits to explicitly promoted files only."""
    manifest_path = Path(__file__).resolve().parents[1] / "migration" / "promotion-overrides.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read promotion override manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "1.0":
        raise RuntimeError("Promotion override manifest has an unsupported schema.")
    rows = manifest.get("approved_overrides")
    if not isinstance(rows, list):
        raise RuntimeError("Promotion override manifest must contain an approved_overrides array.")

    promotion_roots = {
        "Dynamic active API promotion": {
            "source": "migration/source-snapshots/dynamic/Backend/",
            "destination": "apps/api/",
            "verification": "apps/api/tests/",
        },
        "Dynamic frontend promotion": {
            "source": "migration/source-snapshots/dynamic/Frontend/",
            "destination": "apps/web/",
            "verification": "apps/web/src/",
        },
        "Find Displacements tools promotion": {
            "source": "migration/source-snapshots/backend-main/tools/",
            "destination": "engines/find-displacements/tools/",
            "verification": "engines/find-displacements/tools/tests/",
        },
    }
    approved: dict[str, dict[str, str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("Promotion override row must be an object.")
        scope = row.get("promotion_scope")
        roots = promotion_roots.get(scope) if isinstance(scope, str) else None
        source_path = row.get("source_path")
        destination_path = row.get("destination_path")
        if (
            roots is None
            or not isinstance(source_path, str)
            or not source_path.startswith(roots["source"])
            or not isinstance(destination_path, str)
            or not destination_path.startswith(roots["destination"])
        ):
            raise RuntimeError("Promotion override scope, source and destination roots do not match an approved promotion.")
        relative_source = source_path[len(roots["source"]):]
        relative_destination = destination_path[len(roots["destination"]):]
        if not relative_source or relative_source != relative_destination or ".." in Path(relative_source).parts:
            raise RuntimeError(f"Promotion override source/destination paths do not correspond: {source_path}.")
        source_sha = row.get("source_blob_sha")
        destination_sha = row.get("destination_blob_sha")
        if (
            not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", source_sha)
            or not isinstance(destination_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", destination_sha)
            or row.get("mode") != "100644" or row.get("object_type") != "blob"
        ):
            raise RuntimeError(f"Promotion override has an invalid Git object pin: {destination_path}.")
        reason = row.get("reason")
        commits = row.get("implementation_commits")
        tests = row.get("verification_paths")
        if (
            not isinstance(reason, str) or len(reason.strip()) < 20
            or not isinstance(commits, list) or not commits
            or any(not isinstance(item, str) or not re.fullmatch(r"[0-9a-f]{40}", item) for item in commits)
            or not isinstance(tests, list) or not tests
            or any(
                not isinstance(item, str)
                or not item.startswith(roots["verification"])
                or not ("/tests/" in item or ".test." in item or ".spec." in item)
                for item in tests
            )
        ):
            raise RuntimeError(f"Promotion override lacks reviewable reason, commit or test evidence: {destination_path}.")
        override_key = f"{scope}:{relative_source}"
        if override_key in approved:
            raise RuntimeError(f"Duplicate promotion override for {destination_path}.")
        approved[override_key] = row
    return approved



def verify_source_branch_archives(target_entries: dict[str, tuple[str, str, str]]) -> int:
    """Verify archived RiverShift validation refs against exact source blob pins.

    These are evidence snapshots, not activated workflows or full source-tree
    imports. Their Git blob identities must remain exact and every archived
    file must be accounted for by the provenance manifest.
    """
    manifest_path = (
        Path(__file__).resolve().parents[1]
        / "migration"
        / "source-branch-snapshots"
        / "rivershift-validation-pins.json"
    )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read RiverShift source-branch pin manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "1.0":
        raise RuntimeError("RiverShift source-branch pin manifest has an unsupported schema.")
    if manifest.get("policy") != "ARCHIVAL_SNAPSHOTS_WITH_SEPARATE_REVIEWED_ROOT_PORTS":
        raise RuntimeError("RiverShift source-branch snapshots must remain explicitly archival-only.")

    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise RuntimeError("RiverShift source-branch manifest must contain source entries.")

    expected_paths: set[str] = set()
    verified = 0
    for source in sources:
        if not isinstance(source, dict):
            raise RuntimeError("RiverShift source-branch entry must be an object.")
        if source.get("source_repository") != "moshiour0/SARGuardian-backend":
            raise RuntimeError("Unexpected repository in RiverShift source-branch manifest.")
        source_head = source.get("source_head_commit")
        if not isinstance(source_head, str) or not re.fullmatch(r"[0-9a-f]{40}", source_head):
            raise RuntimeError("RiverShift source-branch manifest has an invalid source commit pin.")
        prefix = source.get("destination_prefix")
        if (
            not isinstance(prefix, str)
            or not prefix.startswith("migration/source-branch-snapshots/")
            or not prefix.endswith("/")
            or ".." in Path(prefix).parts
        ):
            raise RuntimeError("RiverShift archive destination must remain under migration/source-branch-snapshots/.")
        rows = source.get("files")
        if not isinstance(rows, list) or not rows:
            raise RuntimeError(f"RiverShift archive {source_head} has no pinned files.")
        for row in rows:
            if not isinstance(row, dict):
                raise RuntimeError("RiverShift source-branch file pin must be an object.")
            source_path = row.get("source_path")
            destination_path = row.get("destination_path")
            source_blob = row.get("source_blob_sha")
            destination_blob = row.get("destination_blob_sha")
            if (
                not isinstance(source_path, str)
                or source_path.startswith("/")
                or ".." in Path(source_path).parts
                or not isinstance(destination_path, str)
                or not destination_path.startswith(prefix)
                or ".." in Path(destination_path).parts
                or not isinstance(source_blob, str)
                or not re.fullmatch(r"[0-9a-f]{40}", source_blob)
                or destination_blob != source_blob
            ):
                raise RuntimeError(f"Invalid or non-identical RiverShift archive blob pin: {destination_path!r}.")
            if destination_path in expected_paths:
                raise RuntimeError(f"Duplicate RiverShift archive destination: {destination_path}.")
            expected_paths.add(destination_path)
            if source_path.startswith(".github/workflows/"):
                active_copy = (
                    Path(__file__).resolve().parents[1]
                    / ".github"
                    / "workflows"
                    / Path(source_path).name
                )
                if active_copy.exists():
                    active_relative = f".github/workflows/{Path(source_path).name}"
                    active_entry = target_entries.get(active_relative)
                    if active_entry is None or active_entry[2] == source_blob:
                        raise RuntimeError(
                            f"Active RiverShift root workflow must be a distinct promoted port, not an identical archive copy: {active_copy}"
                        )
                    active_text = active_copy.read_text(encoding="utf-8")
                    if (
                        "workflow_dispatch:" not in active_text
                        or re.search(r"(?m)^\s*push\s*:", active_text)
                        or not re.search(r"MONOREPO_RIVERSHIFT_[A-Z0-9_]+", active_text)
                        or '!= "true"' not in active_text
                    ):
                        raise RuntimeError(
                            f"Promoted RiverShift root workflow is not manual-only and fail-closed: {active_copy}"
                        )
                    print(
                        f"SOURCE_BRANCH_ROOT_PORT_PASS {active_relative}: "
                        "distinct_blob manual_only fail_closed"
                    )
            actual = target_entries.get(destination_path)
            expected = ("100644", "blob", source_blob)
            if actual != expected:
                raise RuntimeError(
                    f"RiverShift source-branch archive blob mismatch: {destination_path}; "
                    f"expected={expected}; actual={actual}"
                )
            verified += 1
            print(f"SOURCE_BRANCH_ARCHIVE_BLOB_PASS {destination_path}: {source_blob}")

    archive_prefix = "migration/source-branch-snapshots/"
    actual_paths = {
        path for path in target_entries
        if path.startswith(archive_prefix) and path != (
            archive_prefix + "rivershift-validation-pins.json"
        )
    }
    missing = sorted(expected_paths - actual_paths)
    extra = sorted(actual_paths - expected_paths)
    if missing or extra:
        raise RuntimeError(
            f"RiverShift source-branch archive manifest mismatch: missing={missing[:10]}; extra={extra[:10]}"
        )
    print(
        f"SOURCE_BRANCH_ARCHIVE_MANIFEST_PASS files={verified} sources={len(sources)}; "
        "separate_root_ports=manual_only_fail_closed"
    )
    return verified

def main() -> int:
    target = git("rev-parse", "HEAD").decode("ascii").strip()
    target_entries = tree_entries(target)
    print(f"TARGET_COMMIT={target}")
    print(f"TARGET_TRACKED_ENTRIES={len(target_entries)}")

    total = 0
    archived_branch_files = verify_source_branch_archives(target_entries)
    for snapshot in SNAPSHOTS:
        # Divergent code pins can be preserved by their exact tree even when
        # their full commit history is not an ancestor of an imported branch.
        tree_revision = snapshot.source_tree_sha or snapshot.source_sha
        git("cat-file", "-e", f"{tree_revision}^{{tree}}")
        source_entries = tree_entries(tree_revision)
        prefix = snapshot.destination_prefix + "/"
        imported_entries = {
            path[len(prefix) :]: entry
            for path, entry in target_entries.items()
            if path.startswith(prefix)
        }

        missing = sorted(set(source_entries) - set(imported_entries))
        extra = sorted(set(imported_entries) - set(source_entries))
        changed = sorted(
            path
            for path in set(source_entries) & set(imported_entries)
            if source_entries[path] != imported_entries[path]
        )
        if missing or extra or changed:
            details = [
                f"{snapshot.label}: expected={len(source_entries)} imported={len(imported_entries)}",
                f"missing sample={missing[:10]}",
                f"extra sample={extra[:10]}",
                f"changed object sample={changed[:10]}",
            ]
            raise RuntimeError("; ".join(details))

        total += len(source_entries)
        source_identity = (
            f"commit={snapshot.source_sha} tree={tree_revision}"
            if snapshot.source_tree_sha
            else f"commit={snapshot.source_sha}"
        )
        print(
            f"SNAPSHOT_BLOB_INTEGRITY_PASS {snapshot.label}: "
            f"{len(source_entries)} entries {source_identity}"
        )

    promotion_overrides = load_promotion_overrides()
    used_promotion_overrides: set[str] = set()

    promoted_paths = (
        (
            "Dynamic frontend promotion",
            "migration/source-snapshots/dynamic/Frontend/",
            "apps/web/",
            (),
        ),
        (
            "Dynamic active API promotion",
            "migration/source-snapshots/dynamic/Backend/",
            "apps/api/",
            (),
        ),
        (
            "Dynamic shared tools promotion",
            "migration/source-snapshots/dynamic/tools/",
            "apps/tools/",
            (),
        ),
        (
            "Dynamic workflow compatibility promotion",
            "migration/source-snapshots/dynamic/.github/workflows/",
            "apps/.github/workflows/",
            (),
        ),
        (
            "Known Place PR #85 promotion (excluding separately pinned active generic runtime overlay)",
            "migration/source-snapshots/backend-known-place-pr85/",
            "engines/known-place/",
            (
                "tools/know_place/aoi_request.py",
                "tools/know_place/aoi_runner.py",
                "tools/know_place/geometry.py",
                "tools/know_place/series.py",
                "tools/know_place/upload_bundle_to_drive.py",
                "tools/tests/test_know_place_aoi_runner.py",
                "tools/tests/test_know_place_geometry.py",
                "tools/tests/test_know_place_series.py",
                "tools/tests/test_know_place_upload_bundle.py",
                "app/storage/drive_client.py",
            ),
        ),
        (
            "NISAR science promotion",
            "migration/source-snapshots/nisar-science/",
            "science/nisar-core/",
            (),
        ),
        (
            "Find Displacements dashboard promotion",
            "migration/source-snapshots/backend-main/dashboard/",
            "engines/find-displacements/dashboard/",
            (),
        ),
        (
            "Find Displacements tools promotion",
            "migration/source-snapshots/backend-main/tools/",
            "engines/find-displacements/tools/",
            ("river_shift/",),
        ),
        (
            "RiverShift GCOV engine promotion",
            "migration/source-snapshots/backend-main/tools/river_shift/",
            "engines/river-shift/tools/river_shift/",
            # These two Monorepo-only helpers are reviewed by the retained replay
            # contract suite below; the imported engine files remain byte-identical.
            ("replay_retained_run36_monorepo.py", "verify_monorepo_source_run.py"),
        ),
        (
            "Supabase configuration and migration promotion",
            "migration/source-snapshots/dynamic/Backend/supabase/",
            "infrastructure/supabase/",
            # These Monorepo-only additions are not source snapshot files:
            # - README.md documents the isolated target project and key setup.
            # - the retention migration is a separately reviewed forward migration.
            (
                "README.md",
                # SQL filenames are aligned to the target project's actual remote
                # migration timestamps; their unchanged source blobs are verified
                # against migration/supabase-history-alignment.json below.
                "migrations/",
            ),
        ),
    )
    for label, source_prefix, destination_prefix, excluded_prefixes in promoted_paths:
        source_view = {
            path[len(source_prefix) :]: entry
            for path, entry in target_entries.items()
            if path.startswith(source_prefix)
            and not any(
                path[len(source_prefix) :].startswith(excluded)
                for excluded in excluded_prefixes
            )
        }
        destination_view = {
            path[len(destination_prefix) :]: entry
            for path, entry in target_entries.items()
            if path.startswith(destination_prefix)
            and not any(
                path[len(destination_prefix) :].startswith(excluded)
                for excluded in excluded_prefixes
            )
        }
        missing = sorted(set(source_view) - set(destination_view))
        extra = sorted(set(destination_view) - set(source_view))
        changed = sorted(
            path
            for path in set(source_view) & set(destination_view)
            if source_view[path] != destination_view[path]
        )
        unapproved_changed: list[str] = []
        for relative_path in changed:
            override_key = f"{label}:{relative_path}"
            override = promotion_overrides.get(override_key)
            if override is None:
                unapproved_changed.append(relative_path)
                continue
            source_entry = source_view[relative_path]
            destination_entry = destination_view[relative_path]
            expected_source = (
                override["mode"], override["object_type"], override["source_blob_sha"]
            )
            expected_destination = (
                override["mode"], override["object_type"], override["destination_blob_sha"]
            )
            if source_entry != expected_source or destination_entry != expected_destination:
                unapproved_changed.append(relative_path)
                continue
            used_promotion_overrides.add(override_key)
            print(
                f"PROMOTED_PATH_OVERRIDE_PASS {override['destination_path']}: "
                f"{override['source_blob_sha']} -> {override['destination_blob_sha']}"
            )
        if missing or extra or unapproved_changed:
            raise RuntimeError(
                f"{label}: source={len(source_view)} destination={len(destination_view)}; "
                f"missing={missing[:10]}; extra={extra[:10]}; "
                f"unapproved_changed={unapproved_changed[:10]}"
            )
        if changed and label not in {
            "Dynamic active API promotion",
            "Dynamic frontend promotion",
            "Find Displacements tools promotion",
        }:
            raise RuntimeError(f"{label}: promotion overrides are not permitted for this source.")
        print(f"PROMOTED_PATH_BLOB_INTEGRITY_PASS {label}: {len(source_view)} entries")

    unused_overrides = sorted(set(promotion_overrides) - used_promotion_overrides)
    if unused_overrides:
        raise RuntimeError(f"Promotion override manifest contains stale or unapplied entries: {unused_overrides[:10]}")

    promoted_files = (
        (
            "Find Displacements dashboard workflow",
            "migration/source-snapshots/backend-main/.github/workflows/sarguardian-aoi-wkt-dashboard.yml",
            "engines/find-displacements/.github/workflows/sarguardian-aoi-wkt-dashboard.yml",
        ),
        (
            "Find Displacements reusable worker workflow",
            "migration/source-snapshots/backend-main/.github/workflows/sarguardian-aoi-product-worker.yml",
            "engines/find-displacements/.github/workflows/sarguardian-aoi-product-worker.yml",
        ),
        (
            "Find Displacements code-validation workflow",
            "migration/source-snapshots/backend-main/.github/workflows/sarguardian-aoi-code-validation.yml",
            "engines/find-displacements/.github/workflows/sarguardian-aoi-code-validation.yml",
        ),
        (
            "Find Displacements retained artifact smoke test fixture",
            "migration/source-snapshots/backend-main/.github/workflows/dashboard-real-artifact-smoke.yml",
            "engines/find-displacements/.github/workflows/dashboard-real-artifact-smoke.yml",
        ),
        (
            "Find Displacements Known Place AOI dispatcher compatibility fixture",
            "migration/source-snapshots/backend-main/.github/workflows/know-place-aoi-dispatcher.yml",
            "engines/find-displacements/.github/workflows/know-place-aoi-dispatcher.yml",
        ),
        (
            "Find Displacements Known Place paper dispatcher compatibility fixture",
            "migration/source-snapshots/backend-main/.github/workflows/know-place-paper-reproduction-dispatcher.yml",
            "engines/find-displacements/.github/workflows/know-place-paper-reproduction-dispatcher.yml",
        ),
        (
            "Find Displacements AOI WKT dispatcher compatibility fixture",
            "migration/source-snapshots/backend-main/.github/workflows/sarguardian-aoi-wkt-dispatcher.yml",
            "engines/find-displacements/.github/workflows/sarguardian-aoi-wkt-dispatcher.yml",
        ),
        (
            "RiverShift independent-reference validation fixture",
            "migration/source-snapshots/backend-main/.github/workflows/river-shift-independent-reference-validation.yml",
            "engines/river-shift/.github/workflows/river-shift-independent-reference-validation.yml",
        ),
        (
            "Find Displacements retained-artifact smoke workflow fixture",
            "migration/source-snapshots/backend-main/.github/workflows/dashboard-real-artifact-smoke.yml",
            "engines/find-displacements/.github/workflows/dashboard-real-artifact-smoke.yml",
        ),
        (
            "Known Place AOI dispatcher workflow fixture",
            "migration/source-snapshots/backend-main/.github/workflows/know-place-aoi-dispatcher.yml",
            "engines/find-displacements/.github/workflows/know-place-aoi-dispatcher.yml",
        ),
        (
            "Known Place author-exact dispatcher workflow fixture",
            "migration/source-snapshots/backend-main/.github/workflows/know-place-paper-reproduction-dispatcher.yml",
            "engines/find-displacements/.github/workflows/know-place-paper-reproduction-dispatcher.yml",
        ),
        (
            "Find Displacements AOI dispatcher workflow fixture",
            "migration/source-snapshots/backend-main/.github/workflows/sarguardian-aoi-wkt-dispatcher.yml",
            "engines/find-displacements/.github/workflows/sarguardian-aoi-wkt-dispatcher.yml",
        ),
        (
            "RiverShift GCOV workflow fixture",
            "migration/source-snapshots/backend-main/.github/workflows/river-shift-gcov-process.yml",
            "engines/river-shift/.github/workflows/river-shift-gcov-process.yml",
        ),
        (
            "RiverShift independent-reference workflow fixture",
            "migration/source-snapshots/backend-main/.github/workflows/river-shift-independent-reference-validation.yml",
            "engines/river-shift/.github/workflows/river-shift-independent-reference-validation.yml",
        ),
        (
            "Find Displacements development requirements",
            "migration/source-snapshots/backend-main/requirements-dev.txt",
            "engines/find-displacements/requirements-dev.txt",
        ),
        (
            "Find Displacements runtime requirements",
            "migration/source-snapshots/backend-main/requirements.txt",
            "engines/find-displacements/requirements.txt",
        ),
        (
            "Supabase CLI configuration",
            "migration/source-snapshots/dynamic/Backend/supabase/config.toml",
            "infrastructure/supabase/config.toml",
        ),
    )
    for label, source_path, destination_path in promoted_files:
        if source_path not in target_entries or destination_path not in target_entries:
            raise RuntimeError(f"{label}: source or destination file is missing")
        if target_entries[source_path] != target_entries[destination_path]:
            raise RuntimeError(f"{label}: source and destination Git objects differ")
        print(f"PROMOTED_FILE_BLOB_INTEGRITY_PASS {label}")

    alignment_path = Path(__file__).resolve().parents[1] / "migration" / "supabase-history-alignment.json"
    alignment = json.loads(alignment_path.read_text(encoding="utf-8"))
    if alignment.get("schema_version") != 1:
        raise RuntimeError("Supabase history alignment manifest has an unsupported schema.")
    if alignment.get("project_ref") != "qbmhpdprvxssqinnommz":
        raise RuntimeError("Supabase history alignment manifest targets the wrong project.")
    migration_records = alignment.get("records")
    if not isinstance(migration_records, list) or len(migration_records) != 12:
        raise RuntimeError("Supabase history alignment must contain exactly twelve remote migrations.")

    expected_sql_paths: set[str] = set()
    seen_versions: set[str] = set()
    seen_names: set[str] = set()
    for record in migration_records:
        version = str(record.get("remote_version", ""))
        name = str(record.get("remote_name", ""))
        destination_path = str(record.get("destination_path", ""))
        blob_sha = str(record.get("blob_sha", ""))
        if not re.fullmatch(r"[0-9]{14}", version):
            raise RuntimeError(f"Supabase migration has an invalid remote version: {version}")
        if not name or "/" in name or not re.fullmatch(r"[a-zA-Z0-9_]+", name):
            raise RuntimeError(f"Supabase migration has an invalid remote name: {name}")
        if version in seen_versions or name in seen_names:
            raise RuntimeError(f"Supabase migration version/name is duplicated: {version} / {name}")
        seen_versions.add(version)
        seen_names.add(name)
        expected_path = f"infrastructure/supabase/migrations/{version}_{name}.sql"
        if destination_path != expected_path:
            raise RuntimeError(
                f"Supabase migration filename does not match its remote history: {destination_path}; "
                f"expected={expected_path}"
            )
        expected_sql_paths.add(destination_path)
        destination_entry = target_entries.get(destination_path)
        if destination_entry != ("100644", "blob", blob_sha):
            raise RuntimeError(
                f"Supabase migration destination blob mismatch: {destination_path}; "
                f"expected={blob_sha}; actual={destination_entry}"
            )

        source_path = record.get("source_path")
        if source_path:
            source_entry = target_entries.get(str(source_path))
            if source_entry != destination_entry:
                raise RuntimeError(
                    f"Supabase source SQL blob changed while aligning remote filename: "
                    f"{source_path} -> {destination_path}"
                )
        elif record.get("kind") != "monorepo-forward-migration":
            raise RuntimeError(f"Supabase migration lacks source provenance or forward-migration label: {destination_path}")

        print(
            f"SUPABASE_MIGRATION_HISTORY_ALIGNMENT_PASS version={version} "
            f"name={name} blob={blob_sha}"
        )

    actual_sql_paths = {
        path for path in target_entries
        if path.startswith("infrastructure/supabase/migrations/") and path.endswith(".sql")
    }
    if actual_sql_paths != expected_sql_paths:
        raise RuntimeError(
            "Supabase migration directory differs from the twelve-record remote alignment manifest: "
            f"missing={sorted(expected_sql_paths - actual_sql_paths)}; "
            f"extra={sorted(actual_sql_paths - expected_sql_paths)}"
        )
    print(
        f"SUPABASE_REMOTE_HISTORY_FILENAME_ALIGNMENT_PASS "
        f"project={alignment['project_ref']} migrations={len(expected_sql_paths)}"
    )

    for label, ancestor, descendant in ANCESTOR_CHECKS:
        check_ancestor(label, ancestor, descendant)

    print(
        f"ALL_SNAPSHOT_BLOB_INTEGRITY_PASS total_entries={total} "
        f"source_branch_archive_files={archived_branch_files}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
