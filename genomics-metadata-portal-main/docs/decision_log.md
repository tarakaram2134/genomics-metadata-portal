# Decision Log

## 2026-02-20 - Local development model
- Decision: Use Python virtual environment for local app development on Mac and Docker Compose for PostgreSQL first.
- Rationale: Faster iteration for Python/Streamlit while keeping database environment consistent and cloud-aligned.
- Consequence: The app remains easy to run locally during development, while the database behaves like a managed external dependency.

## 2026-02-20 - PostgreSQL-first containerization
- Decision: Start with PostgreSQL-only Docker Compose and add full app containerization later.
- Rationale: Matches implementation priorities and reduces early debugging complexity.
- Consequence: Database can be validated independently before introducing full-stack container orchestration.

## 2026-02-20 - Python runtime standardization
- Decision: Use Homebrew Python instead of macOS system Python.
- Rationale: Ensures stable virtual environments and compatibility with modern Python tooling.
- Consequence: Prevents environment inconsistencies and improves reproducibility.

## 2026-02-21 - Python interpreter standardization enforcement
- Decision: Explicitly require Homebrew Python for local development instead of system Python.
- Rationale: macOS system Python can produce incomplete virtual environments and inconsistent dependency behavior.
- Consequence: Slight setup overhead, but significantly improved stability and reproducibility.

## 2026-02-21 - Early infrastructure validation
- Decision: Validate PostgreSQL container health and connectivity before implementing schema.
- Rationale: Prevents misattributing future schema or ingestion issues to infrastructure problems.
- Consequence: Cleaner debugging boundaries during database and service layer implementation.

## 2026-02-22 - Controlled vocabularies enforced with database checks
- Decision: Enforce key controlled vocabularies using PostgreSQL CHECK constraints rather than separate lookup tables in the first implementation.
- Rationale: Keeps the schema readable, strongly validated, and easier to demonstrate in a portfolio project while preserving operational realism.
- Consequence: Vocabulary expansion requires schema edits, but the design remains clear and robust for the intended scope.

## 2026-02-22 - Provenance modeled as explicit relational links
- Decision: Represent run-level tools and references with dedicated association tables (`pipeline_run_tools`, `pipeline_run_references`).
- Rationale: Supports precise provenance tracing and avoids burying critical lineage data inside JSON blobs.
- Consequence: More joins are required, but traceability and analytical value are much stronger.

## 2026-02-22 - Non-interactive SQL execution in Docker Compose
- Decision: Use `docker compose exec -T` when executing SQL files through stdin redirection on macOS.
- Rationale: Prevents TTY allocation errors during scripted PostgreSQL execution.
- Consequence: Local database initialization commands are more robust and reproducible.

## 2026-02-23 - Centralized configuration and session management
- Decision: Use a shared settings module and centralized SQLAlchemy session factory for all application components.
- Rationale: Prevents duplicated connection logic and supports clean reuse across scripts, repositories, tests, and UI pages.
- Consequence: Configuration becomes easier to manage and the codebase remains more maintainable as features expand.

## 2026-02-23 - ORM models aligned to existing SQL-first schema
- Decision: Build SQLAlchemy models against the already-implemented PostgreSQL schema rather than generating schema from ORM first.
- Rationale: The project is intentionally database-first to emphasize SQL design, integrity rules, and provenance-aware relational modeling.
- Consequence: SQL remains the primary schema contract, while Python models serve as an application access layer.

## 2026-02-23 - Module-style script execution
- Decision: Run project scripts using `python -m ...` from the repository root instead of direct file execution.
- Rationale: Ensures the repo root is on the Python import path and avoids fragile import behavior.
- Consequence: Script execution is more consistent across local development, testing, and future CI environments.

## 2026-02-24 - File-first synthetic data workflow
- Decision: Generate synthetic manifests and output-like files under `data/raw/` before implementing DB ingestion.
- Rationale: Mirrors real bioinformatics operations where systems ingest pipeline outputs and metadata artifacts rather than creating records directly in the database.
- Consequence: Ingestion scripts can be designed and tested against realistic source artifacts.

