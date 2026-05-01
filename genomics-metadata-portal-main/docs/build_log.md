# Build Log

## 2026-02-20 - Project initialization
- Created repository root structure for Genomics Metadata, Provenance & Analysis Portal.
- Initialized Git repository on main branch.
- Created Python virtual environment for local Mac development.
- Installed initial Python dependencies for PostgreSQL, SQLAlchemy, Streamlit, testing, linting, and synthetic data generation.
- Added project skeleton directories and starter files.
- Added Docker Compose configuration for local PostgreSQL.
- Added root config files: `.gitignore`, `.dockerignore`, `.env.example`, `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `Makefile`, and `Dockerfile`.

## 2026-02-21 - Environment stabilization and infrastructure verification
- Identified incomplete virtual environment caused by macOS system Python (CommandLineTools).
- Removed broken `.venv` and recreated environment using Homebrew-managed Python interpreter.
- Successfully activated virtual environment and verified interpreter isolation.
- Installed full project dependency set (runtime + dev tools).
- Created all root configuration files (`pyproject.toml`, `.gitignore`, `.dockerignore`, `.env`, `Makefile`, `Dockerfile`).
- Verified repository structure integrity using directory inspection.
- Started PostgreSQL container using Docker Compose and confirmed healthy status.
- Validated database connectivity using `psql` inside container.
- Confirmed clean Git working tree after initial commit.

## 2026-02-22 - Core relational schema implemented
- Implemented normalized PostgreSQL schema covering patients, samples, sequencing runs, pipelines, provenance, QC, variant summaries, file assets, and audit events.
- Added foreign key relationships, integrity constraints, controlled vocabulary checks, and analytical indexes.
- Seeded core reference/master data for pipelines, pipeline versions, references, tools, and QC metric definitions.
- Verified table creation and seed counts directly in PostgreSQL container.
- Resolved Docker Compose stdin execution issue on macOS by using non-TTY SQL execution with `docker compose exec -T`.

## 2026-02-23 - Python database layer implemented
- Added environment-driven application settings using Pydantic settings.
- Implemented SQLAlchemy engine, session factory, and declarative base.
- Added structured application logging configuration.
- Implemented SQLAlchemy ORM models aligned to the PostgreSQL schema.
- Added Python-based database smoke test to validate connectivity and seeded master data access.
- Resolved Python module import issue by standardizing on module-style script execution from repository root.
- Added `scripts/__init__.py` and VS Code workspace settings to improve local interpreter and import resolution.

## 2026-02-24 - Synthetic data generation implemented
- Added shared enum definitions, ID generators, and date utilities for controlled synthetic record creation.
- Implemented synthetic data generator for patients, batches, samples, sequencing runs, pipeline runs, QC results, variant summaries, file assets, analysis summaries, and audit events.
- Generated realistic raw manifests and example files aligned to the production schema and ingestion plan.
- Introduced operational realism including reruns, failed runs, WARN/FAIL QC cases, outdated pipeline version usage, high-TMB cases, and KRAS-mutated samples.
- Standardized the local runtime on Homebrew Python 3.11 to support the intended project feature set and reproducible script execution.
- Verified generated artifact structure and manifest summary from the local filesystem.

## 2026-02-25 - Initial ingestion layer implemented
- Added reusable validation service for manifest structure, required fields, uniqueness, and controlled-value checks.
- Implemented sample ingest service for patients, batches, and samples.
- Added Python ingestion script for loading sample metadata manifests into PostgreSQL through the ORM/session layer.
- Verified loaded record counts and patient-sample joins in PostgreSQL after ingestion.
- Confirmed idempotent rerun behavior by re-executing sample ingestion without creating duplicate records.

## 2026-02-26 - Sequencing run registration implemented
- Added sequencing run registration service for loading sequencing runs and sample-run assignment manifests.
- Validated run metadata, allowed statuses/platforms, and foreign-key compatibility with previously loaded samples.
- Loaded sequencing run records and sample-to-run assignments into PostgreSQL.
- Verified sequencing lineage joins and confirmed idempotent rerun behavior for sequencing registration.

## 2026-02-27 - Synthetic provenance manifests added
- Extended the synthetic data generator to produce `pipeline_run_references.json` and `pipeline_run_tools.json`.
- Added explicit run-level provenance linkage between each pipeline run and seeded reference/tool master data.
- Included `usage_role`, `execution_order`, and `step_label` fields in generated provenance manifests to support downstream lineage ingestion and traceability.
- Regenerated synthetic raw artifacts and verified manifest summary counts for pipeline provenance outputs (`pipeline_run_references`: 250, `pipeline_run_tools`: 282).

## 2026-02-28 - Provenance ingestion service implemented
- Added `app/services/provenance_service.py` to register pipeline runs, run-level reference links, run-level tool links, and sample analysis summaries.
- Implemented foreign-key readiness checks against samples, sequencing runs, pipeline versions, reference master data, and tool master data before insertion.
- Added idempotent insert-if-missing behavior for pipeline runs, provenance association rows, and sample analysis summaries.
- Standardized provenance registration summary reporting for downstream script entry points.

## 2026-02-28 - Pipeline provenance ingestion implemented
- Extended the synthetic data workflow to emit `pipeline_run_references.json` and `pipeline_run_tools.json` as first-class provenance manifests.
- Added `app/services/provenance_service.py` to register pipeline runs, run-level reference links, run-level tool links, and sample analysis summaries.
- Added `scripts/register_pipeline_run.py` as the operational entry point for provenance ingestion from raw JSON manifests.
- Aligned synthetic provenance IDs to seeded master data in `reference_resources` and `tool_registry`.
- Resolved ORM/schema drift for provenance association tables by updating model definitions and applying a schema patch to add missing provenance columns.
- Successfully loaded pipeline provenance into PostgreSQL with summary counts: `pipeline_runs_loaded=105`, `pipeline_run_references_loaded=253`, `pipeline_run_tools_loaded=345`, `sample_analysis_summaries_loaded=85`.
- Verified idempotent rerun behavior by re-executing provenance registration and confirming zero additional records were inserted.

## 2026-03-01 - File asset registration implemented
- Added `app/services/file_asset_service.py` to validate and register file asset manifests into PostgreSQL.
- Added `scripts/register_file_assets.py` as the operational entry point for file asset ingestion from `data/raw/file_manifests/file_assets.tsv`.
- Validated file asset foreign-key readiness against registered samples and pipeline runs before insertion.
- Successfully loaded file assets with idempotent rerun behavior.

## 2026-03-01 - QC ingestion implemented
- Added `app/services/qc_ingest_service.py` to validate and load QC result records into PostgreSQL.
- Added `scripts/ingest_qc_results.py` as the operational entry point for QC ingestion from `data/raw/qc_metrics/qc_results.json`.
- Implemented QC metric name to `qc_metric_def_id` resolution against seeded QC metric definition master data before insert.
- Validated QC result foreign-key readiness against samples, pipeline runs, QC metric definitions, and source file assets before insertion.
- Successfully loaded QC results with summary count `qc_results_loaded=319` and verified idempotent rerun behavior with zero additional inserts.

## 2026-03-01 - Variant ingestion implemented
- Added `app/services/variant_ingest_service.py` to validate and load variant summary records into PostgreSQL.
- Added `scripts/ingest_variant_summaries.py` as the operational entry point for variant ingestion from `data/raw/variant_summaries/variant_summary.tsv`.
- Validated variant summary foreign-key readiness against samples, pipeline runs, and source file assets before insertion.
- Successfully loaded variant summaries with summary count `variant_summaries_loaded=220` and verified idempotent rerun behavior with zero additional inserts.

## 2026-03-02 - Sample repository/query layer started
- Added `app/repositories/sample_repository.py` as the first repository-layer component for sample-centric exploration.
- Implemented sample listing, detail lookup, provenance tracing, QC retrieval, and variant retrieval queries on top of the ORM/session layer.
- Added `scripts/test_sample_repository.py` to smoke test repository methods against the populated PostgreSQL database.
- Verified end-to-end retrieval of sample metadata, sequencing lineage, pipeline provenance, QC results, and variant summaries from PostgreSQL.

## 2026-03-02 - Sample repository query behavior refined
- Refined `SampleRepository.list_samples()` to resolve latest sample-level QC status through the `qc_summary_flag` metric rather than allowing duplicate sample rows from broader QC joins.
- Re-ran repository smoke testing and confirmed distinct sample rows in listing output while preserving provenance, QC, and variant retrieval behavior.

## 2026-03-02 - Streamlit app entrypoint added
- Added `streamlit_app/Home.py` as the main Streamlit entrypoint for the portal.
- Standardized Streamlit import path handling so page modules can import the `app` package reliably from the repository root.
- Confirmed the Sample Explorer page should be launched through the Streamlit app entrypoint rather than directly as a standalone page file.

## 2026-03-02 - QC dashboard page implemented
- Added `app/repositories/qc_repository.py` for QC-focused summary and recent-result queries.
- Added `streamlit_app/pages/03_QC_Dashboard.py` as an analyst-facing QC monitoring page.
- Implemented assay, QC status, and metric-name filters along with QC status summary metrics and recent QC result inspection.

## 2026-03-02 - Variant search page implemented
- Added `app/repositories/variant_repository.py` for cross-sample variant querying.
- Added `streamlit_app/pages/04_Variant_Search.py` for analyst-facing variant exploration.
- Implemented gene-level and clinical significance filtering with optional reported-only constraint.

## 2026-03-02 - Provenance trace page implemented
- Added `app/repositories/provenance_repository.py` for sample-level end-to-end provenance trace workflows.
- Added `streamlit_app/pages/05_Provenance_Trace.py` as an analyst-facing lineage page spanning sequencing, pipeline execution, tools, references, files, QC, and variant outputs.
- Implemented sample-level trace exploration that groups downstream assets and results by pipeline run.

## 2026-03-02 - Data dictionary page implemented
- Added `app/repositories/data_dictionary_repository.py` for schema-introspection-driven dictionary views.
- Added `streamlit_app/pages/06_Data_Dictionary.py` as an interactive in-app schema reference.
- Implemented table inventory, column metadata, primary key, foreign key, and index inspection through the Streamlit UI.

## 2026-03-02 - Initial smoke tests added
- Added `tests/test_smoke_pipeline.py` to verify database connectivity and expected core table counts.
- Added `tests/test_sample_repository.py` to validate sample-centric repository workflows.
- Added `tests/test_run_repository.py` to validate run-centric repository workflows.
- Executed targeted smoke tests for connectivity, core counts, and repository behavior and confirmed all tests passed.

## 2026-03-30 - Full stack containerization implemented
- Extended existing PostgreSQL-only Docker Compose setup to full-stack orchestration including Streamlit application container.
- Added production-ready Dockerfile for Streamlit app using Python 3.11 slim base image and dependency installation via requirements.txt.
- Configured container-to-container networking with application connecting to PostgreSQL using Docker service name (`postgres`) instead of localhost.
- Standardized environment-driven configuration to support both local venv execution and Docker runtime without code changes.
- Added health checks for both PostgreSQL and Streamlit services to ensure reliable startup sequencing.
- Verified successful end-to-end startup using `docker compose up --build` with working UI and database connectivity across all pages.
- Ensured no credentials or environment-specific values are baked into the container image.