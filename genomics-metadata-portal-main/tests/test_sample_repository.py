from __future__ import annotations

from app.db import SessionLocal
from app.repositories.sample_repository import SampleRepository


def test_list_samples_returns_rows() -> None:
    with SessionLocal() as session:
        repo = SampleRepository(session)
        rows = repo.list_samples(limit=10)

    assert len(rows) > 0
    assert "sample_id" in rows[0]
    assert "disease_type" in rows[0]


def test_sample_detail_provenance_qc_and_variants() -> None:
    with SessionLocal() as session:
        repo = SampleRepository(session)
        samples = repo.list_samples(limit=1)
        assert samples, "No sample rows returned"

        sample_id = samples[0]["sample_id"]

        detail = repo.get_sample_detail(sample_id)
        provenance = repo.get_sample_provenance(sample_id)
        qc_results = repo.get_sample_qc_results(sample_id)
        variants = repo.get_sample_variants(sample_id)

    assert detail is not None
    assert detail["sample_id"] == sample_id
    assert "sequencing" in provenance
    assert "pipeline_runs" in provenance
    assert isinstance(qc_results, list)
    assert isinstance(variants, list)