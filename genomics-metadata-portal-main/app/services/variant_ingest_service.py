from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.models import FileAsset, PipelineRun, Sample, VariantSummary

logger = get_logger(__name__)


class VariantIngestService:
    """
    Registers variant summary records into the relational model.

    Responsibilities:
    - validate manifest structure
    - validate foreign-key readiness
    - insert variant summaries with idempotent behavior
    """

    REQUIRED_VARIANT_FIELDS = {
        "variant_summary_id",
        "sample_id",
        "pipeline_run_id",
        "gene_symbol",
        "variant_class",
        "protein_change",
        "chromosome",
        "position",
        "ref_allele",
        "alt_allele",
        "tumor_vaf",
        "clinical_significance",
        "is_driver",
        "reported_flag",
        "created_at",
    }

    def __init__(self, session: Session) -> None:
        self.session = session

    def ingest_variant_summaries(
        self,
        variant_summaries: list[dict[str, Any]],
    ) -> dict[str, int]:
        logger.info("Starting variant summary ingestion")

        self._validate_required_fields(variant_summaries)
        self._validate_foreign_keys(variant_summaries)

        inserted = self._insert_variant_summaries(variant_summaries)

        self.session.commit()

        summary = {
            "variant_summaries_loaded": inserted,
        }
        logger.info("Variant summary ingestion summary: %s", summary)
        return summary

    def _validate_required_fields(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            raise ValueError("variant_summary payload is empty")

        for index, row in enumerate(rows, start=1):
            missing = [field for field in self.REQUIRED_VARIANT_FIELDS if field not in row]
            if missing:
                raise ValueError(
                    "variant_summary row "
                    f"{index} is missing required fields: {', '.join(sorted(missing))}"
                )

    def _validate_foreign_keys(self, rows: list[dict[str, Any]]) -> None:
        sample_ids = {str(row["sample_id"]) for row in rows if self._present(row.get("sample_id"))}
        pipeline_run_ids = {
            str(row["pipeline_run_id"])
            for row in rows
            if self._present(row.get("pipeline_run_id"))
        }
        source_file_asset_ids = {
            str(row["source_file_asset_id"])
            for row in rows
            if self._present(row.get("source_file_asset_id"))
        }

        existing_sample_ids = set(self.session.scalars(select(Sample.sample_id)).all())
        existing_pipeline_run_ids = set(
            self.session.scalars(select(PipelineRun.pipeline_run_id)).all()
        )
        existing_file_asset_ids = set(self.session.scalars(select(FileAsset.file_asset_id)).all())

        missing_samples = sorted(sample_ids - existing_sample_ids)
        missing_pipeline_runs = sorted(pipeline_run_ids - existing_pipeline_run_ids)
        missing_file_assets = sorted(source_file_asset_ids - existing_file_asset_ids)

        if missing_samples:
            raise ValueError(
                f"variant_summary contains unknown sample_id values: {missing_samples[:10]}"
            )
        if missing_pipeline_runs:
            raise ValueError(
                "variant_summary contains unknown pipeline_run_id values: "
                f"{missing_pipeline_runs[:10]}"
            )
        if missing_file_assets:
            raise ValueError(
                "variant_summary contains unknown source_file_asset_id values: "
                f"{missing_file_assets[:10]}"
            )

    def _insert_variant_summaries(self, rows: list[dict[str, Any]]) -> int:
        existing_ids = set(self.session.scalars(select(VariantSummary.variant_summary_id)).all())
        inserted = 0

        for row in rows:
            variant_summary_id = str(row["variant_summary_id"])
            if variant_summary_id in existing_ids:
                continue

            self.session.add(
                VariantSummary(
                    variant_summary_id=variant_summary_id,
                    sample_id=str(row["sample_id"]),
                    pipeline_run_id=str(row["pipeline_run_id"]),
                    gene_symbol=str(row["gene_symbol"]),
                    variant_class=str(row["variant_class"]),
                    protein_change=str(row["protein_change"]),
                    chromosome=str(row["chromosome"]),
                    position=self._coerce_int(row["position"]),
                    ref_allele=str(row["ref_allele"]),
                    alt_allele=str(row["alt_allele"]),
                    tumor_vaf=self._coerce_float(row["tumor_vaf"]),
                    clinical_significance=str(row["clinical_significance"]),
                    is_driver=self._coerce_bool(row["is_driver"]),
                    reported_flag=self._coerce_bool(row["reported_flag"]),
                    source_file_asset_id=self._clean_nullable_text(row.get("source_file_asset_id")),
                    created_at=row["created_at"],
                )
            )
            inserted += 1

        self.session.flush()
        return inserted

    @staticmethod
    def _present(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        try:
            return bool(value == value)
        except Exception:
            return True

    @staticmethod
    def _clean_nullable_text(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        try:
            if value != value:
                return None
        except Exception:
            pass
        return str(value)

    @staticmethod
    def _coerce_int(value: Any) -> int:
        if isinstance(value, str):
            return int(value.strip())
        return int(value)

    @staticmethod
    def _coerce_float(value: Any) -> float:
        if isinstance(value, str):
            return float(value.strip())
        return float(value)

    @staticmethod
    def _coerce_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "t", "1", "yes", "y"}:
                return True
            if normalized in {"false", "f", "0", "no", "n"}:
                return False
            raise ValueError(f"Cannot coerce string to bool: {value}")
        return bool(value)