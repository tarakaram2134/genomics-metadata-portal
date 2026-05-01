BEGIN;

CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    external_subject_id TEXT NOT NULL UNIQUE,
    disease_type TEXT NOT NULL,
    condition_group TEXT NOT NULL,
    sex TEXT NULL,
    age_band TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS batches (
    batch_id TEXT PRIMARY KEY,
    batch_name TEXT NOT NULL UNIQUE,
    project_code TEXT NOT NULL,
    submitted_by TEXT NOT NULL,
    submission_date DATE NOT NULL,
    notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS samples (
    sample_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    batch_id TEXT NULL,
    sample_type TEXT NOT NULL,
    assay_type TEXT NOT NULL,
    collection_date DATE NULL,
    received_date DATE NULL,
    specimen_site TEXT NULL,
    condition_label TEXT NOT NULL,
    sample_status TEXT NOT NULL,
    tumor_normal_status TEXT NULL,
    library_prep_kit TEXT NULL,
    notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sequencing_runs (
    seq_run_id TEXT PRIMARY KEY,
    instrument_run_name TEXT NOT NULL UNIQUE,
    platform TEXT NOT NULL,
    instrument_model TEXT NULL,
    flowcell_id TEXT NOT NULL,
    run_date DATE NOT NULL,
    read_length TEXT NULL,
    paired_end BOOLEAN NOT NULL DEFAULT TRUE,
    center_name TEXT NOT NULL,
    run_status TEXT NOT NULL,
    notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sample_run_assignments (
    sample_run_assignment_id BIGSERIAL PRIMARY KEY,
    sample_id TEXT NOT NULL,
    seq_run_id TEXT NOT NULL,
    lane_or_partition TEXT NULL,
    library_id TEXT NULL,
    barcode TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipelines (
    pipeline_id TEXT PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    pipeline_category TEXT NOT NULL,
    description TEXT NULL,
    repo_url TEXT NULL,
    maintainer TEXT NULL,
    active_flag BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipeline_versions (
    pipeline_version_id TEXT PRIMARY KEY,
    pipeline_id TEXT NOT NULL,
    version_label TEXT NOT NULL,
    container_image TEXT NULL,
    container_tag TEXT NULL,
    workflow_definition_version TEXT NULL,
    release_date DATE NULL,
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reference_resources (
    reference_id TEXT PRIMARY KEY,
    reference_name TEXT NOT NULL,
    reference_type TEXT NOT NULL,
    reference_version TEXT NOT NULL,
    source_uri TEXT NULL,
    description TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tool_registry (
    tool_id TEXT PRIMARY KEY,
    tool_name TEXT NOT NULL,
    tool_version TEXT NOT NULL,
    tool_category TEXT NOT NULL,
    container_image TEXT NULL,
    notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    pipeline_run_id TEXT PRIMARY KEY,
    sample_id TEXT NOT NULL,
    seq_run_id TEXT NULL,
    pipeline_version_id TEXT NOT NULL,
    run_started_at TIMESTAMPTZ NOT NULL,
    run_finished_at TIMESTAMPTZ NULL,
    run_status TEXT NOT NULL,
    parameter_set_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    execution_environment TEXT NULL,
    triggered_by TEXT NULL,
    workflow_run_uuid TEXT NULL,
    log_path TEXT NULL,
    work_dir_path TEXT NULL,
    failure_reason TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipeline_run_references (
    pipeline_run_reference_id BIGSERIAL PRIMARY KEY,
    pipeline_run_id TEXT NOT NULL,
    reference_id TEXT NOT NULL,
    usage_role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_run_tools (
    pipeline_run_tool_id BIGSERIAL PRIMARY KEY,
    pipeline_run_id TEXT NOT NULL,
    tool_id TEXT NOT NULL,
    execution_order INTEGER NULL,
    step_label TEXT NULL
);

CREATE TABLE IF NOT EXISTS file_assets (
    file_asset_id TEXT PRIMARY KEY,
    sample_id TEXT NULL,
    pipeline_run_id TEXT NULL,
    file_role TEXT NOT NULL,
    file_format TEXT NOT NULL,
    path_uri TEXT NOT NULL,
    checksum TEXT NULL,
    file_size_bytes BIGINT NULL,
    source_system TEXT NULL,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS qc_metric_definitions (
    qc_metric_def_id TEXT PRIMARY KEY,
    metric_name TEXT NOT NULL UNIQUE,
    metric_category TEXT NOT NULL,
    description TEXT NULL,
    data_type TEXT NOT NULL,
    unit TEXT NULL,
    lower_bound NUMERIC NULL,
    upper_bound NUMERIC NULL,
    failure_rule_text TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS qc_results (
    qc_result_id TEXT PRIMARY KEY,
    sample_id TEXT NOT NULL,
    pipeline_run_id TEXT NOT NULL,
    qc_metric_def_id TEXT NOT NULL,
    metric_value_numeric NUMERIC NULL,
    metric_value_text TEXT NULL,
    qc_status TEXT NOT NULL,
    measured_at TIMESTAMPTZ NOT NULL,
    source_file_asset_id TEXT NULL
);

CREATE TABLE IF NOT EXISTS variant_summary (
    variant_summary_id TEXT PRIMARY KEY,
    sample_id TEXT NOT NULL,
    pipeline_run_id TEXT NOT NULL,
    gene_symbol TEXT NOT NULL,
    variant_class TEXT NOT NULL,
    protein_change TEXT NULL,
    chromosome TEXT NULL,
    position BIGINT NULL,
    ref_allele TEXT NULL,
    alt_allele TEXT NULL,
    tumor_vaf NUMERIC NULL,
    clinical_significance TEXT NULL,
    is_driver BOOLEAN NOT NULL DEFAULT FALSE,
    reported_flag BOOLEAN NOT NULL DEFAULT FALSE,
    source_file_asset_id TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sample_analysis_summary (
    sample_analysis_summary_id TEXT PRIMARY KEY,
    sample_id TEXT NOT NULL UNIQUE,
    tmb_score NUMERIC NULL,
    msi_status TEXT NULL,
    purity_estimate NUMERIC NULL,
    ploidy_estimate NUMERIC NULL,
    expression_subtype TEXT NULL,
    analysis_summary_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_events (
    audit_event_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor TEXT NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

COMMIT;