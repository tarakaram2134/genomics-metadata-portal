from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.models import FileAsset, PipelineRun, QcMetricDefinition, QcResult, Sample

logger = get_logger(__name__)


class QcIngestService:
    """
    Registers QC result records into the relational model.

    Responsibilities:
    - validate manifest structure
    - validate foreign-key readiness
    - insert QC results with idempotent behavior
    """

    REQUIRED_QC_RESULT_FIELDS = {
        "qc_result_id",
        "sample_id",
        "pipeline_run_id",
        "qc_metric_name",
        "qc_status",
        "measured_at",
    }

    def __init__(self, session: Session) -> None:
        self.session = session

    def ingest_qc_results(self, qc_results: list[dict[str, Any]]) -> dict[str, int]:
        logger.info("Starting QC result ingestion")

        self._validate_required_fields(qc_results)
        metric_name_to_def_id = self._validate_foreign_keys(qc_results)

        inserted = self._insert_qc_results(qc_results, metric_name_to_def_id)

        self.session.commit()

        summary = {
            "qc_results_loaded": inserted,
        }
        logger.info("QC result ingestion summary: %s", summary)
        return summary

    def _validate_required_fields(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            raise ValueError("qc_results payload is empty")

        for index, row in enumerate(rows, start=1):
            missing = [field for field in self.REQUIRED_QC_RESULT_FIELDS if field not in row]
            if missing:
                raise ValueError(
                    f"qc_results row {index} is missing required fields: {', '.join(sorted(missing))}"
                )

    def _validate_foreign_keys(self, rows: list[dict[str, Any]]) -> dict[str, str]:
        sample_ids = {str(row["sample_id"]) for row in rows if self._present(row.get("sample_id"))}
        pipeline_run_ids = {
            str(row["pipeline_run_id"])
            for row in rows
            if self._present(row.get("pipeline_run_id"))
        }
        metric_names = {
            str(row["qc_metric_name"]) for row in rows if self._present(row.get("qc_metric_name"))
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

        metric_rows = self.session.execute(
            select(QcMetricDefinition.qc_metric_def_id, QcMetricDefinition.metric_name)
        ).all()
        metric_name_to_def_id = {
            row.metric_name: row.qc_metric_def_id
            for row in metric_rows
        }
        existing_metric_names = set(metric_name_to_def_id.keys())

        missing_samples = sorted(sample_ids - existing_sample_ids)
        missing_pipeline_runs = sorted(pipeline_run_ids - existing_pipeline_run_ids)
        missing_metric_names = sorted(metric_names - existing_metric_names)
        missing_file_assets = sorted(source_file_asset_ids - existing_file_asset_ids)

        if missing_samples:
            raise ValueError(
                f"qc_results contains unknown sample_id values: {missing_samples[:10]}"
            )
        if missing_pipeline_runs:
            raise ValueError(
                f"qc_results contains unknown pipeline_run_id values: {missing_pipeline_runs[:10]}"
            )
        if missing_metric_names:
            raise ValueError(
                f"qc_results contains unknown qc_metric_name values: {missing_metric_names[:10]}"
            )
        if missing_file_assets:
            raise ValueError(
                "qc_results contains unknown source_file_asset_id values: "
                f"{missing_file_assets[:10]}"
            )

        return metric_name_to_def_id

    def _insert_qc_results(
        self,
        rows: list[dict[str, Any]],
        metric_name_to_def_id: dict[str, str],
    ) -> int:
        existing_ids = set(self.session.scalars(select(QcResult.qc_result_id)).all())
        inserted = 0

        for row in rows:
            qc_result_id = str(row["qc_result_id"])
            if qc_result_id in existing_ids:
                continue

            qc_metric_name = str(row["qc_metric_name"])
            qc_metric_def_id = metric_name_to_def_id[qc_metric_name]

            numeric_value = self._coerce_float(row.get("metric_value_numeric"))
            text_value = self._clean_nullable_text(row.get("metric_value_text"))
            source_file_asset_id = self._clean_nullable_text(row.get("source_file_asset_id"))

            self.session.add(
                QcResult(
                    qc_result_id=qc_result_id,
                    sample_id=str(row["sample_id"]),
                    pipeline_run_id=str(row["pipeline_run_id"]),
                    qc_metric_def_id=qc_metric_def_id,
                    metric_value_numeric=numeric_value,
                    metric_value_text=text_value,
                    qc_status=str(row["qc_status"]),
                    measured_at=row["measured_at"],
                    source_file_asset_id=source_file_asset_id,
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
    def _coerce_float(value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                return None
            return float(stripped)
        try:
            if value != value:
                return None
        except Exception:
            pass
        return float(value)