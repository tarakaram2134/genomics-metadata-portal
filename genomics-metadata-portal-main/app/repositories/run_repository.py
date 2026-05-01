from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, and_, select
from sqlalchemy.orm import Session

from app.models import (
    PipelineRun,
    PipelineRunReference,
    PipelineRunTool,
    PipelineVersion,
    Sample,
)


class RunRepository:
    """
    Query repository for pipeline run exploration workflows.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_runs(
        self,
        *,
        run_status: str | None = None,
        pipeline_id: str | None = None,
        search_text: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        stmt = (
            select(
                PipelineRun.pipeline_run_id,
                PipelineRun.sample_id,
                PipelineRun.pipeline_version_id,
                PipelineVersion.pipeline_id,
                PipelineVersion.version_label,
                PipelineRun.run_status,
                PipelineRun.run_started_at,
                PipelineRun.run_finished_at,
                PipelineRun.execution_environment,
                PipelineRun.triggered_by,
            )
            .join(
                PipelineVersion,
                PipelineRun.pipeline_version_id == PipelineVersion.pipeline_version_id,
            )
            .order_by(PipelineRun.run_started_at.desc())
            .limit(limit)
        )

        if run_status:
            stmt = stmt.where(PipelineRun.run_status == run_status)

        if pipeline_id:
            stmt = stmt.where(PipelineVersion.pipeline_id == pipeline_id)

        if search_text:
            pattern = f"%{search_text}%"
            stmt = stmt.where(
                (PipelineRun.pipeline_run_id.ilike(pattern))
                | (PipelineRun.sample_id.ilike(pattern))
                | (PipelineVersion.pipeline_id.ilike(pattern))
            )

        rows = self.session.execute(stmt).all()

        return [
            {
                "pipeline_run_id": row.pipeline_run_id,
                "sample_id": row.sample_id,
                "pipeline_id": row.pipeline_id,
                "pipeline_version_id": row.pipeline_version_id,
                "version_label": row.version_label,
                "run_status": row.run_status,
                "run_started_at": row.run_started_at,
                "run_finished_at": row.run_finished_at,
                "execution_environment": row.execution_environment,
                "triggered_by": row.triggered_by,
            }
            for row in rows
        ]

    def get_run_detail(self, pipeline_run_id: str) -> dict[str, Any] | None:
        stmt = (
            select(
                PipelineRun,
                PipelineVersion.pipeline_id,
                PipelineVersion.version_label,
                Sample.sample_id,
                Sample.assay_type,
                Sample.sample_type,
            )
            .join(
                PipelineVersion,
                PipelineRun.pipeline_version_id == PipelineVersion.pipeline_version_id,
            )
            .join(Sample, PipelineRun.sample_id == Sample.sample_id)
            .where(PipelineRun.pipeline_run_id == pipeline_run_id)
        )

        row = self.session.execute(stmt).first()
        if row is None:
            return None

        run = row.PipelineRun

        return {
            "pipeline_run_id": run.pipeline_run_id,
            "sample_id": row.sample_id,
            "assay_type": row.assay_type,
            "sample_type": row.sample_type,
            "pipeline_id": row.pipeline_id,
            "pipeline_version_id": run.pipeline_version_id,
            "version_label": row.version_label,
            "run_status": run.run_status,
            "run_started_at": run.run_started_at,
            "run_finished_at": run.run_finished_at,
            "execution_environment": run.execution_environment,
            "triggered_by": run.triggered_by,
            "parameter_set_json": run.parameter_set_json,
            "log_path": run.log_path,
            "work_dir_path": run.work_dir_path,
            "failure_reason": run.failure_reason,
        }

    def get_run_provenance(self, pipeline_run_id: str) -> dict[str, Any]:
        refs = self.session.execute(
            select(
                PipelineRunReference.reference_id,
                PipelineRunReference.usage_role,
                PipelineRunReference.execution_order,
                PipelineRunReference.step_label,
            )
            .where(PipelineRunReference.pipeline_run_id == pipeline_run_id)
            .order_by(PipelineRunReference.execution_order.asc().nullslast())
        ).all()

        tools = self.session.execute(
            select(
                PipelineRunTool.tool_id,
                PipelineRunTool.usage_role,
                PipelineRunTool.execution_order,
                PipelineRunTool.step_label,
            )
            .where(PipelineRunTool.pipeline_run_id == pipeline_run_id)
            .order_by(PipelineRunTool.execution_order.asc().nullslast())
        ).all()

        return {
            "references": [dict(r._mapping) for r in refs],
            "tools": [dict(t._mapping) for t in tools],
        }