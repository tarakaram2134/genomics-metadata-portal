BEGIN;

ALTER TABLE samples
    ADD CONSTRAINT fk_samples_patient
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_samples_batch
        FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT chk_samples_received_after_collection
        CHECK (received_date IS NULL OR collection_date IS NULL OR received_date >= collection_date);

ALTER TABLE sample_run_assignments
    ADD CONSTRAINT fk_sample_run_assignments_sample
        FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_sample_run_assignments_seq_run
        FOREIGN KEY (seq_run_id) REFERENCES sequencing_runs(seq_run_id)
        ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE pipeline_versions
    ADD CONSTRAINT fk_pipeline_versions_pipeline
        FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT uq_pipeline_versions_pipeline_label
        UNIQUE (pipeline_id, version_label);

ALTER TABLE pipeline_runs
    ADD CONSTRAINT fk_pipeline_runs_sample
        FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_pipeline_runs_seq_run
        FOREIGN KEY (seq_run_id) REFERENCES sequencing_runs(seq_run_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_pipeline_runs_pipeline_version
        FOREIGN KEY (pipeline_version_id) REFERENCES pipeline_versions(pipeline_version_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT chk_pipeline_run_time_order
        CHECK (run_finished_at IS NULL OR run_finished_at >= run_started_at);

ALTER TABLE pipeline_run_references
    ADD CONSTRAINT fk_pipeline_run_references_run
        FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(pipeline_run_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_pipeline_run_references_reference
        FOREIGN KEY (reference_id) REFERENCES reference_resources(reference_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT uq_pipeline_run_reference_usage
        UNIQUE (pipeline_run_id, reference_id, usage_role);

ALTER TABLE pipeline_run_tools
    ADD CONSTRAINT fk_pipeline_run_tools_run
        FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(pipeline_run_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_pipeline_run_tools_tool
        FOREIGN KEY (tool_id) REFERENCES tool_registry(tool_id)
        ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE file_assets
    ADD CONSTRAINT fk_file_assets_sample
        FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_file_assets_pipeline_run
        FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(pipeline_run_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT chk_file_assets_positive_size
        CHECK (file_size_bytes IS NULL OR file_size_bytes >= 0),
    ADD CONSTRAINT chk_file_assets_has_parent
        CHECK (sample_id IS NOT NULL OR pipeline_run_id IS NOT NULL);

ALTER TABLE qc_results
    ADD CONSTRAINT fk_qc_results_sample
        FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_qc_results_pipeline_run
        FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(pipeline_run_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_qc_results_metric_def
        FOREIGN KEY (qc_metric_def_id) REFERENCES qc_metric_definitions(qc_metric_def_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_qc_results_source_file
        FOREIGN KEY (source_file_asset_id) REFERENCES file_assets(file_asset_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT chk_qc_results_has_value
        CHECK (metric_value_numeric IS NOT NULL OR metric_value_text IS NOT NULL);

ALTER TABLE variant_summary
    ADD CONSTRAINT fk_variant_summary_sample
        FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_variant_summary_pipeline_run
        FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(pipeline_run_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_variant_summary_source_file
        FOREIGN KEY (source_file_asset_id) REFERENCES file_assets(file_asset_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT chk_variant_summary_vaf_range
        CHECK (tumor_vaf IS NULL OR (tumor_vaf >= 0 AND tumor_vaf <= 1));

ALTER TABLE sample_analysis_summary
    ADD CONSTRAINT fk_sample_analysis_summary_sample
        FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT chk_sample_analysis_summary_tmb_nonnegative
        CHECK (tmb_score IS NULL OR tmb_score >= 0),
    ADD CONSTRAINT chk_sample_analysis_summary_purity_range
        CHECK (purity_estimate IS NULL OR (purity_estimate >= 0 AND purity_estimate <= 1)),
    ADD CONSTRAINT chk_sample_analysis_summary_ploidy_nonnegative
        CHECK (ploidy_estimate IS NULL OR ploidy_estimate >= 0);

ALTER TABLE patients
    ADD CONSTRAINT chk_patients_sex
        CHECK (sex IS NULL OR sex IN ('FEMALE', 'MALE', 'UNKNOWN')),
    ADD CONSTRAINT chk_patients_age_band
        CHECK (age_band IS NULL OR age_band IN ('PEDIATRIC', 'YOUNG_ADULT', 'ADULT', 'OLDER_ADULT', 'UNKNOWN'));

ALTER TABLE samples
    ADD CONSTRAINT chk_samples_sample_type
        CHECK (sample_type IN ('TUMOR', 'NORMAL', 'BLOOD', 'RNA', 'CFDNA')),
    ADD CONSTRAINT chk_samples_assay_type
        CHECK (assay_type IN ('WES', 'RNA_SEQ', 'TARGETED_PANEL')),
    ADD CONSTRAINT chk_samples_sample_status
        CHECK (sample_status IN ('RECEIVED', 'REGISTERED', 'IN_PROCESS', 'COMPLETE', 'HOLD')),
    ADD CONSTRAINT chk_samples_tumor_normal_status
        CHECK (tumor_normal_status IS NULL OR tumor_normal_status IN ('TUMOR', 'NORMAL', 'PAIRED_NORMAL', 'UNKNOWN'));

ALTER TABLE sequencing_runs
    ADD CONSTRAINT chk_sequencing_runs_platform
        CHECK (platform IN ('ILLUMINA', 'ONT')),
    ADD CONSTRAINT chk_sequencing_runs_status
        CHECK (run_status IN ('PLANNED', 'COMPLETE', 'PARTIAL', 'FAILED'));

ALTER TABLE pipelines
    ADD CONSTRAINT chk_pipelines_category
        CHECK (pipeline_category IN ('ALIGNMENT', 'RNA_QUANT', 'SOMATIC_VARIANT', 'QC_AGGREGATION'));

ALTER TABLE reference_resources
    ADD CONSTRAINT chk_reference_resources_type
        CHECK (reference_type IN ('GENOME', 'ANNOTATION', 'TARGET_BED', 'TRANSCRIPTOME', 'BLACKLIST'));

ALTER TABLE tool_registry
    ADD CONSTRAINT chk_tool_registry_category
        CHECK (tool_category IN ('ALIGNER', 'VARIANT_CALLER', 'QC_TOOL', 'RNA_TOOL', 'ANNOTATOR', 'UTILITY'));

ALTER TABLE pipeline_runs
    ADD CONSTRAINT chk_pipeline_runs_status
        CHECK (run_status IN ('QUEUED', 'RUNNING', 'SUCCESS', 'FAILED', 'PARTIAL'));

ALTER TABLE pipeline_run_references
    ADD CONSTRAINT chk_pipeline_run_references_usage_role
        CHECK (
            usage_role IN (
                'PRIMARY_GENOME',
                'PRIMARY_ANNOTATION',
                'TARGET_INTERVALS',
                'TRANSCRIPTOME_INDEX',
                'FILTER_RESOURCE',
                'GENOME',
                'KNOWN_SITES',
                'CLINICAL_ANNOTATION',
                'CANCER_ANNOTATION',
                'GENOME_CONTEXT',
                'ANNOTATION',
                'ALIGNMENT_INDEX',
                'TRANSCRIPTOME'
            )
        );

ALTER TABLE file_assets
    ADD CONSTRAINT chk_file_assets_role
        CHECK (file_role IN ('RAW_FASTQ', 'BAM', 'CRAM', 'BAI', 'CRAI', 'VCF', 'MAF', 'QC_JSON', 'QC_TSV', 'COUNTS_MATRIX', 'LOG', 'REPORT')),
    ADD CONSTRAINT chk_file_assets_format
        CHECK (file_format IN ('FASTQ_GZ', 'BAM', 'CRAM', 'BAI', 'CRAI', 'VCF_GZ', 'TSV', 'JSON', 'TXT', 'MAF'));

ALTER TABLE qc_metric_definitions
    ADD CONSTRAINT chk_qc_metric_definitions_category
        CHECK (metric_category IN ('ALIGNMENT', 'COVERAGE', 'RNA_QC', 'VARIANT_QC', 'GENERAL')),
    ADD CONSTRAINT chk_qc_metric_definitions_data_type
        CHECK (data_type IN ('NUMERIC', 'TEXT', 'BOOLEAN')),
    ADD CONSTRAINT chk_qc_metric_definitions_bounds
        CHECK (
            lower_bound IS NULL
            OR upper_bound IS NULL
            OR lower_bound <= upper_bound
        );

ALTER TABLE qc_results
    ADD CONSTRAINT chk_qc_results_status
        CHECK (qc_status IN ('PASS', 'WARN', 'FAIL'));

ALTER TABLE variant_summary
    ADD CONSTRAINT chk_variant_summary_class
        CHECK (variant_class IN ('SNV', 'INDEL', 'CNV', 'FUSION')),
    ADD CONSTRAINT chk_variant_summary_clin_sig
        CHECK (clinical_significance IS NULL OR clinical_significance IN ('PATHOGENIC', 'LIKELY_PATHOGENIC', 'VUS', 'BENIGN', 'UNKNOWN'));

ALTER TABLE sample_analysis_summary
    ADD CONSTRAINT chk_sample_analysis_summary_msi_status
        CHECK (msi_status IS NULL OR msi_status IN ('MSI_HIGH', 'MSI_STABLE', 'INDETERMINATE'));

ALTER TABLE audit_events
    ADD CONSTRAINT chk_audit_events_entity_type
        CHECK (entity_type IN ('PATIENT', 'SAMPLE', 'SEQUENCING_RUN', 'PIPELINE_RUN', 'FILE_ASSET', 'QC_RESULT', 'VARIANT_SUMMARY')),
    ADD CONSTRAINT chk_audit_events_event_type
        CHECK (event_type IN ('CREATED', 'REGISTERED', 'INGESTED', 'UPDATED', 'STATUS_CHANGED', 'LINKED', 'FAILED'));

CREATE UNIQUE INDEX IF NOT EXISTS uq_sample_run_assignment_unique
ON sample_run_assignments (
    sample_id,
    seq_run_id,
    COALESCE(lane_or_partition, ''),
    COALESCE(library_id, ''),
    COALESCE(barcode, '')
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_pipeline_run_tool_step
ON pipeline_run_tools (
    pipeline_run_id,
    tool_id,
    COALESCE(step_label, ''),
    COALESCE(execution_order, -1)
);

CREATE INDEX IF NOT EXISTS idx_samples_patient_id
    ON samples(patient_id);

CREATE INDEX IF NOT EXISTS idx_samples_batch_id
    ON samples(batch_id);

CREATE INDEX IF NOT EXISTS idx_samples_condition_label
    ON samples(condition_label);

CREATE INDEX IF NOT EXISTS idx_samples_assay_type
    ON samples(assay_type);

CREATE INDEX IF NOT EXISTS idx_samples_sample_status
    ON samples(sample_status);

CREATE INDEX IF NOT EXISTS idx_sequencing_runs_run_date
    ON sequencing_runs(run_date);

CREATE INDEX IF NOT EXISTS idx_sequencing_runs_run_status
    ON sequencing_runs(run_status);

CREATE INDEX IF NOT EXISTS idx_sample_run_assignments_sample_id
    ON sample_run_assignments(sample_id);

CREATE INDEX IF NOT EXISTS idx_sample_run_assignments_seq_run_id
    ON sample_run_assignments(seq_run_id);

CREATE INDEX IF NOT EXISTS idx_pipeline_versions_pipeline_id
    ON pipeline_versions(pipeline_id);

CREATE INDEX IF NOT EXISTS idx_pipeline_versions_is_current
    ON pipeline_versions(is_current);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_sample_id
    ON pipeline_runs(sample_id);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_seq_run_id
    ON pipeline_runs(seq_run_id);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_pipeline_version_id
    ON pipeline_runs(pipeline_version_id);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_run_status
    ON pipeline_runs(run_status);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started_at
    ON pipeline_runs(run_started_at);

CREATE INDEX IF NOT EXISTS idx_pipeline_run_references_run_id
    ON pipeline_run_references(pipeline_run_id);

CREATE INDEX IF NOT EXISTS idx_pipeline_run_tools_run_id
    ON pipeline_run_tools(pipeline_run_id);

CREATE INDEX IF NOT EXISTS idx_file_assets_sample_id
    ON file_assets(sample_id);

CREATE INDEX IF NOT EXISTS idx_file_assets_pipeline_run_id
    ON file_assets(pipeline_run_id);

CREATE INDEX IF NOT EXISTS idx_file_assets_file_role
    ON file_assets(file_role);

CREATE INDEX IF NOT EXISTS idx_file_assets_is_current
    ON file_assets(is_current);

CREATE INDEX IF NOT EXISTS idx_qc_results_sample_id
    ON qc_results(sample_id);

CREATE INDEX IF NOT EXISTS idx_qc_results_pipeline_run_id
    ON qc_results(pipeline_run_id);

CREATE INDEX IF NOT EXISTS idx_qc_results_metric_def_id
    ON qc_results(qc_metric_def_id);

CREATE INDEX IF NOT EXISTS idx_qc_results_status
    ON qc_results(qc_status);

CREATE INDEX IF NOT EXISTS idx_variant_summary_sample_id
    ON variant_summary(sample_id);

CREATE INDEX IF NOT EXISTS idx_variant_summary_pipeline_run_id
    ON variant_summary(pipeline_run_id);

CREATE INDEX IF NOT EXISTS idx_variant_summary_gene_symbol
    ON variant_summary(gene_symbol);

CREATE INDEX IF NOT EXISTS idx_variant_summary_reported_flag
    ON variant_summary(reported_flag);

CREATE INDEX IF NOT EXISTS idx_sample_analysis_summary_sample_id
    ON sample_analysis_summary(sample_id);

CREATE INDEX IF NOT EXISTS idx_audit_events_entity_lookup
    ON audit_events(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp
    ON audit_events(event_timestamp);

COMMIT;