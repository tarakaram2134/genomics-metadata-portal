from __future__ import annotations

from pprint import pprint

from app.db import SessionLocal
from app.logging_config import configure_logging, get_logger
from app.repositories.sample_repository import SampleRepository

configure_logging()
logger = get_logger(__name__)


def main() -> None:
    with SessionLocal() as session:
        repo = SampleRepository(session)

        samples = repo.list_samples(limit=5)
        logger.info("Retrieved %s sample rows", len(samples))
        pprint(samples[:2])

        if not samples:
            logger.warning("No samples found")
            return

        sample_id = samples[0]["sample_id"]
        logger.info("Testing repository methods with sample_id=%s", sample_id)

        detail = repo.get_sample_detail(sample_id)
        provenance = repo.get_sample_provenance(sample_id)
        qc_results = repo.get_sample_qc_results(sample_id)
        variants = repo.get_sample_variants(sample_id)

        pprint({"detail": detail})
        pprint({"provenance_preview": provenance["pipeline_runs"][:2]})
        pprint({"qc_results_preview": qc_results[:5]})
        pprint({"variants_preview": variants[:5]})


if __name__ == "__main__":
    main()