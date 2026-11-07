# Upstream displacement engine import

The Find Displacements runtime in this monorepo is copied from the successful
upstream SARGuardian-Monorepo revision used by GitHub Actions run
`42349556965`.

- Source repository: `moshiour0/SARGuardian-Monorepo`
- Source commit: `2cb521ea11376b2f48e903fb00b0c480796d6578`
- Imported engine: `engines/find-displacements/`
- Imported canonical worker: `.github/workflows/sarguardian-aoi-product-worker.yml`
- Imported immutable science snapshot:
  `migration/source-snapshots/nisar-pins/006d4cd/`
- Science source commit:
  `006d4cd1485cf80e509eaf8717c12e9c6390ac09`

The engine and immutable science snapshot are unmodified upstream files. The
repository-specific scheduling wrapper adds the requested execution policy:

1. Balance products across at most ten primary runners, with at least three
   products per runner when there are enough products.
2. Run each primary runner's assigned products sequentially.
3. Retry a failed product once on its original runner.
4. Audit the per-product receipts after both primary attempts.
5. Send only products that remain incomplete to one final recovery runner for
   one last attempt.

The reusable batch and recovery workflows are generated from the imported
canonical one-product worker by `scripts/generate_aoi_batch_assets.py`. This
keeps every per-product science, retention, validation, and cleanup step aligned
with the upstream engine while changing only runner allocation.
