from pathlib import Path

from app.db import SessionLocal
from app.logging_config import configure_logging, get_logger
from app.services.sample_ingest_service import SampleIngestService

configure_logging()
logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_METADATA_DIR = BASE_DIR / "data" / "raw" / "sample_metadata"


def main() -> None:
    logger.info("Starting sample metadata ingestion")

    patients_path = SAMPLE_METADATA_DIR / "patients.tsv"
    batches_path = SAMPLE_METADATA_DIR / "batches.tsv"
    samples_path = SAMPLE_METADATA_DIR / "samples.tsv"

    with SessionLocal() as session:
        service = SampleIngestService(session)
        summary = service.ingest_patients_batches_samples(
            patients_path=str(patients_path),
            batches_path=str(batches_path),
            samples_path=str(samples_path),
        )

    logger.info("Sample metadata ingestion completed")
    logger.info("Summary: %s", summary)


if __name__ == "__main__":
    main()
