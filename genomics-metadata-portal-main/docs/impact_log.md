# Impact Log

## 2026-02-20 - Foundation established
- Established a professional, production-style repository structure suitable for a bioinformatics metadata and provenance platform.
- Set up a dual-mode development model: local Python venv for application development and Docker Compose for PostgreSQL infrastructure.
- Improved future deployability by enforcing environment-driven configuration from the beginning.
- Reduced implementation risk by defining dedicated locations for SQL, app layers, data simulation, ingestion scripts, tests, and analyst-facing UI.

## 2026-02-21 - Development environment reliability improved
- Eliminated unstable dependency on macOS system Python by standardizing on Homebrew Python.
- Ensured reproducible and isolated Python runtime for all future development steps.
- Established verified PostgreSQL runtime environment using Docker Compose with health checks.
- Reduced future debugging risk by validating infrastructure (Python + DB) before application logic implementation.

## 2026-02-22 - Database foundation established
- Converted project design into a working relational PostgreSQL schema suitable for metadata governance and provenance tracking.
- Enforced data quality through foreign keys, check constraints, and domain-controlled values.
- Enabled realistic downstream ingestion and provenance workflows by seeding pipeline, reference, tool, and QC definition master data.

## 2026-02-23 - Application data layer established
- Created reusable Python database infrastructure for scripts, repositories, and Streamlit pages.
- Aligned ORM models directly to the relational schema, enabling future ingestion and query workflows.
- Reduced downstream implementation risk by validating Python-to-PostgreSQL connectivity before service-layer development.
- Improved local development reliability by fixing editor interpreter resolution and Python module path behavior.

## 2026-02-24 - Realistic demo dataset established
- Created a believable synthetic bioinformatics dataset suitable for ingestion, querying, provenance tracing, and UI demonstration.
- Improved project realism by modeling non-happy-path conditions such as failed runs, partial outputs, QC warnings, and reprocessing events.
- Enabled downstream recruiter-facing demos by generating analyst-meaningful cases including KRAS mutations and high-TMB samples.
- Improved implementation stability by aligning local development to a consistent Python 3.11 runtime baseline.

## 2026-02-25 - Database population workflow started
- Transitioned the project from static schema plus raw files to an operational ingestion workflow.
- Established a reusable validation-and-load pattern for bringing manifest data into PostgreSQL safely.
- Enabled downstream sequencing, provenance, QC, and variant ingestion by loading foundational patient and sample metadata first.
- Improved local operational reliability by confirming idempotent rerun behavior for sample metadata ingestion.

## 2026-02-26 - Sequencing lineage established
- Extended the ingestion workflow beyond sample metadata into operational sequencing run tracking.
- Connected samples to concrete sequencing runs, enabling downstream provenance and pipeline execution linkage.
- Improved analytical traceability by making sample-to-run relationships queryable in PostgreSQL.

## 2026-02-27 - Provenance realism strengthened
- Improved the realism of the synthetic bioinformatics dataset by generating explicit run-to-reference and run-to-tool lineage artifacts.
- Enabled downstream provenance ingestion needed to answer how a sample was processed, which computational components were used, and what changed across reruns.
- Increased the project’s analytical and governance value by making execution lineage queryable instead of inferred.

## 2026-02-28 - Database-ready provenance registration established
- Converted synthetic provenance artifacts into a service-layer registration workflow suitable for loading execution lineage into PostgreSQL.
- Improved traceability by preparing the system to persist exact run-to-tool and run-to-reference relationships instead of inferring them later.
- Reduced downstream ingestion risk by adding pre-insert validation for foundational provenance foreign keys.

## 2026-02-28 - End-to-end provenance registration established
- Enabled the system to persist run-level execution lineage for pipeline processing, including exact reference resources, tools, and sample-level downstream analysis summaries.
- Improved the project’s governance and traceability value by making provenance queryable in PostgreSQL instead of leaving it only in generated manifest files.
- Increased realism and portfolio strength by enforcing that provenance manifests resolve to seeded, versioned master data before insertion.
- Reduced operational risk through idempotent provenance registration behavior and early validation of lineage foreign keys.

