from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Sample, VariantSummary


class VariantRepository:
    """
    Repository for cross-sample variant exploration.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def search_variants(
        self,
        *,
        gene_symbol: str | None = None,
        clinical_significance: str | None = None,
        reported_only: bool = False,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        stmt = (
            select(
                VariantSummary.variant_summary_id,
                VariantSummary.sample_id,
                Sample.assay_type,
                VariantSummary.pipeline_run_id,
                VariantSummary.gene_symbol,
                VariantSummary.variant_class,
                VariantSummary.protein_change,
                VariantSummary.chromosome,
                VariantSummary.position,
                VariantSummary.tumor_vaf,
                VariantSummary.clinical_significance,
                VariantSummary.is_driver,
                VariantSummary.reported_flag,
                VariantSummary.created_at,
            )
            .join(Sample, VariantSummary.sample_id == Sample.sample_id)
            .order_by(
                VariantSummary.reported_flag.desc(),
                VariantSummary.is_driver.desc(),
                VariantSummary.gene_symbol.asc(),
            )
            .limit(limit)
        )

        if gene_symbol:
            stmt = stmt.where(VariantSummary.gene_symbol == gene_symbol)

        if clinical_significance:
            stmt = stmt.where(
                VariantSummary.clinical_significance == clinical_significance
            )

        if reported_only:
            stmt = stmt.where(VariantSummary.reported_flag.is_(True))

        rows = self.session.execute(stmt).all()

        return [
            {
                "variant_summary_id": row.variant_summary_id,
                "sample_id": row.sample_id,
                "assay_type": row.assay_type,
                "pipeline_run_id": row.pipeline_run_id,
                "gene_symbol": row.gene_symbol,
                "variant_class": row.variant_class,
                "protein_change": row.protein_change,
                "chromosome": row.chromosome,
                "position": row.position,
                "tumor_vaf": float(row.tumor_vaf)
                if row.tumor_vaf is not None
                else None,
                "clinical_significance": row.clinical_significance,
                "is_driver": row.is_driver,
                "reported_flag": row.reported_flag,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    def list_genes(self) -> list[str]:
        rows = self.session.scalars(
            select(VariantSummary.gene_symbol)
            .distinct()
            .order_by(VariantSummary.gene_symbol)
        ).all()
        return [row for row in rows if row]

    def list_clinical_significance(self) -> list[str]:
        rows = self.session.scalars(
            select(VariantSummary.clinical_significance)
            .distinct()
            .order_by(VariantSummary.clinical_significance)
        ).all()
        return [row for row in rows if row]