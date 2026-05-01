from __future__ import annotations

from typing import Any

from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


TABLE_DESCRIPTIONS: dict[str, str] = {
    "patients": "Subject-level registry containing disease context and demographic metadata.",
    "batches": "Operational intake batches grouping submitted samples.",
    "samples": "Sample-level metadata including assay, specimen context, and lifecycle status.",
    "sequencing_runs": "Sequencing instrument runs and their operational metadata.",
    "sample_run_assignments": "Links samples to sequencing runs, lanes/partitions, and barcodes.",
    "pipelines": "Master registry of logical analysis pipelines.",
    "pipeline_versions": "Versioned implementations of pipelines used for provenance tracking.",
    "pipeline_runs": "Concrete executions of a pipeline version for a sample/run context.",
    "pipeline_run_references": "Run-level lineage links between pipeline runs and reference resources.",
    "pipeline_run_tools": "Run-level lineage links between pipeline runs and tools used in execution.",
    "reference_resources": "Master registry of genome, annotation, transcriptome, and interval references.",
    "tool_registry": "Master registry of bioinformatics tools used across workflows.",
    "qc_metric_definitions": "Controlled definitions for QC metrics stored in QC results.",
    "qc_results": "Measured QC results linked to samples, pipeline runs, and source assets.",
    "variant_summary": "Variant-level summary results used for cross-sample and sample-centric review.",
    "sample_analysis_summary": "Sample-level analytical summary including TMB, MSI, purity, and subtype.",
    "file_assets": "Registered raw and derived file assets with current/outdated lineage context.",
    "audit_events": "Audit trail of important metadata, file, QC, variant, and run events.",
}


COLUMN_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "patients": {
        "patient_id": "Internal unique patient identifier.",
        "external_subject_id": "External or study-facing subject identifier.",
        "disease_type": "Disease or cohort classification for the patient.",
        "condition_group": "High-level grouping such as case or control.",
        "sex": "Recorded biological sex or unknown.",
        "age_band": "Age bucket rather than exact age for safer synthetic metadata.",
        "created_at": "Timestamp when the patient record was created.",
    },
    "samples": {
        "sample_id": "Internal unique sample identifier.",
        "patient_id": "Foreign key to the patient owning the sample.",
        "batch_id": "Foreign key to the intake batch containing the sample.",
        "sample_type": "Material type such as tumor, blood, RNA, or cfDNA.",
        "assay_type": "Assay performed for this sample.",
        "collection_date": "Date specimen was collected.",
        "received_date": "Date specimen was received for processing.",
        "specimen_site": "Tissue or body site of the specimen.",
        "condition_label": "Disease/condition context for the sample.",
        "sample_status": "Operational status of the sample.",
        "tumor_normal_status": "Tumor vs normal designation.",
        "library_prep_kit": "Library preparation kit used.",
        "notes": "Free-text sample notes.",
        "created_at": "Timestamp when the sample was registered.",
    },
    "pipeline_runs": {
        "pipeline_run_id": "Unique identifier for a concrete pipeline execution.",
        "sample_id": "Sample processed by the run.",
        "seq_run_id": "Optional sequencing run that fed the pipeline execution.",
        "pipeline_version_id": "Exact pipeline version used.",
        "run_started_at": "Timestamp when the run started.",
        "run_finished_at": "Timestamp when the run finished.",
        "run_status": "Execution status such as success, partial, or failed.",
        "parameter_set_json": "JSON payload of runtime parameters used.",
        "execution_environment": "Execution environment such as docker-local or slurm-cluster.",
        "triggered_by": "Actor or system that triggered the run.",
        "workflow_run_uuid": "External workflow engine execution UUID.",
        "log_path": "Location of the run log.",
        "work_dir_path": "Location of the run work directory.",
        "failure_reason": "Failure reason when applicable.",
        "created_at": "Timestamp when the record was created.",
    },
    "pipeline_run_references": {
        "pipeline_run_reference_id": "Synthetic surrogate key for the association row.",
        "pipeline_run_id": "Pipeline run linked to a reference.",
        "reference_id": "Reference resource used by the run.",
        "usage_role": "How the reference was used, such as genome or annotation.",
        "execution_order": "Relative order within execution context.",
        "step_label": "Named workflow step for this association.",
        "created_at": "Timestamp when the association was recorded.",
    },
    "pipeline_run_tools": {
        "pipeline_run_tool_id": "Synthetic surrogate key for the association row.",
        "pipeline_run_id": "Pipeline run linked to a tool.",
        "tool_id": "Tool used by the run.",
        "usage_role": "How the tool was used, such as aligner or annotator.",
        "execution_order": "Relative execution order of the tool within the run.",
        "step_label": "Named workflow step for this association.",
        "created_at": "Timestamp when the association was recorded.",
    },
    "file_assets": {
        "file_asset_id": "Unique identifier for a registered file.",
        "sample_id": "Sample linked to the file.",
        "pipeline_run_id": "Optional pipeline run that generated the file.",
        "file_role": "Role of the file in the workflow, such as BAM, VCF, QC_JSON.",
        "file_format": "Storage/serialization format of the file.",
        "path_uri": "URI where the file is stored.",
        "checksum": "Checksum for integrity verification.",
        "file_size_bytes": "File size in bytes.",
        "source_system": "System or process that registered/generated the file.",
        "is_current": "Whether the file is considered current vs outdated.",
        "created_at": "Timestamp when the file asset record was created.",
    },
    "qc_results": {
        "qc_result_id": "Unique identifier for a QC result row.",
        "sample_id": "Sample linked to the QC result.",
        "pipeline_run_id": "Pipeline run linked to the QC result.",
        "qc_metric_def_id": "Normalized QC metric definition ID.",
        "metric_value_numeric": "Numeric metric value when applicable.",
        "metric_value_text": "Text metric value when applicable.",
        "qc_status": "PASS/WARN/FAIL status for the metric.",
        "measured_at": "Timestamp the QC metric was measured.",
        "source_file_asset_id": "Optional source asset from which the metric was derived.",
    },
    "variant_summary": {
        "variant_summary_id": "Unique identifier for the variant summary row.",
        "sample_id": "Sample carrying the variant call/summary.",
        "pipeline_run_id": "Pipeline run that generated the variant summary.",
        "gene_symbol": "Gene symbol associated with the variant.",
        "variant_class": "Variant class such as SNV, INDEL, CNV, or FUSION.",
        "protein_change": "Protein-level representation when applicable.",
        "chromosome": "Chromosome identifier.",
        "position": "Genomic position.",
        "ref_allele": "Reference allele.",
        "alt_allele": "Alternate allele.",
        "tumor_vaf": "Tumor variant allele frequency.",
        "clinical_significance": "Clinical significance classification.",
        "is_driver": "Whether the variant is considered a driver.",
        "reported_flag": "Whether the variant is reportable/high priority.",
        "source_file_asset_id": "Optional source asset containing the variant.",
        "created_at": "Timestamp when the variant summary row was created.",
    },
}


