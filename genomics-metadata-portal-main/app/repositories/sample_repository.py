from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import Session, aliased

from app.models import (
    Batch,
    Patient,
    PipelineRun,
    PipelineRunReference,
    PipelineRunTool,
    PipelineVersion,
    QcResult,
    QcMetricDefinition, 
    Sample,
    SampleAnalysisSummary,
    SampleRunAssignment,
    SequencingRun,
    VariantSummary,
)


class SampleRepository:
    """
    Query repository for sample-centric exploration workflows.

    This repository provides read-oriented access patterns for:
    - sample listing and filtering
    - sample detail lookup
    - sequencing lineage
    - pipeline provenance
    - QC result inspection
    - variant inspection
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_samples(
        self,
        *,
        disease_type: str | None = None,
        assay_type: str | None = None,
        sample_status: str | None = None,
        tumor_normal_status: str | None = None,
        search_text: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        latest_qc_subquery = (
            select(
                QcResult.sample_id.label("sample_id"),
                func.max(QcResult.measured_at).label("latest_measured_at"),
            )
            .group_by(QcResult.sample_id)
            .subquery()
        )

        qc_summary_subquery = (
            select(
                QcResult.sample_id.label("sample_id"),
                QcResult.qc_status.label("latest_qc_status"),
            )
            .join(
                latest_qc_subquery,
                and_(
                    QcResult.sample_id == latest_qc_subquery.c.sample_id,
                    QcResult.measured_at == latest_qc_subquery.c.latest_measured_at,
                ),
            )
            .join(
                QcMetricDefinition,
                QcResult.qc_metric_def_id == QcMetricDefinition.qc_metric_def_id,
            )
            .where(QcMetricDefinition.metric_name == "qc_summary_flag")
            .subquery()
        )

        latest_analysis_subquery = (
            select(
                SampleAnalysisSummary.sample_id.label("sample_id"),
                func.max(SampleAnalysisSummary.last_updated_at).label("latest_updated_at"),
            )
            .group_by(SampleAnalysisSummary.sample_id)
            .subquery()
        )

        analysis_subquery = (
            select(
                SampleAnalysisSummary.sample_id.label("sample_id"),
                SampleAnalysisSummary.tmb_score.label("tmb_score"),
                SampleAnalysisSummary.msi_status.label("msi_status"),
            )
            .join(
                latest_analysis_subquery,
                and_(
                    SampleAnalysisSummary.sample_id == latest_analysis_subquery.c.sample_id,
                    SampleAnalysisSummary.last_updated_at
                    == latest_analysis_subquery.c.latest_updated_at,
                ),
            )
            .subquery()
        )

        stmt = (
            select(
                Sample.sample_id,
                Patient.external_subject_id,
                Patient.disease_type,
                Sample.assay_type,
                Sample.sample_type,
                Sample.sample_status,
                Sample.tumor_normal_status,
                Sample.specimen_site,
                Sample.received_date,
                Batch.batch_name,
                qc_summary_subquery.c.latest_qc_status,
                analysis_subquery.c.tmb_score,
                analysis_subquery.c.msi_status,
            )
            .join(Patient, Sample.patient_id == Patient.patient_id)
            .join(Batch, Sample.batch_id == Batch.batch_id)
            .outerjoin(
                qc_summary_subquery,
                Sample.sample_id == qc_summary_subquery.c.sample_id,
            )
            .outerjoin(
                analysis_subquery,
                Sample.sample_id == analysis_subquery.c.sample_id,
            )
            .order_by(Sample.received_date.desc(), Sample.sample_id)
            .limit(limit)
            .offset(offset)
        )

        stmt = self._apply_sample_filters(
            stmt,
            disease_type=disease_type,
            assay_type=assay_type,
            sample_status=sample_status,
            tumor_normal_status=tumor_normal_status,
            search_text=search_text,
        )

        rows = self.session.execute(stmt).all()
        return [
            {
                "sample_id": row.sample_id,
                "external_subject_id": row.external_subject_id,
                "disease_type": row.disease_type,
                "assay_type": row.assay_type,
                "sample_type": row.sample_type,
                "sample_status": row.sample_status,
                "tumor_normal_status": row.tumor_normal_status,
                "specimen_site": row.specimen_site,
                "received_date": row.received_date,
                "batch_name": row.batch_name,
                "latest_qc_status": row.latest_qc_status,
                "tmb_score": float(row.tmb_score) if row.tmb_score is not None else None,
                "msi_status": row.msi_status,
            }
            for row in rows
        ]

    def get_sample_detail(self, sample_id: str) -> dict[str, Any] | None:
        stmt = (
            select(
                Sample.sample_id,
                Sample.patient_id,
                Patient.external_subject_id,
                Patient.disease_type,
                Patient.condition_group,
                Patient.sex,
                Patient.age_band,
                Sample.batch_id,
                Batch.batch_name,
                Sample.sample_type,
                Sample.assay_type,
                Sample.collection_date,
                Sample.received_date,
                Sample.specimen_site,
                Sample.condition_label,
                Sample.sample_status,
                Sample.tumor_normal_status,
                Sample.library_prep_kit,
                Sample.notes,
                Sample.created_at,
                SampleAnalysisSummary.tmb_score,
                SampleAnalysisSummary.msi_status,
                SampleAnalysisSummary.purity_estimate,
                SampleAnalysisSummary.ploidy_estimate,
                SampleAnalysisSummary.expression_subtype,
                SampleAnalysisSummary.analysis_summary_json,
                SampleAnalysisSummary.last_updated_at,
            )
            .join(Patient, Sample.patient_id == Patient.patient_id)
            .join(Batch, Sample.batch_id == Batch.batch_id)
            .outerjoin(
                SampleAnalysisSummary,
                Sample.sample_id == SampleAnalysisSummary.sample_id,
            )
            .where(Sample.sample_id == sample_id)
            .order_by(SampleAnalysisSummary.last_updated_at.desc().nullslast())
        )

        row = self.session.execute(stmt).first()
        if row is None:
            return None

        return {
            "sample_id": row.sample_id,
            "patient_id": row.patient_id,
            "external_subject_id": row.external_subject_id,
            "disease_type": row.disease_type,
            "condition_group": row.condition_group,
            "sex": row.sex,
            "age_band": row.age_band,
            "batch_id": row.batch_id,
            "batch_name": row.batch_name,
            "sample_type": row.sample_type,
            "assay_type": row.assay_type,
            "collection_date": row.collection_date,
            "received_date": row.received_date,
            "specimen_site": row.specimen_site,
            "condition_label": row.condition_label,
            "sample_status": row.sample_status,
            "tumor_normal_status": row.tumor_normal_status,
            "library_prep_kit": row.library_prep_kit,
            "notes": row.notes,
            "created_at": row.created_at,
            "analysis_summary": {
                "tmb_score": float(row.tmb_score) if row.tmb_score is not None else None,
                "msi_status": row.msi_status,
                "purity_estimate": (
                    float(row.purity_estimate) if row.purity_estimate is not None else None
                ),
                "ploidy_estimate": (
                    float(row.ploidy_estimate) if row.ploidy_estimate is not None else None
                ),
                "expression_subtype": row.expression_subtype,
                "analysis_summary_json": row.analysis_summary_json,
                "last_updated_at": row.last_updated_at,
            }
            if row.last_updated_at is not None
            else None,
        }

    def get_sample_provenance(self, sample_id: str) -> dict[str, Any]:
        sequencing_stmt = (
            select(
                SampleRunAssignment.seq_run_id,
                SequencingRun.instrument_run_name,
                SequencingRun.platform,
                SequencingRun.instrument_model,
                SequencingRun.run_date,
                SequencingRun.run_status,
                SampleRunAssignment.lane_or_partition,
                SampleRunAssignment.library_id,
                SampleRunAssignment.barcode,
            )
            .join(
                SequencingRun,
                SampleRunAssignment.seq_run_id == SequencingRun.seq_run_id,
            )
            .where(SampleRunAssignment.sample_id == sample_id)
            .order_by(SequencingRun.run_date.desc(), SampleRunAssignment.lane_or_partition)
        )

        pipeline_stmt = (
            select(
                PipelineRun.pipeline_run_id,
                PipelineRun.pipeline_version_id,
                PipelineVersion.pipeline_id,
                PipelineVersion.version_label,
                PipelineRun.run_started_at,
                PipelineRun.run_finished_at,
                PipelineRun.run_status,
                PipelineRun.parameter_set_json,
                PipelineRun.execution_environment,
                PipelineRun.triggered_by,
                PipelineRun.workflow_run_uuid,
                PipelineRun.log_path,
                PipelineRun.work_dir_path,
                PipelineRun.failure_reason,
            )
            .join(
                PipelineVersion,
                PipelineRun.pipeline_version_id == PipelineVersion.pipeline_version_id,
            )
            .where(PipelineRun.sample_id == sample_id)
            .order_by(PipelineRun.run_started_at.desc(), PipelineRun.pipeline_run_id)
        )

        pipeline_rows = self.session.execute(pipeline_stmt).all()
        pipeline_run_ids = [row.pipeline_run_id for row in pipeline_rows]

        references_by_run = self._get_pipeline_references_by_run(pipeline_run_ids)
        tools_by_run = self._get_pipeline_tools_by_run(pipeline_run_ids)

        sequencing = [
            {
                "seq_run_id": row.seq_run_id,
                "instrument_run_name": row.instrument_run_name,
                "platform": row.platform,
                "instrument_model": row.instrument_model,
                "run_date": row.run_date,
                "run_status": row.run_status,
                "lane_or_partition": row.lane_or_partition,
                "library_id": row.library_id,
                "barcode": row.barcode,
            }
            for row in self.session.execute(sequencing_stmt).all()
        ]

        pipeline_runs = [
            {
                "pipeline_run_id": row.pipeline_run_id,
                "pipeline_version_id": row.pipeline_version_id,
                "pipeline_id": row.pipeline_id,
                "version_label": row.version_label,
                "run_started_at": row.run_started_at,
                "run_finished_at": row.run_finished_at,
                "run_status": row.run_status,
                "parameter_set_json": row.parameter_set_json,
                "execution_environment": row.execution_environment,
                "triggered_by": row.triggered_by,
                "workflow_run_uuid": row.workflow_run_uuid,
                "log_path": row.log_path,
                "work_dir_path": row.work_dir_path,
                "failure_reason": row.failure_reason,
                "references": references_by_run.get(row.pipeline_run_id, []),
                "tools": tools_by_run.get(row.pipeline_run_id, []),
            }
            for row in pipeline_rows
        ]

        return {
            "sample_id": sample_id,
            "sequencing": sequencing,
            "pipeline_runs": pipeline_runs,
        }

    def get_sample_qc_results(self, sample_id: str) -> list[dict[str, Any]]:
        stmt = (
            select(
                QcResult.qc_result_id,
                QcResult.pipeline_run_id,
                QcResult.qc_metric_def_id,
                QcResult.metric_value_numeric,
                QcResult.metric_value_text,
                QcResult.qc_status,
                QcResult.measured_at,
                QcResult.source_file_asset_id,
            )
            .where(QcResult.sample_id == sample_id)
            .order_by(QcResult.measured_at.desc(), QcResult.qc_result_id)
        )

        rows = self.session.execute(stmt).all()
        return [
            {
                "qc_result_id": row.qc_result_id,
                "pipeline_run_id": row.pipeline_run_id,
                "qc_metric_def_id": row.qc_metric_def_id,
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

    def get_sample_variants(self, sample_id: str) -> list[dict[str, Any]]:
        stmt = (
            select(
                VariantSummary.variant_summary_id,
                VariantSummary.pipeline_run_id,
                VariantSummary.gene_symbol,
                VariantSummary.variant_class,
                VariantSummary.protein_change,
                VariantSummary.chromosome,
                VariantSummary.position,
                VariantSummary.ref_allele,
                VariantSummary.alt_allele,
                VariantSummary.tumor_vaf,
                VariantSummary.clinical_significance,
                VariantSummary.is_driver,
                VariantSummary.reported_flag,
                VariantSummary.source_file_asset_id,
                VariantSummary.created_at,
            )
            .where(VariantSummary.sample_id == sample_id)
            .order_by(
                VariantSummary.reported_flag.desc(),
                VariantSummary.is_driver.desc(),
                VariantSummary.gene_symbol.asc(),
            )
        )

        rows = self.session.execute(stmt).all()
        return [
            {
                "variant_summary_id": row.variant_summary_id,
                "pipeline_run_id": row.pipeline_run_id,
                "gene_symbol": row.gene_symbol,
                "variant_class": row.variant_class,
                "protein_change": row.protein_change,
                "chromosome": row.chromosome,
                "position": row.position,
                "ref_allele": row.ref_allele,
                "alt_allele": row.alt_allele,
                "tumor_vaf": float(row.tumor_vaf) if row.tumor_vaf is not None else None,
                "clinical_significance": row.clinical_significance,
                "is_driver": row.is_driver,
                "reported_flag": row.reported_flag,
                "source_file_asset_id": row.source_file_asset_id,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    def _apply_sample_filters(
        self,
        stmt: Select[Any],
        *,
        disease_type: str | None,
        assay_type: str | None,
        sample_status: str | None,
        tumor_normal_status: str | None,
        search_text: str | None,
    ) -> Select[Any]:
        if disease_type:
            stmt = stmt.where(Patient.disease_type == disease_type)

        if assay_type:
            stmt = stmt.where(Sample.assay_type == assay_type)

        if sample_status:
            stmt = stmt.where(Sample.sample_status == sample_status)

        if tumor_normal_status:
            stmt = stmt.where(Sample.tumor_normal_status == tumor_normal_status)

        if search_text:
            pattern = f"%{search_text.strip()}%"
            stmt = stmt.where(
                (Sample.sample_id.ilike(pattern))
                | (Patient.external_subject_id.ilike(pattern))
                | (Patient.disease_type.ilike(pattern))
                | (Sample.condition_label.ilike(pattern))
                | (Sample.specimen_site.ilike(pattern))
            )

        return stmt

    def _get_pipeline_references_by_run(
        self,
        pipeline_run_ids: Sequence[str],
    ) -> dict[str, list[dict[str, Any]]]:
        if not pipeline_run_ids:
            return {}

        stmt = (
            select(
                PipelineRunReference.pipeline_run_id,
                PipelineRunReference.reference_id,
                PipelineRunReference.usage_role,
                PipelineRunReference.execution_order,
                PipelineRunReference.step_label,
                PipelineRunReference.created_at,
            )
            .where(PipelineRunReference.pipeline_run_id.in_(pipeline_run_ids))
            .order_by(
                PipelineRunReference.pipeline_run_id,
                PipelineRunReference.execution_order.asc().nullslast(),
                PipelineRunReference.reference_id,
            )
        )

        rows = self.session.execute(stmt).all()
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            grouped.setdefault(row.pipeline_run_id, []).append(
                {
                    "reference_id": row.reference_id,
                    "usage_role": row.usage_role,
                    "execution_order": row.execution_order,
                    "step_label": row.step_label,
                    "created_at": row.created_at,
                }
            )
        return grouped

    def _get_pipeline_tools_by_run(
        self,
        pipeline_run_ids: Sequence[str],
    ) -> dict[str, list[dict[str, Any]]]:
        if not pipeline_run_ids:
            return {}

        stmt = (
            select(
                PipelineRunTool.pipeline_run_id,
                PipelineRunTool.tool_id,
                PipelineRunTool.usage_role,
                PipelineRunTool.execution_order,
                PipelineRunTool.step_label,
                PipelineRunTool.created_at,
            )
            .where(PipelineRunTool.pipeline_run_id.in_(pipeline_run_ids))
            .order_by(
                PipelineRunTool.pipeline_run_id,
                PipelineRunTool.execution_order.asc().nullslast(),
                PipelineRunTool.tool_id,
            )
        )

        rows = self.session.execute(stmt).all()
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            grouped.setdefault(row.pipeline_run_id, []).append(
                {
                    "tool_id": row.tool_id,
                    "usage_role": row.usage_role,
                    "execution_order": row.execution_order,
                    "step_label": row.step_label,
                    "created_at": row.created_at,
                }
            )
        return grouped