## 2026-02-24 - Deterministic synthetic data generation
- Decision: Use a fixed random seed for synthetic data generation.
- Rationale: Keeps development, testing, screenshots, and demonstrations reproducible across runs.
- Consequence: Generated datasets are stable unless the generator logic is intentionally changed.

## 2026-02-24 - Pin local development runtime to Python 3.11
- Decision: Standardize local development on Homebrew Python 3.11 instead of the newest available Python release.
- Rationale: Python 3.11 is modern, actively supported, broadly compatible with current libraries, and stable for portfolio development.
- Consequence: Reduces risk of version-edge compatibility issues while keeping the project on a current supported runtime.

## 2026-02-25 - Validation before ORM insertion
- Decision: Validate required columns, uniqueness, non-null rules, and controlled values before inserting manifests into the database.
- Rationale: Failing fast at the manifest layer produces cleaner debugging and prevents avoidable database integrity errors.
- Consequence: Ingestion scripts become more reliable and easier to reason about.

## 2026-02-25 - Idempotent primary-key-based ingest behavior
- Decision: Skip records whose primary keys already exist during initial ingestion scripts.
- Rationale: Allows safe local reruns during development without creating duplicates.
- Consequence: Current behavior favors insert-if-missing rather than full synchronization logic, which is sufficient for this project stage.

## 2026-02-26 - Register runs only after foundational sample ingest
- Decision: Load sequencing runs and sample-run assignments only after patients, batches, and samples are already present.
- Rationale: Keeps ingestion aligned with foreign-key dependencies and simplifies validation.
- Consequence: Registration order becomes explicit and easier to debug.

## 2026-02-26 - Assignment idempotency based on composite operational key
- Decision: Treat sample-run assignments as already loaded when the combination of sample, run, lane/partition, library_id, and barcode already exists.
- Rationale: Mirrors the uniqueness rule enforced in the database and prevents duplicate assignment records on rerun.
- Consequence: Local reloads remain safe without extra cleanup steps.

## 2026-02-27 - Synthetic provenance emitted as first-class manifests
- Decision: Generate `pipeline_run_references` and `pipeline_run_tools` as explicit synthetic manifests rather than deriving them during ingestion.
- Rationale: Keeps provenance closer to realistic pipeline metadata handoff, makes ingest deterministic, and preserves auditable lineage inputs.
- Consequence: Synthetic data generation becomes more detailed, but provenance registration logic becomes cleaner, simpler, and easier to validate.

## 2026-02-28 - Provenance registration uses validate-then-insert idempotent loading
- Decision: Implement provenance ingestion with service-level foreign-key validation followed by insert-if-missing behavior.
- Rationale: Keeps reruns safe during development while failing early on lineage integrity problems before partial provenance loads occur.
- Consequence: The service remains simple and reliable for the current phase, though full synchronization/update behavior can be added later if needed.

## 2026-02-28 - Provenance ingestion aligned to seeded master data and patched schema
- Decision: Keep provenance ingestion strict by requiring synthetic run-reference and run-tool manifests to use real seeded `reference_id` and `tool_id` values from master tables.
- Rationale: Preserves auditable lineage integrity and ensures provenance records remain compatible with relational trace queries.
- Consequence: Synthetic generator plans must stay aligned with reference/tool seed data, but the resulting provenance model is much stronger and more realistic.

## 2026-02-28 - Patch provenance association schema to match intended lineage model
- Decision: Add missing provenance fields to association tables (`execution_order`, `step_label`, `usage_role`, `created_at`) through an incremental SQL patch rather than weakening the service contract.
- Rationale: The provenance service and synthetic manifests were already designed around richer lineage metadata needed for execution-order and step-level traceability.
- Consequence: Slight schema maintenance overhead, but the database now better reflects the intended provenance design.

## 2026-03-01 - File assets registered before QC ingestion
- Decision: Load file assets before QC results instead of ingesting QC immediately after provenance registration.
- Rationale: QC manifests include `source_file_asset_id`, so file asset registration is a dependency for strict foreign-key validation.
- Consequence: Ingestion order becomes sample metadata -> sequencing -> provenance -> file assets -> QC, but lineage integrity is preserved.

