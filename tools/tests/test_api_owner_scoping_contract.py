from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from app.persistence import SupabaseJobStore


class RecordingQuery:
    def __init__(self, table_name: str) -> None:
        self.table_name = table_name
        self.filters: list[tuple[str, object]] = []

    def select(self, _columns: str) -> "RecordingQuery":
        return self

    def eq(self, column: str, value: object) -> "RecordingQuery":
        self.filters.append((column, value))
        return self

    def in_(self, column: str, values: list[object]) -> "RecordingQuery":
        self.filters.append((column, tuple(values)))
        return self

    def order(self, _column: str, *, desc: bool = False) -> "RecordingQuery":
        return self

    def limit(self, _count: int) -> "RecordingQuery":
        return self

    def execute(self) -> SimpleNamespace:
        return SimpleNamespace(data=[])


class RecordingClient:
    def __init__(self) -> None:
        self.queries: list[RecordingQuery] = []

    def table(self, table_name: str) -> RecordingQuery:
        query = RecordingQuery(table_name)
        self.queries.append(query)
        return query


def test_every_user_facing_job_read_filters_by_firebase_owner_uid() -> None:
    """The server client uses service_role (BYPASSRLS), so API-side owner scoping is mandatory."""
    owner_uid = "firebase-user-a"
    job_id = uuid4()
    preflight_id = uuid4()
    client = RecordingClient()
    store = SupabaseJobStore(client, preflight_ttl_seconds=86_400)

    owner_reads = [
        ("catalog_preflights", lambda: store.get_preflight(owner_uid, preflight_id)),
        ("processing_jobs", lambda: store.get_job_by_idempotency(owner_uid, "idempotency-key-0001")),
        ("processing_jobs", lambda: store.list_jobs(owner_uid)),
        ("processing_jobs", lambda: store.get_job(owner_uid, job_id)),
        ("displacement_jobs", lambda: store.get_displacement_job_by_idempotency(owner_uid, "idempotency-key-0002")),
        ("displacement_jobs", lambda: store.list_displacement_jobs(owner_uid)),
        ("displacement_jobs", lambda: store.find_active_displacement_job(owner_uid, "POLYGON EMPTY", "2026-01-01", "2026-01-02")),
        ("displacement_jobs", lambda: store.list_active_displacement_jobs(owner_uid)),
        ("displacement_jobs", lambda: store.get_displacement_job(owner_uid, job_id)),
        ("river_shift_jobs", lambda: store.get_river_shift_job_by_idempotency(owner_uid, "idempotency-key-0003")),
        ("river_shift_jobs", lambda: store.list_river_shift_jobs(owner_uid)),
        ("river_shift_jobs", lambda: store.list_active_river_shift_jobs(owner_uid)),
        ("river_shift_jobs", lambda: store.get_river_shift_job(owner_uid, job_id)),
    ]

    for expected_table, read in owner_reads:
        read()
        query = client.queries[-1]
        assert query.table_name == expected_table
        assert ("owner_uid", owner_uid) in query.filters, (
            f"{expected_table} owner-facing read omitted owner_uid={owner_uid}"
        )

    assert len(client.queries) == len(owner_reads) == 13
