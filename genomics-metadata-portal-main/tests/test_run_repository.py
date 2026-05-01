from __future__ import annotations

from app.db import SessionLocal
from app.repositories.run_repository import RunRepository


def test_list_runs_returns_rows() -> None:
    with SessionLocal() as session:
        repo = RunRepository(session)
        rows = repo.list_runs(limit=10)

    assert len(rows) > 0
    assert "pipeline_run_id" in rows[0]
    assert "run_status" in rows[0]


def test_run_detail_and_provenance() -> None:
    with SessionLocal() as session:
        repo = RunRepository(session)
        rows = repo.list_runs(limit=1)
        assert rows, "No pipeline runs returned"

        pipeline_run_id = rows[0]["pipeline_run_id"]
        detail = repo.get_run_detail(pipeline_run_id)
        provenance = repo.get_run_provenance(pipeline_run_id)

    assert detail is not None
    assert detail["pipeline_run_id"] == pipeline_run_id
    assert "references" in provenance
    assert "tools" in provenance
    assert isinstance(provenance["references"], list)
    assert isinstance(provenance["tools"], list)