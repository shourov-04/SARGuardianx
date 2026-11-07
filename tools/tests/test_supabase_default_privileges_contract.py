from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "infrastructure/supabase/migrations/20261106064055_20261106100000_public_default_privileges_hardening.sql"


def test_default_privilege_migration_is_narrow_and_service_role_preserving() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")
    normalized = re.sub(r"--[^\n]*", "", sql).lower()
    normalized = re.sub(r"\s+", " ", normalized).strip()

    expected = (
        "alter default privileges for role postgres in schema public "
        "revoke all on tables from anon, authenticated",
        "alter default privileges for role postgres in schema public "
        "revoke all on sequences from anon, authenticated",
        "alter default privileges for role postgres in schema public "
        "revoke execute on functions from anon, authenticated",
        "alter default privileges for role postgres "
        "revoke execute on functions from public",
    )
    for statement in expected:
        assert statement in normalized

    # The migration must not attempt to change Supabase-managed objects or
    # take away the server API's explicitly retained service_role defaults.
    assert "for role supabase_admin" not in normalized
    assert not re.search(r"\brevoke\b[^;]*\bservice_role\b", normalized)
    assert "alter default privileges" in normalized
    assert normalized.startswith("begin;")
    assert normalized.endswith("commit;")
