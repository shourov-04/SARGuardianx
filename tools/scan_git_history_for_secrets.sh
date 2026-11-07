#!/usr/bin/env bash
# Scan all commits reachable from all refs in this checkout.
# Findings are redacted and summarized without exposing Match/Secret fields.

set -euo pipefail

VERSION="8.30.1"
ASSET="gitleaks_${VERSION}_linux_x64.tar.gz"
EXPECTED_SHA256="551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
BASE_URL="https://github.com/gitleaks/gitleaks/releases/download/v${VERSION}"
WORK_DIR="$(mktemp -d)"
REPORT_PATH="$RUNNER_TEMP/sarguardian-gitleaks-history.json"
trap 'rm -rf "$WORK_DIR"; rm -f "$REPORT_PATH"' EXIT

echo "Downloading pinned Gitleaks ${VERSION}"
curl --fail --silent --show-error --location "${BASE_URL}/${ASSET}" --output "${WORK_DIR}/${ASSET}"
printf '%s  %s\n' "$EXPECTED_SHA256" "${WORK_DIR}/${ASSET}" | sha256sum --check --status

tar -xzf "${WORK_DIR}/${ASSET}" -C "$WORK_DIR" gitleaks
GITLEAKS="$WORK_DIR/gitleaks"
"$GITLEAKS" version

echo "Scanning all commits reachable from all fetched refs; values are redacted."
set +e
"$GITLEAKS" git \
  --redact \
  --exit-code=1 \
  --report-format=json \
  --report-path="$REPORT_PATH" \
  --log-opts=--all \
  .
SCAN_STATUS=$?
set -e

if [[ -f "$REPORT_PATH" ]]; then
  python3 - "$REPORT_PATH" <<'PY'
import json
import sys
from pathlib import Path

report_path = Path(sys.argv[1])
try:
    data = json.loads(report_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"SECRET_SCAN_REPORT_PARSE_ERROR={type(exc).__name__}")
    raise SystemExit(2)

if not isinstance(data, list):
    print("SECRET_SCAN_REPORT_INVALID_FORMAT")
    raise SystemExit(2)

print(f"SECRET_SCAN_FINDING_COUNT={len(data)}")
for finding in data:
    if not isinstance(finding, dict):
        continue
    rule = str(finding.get("RuleID", "unknown"))[:100]
    file_path = str(finding.get("File", "unknown"))[:300]
    line = finding.get("StartLine", "unknown")
    commit = str(finding.get("Commit", "unknown"))[:40]
    fingerprint = str(finding.get("Fingerprint", "unknown"))[:240]
    # Never print Description, Match, Secret, Author, Email, or raw report JSON.
    print(
        f"FINDING rule={rule} file={file_path} line={line} "
        f"commit={commit} fingerprint={fingerprint}"
    )
PY
else
  echo "SECRET_SCAN_REPORT_NOT_CREATED"
fi

if [[ "$SCAN_STATUS" -ne 0 ]]; then
  echo "SECRET_SCAN_FAILED: review redacted file/line/commit references; do not copy secret values into logs."
  exit "$SCAN_STATUS"
fi

echo "SECRET_SCAN_PASS: no Gitleaks findings in reachable repository history."
