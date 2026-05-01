# Repo Inventory

## Current Top-Level Structure
- `app/` - Python application package for config, DB access, models, repositories, services, schemas, and utilities
- `sql/` - PostgreSQL schema, indexes, reference data, views, reporting queries, and validation checks
- `streamlit_app/` - Analyst-facing Streamlit interface
- `scripts/` - Operational scripts for DB initialization, seeding, ingestion, synthetic data generation, and smoke testing
- `data/` - Example inputs plus generated raw and processed artifacts
- `tests/` - Schema, ingestion, query, provenance, and Streamlit smoke tests
- `docs/` - Architecture, logs, deployment plan, workflow examples, and screenshots

## Infrastructure Status

- Python virtual environment: configured and verified (`.venv`)
- PostgreSQL: running via Docker Compose (`postgres:16`)
- Streamlit application: containerized and running via Docker Compose
- Full-stack containerization: PostgreSQL + Streamlit app orchestrated with Docker Compose
- Environment configuration: `.env` and `.env.example` in place
- Dependency management: `requirements.txt` and `requirements-dev.txt`
- Build tooling: `Makefile` with standard commands
- Containerization: production-ready `Dockerfile` and `docker-compose.yml` supporting local and deployment environments

## Database Artifacts Added
- `sql/001_schema.sql` - base relational table definitions
- `sql/002_constraints_indexes.sql` - foreign keys, checks, uniqueness rules, and indexes
- `sql/003_seed_reference_data.sql` - master/reference data for pipelines, versions, tools, references, and QC metrics

## Python Data Layer Artifacts Added
- `app/config.py` - environment-driven application settings
- `app/db.py` - SQLAlchemy engine, session factory, and declarative base
- `app/logging_config.py` - shared structured logging configuration
- `app/models/` - ORM definitions aligned to relational schema
- `scripts/smoke_test.py` - Python database connectivity and seed-data verification
- `scripts/__init__.py` - enables module-style script execution
- `.vscode/settings.json` - local editor interpreter and import path configuration

## Synthetic Data Artifacts Added
- `app/utils/enums.py` - controlled vocabulary enums used across generation and ingestion
- `app/utils/id_generators.py` - deterministic ID helpers for project entities
- `app/utils/date_utils.py` - shared synthetic timeline utilities
- `app/utils/manifest_parsers.py` - starter manifest readers for TSV/JSON inputs
- `scripts/generate_synthetic_data.py` - synthetic manifest and output generator
- `data/raw/` - generated synthetic source artifacts for ingestion

## Ingestion Layer Artifacts Added
- `app/services/validation_service.py` - reusable manifest validation helpers
- `app/services/sample_ingest_service.py` - patient, batch, and sample ingestion logic
- `scripts/init_db.py` - Python-driven database initialization from SQL files
- `scripts/ingest_samples.py` - sample metadata ingestion entry point

## Sequencing Registration Artifacts Added
- `app/services/run_registration_service.py` - sequencing run and assignment registration logic
- `scripts/register_sequencing_run.py` - sequencing registration entry point

## Synthetic Data Artifacts Added
- `data/raw/pipeline_runs/pipeline_run_references.json` - synthetic run-to-reference provenance links with usage role, step label, and execution order
- `data/raw/pipeline_runs/pipeline_run_tools.json` - synthetic run-to-tool provenance links with usage role, step label, and execution order

## Ingestion Layer Artifacts Added
- `app/services/provenance_service.py` - registers pipeline runs, run-level provenance links, and sample analysis summaries

## Database Artifacts Added
- `sql/004_provenance_association_alignment.sql` - schema patch aligning provenance association tables to the intended lineage model

## Synthetic Data Artifacts Added
- `data/raw/pipeline_runs/pipeline_run_references.json` - synthetic run-to-reference provenance links with usage role, execution order, and step label
- `data/raw/pipeline_runs/pipeline_run_tools.json` - synthetic run-to-tool provenance links with usage role, execution order, and step label

## Ingestion Layer Artifacts Added
- `app/services/provenance_service.py` - registers pipeline runs, run-level provenance links, and sample analysis summaries
- `scripts/register_pipeline_run.py` - provenance registration entry point for pipeline runs, run references, run tools, and analysis summaries
- `app/services/file_asset_service.py` - validates and registers file asset records into PostgreSQL
- `scripts/register_file_assets.py` - file asset ingestion entry point for raw file manifests
- `app/services/qc_ingest_service.py` - validates and loads QC result records into PostgreSQL
- `scripts/ingest_qc_results.py` - QC ingestion entry point for raw QC metric manifests
- `app/services/variant_ingest_service.py` - validates and loads variant summary records into PostgreSQL
- `scripts/ingest_variant_summaries.py` - variant ingestion entry point for raw variant summary manifests

## Query Layer Artifacts Added
- `app/repositories/sample_repository.py` - sample-centric repository for listing, detail lookup, provenance tracing, QC retrieval, and variant retrieval
- `scripts/test_sample_repository.py` - repository smoke test for sample-centric query workflows
- `streamlit_app/Home.py` - main Streamlit entrypoint for the multi-page analyst-facing app
- `app/repositories/qc_repository.py` - QC-focused repository for status summaries and recent result inspection
- `streamlit_app/pages/03_QC_Dashboard.py` - analyst-facing Streamlit page for QC monitoring and QC result review
- `app/repositories/provenance_repository.py` - repository for end-to-end sample provenance trace workflows
- `streamlit_app/pages/05_Provenance_Trace.py` - analyst-facing Streamlit page for end-to-end lineage tracing
- `app/repositories/data_dictionary_repository.py` - repository for interactive schema/data-dictionary exploration
- `streamlit_app/pages/06_Data_Dictionary.py` - analyst-facing Streamlit page for schema and metadata inspection

## Test Artifacts Added
- `tests/test_smoke_pipeline.py` - smoke checks for DB connectivity and core table counts
- `tests/test_sample_repository.py` - smoke tests for sample-centric repository workflows
- `tests/test_run_repository.py` - smoke tests for run-centric repository workflows