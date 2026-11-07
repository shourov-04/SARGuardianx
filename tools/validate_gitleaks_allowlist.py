#!/usr/bin/env python3
"""Keep Gitleaks false-positive exceptions exact and narrowly reviewed."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / ".gitleaksignore"
EXPECTED_COUNT = 21
EXPECTED_TEST_COUNT = 20
DOCUMENTATION_FALSE_POSITIVE = "c246f3b16a5b7320ab97250f202847b9f4d5c8c2:docs/migration/active-runtime-scope-2026-11-06.md:generic-api-key:43"
FINGERPRINT_RE = re.compile(
    r"^(?P<commit>[0-9a-f]{40}):(?P<path>[A-Za-z0-9_./-]+):"
    r"(?P<rule>generic-api-key):(?P<line>[1-9][0-9]*)$"
)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not ALLOWLIST.is_file():
        fail("Missing .gitleaksignore")

    entries = [
        line.strip()
        for line in ALLOWLIST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(entries) != EXPECTED_COUNT:
        fail(f"Expected exactly {EXPECTED_COUNT} reviewed fingerprints, found {len(entries)}")
    if len(set(entries)) != len(entries):
        fail("Duplicate fingerprints are not allowed")

    for number, entry in enumerate(entries, start=1):
        match = FINGERPRINT_RE.fullmatch(entry)
        if not match:
            fail(f"Fingerprint {number} does not match the approved exact format")
        path = match.group("path")
        if ".." in Path(path).parts:
            fail(f"Fingerprint {number} contains path traversal")
        if entry == DOCUMENTATION_FALSE_POSITIVE:
            continue
        is_test_path = (
            "/tests/" in f"/{path}"
            or path.endswith((".test.ts", ".test.tsx", ".test.js", ".test.mjs"))
        )
        if not is_test_path:
            fail(f"Fingerprint {number} is outside an approved test file or the single exact documentation false-positive")
    if entries.count(DOCUMENTATION_FALSE_POSITIVE) != 1:
        fail("The single reviewed documentation false-positive fingerprint must appear exactly once")
    if sum(entry != DOCUMENTATION_FALSE_POSITIVE for entry in entries) != EXPECTED_TEST_COUNT:
        fail(f"Expected exactly {EXPECTED_TEST_COUNT} synthetic test-fixture fingerprints")

    print(
        "GITLEAKS_ALLOWLIST_VALID: "
        f"{EXPECTED_TEST_COUNT} exact synthetic test-fixture fingerprints and one exact reviewed documentation false-positive; "
        "no directory-wide or rule-wide ignores."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
