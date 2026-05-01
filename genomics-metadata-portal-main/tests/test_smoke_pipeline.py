from __future__ import annotations

from sqlalchemy import text

from app.db import SessionLocal


def test_database_connectivity() -> None:
    with SessionLocal() as session:
        result = session.execute(text("SELECT 1")).scalar_one()
        assert result == 1


def test_core_table_counts_present() -> None:
    expected_minimums = {
        "patients": 50,
        "samples": 85,
        "sequencing_runs": 6,
        "pipeline_runs": 105,
        "file_assets": 280,
        "qc_results": 319,
        "variant_summary": 220,
    }

    with SessionLocal() as session:
        for table_name, minimum_count in expected_minimums.items():
            count = session.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar_one()
            assert count >= minimum_count, f"{table_name} count {count} < {minimum_count}"