#!/usr/bin/env python3
"""Build balanced primary-runner batches for the dynamic AOI workflow."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

MAX_PRIMARY_RUNNERS = 10
MIN_PRODUCTS_PER_RUNNER = 3
MAX_PRODUCTS = 200
MAX_PRODUCTS_PER_RUNNER = MAX_PRODUCTS // MAX_PRIMARY_RUNNERS


def _product(row: Any) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("BATCH_PRODUCT_NOT_AN_OBJECT")
    required = ("id", "granule_name", "product_type", "maturity", "expected_source_bytes")
    if any(row.get(key) in (None, "") for key in required):
        raise ValueError("BATCH_PRODUCT_REQUIRED_FIELD_MISSING")
    return {key: row[key] for key in required}


def primary_runner_count(product_count: int) -> int:
    if product_count < 0 or product_count > MAX_PRODUCTS:
        raise ValueError("BATCH_PRODUCT_COUNT_OUT_OF_RANGE")
    if product_count == 0:
        return 0
    return min(MAX_PRIMARY_RUNNERS, max(1, product_count // MIN_PRODUCTS_PER_RUNNER))


def build_batches(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = [_product(row) for row in products]
    if len({row["id"] for row in normalized}) != len(normalized):
        raise ValueError("BATCH_PRODUCT_ID_DUPLICATE")
    worker_count = primary_runner_count(len(normalized))
    if not worker_count:
        return []
    base, extra = divmod(len(normalized), worker_count)
    batches: list[dict[str, Any]] = []
    offset = 0
    for index in range(worker_count):
        size = base + (1 if index < extra else 0)
        assigned = normalized[offset:offset + size]
        offset += size
        padded = [dict(row, present=True) for row in assigned]
        padded.extend({"present": False} for _ in range(MAX_PRODUCTS_PER_RUNNER - size))
        batches.append({
            "batch_id": f"primary-{index + 1:02d}",
            "batch_index": index + 1,
            "product_count": size,
            "products": padded,
        })
    if offset != len(normalized):
        raise AssertionError("BATCH_ASSIGNMENT_INCOMPLETE")
    if len(normalized) >= MIN_PRODUCTS_PER_RUNNER and any(
        batch["product_count"] < MIN_PRODUCTS_PER_RUNNER for batch in batches
    ):
        raise AssertionError("BATCH_MINIMUM_PRODUCT_COUNT_VIOLATED")
    return batches


def plan(manifest: dict[str, Any]) -> dict[str, Any]:
    products = manifest.get("products")
    if not isinstance(products, list) or not products:
        raise ValueError("BATCH_MANIFEST_PRODUCTS_MISSING")
    batches = build_batches(products)
    counts = [batch["product_count"] for batch in batches]
    return {
        "schema_version": "sarguardian-primary-runner-plan/1.0",
        "product_count": len(products),
        "runner_count": len(batches),
        "minimum_products_per_runner": min(counts),
        "maximum_products_per_runner": max(counts),
        "batches": batches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = plan(json.loads(args.manifest.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            output.write("batch_matrix=" + json.dumps(result["batches"], separators=(",", ":")) + "\n")
            output.write(f"batch_count={result['runner_count']}\n")
            output.write(f"max_batch_size={result['maximum_products_per_runner']}\n")
    print(
        "PRIMARY_BATCH_PLAN "
        f"products={result['product_count']} runners={result['runner_count']} "
        f"min={result['minimum_products_per_runner']} max={result['maximum_products_per_runner']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
