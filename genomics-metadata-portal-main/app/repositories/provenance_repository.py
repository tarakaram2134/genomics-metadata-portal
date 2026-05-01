from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FileAsset, QcResult, Sample, VariantSummary
from app.repositories.sample_repository import SampleRepository


class ProvenanceRepository:
    """
    Repository for provenance-trace workflows.

    Builds on sample-centric provenance and adds downstream file/QC/variant context.
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self.sample_repo = SampleRepository(session)

    def list_sample_ids(self, limit: int = 500) -> list[str]:
        rows = self.session.scalars(
            select(Sample.sample_id).order_by(Sample.sample_id).limit(limit)
        ).all()
        return [row for row in rows if row]

    def get_sample_trace(self, sample_id: str) -> dict[str, Any]:
        detail = self.sample_repo.get_sample_detail(sample_id)
        provenance = self.sample_repo.get_sample_provenance(sample_id)

        file_assets = self.session.execute(
            select(
                FileAsset.file_asset_id,
                FileAsset.pipeline_run_id,
                FileAsset.file_role,
                FileAsset.file_format,
                FileAsset.path_uri,
                FileAsset.is_current,
                FileAsset.created_at,
            )
            .where(FileAsset.sample_id == sample_id)
            .order_by(
                FileAsset.is_current.desc(),
                FileAsset.created_at.desc(),
                FileAsset.file_asset_id,
            )
        ).all()

        qc_results = self.session.execute(
            select(
                QcResult.qc_result_id,
                QcResult.pipeline_run_id,
                QcResult.qc_metric_def_id,
                QcResult.qc_status,
                QcResult.measured_at,
                QcResult.source_file_asset_id,
            )
            .where(QcResult.sample_id == sample_id)
            .order_by(QcResult.measured_at.desc(), QcResult.qc_result_id)
        ).all()

        variants = self.session.execute(
            select(
                VariantSummary.variant_summary_id,
                VariantSummary.pipeline_run_id,
                VariantSummary.gene_symbol,
                VariantSummary.protein_change,
                VariantSummary.clinical_significance,
                VariantSummary.reported_flag,
                VariantSummary.source_file_asset_id,
                VariantSummary.created_at,
            )
            .where(VariantSummary.sample_id == sample_id)
            .order_by(
                VariantSummary.reported_flag.desc(),
                VariantSummary.created_at.desc(),
            )
        ).all()

        return {
            "detail": detail,
            "provenance": provenance,
            "file_assets": [dict(row._mapping) for row in file_assets],
            "qc_results": [dict(row._mapping) for row in qc_results],
            "variants": [dict(row._mapping) for row in variants],
        }