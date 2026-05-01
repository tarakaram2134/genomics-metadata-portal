from pathlib import Path

from app.db import SessionLocal
from app.logging_config import configure_logging, get_logger
from app.services.run_registration_service import RunRegistrationService

configure_logging()
logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SEQUENCING_RUNS_DIR = BASE_DIR / "data" / "raw" / "sequencing_runs"


def main() -> None:
    logger.info("Starting sequencing run registration")

    sequencing_runs_path = SEQUENCING_RUNS_DIR / "sequencing_runs.tsv"
    sample_run_assignments_path = SEQUENCING_RUNS_DIR / "sample_run_assignments.tsv"

    with SessionLocal() as session:
        service = RunRegistrationService(session)
        summary = service.register_sequencing_runs_and_assignments(
            sequencing_runs_path=str(sequencing_runs_path),
            sample_run_assignments_path=str(sample_run_assignments_path),
        )

    logger.info("Sequencing run registration completed")
    logger.info("Summary: %s", summary)


if __name__ == "__main__":
    main()