class DataDictionaryRepository:
    """
    Repository for schema/data-dictionary exploration.
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self.inspector = inspect(session.get_bind())

    def list_tables(self) -> list[dict[str, Any]]:
        table_names = sorted(self.inspector.get_table_names())
        tables: list[dict[str, Any]] = []

        for table_name in table_names:
            columns = self.inspector.get_columns(table_name)
            pk = self.inspector.get_pk_constraint(table_name) or {}
            fks = self.inspector.get_foreign_keys(table_name) or []

            tables.append(
                {
                    "table_name": table_name,
                    "description": TABLE_DESCRIPTIONS.get(table_name, ""),
                    "column_count": len(columns),
                    "primary_key": pk.get("constrained_columns", []),
                    "foreign_key_count": len(fks),
                }
            )

        return tables

    def get_table_dictionary(self, table_name: str) -> dict[str, Any]:
        columns = self.inspector.get_columns(table_name)
        pk = self.inspector.get_pk_constraint(table_name) or {}
        fks = self.inspector.get_foreign_keys(table_name) or []
        indexes = self.inspector.get_indexes(table_name) or []

        fk_map: dict[str, list[dict[str, Any]]] = {}
        for fk in fks:
            constrained = fk.get("constrained_columns", [])
            referred_table = fk.get("referred_table")
            referred_columns = fk.get("referred_columns", [])
            name = fk.get("name")
            for idx, constrained_col in enumerate(constrained):
                fk_map.setdefault(constrained_col, []).append(
                    {
                        "constraint_name": name,
                        "referred_table": referred_table,
                        "referred_column": referred_columns[idx] if idx < len(referred_columns) else None,
                    }
                )

        primary_key_columns = set(pk.get("constrained_columns", []))

        column_rows: list[dict[str, Any]] = []
        for column in columns:
            name = column["name"]
            raw_type = column["type"]
            nullable = column.get("nullable", True)
            default = column.get("default")

            column_rows.append(
                {
                    "column_name": name,
                    "data_type": str(raw_type),
                    "nullable": nullable,
                    "primary_key": name in primary_key_columns,
                    "foreign_keys": fk_map.get(name, []),
                    "default": str(default) if default is not None else None,
                    "description": COLUMN_DESCRIPTIONS.get(table_name, {}).get(name, ""),
                }
            )

        return {
            "table_name": table_name,
            "description": TABLE_DESCRIPTIONS.get(table_name, ""),
            "columns": column_rows,
            "primary_key": list(primary_key_columns),
            "foreign_keys": fks,
            "indexes": indexes,
        }