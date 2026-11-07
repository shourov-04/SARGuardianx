# Historical secret scan report

**Latest scan:** [GitHub Actions run 41964653151](https://github.com/moshiour0/SARGuardian-Monorepo/actions/runs/41964653151)  
**Scanned commit:** `0550110584726ac873f0c0b87a623c1674bfd091`  
**Result:** PASS — zero findings after exact reviewed-fingerprint suppression.

## Method

- Gitleaks CLI `8.30.1`, downloaded from its official release.
- Linux x64 archive SHA-256 is pinned in `tools/scan_git_history_for_secrets.sh`.
- Full-depth checkout; scan command uses `gitleaks git --log-opts=--all`, so the scan covers commits reachable from the repository refs fetched into the runner, including imported source commit histories.
- Reports are written only to runner temporary storage and deleted on exit.
- Log output contains only rule ID, file path, line, commit, and fingerprint. It never prints the matched value, secret, author email, or raw JSON report.

## Reviewed findings

The initial full-history scan surfaced 20 `generic-api-key` matches. Each occurrence was inspected in source context. They resolve to:
- deterministic test-only idempotency and displacement-job identifiers;
- an explicit dummy Google Maps test stub containing a `DUMMY` marker;
- test fixture lines that the detector associated with those values.

No match was identified as a production credential. No token or key value is reproduced in this report.

The repository uses `.gitleaksignore` only for the 20 exact `commit:path:rule:line` fingerprints reviewed above. It does **not** suppress an entire test directory, rule, file, or commit. A new finding in the same file at another line, a new commit, or a different rule remains reportable.

## Result and ongoing controls

- [x] Full-history scan passed with `SECRET_SCAN_FINDING_COUNT=0`.
- [x] The scan tool version and binary checksum are pinned.
- [x] Finding values are not emitted to GitHub Actions logs or artifacts.
- [x] Exact finding fingerprints, rather than broad path allowlists, are used.
- [ ] Re-run full-history Gitleaks after every source import or history rewrite.
- [ ] Rotate any credential immediately if future review identifies a real secret; an allowlist is never a substitute for rotation.

This result is a scan of the current Monorepo's reachable history and reviewed synthetic test fixtures. It is not a claim that all external source-repository refs or GitHub/Vercel secret stores have been scanned.
