#!/usr/bin/env python3
"""Re-run the historical Run #36 area benchmark from Monorepo-retained GCOV COGs.

This is a new retrospective replay using current RiverShift science functions;
it is not the original Run #36 worker artifact. The original displayed metrics
remain an immutable comparison baseline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import replay_retained_run36 as original


LEGACY_REFERENCE = {
    "repository": "moshiour0/SARGuardian-backend",
    "run_id": 41803576163,
    "run_number": 36,
    "job_id": "4e6e4071-fb9d-4e20-a331-867f3f2bd88f",
    "metrics": original.ORIGINAL_METRICS,
}


def _find_prepared(root: Path) -> Path:
    matches = sorted(root.rglob("prepared.json"))
    if len(matches) != 1:
        raise ValueError(f"Expected one prepared.json; found {len(matches)}")
    return matches[0]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def replay_monorepo(
    *,
    prepared_root: Path,
    products_root: Path,
    output_root: Path,
    source_run_id: int,
    source_run_number: int,
    source_job_id: str,
) -> dict:
    if source_run_id < 1 or source_run_number < 1:
        raise ValueError("Monorepo source run ID and run number must be positive.")
    source_job_id = str(UUID(source_job_id))
    prepared_path = _find_prepared(prepared_root)
    prepared = original._json(prepared_path)
    if prepared.get("job_id") != source_job_id:
        raise ValueError("Prepared RiverShift job UUID does not match the requested source job.")
    names = prepared.get("selected_product_names")
    dates = prepared.get("date_by_name")
    if not isinstance(names, list) or len(names) != 6 or len(set(names)) != 6:
        raise ValueError("Run #36 benchmark replay requires exactly six distinct retained GCOV granules.")
    if not isinstance(dates, dict) or set(names) != set(dates):
        raise ValueError("Prepared product/date mapping is incomplete for the six-granule benchmark.")
    retained_cogs = list(products_root.rglob("*.tif"))
    if len(retained_cogs) != 6:
        raise ValueError(f"Expected exactly six retained COGs, found {len(retained_cogs)}.")

    request = prepared.get("request") or {}
    if (
        request.get("analysis_mode") != "event_based"
        or request.get("maturity") != "PROVISIONAL"
        or request.get("frequency") != "frequencyA"
        or request.get("term") != "HHHH"
        or request.get("threshold_method") != "otsu"
    ):
        raise ValueError("Retained inputs do not meet the historical Run #36 event-based product/threshold contract.")

    # Set source provenance for the canonical replay function. Its scientific
    # functions and original comparison metrics remain unchanged.
    original.SOURCE_RUN_ID = source_run_id
    original.SOURCE_RUN_NUMBER = source_run_number
    original.SOURCE_JOB_ID = source_job_id
    result = original.replay(prepared_root, products_root, output_root)

    manifest_path = output_root / "run36_retrospective_overlap_replay.json"
    manifest = original._json(manifest_path)
    manifest["source_run"]["repository"] = "moshiour0/SARGuardian-Monorepo"
    manifest["source_run"]["run_id"] = source_run_id
    manifest["source_run"]["run_number"] = source_run_number
    manifest["source_run"]["job_id"] = source_job_id
    manifest["source_run"]["source_run_head"] = "Monorepo RiverShift GCOV retained-artifact replay"
    manifest["historical_reference"] = {
        "label": "Original RiverShift Run #36 displayed area metrics",
        "original_repository": LEGACY_REFERENCE["repository"],
        "original_run_id": LEGACY_REFERENCE["run_id"],
        "original_run_number": LEGACY_REFERENCE["run_number"],
        "original_job_id": LEGACY_REFERENCE["job_id"],
        "comparison_metrics": LEGACY_REFERENCE["metrics"],
        "note": "These values are comparison baselines only; source COGs in this replay were retained by the Monorepo run above.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    manifest_sha = _sha256(manifest_path)
    manifest_path.with_suffix(".json.sha256").write_text(
        f"{manifest_sha}  {manifest_path.name}\n",
        encoding="utf-8",
    )
    result["manifest_sha256"] = manifest_sha
    result["source_run_id"] = source_run_id
    result["source_job_id"] = source_job_id
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared-root", required=True, type=Path)
    parser.add_argument("--products-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--source-run-id", required=True, type=int)
    parser.add_argument("--source-run-number", required=True, type=int)
    parser.add_argument("--source-job-id", required=True)
    args = parser.parse_args()
    try:
        result = replay_monorepo(
            prepared_root=args.prepared_root,
            products_root=args.products_root,
            output_root=args.output_root,
            source_run_id=args.source_run_id,
            source_run_number=args.source_run_number,
            source_job_id=args.source_job_id,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"RIVERSHIFT_RUN36_REPLAY=FAIL reason={type(exc).__name__}:{exc}", flush=True)
        return 1
    status = result["area_reproduction"]["status"]
    print("RIVERSHIFT_RUN36_REPLAY_STATUS=" + status, flush=True)
    print("RIVERSHIFT_RUN36_SOURCE_JOB_ID=" + args.source_job_id, flush=True)
    print("RIVERSHIFT_RUN36_REPLAY_MANIFEST_SHA256=" + result["manifest_sha256"], flush=True)
    return 0 if status == "EXACT_AREA_REPRODUCTION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
