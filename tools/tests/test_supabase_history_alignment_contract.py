from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "migration/supabase-history-alignment.json"
MIGRATION_DIR = ROOT / "infrastructure/supabase/migrations"


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}".encode("ascii") + bytes([0])
    return hashlib.sha1(header + data).hexdigest()


def test_monorepo_local_migration_versions_match_remote_history_and_exact_sql_blobs() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["project_ref"] == "qbmhpdprvxssqinnommz"
    records = manifest["records"]
    assert len(records) == 12

    paths = set()
    versions = set()
    names = set()
    for record in records:
        version = record["remote_version"]
        name = record["remote_name"]
        path = record["destination_path"]
        assert len(version) == 14 and version.isdigit()
        assert path == f"infrastructure/supabase/migrations/{version}_{name}.sql"
        assert version not in versions
        assert name not in names
        versions.add(version)
        names.add(name)
        paths.add(path)

        destination = (ROOT / path).read_bytes()
        assert git_blob_sha(destination) == record["blob_sha"]
        if record["source_path"]:
            source = (ROOT / record["source_path"]).read_bytes()
            assert source == destination
            assert git_blob_sha(source) == record["blob_sha"]
        else:
            assert record["kind"] == "monorepo-forward-migration"

    actual = {
        str(path.relative_to(ROOT))
        for path in MIGRATION_DIR.glob("*.sql")
    }
    assert actual == paths
