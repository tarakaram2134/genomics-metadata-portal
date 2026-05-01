from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import QcMetricDefinition, QcResult, Sample


class QcRepository:
    """
    Query repository for QC-focused dashboard workflows.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_qc_status_summary(
        self,
        *,
        assay_type: str | None = None,
    ) -> list[dict[str, Any]]:
        stmt = (
            select(
                QcResult.qc_status,
                func.count(QcResult.qc_result_id).label("result_count"),
            )
            .join(Sample, QcResult.sample_id == Sample.sample_id)
            .group_by(QcResult.qc_status)
            .order_by(QcResult.qc_status)
        )

        if assay_type:
            stmt = stmt.where(Sample.assay_type == assay_type)

        rows = self.session.execute(stmt).all()
        return [
            {
                "qc_status": row.qc_status,
                "result_count": row.result_count,
            }
            for row in rows
        ]

    def get_recent_qc_results(
        self,
        *,
        assay_type: str | None = None,
        qc_status: str | None = None,
        metric_name: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        stmt = (
            select(
                QcResult.qc_result_id,
                QcResult.sample_id,
                QcResult.pipeline_run_id,
                Sample.assay_type,
                QcMetricDefinition.metric_name,
                QcResult.metric_value_numeric,
                QcResult.metric_value_text,
                QcResult.qc_status,
                QcResult.measured_at,
                QcResult.source_file_asset_id,
            )
            .join(Sample, QcResult.sample_id == Sample.sample_id)
            .join(
                QcMetricDefinition,
                QcResult.qc_metric_def_id == QcMetricDefinition.qc_metric_def_id,
            )
            .order_by(QcResult.measured_at.desc(), QcResult.qc_result_id)
            .limit(limit)
        )

        if assay_type:
            stmt = stmt.where(Sample.assay_type == assay_type)

        if qc_status:
            stmt = stmt.where(QcResult.qc_status == qc_status)

        if metric_name:
            stmt = stmt.where(QcMetricDefinition.metric_name == metric_name)

        rows = self.session.execute(stmt).all()
        return [
            {
                "qc_result_id": row.qc_result_id,
                "sample_id": row.sample_id,
                "pipeline_run_id": row.pipeline_run_id,
                "assay_type": row.assay_type,
                "metric_name": row.metric_name,
                "metric_value_numeric": (
                    float(row.metric_value_numeric)
                    if row.metric_value_numeric is not None
                    else None
                ),
                "metric_value_text": row.metric_value_text,
                "qc_status": row.qc_status,
                "measured_at": row.measured_at,
                "source_file_asset_id": row.source_file_asset_id,
            }
            for row in rows
        ]

    def list_metric_names(self) -> list[str]:
        rows = self.session.scalars(
            select(QcMetricDefinition.metric_name).order_by(QcMetricDefinition.metric_name)
        ).all()
        return [row for row in rows if row]

    def list_assay_types(self) -> list[str]:
        rows = self.session.scalars(
            select(Sample.assay_type).distinct().order_by(Sample.assay_type)
        ).all()
        return [row for row in rows if row]