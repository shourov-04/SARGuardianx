#!/usr/bin/env python3
"""Find commit-like source pins embedded in imported SARGuardian snapshots."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = ROOT / "migration" / "source-snapshots"
TEXT_SUFFIXES = {
    ".py", ".yml", ".yaml", ".json", ".md", ".txt", ".toml", ".ini",
    ".cfg", ".sh", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
}
SHA_RE = re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
PIN_CONTEXT_RE = re.compile(
    r"(?i)\b(ref|revision|commit|science[_-]?ref|source[_-]?ref|git[_-]?ref|checkout|sha)\b"
)


def main() -> int:
    if not SNAPSHOT_ROOT.is_dir():
        raise SystemExit(f"Missing snapshot directory: {SNAPSHOT_ROOT}")

    candidates: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
    scanned = 0
    unreadable = []

    for path in sorted(SNAPSHOT_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            unreadable.append((str(path.relative_to(ROOT)), str(exc)))
            continue
        scanned += 1
        for number, line in enumerate(text.splitlines(), start=1):
            if not PIN_CONTEXT_RE.search(line):
                continue
            for match in SHA_RE.finditer(line):
                sha = match.group(0).lower()
                excerpt = " ".join(line.strip().split())[:240]
                candidates[sha].append((str(path.relative_to(ROOT)), number, excerpt))

    print(f"SCANNED_TEXT_FILES={scanned}")
    print(f"UNREADABLE_TEXT_FILES={len(unreadable)}")
    print(f"PIN_CANDIDATE_SHA_COUNT={len(candidates)}")
    for sha, contexts in sorted(candidates.items()):
        print(f"PIN_CANDIDATE {sha} references={len(contexts)}")
        for path, line, excerpt in contexts[:4]:
            print(f"  {path}:{line}: {excerpt}")

    for path, error in unreadable[:20]:
        print(f"UNREADABLE {path}: {error}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
