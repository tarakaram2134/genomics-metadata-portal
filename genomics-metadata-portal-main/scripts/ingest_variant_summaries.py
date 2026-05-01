from __future__ import annotations

from pathlib import Path
from typing import Any

from app.db import SessionLocal
from app.logging_config import configure_logging, get_logger
from app.services.variant_ingest_service import VariantIngestService
from app.utils.manifest_parsers import read_tsv

configure_logging()
logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
VARIANT_SUMMARY_PATH = BASE_DIR / "data" / "raw" / "variant_summaries" / "variant_summary.tsv"


def _load_required_tsv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Required manifest not found: {path}")

    df = read_tsv(path)
    records = df.to_dict(orient="records")

    if not isinstance(records, list):
        raise ValueError(f"Expected list payload in {path}, got {type(records).__name__}")

    return records


def main() -> None:
    logger.info("Starting variant summary ingestion")

    variant_summaries = _load_required_tsv(VARIANT_SUMMARY_PATH)

    with SessionLocal() as session:
        service = VariantIngestService(session)
        summary = service.ingest_variant_summaries(variant_summaries)

    logger.info("Variant summary ingestion completed")
    logger.info("Summary: %s", summary)


if __name__ == "__main__":
    main()