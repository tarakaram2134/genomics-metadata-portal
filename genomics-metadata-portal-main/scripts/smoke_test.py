from sqlalchemy import text

from app.db import SessionLocal
from app.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


def main() -> None:
    logger.info("Starting database smoke test")

    with SessionLocal() as session:
        query = text(
            """
            SELECT
                (SELECT COUNT(*) FROM pipelines) AS pipelines,
                (SELECT COUNT(*) FROM pipeline_versions) AS pipeline_versions,
                (SELECT COUNT(*) FROM reference_resources) AS reference_resources,
                (SELECT COUNT(*) FROM tool_registry) AS tool_registry,
                (SELECT COUNT(*) FROM qc_metric_definitions) AS qc_metric_definitions
            """
        )
        row = session.execute(query).mappings().one()

    logger.info("Database smoke test completed successfully")
    logger.info("Counts: %s", dict(row))


if __name__ == "__main__":
    main()
