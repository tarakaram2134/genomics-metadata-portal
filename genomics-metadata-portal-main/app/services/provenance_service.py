from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.models import (
    PipelineRun,
    PipelineRunReference,
    PipelineRunTool,
    PipelineVersion,
    ReferenceResource,
    Sample,
    SampleAnalysisSummary,
    SequencingRun,
    ToolRegistry,
)

logger = get_logger(__name__)


class ProvenanceService:
    """
    Registers pipeline execution provenance into the relational model.

    Responsibilities:
    - insert pipeline runs
    - insert pipeline_run -> reference relationships
    - insert pipeline_run -> tool relationships
    - insert sample analysis summaries
    - preserve idempotent rerun behavior
    """

    REQUIRED_PIPELINE_RUN_FIELDS = {
        "pipeline_run_id",
        "sample_id",
        "seq_run_id",
        "pipeline_version_id",
        "run_started_at",
        "run_status",
        "parameter_set_json",
        "execution_environment",
        "triggered_by",
        "workflow_run_uuid",
        "log_path",
        "work_dir_path",
        "created_at",
    }

    REQUIRED_PIPELINE_RUN_REFERENCE_FIELDS = {
        "pipeline_run_id",
        "reference_id",
        "usage_role",
        "execution_order",
        "step_label",
    }

    REQUIRED_PIPELINE_RUN_TOOL_FIELDS = {
        "pipeline_run_id",
        "tool_id",
        "usage_role",
        "execution_order",
        "step_label",
    }

    REQUIRED_SAMPLE_ANALYSIS_SUMMARY_FIELDS = {
        "sample_analysis_summary_id",
        "sample_id",
        "tmb_score",
        "msi_status",
        "purity_estimate",
        "ploidy_estimate",
        "analysis_summary_json",
        "last_updated_at",
    }

    def __init__(self, session: Session) -> None:
        self.session = session

    def register_provenance(
        self,
        pipeline_runs: list[dict[str, Any]],
        pipeline_run_references: list[dict[str, Any]],
        pipeline_run_tools: list[dict[str, Any]],
        sample_analysis_summaries: list[dict[str, Any]],
    ) -> dict[str, int]:
        logger.info("Starting provenance registration")

        self._validate_required_fields(
            rows=pipeline_runs,
            required_fields=self.REQUIRED_PIPELINE_RUN_FIELDS,
            row_name="pipeline_runs",
        )
        self._validate_required_fields(
            rows=pipeline_run_references,
            required_fields=self.REQUIRED_PIPELINE_RUN_REFERENCE_FIELDS,
            row_name="pipeline_run_references",
        )
        self._validate_required_fields(
            rows=pipeline_run_tools,
            required_fields=self.REQUIRED_PIPELINE_RUN_TOOL_FIELDS,
            row_name="pipeline_run_tools",
        )
        self._validate_required_fields(
            rows=sample_analysis_summaries,
            required_fields=self.REQUIRED_SAMPLE_ANALYSIS_SUMMARY_FIELDS,
            row_name="sample_analysis_summary",
        )

        self._validate_pipeline_run_foreign_keys(pipeline_runs)
        pipeline_runs_inserted = self._insert_pipeline_runs(pipeline_runs)

        self._validate_pipeline_reference_foreign_keys(pipeline_run_references)
        self._validate_pipeline_tool_foreign_keys(pipeline_run_tools)
        self._validate_sample_analysis_foreign_keys(sample_analysis_summaries)

        pipeline_run_references_inserted = self._insert_pipeline_run_references(
            pipeline_run_references
        )
        pipeline_run_tools_inserted = self._insert_pipeline_run_tools(pipeline_run_tools)
        sample_analysis_summaries_inserted = self._insert_sample_analysis_summaries(
            sample_analysis_summaries
        )

        self.session.commit()

        summary = {
            "pipeline_runs_loaded": pipeline_runs_inserted,
            "pipeline_run_references_loaded": pipeline_run_references_inserted,
            "pipeline_run_tools_loaded": pipeline_run_tools_inserted,
            "sample_analysis_summaries_loaded": sample_analysis_summaries_inserted,
        }

        logger.info("Provenance registration summary: %s", summary)
        return summary

    def _validate_required_fields(
        self,
        rows: list[dict[str, Any]],
        required_fields: set[str],
        row_name: str,
    ) -> None:
        if not rows:
            raise ValueError(f"{row_name} payload is empty")

        for index, row in enumerate(rows, start=1):
            missing = [field for field in required_fields if field not in row]
            if missing:
                raise ValueError(
                    f"{row_name} row {index} is missing required fields: {', '.join(sorted(missing))}"
                )

    def _validate_pipeline_run_foreign_keys(self, rows: list[dict[str, Any]]) -> None:
        sample_ids = {row["sample_id"] for row in rows if row.get("sample_id")}
        seq_run_ids = {row["seq_run_id"] for row in rows if row.get("seq_run_id")}
        pipeline_version_ids = {row["pipeline_version_id"] for row in rows if row.get("pipeline_version_id")}

        existing_sample_ids = set(self.session.scalars(select(Sample.sample_id)).all())
        existing_seq_run_ids = set(self.session.scalars(select(SequencingRun.seq_run_id)).all())
        existing_pipeline_version_ids = set(
            self.session.scalars(select(PipelineVersion.pipeline_version_id)).all()
        )

        missing_samples = sorted(sample_ids - existing_sample_ids)
        missing_seq_runs = sorted(seq_run_ids - existing_seq_run_ids)
        missing_pipeline_versions = sorted(pipeline_version_ids - existing_pipeline_version_ids)

        if missing_samples:
            raise ValueError(
                f"pipeline_runs contains unknown sample_id values: {missing_samples[:10]}"
            )
        if missing_seq_runs:
            raise ValueError(
                f"pipeline_runs contains unknown seq_run_id values: {missing_seq_runs[:10]}"
            )
        if missing_pipeline_versions:
            raise ValueError(
                "pipeline_runs contains unknown pipeline_version_id values: "
                f"{missing_pipeline_versions[:10]}"
            )

    def _validate_pipeline_reference_foreign_keys(
        self, rows: list[dict[str, Any]]
    ) -> None:
        pipeline_run_ids = {row["pipeline_run_id"] for row in rows if row.get("pipeline_run_id")}
        reference_ids = {row["reference_id"] for row in rows if row.get("reference_id")}

        existing_pipeline_run_ids = self._existing_pipeline_run_ids(pipeline_run_ids)
        existing_reference_ids = set(self.session.scalars(select(ReferenceResource.reference_id)).all())

        missing_pipeline_runs = sorted(pipeline_run_ids - existing_pipeline_run_ids)
        missing_references = sorted(reference_ids - existing_reference_ids)

        if missing_pipeline_runs:
            raise ValueError(
                "pipeline_run_references contains unknown pipeline_run_id values: "
                f"{missing_pipeline_runs[:10]}"
            )
        if missing_references:
            raise ValueError(
                f"pipeline_run_references contains unknown reference_id values: {missing_references[:10]}"
            )

    def _validate_pipeline_tool_foreign_keys(self, rows: list[dict[str, Any]]) -> None:
        pipeline_run_ids = {row["pipeline_run_id"] for row in rows if row.get("pipeline_run_id")}
        tool_ids = {row["tool_id"] for row in rows if row.get("tool_id")}

        existing_pipeline_run_ids = self._existing_pipeline_run_ids(pipeline_run_ids)
        existing_tool_ids = set(self.session.scalars(select(ToolRegistry.tool_id)).all())

        missing_pipeline_runs = sorted(pipeline_run_ids - existing_pipeline_run_ids)
        missing_tools = sorted(tool_ids - existing_tool_ids)

        if missing_pipeline_runs:
            raise ValueError(
                f"pipeline_run_tools contains unknown pipeline_run_id values: {missing_pipeline_runs[:10]}"
            )
        if missing_tools:
            raise ValueError(
                f"pipeline_run_tools contains unknown tool_id values: {missing_tools[:10]}"
            )

    def _validate_sample_analysis_foreign_keys(
        self, rows: list[dict[str, Any]]
    ) -> None:
        sample_ids = {row["sample_id"] for row in rows if row.get("sample_id")}
        existing_sample_ids = set(self.session.scalars(select(Sample.sample_id)).all())
        missing_samples = sorted(sample_ids - existing_sample_ids)

        if missing_samples:
            raise ValueError(
                "sample_analysis_summary contains unknown sample_id values: "
                f"{missing_samples[:10]}"
            )

    def _insert_pipeline_runs(self, rows: list[dict[str, Any]]) -> int:
        existing_ids = set(self.session.scalars(select(PipelineRun.pipeline_run_id)).all())
        inserted = 0

        for row in rows:
            if row["pipeline_run_id"] in existing_ids:
                continue

            parameter_set_json = row.get("parameter_set_json", "")
            parameter_payload: dict[str, Any] | None
            if parameter_set_json in ("", None):
                parameter_payload = None
            elif isinstance(parameter_set_json, str):
                parameter_payload = json.loads(parameter_set_json)
            elif isinstance(parameter_set_json, dict):
                parameter_payload = parameter_set_json
            else:
                raise ValueError(
                    f"Unsupported parameter_set_json type for pipeline_run_id={row['pipeline_run_id']}"
                )

            self.session.add(
                PipelineRun(
                    pipeline_run_id=row["pipeline_run_id"],
                    sample_id=row["sample_id"],
                    seq_run_id=row["seq_run_id"],
                    pipeline_version_id=row["pipeline_version_id"],
                    run_started_at=row["run_started_at"],
                    run_finished_at=row.get("run_finished_at") or None,
                    run_status=row["run_status"],
                    parameter_set_json=parameter_payload,
                    execution_environment=row["execution_environment"],
                    triggered_by=row["triggered_by"],
                    workflow_run_uuid=row["workflow_run_uuid"],
                    log_path=row["log_path"],
                    work_dir_path=row["work_dir_path"],
                    failure_reason=row.get("failure_reason") or None,
                    created_at=row["created_at"],
                )
            )
            inserted += 1

        self.session.flush()
        return inserted

    def _insert_pipeline_run_references(self, rows: list[dict[str, Any]]) -> int:
        keys = {
            (
                row["pipeline_run_id"],
                row["reference_id"],
                row["usage_role"],
                int(row["execution_order"]),
                row["step_label"],
            )
            for row in rows
        }

        existing_keys = self._existing_pipeline_reference_keys(keys)
        inserted = 0

        for row in rows:
            key = (
                row["pipeline_run_id"],
                row["reference_id"],
                row["usage_role"],
                int(row["execution_order"]),
                row["step_label"],
            )
            if key in existing_keys:
                continue

            self.session.add(
                PipelineRunReference(
                    pipeline_run_id=row["pipeline_run_id"],
                    reference_id=row["reference_id"],
                    usage_role=row["usage_role"],
                    execution_order=int(row["execution_order"]),
                    step_label=row["step_label"],
                    created_at=row.get("created_at"),
                )
            )
            inserted += 1

        self.session.flush()
        return inserted

    def _insert_pipeline_run_tools(self, rows: list[dict[str, Any]]) -> int:
        keys = {
            (
                row["pipeline_run_id"],
                row["tool_id"],
                row["usage_role"],
                int(row["execution_order"]),
                row["step_label"],
            )
            for row in rows
        }

        existing_keys = self._existing_pipeline_tool_keys(keys)
        inserted = 0

        for row in rows:
            key = (
                row["pipeline_run_id"],
                row["tool_id"],
                row["usage_role"],
                int(row["execution_order"]),
                row["step_label"],
            )
            if key in existing_keys:
                continue

            self.session.add(
                PipelineRunTool(
                    pipeline_run_id=row["pipeline_run_id"],
                    tool_id=row["tool_id"],
                    usage_role=row["usage_role"],
                    execution_order=int(row["execution_order"]),
                    step_label=row["step_label"],
                    created_at=row.get("created_at"),
                )
            )
            inserted += 1

        self.session.flush()
        return inserted

    def _insert_sample_analysis_summaries(self, rows: list[dict[str, Any]]) -> int:
        existing_ids = set(
            self.session.scalars(
                select(SampleAnalysisSummary.sample_analysis_summary_id)
            ).all()
        )
        inserted = 0

        for row in rows:
            if row["sample_analysis_summary_id"] in existing_ids:
                continue

            analysis_summary_json = row.get("analysis_summary_json", "")
            analysis_payload: dict[str, Any] | None
            if analysis_summary_json in ("", None):
                analysis_payload = None
            elif isinstance(analysis_summary_json, str):
                analysis_payload = json.loads(analysis_summary_json)
            elif isinstance(analysis_summary_json, dict):
                analysis_payload = analysis_summary_json
            else:
                raise ValueError(
                    "Unsupported analysis_summary_json type for "
                    f"sample_analysis_summary_id={row['sample_analysis_summary_id']}"
                )

            self.session.add(
                SampleAnalysisSummary(
                    sample_analysis_summary_id=row["sample_analysis_summary_id"],
                    sample_id=row["sample_id"],
                    tmb_score=row["tmb_score"],
                    msi_status=row["msi_status"],
                    purity_estimate=row["purity_estimate"],
                    ploidy_estimate=row["ploidy_estimate"],
                    expression_subtype=row.get("expression_subtype") or None,
                    analysis_summary_json=analysis_payload,
                    last_updated_at=row["last_updated_at"],
                )
            )
            inserted += 1

        self.session.flush()
        return inserted

    def _existing_pipeline_run_ids(self, pipeline_run_ids: set[str]) -> set[str]:
        if not pipeline_run_ids:
            return set()

        return set(
            self.session.scalars(
                select(PipelineRun.pipeline_run_id).where(
                    PipelineRun.pipeline_run_id.in_(pipeline_run_ids)
                )
            ).all()
        )

    def _existing_pipeline_reference_keys(
        self,
        keys: set[tuple[str, str, str, int, str]],
    ) -> set[tuple[str, str, str, int, str]]:
        if not keys:
            return set()

        pipeline_run_ids = sorted({key[0] for key in keys})

        existing_rows = self.session.execute(
            select(
                PipelineRunReference.pipeline_run_id,
                PipelineRunReference.reference_id,
                PipelineRunReference.usage_role,
                PipelineRunReference.execution_order,
                PipelineRunReference.step_label,
            ).where(PipelineRunReference.pipeline_run_id.in_(pipeline_run_ids))
        ).all()

        return {
            (
                row.pipeline_run_id,
                row.reference_id,
                row.usage_role,
                int(row.execution_order),
                row.step_label,
            )
            for row in existing_rows
        }

    def _existing_pipeline_tool_keys(
        self,
        keys: set[tuple[str, str, str, int, str]],
    ) -> set[tuple[str, str, str, int, str]]:
        if not keys:
            return set()

        pipeline_run_ids = sorted({key[0] for key in keys})

        existing_rows = self.session.execute(
            select(
                PipelineRunTool.pipeline_run_id,
                PipelineRunTool.tool_id,
                PipelineRunTool.usage_role,
                PipelineRunTool.execution_order,
                PipelineRunTool.step_label,
            ).where(PipelineRunTool.pipeline_run_id.in_(pipeline_run_ids))
        ).all()

        return {
            (
                row.pipeline_run_id,
                row.tool_id,
                row.usage_role,
                int(row.execution_order),
                row.step_label,
            )
            for row in existing_rows
        }