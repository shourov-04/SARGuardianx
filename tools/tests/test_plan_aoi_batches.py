from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plan_aoi_batches import build_batches, primary_runner_count  # noqa: E402


def products(count: int) -> list[dict]:
    return [
        {
            "id": f"GUNW-{index + 1:03d}",
            "granule_name": f"NISAR_L2_PR_GUNW_TEST_{index + 1:03d}",
            "product_type": "GUNW",
            "maturity": "PROVISIONAL",
            "expected_source_bytes": 1000 + index,
        }
        for index in range(count)
    ]


@pytest.mark.parametrize(
    ("count", "expected_runners", "sizes"),
    [
        (1, 1, [1]),
        (2, 1, [2]),
        (3, 1, [3]),
        (9, 3, [3, 3, 3]),
        (29, 9, [4, 4, 3, 3, 3, 3, 3, 3, 3]),
        (30, 10, [3] * 10),
        (40, 10, [4] * 10),
        (43, 10, [5, 5, 5, 4, 4, 4, 4, 4, 4, 4]),
        (200, 10, [20] * 10),
    ],
)
def test_balanced_primary_runner_distribution(count, expected_runners, sizes):
    rows = products(count)
    batches = build_batches(rows)
    assert primary_runner_count(count) == expected_runners
    assert [batch["product_count"] for batch in batches] == sizes
    assert [row["id"] for batch in batches for row in batch["products"] if row["present"]] == [
        row["id"] for row in rows
    ]
    assert all(len(batch["products"]) == 20 for batch in batches)


def test_duplicate_product_identity_is_rejected():
    rows = products(3)
    rows[2]["id"] = rows[0]["id"]
    with pytest.raises(ValueError, match="BATCH_PRODUCT_ID_DUPLICATE"):
        build_batches(rows)