## 2026-03-01 - QC ingestion resolves metric names to seeded definition IDs
- Decision: Translate incoming `qc_metric_name` values to relational `qc_metric_def_id` values during QC ingestion.
- Rationale: The raw QC manifest is easier to generate and inspect using metric names, while the database model correctly normalizes metrics through master definitions.
- Consequence: QC ingestion includes a mapping step, but the schema remains more governed and analytically consistent.

## 2026-03-01 - Variant ingestion remains strict and file-aware
- Decision: Require variant summaries to resolve to registered samples, pipeline runs, and source file assets before insertion.
- Rationale: Preserves lineage integrity and keeps downstream mutation reporting tied to concrete computational outputs rather than detached summary rows.
- Consequence: File asset registration must precede variant ingestion, but provenance and auditability are much stronger.

## 2026-03-02 - Use qc_summary_flag for sample-level QC status in listings
- Decision: Derive `latest_qc_status` in sample list queries from the `qc_summary_flag` metric instead of broader QC result rows.
- Rationale: Prevents duplicate sample rows and aligns list-level QC display with the intended sample summary semantics.
- Consequence: Sample listing queries become more stable and UI-friendly, while detailed QC inspection remains available separately.

## 2026-03-02 - Run Streamlit through a dedicated Home entrypoint
- Decision: Launch the UI through `streamlit_app/Home.py` instead of running page files directly.
- Rationale: Keeps package imports stable, matches Streamlit's multi-page app conventions, and simplifies future growth of the UI layer.
- Consequence: Slightly more app structure is required, but local development becomes more reliable.

## 2026-03-02 - Add a dedicated QC dashboard after sample and run exploration
- Decision: Build a QC-focused page as the third Streamlit page after Sample Explorer and Run Explorer.
- Rationale: QC monitoring is a core workflow in bioinformatics operations and complements both sample-centric and run-centric views.
- Consequence: The UI now covers metadata exploration, provenance exploration, and operational QC review.

## 2026-03-02 - Add variant search as a core UI workflow
- Decision: Include a cross-sample variant search page as part of the initial UI.
- Rationale: Variant-centric querying is a primary workflow in bioinformatics and clinical genomics.
- Consequence: The UI now supports both sample-level and mutation-level exploration.

## 2026-03-02 - Add a dedicated provenance trace page as a core UI workflow
- Decision: Include a separate provenance trace page instead of relying only on provenance sections embedded inside other pages.
- Rationale: Provenance is a primary differentiator of the project and deserves a focused UI workflow for lineage inspection.
- Consequence: The UI now explicitly supports metadata exploration, run exploration, QC review, variant search, and end-to-end lineage tracing.

## 2026-03-02 - Add a dedicated in-app data dictionary page
- Decision: Expose schema metadata through a dedicated Streamlit page in addition to future static documentation.
- Rationale: An in-app data dictionary improves discoverability, supports analyst self-service, and reinforces the project’s governance focus.
- Consequence: The UI now includes both analytical workflows and schema/documentation workflows.

## 2026-03-02 - Start Milestone 6 with targeted smoke tests
- Decision: Add a focused smoke-test layer first instead of attempting full exhaustive test coverage.
- Rationale: High-value integration checks provide strong confidence for a portfolio project while keeping implementation effort proportionate.
- Consequence: The project gains meaningful quality signals quickly, with room for deeper testing later.

## 2026-03-30 - Use Docker Compose service networking for database connectivity
- Decision: Configure the application container to connect to PostgreSQL using the Docker Compose service name (`postgres`) instead of localhost.
- Rationale: Containerized services must communicate over the Docker network, and this pattern aligns with production deployment models.
- Consequence: Local and containerized environments share the same configuration structure while differing only in environment variable values.

## 2026-03-30 - Keep containerization environment-driven and image-safe
- Decision: Pass all database credentials and runtime configuration through environment variables rather than embedding them in the Docker image.
- Rationale: Ensures security, portability, and compatibility with future cloud deployment environments such as AWS Lightsail.
- Consequence: The Docker image remains reusable across environments, with configuration managed externally.