## 2026-03-01 - File lineage became operationally queryable
- Enabled the platform to persist registered raw and derived file assets linked to samples and pipeline runs.
- Improved provenance completeness by making current versus outdated analysis artifacts queryable in PostgreSQL.
- Strengthened downstream QC and variant workflows by registering file assets before dependent ingest steps.

## 2026-03-01 - QC metrics became operationally queryable
- Enabled the platform to persist QC results tied to both samples and pipeline runs.
- Improved downstream traceability by linking QC measurements back to source pipeline executions and supporting file assets.
- Strengthened the project’s analyst and governance value by making QC status and metric-level detail queryable in PostgreSQL.

## 2026-03-01 - Variant summaries became operationally queryable
- Enabled the platform to persist variant summary records linked to both samples and pipeline runs.
- Improved downstream analysis and provenance workflows by tying variant summaries back to registered source file assets.
- Strengthened the project’s value for bioinformatics and research informatics use cases by making mutation-level summaries queryable in PostgreSQL.

## 2026-03-02 - Query layer foundation established
- Introduced a reusable repository layer so future Streamlit pages can access consistent sample-centric query workflows without embedding raw ORM logic in the UI.
- Improved maintainability and UI-readiness by centralizing provenance, QC, and variant access behind a dedicated sample repository.
- Enabled the project to move from ingestion-focused implementation into analyst-facing exploration workflows.

## 2026-03-02 - Build UI on top of repositories instead of direct ORM usage
- Decision: Introduce a repository/query layer before implementing Streamlit pages.
- Rationale: Keeps UI code thinner, improves reuse across pages, and makes sample-centric workflows easier to test and maintain.
- Consequence: Adds one more application layer, but the resulting architecture is cleaner and more extensible.

## 2026-03-02 - Sample listing behavior made UI-ready
- Improved the reliability of sample-centric exploration by ensuring sample list queries return one row per sample.
- Reduced downstream UI complexity by resolving sample-level QC summary status directly in the repository layer.

## 2026-03-02 - Streamlit app structure made runnable
- Improved local UI reliability by introducing a dedicated Streamlit home entrypoint and consistent repository-root import handling.
- Reduced page-level execution issues and aligned the app structure with Streamlit's expected multi-page layout.

## 2026-03-02 - Operational QC monitoring became available
- Enabled an analyst-facing QC dashboard for quick inspection of PASS/WARN/FAIL distributions and recent QC result records.
- Improved the portal’s operational value by making QC patterns easier to review without writing ad hoc SQL queries.

## 2026-03-02 - Cross-sample variant exploration enabled
- Enabled analysts to search variants across samples by gene and clinical significance.
- Improved the platform’s utility for mutation-focused workflows and potential clinical reporting use cases.

## 2026-03-02 - End-to-end lineage exploration became available
- Enabled analysts to trace a sample through sequencing, pipeline execution, reference/tool usage, generated files, QC outputs, and variant summaries in one UI workflow.
- Strengthened the portal’s provenance and governance story by exposing end-to-end lineage as a first-class analyst-facing feature.

## 2026-03-02 - In-app schema governance view added
- Enabled users to inspect the relational schema directly from the portal through an interactive data dictionary page.
- Improved the platform’s governance and documentation posture by exposing table structure, relationships, and schema metadata inside the app.

## 2026-03-02 - Automated smoke validation added
- Improved project reliability by introducing automated checks for core database population and repository behavior.
- Reduced regression risk before deployment by validating key query workflows through repeatable tests.
- Increased confidence in the portal’s readiness for containerization and deployment preparation.

## 2026-03-30 - Full stack deployment readiness achieved
- Enabled the platform to run as a fully containerized application stack including PostgreSQL and Streamlit services.
- Improved deployment readiness by aligning local execution with a production-style service architecture using container networking.
- Reduced environment inconsistencies by standardizing configuration across local and containerized runtimes.
- Strengthened portability by ensuring the application can be started with a single `docker compose up` command.
- Positioned the project for cloud deployment (AWS Lightsail) without requiring architectural changes.