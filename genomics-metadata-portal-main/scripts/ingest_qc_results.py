from __future__ import annotations

from pathlib import Path
from typing import Any

from app.db import SessionLocal
from app.logging_config import configure_logging, get_logger
from app.services.qc_ingest_service import QcIngestService
from app.utils.manifest_parsers import read_json_records

configure_logging()
logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
QC_RESULTS_PATH = BASE_DIR / "data" / "raw" / "qc_metrics" / "qc_results.json"


def _load_required_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Required manifest not found: {path}")

    df = read_json_records(path)
    records = df.to_dict(orient="records")

    if not isinstance(records, list):
        raise ValueError(f"Expected list payload in {path}, got {type(records).__name__}")

    return records


def main() -> None:
    logger.info("Starting QC result ingestion")

    qc_results = _load_required_json(QC_RESULTS_PATH)

    with SessionLocal() as session:
        service = QcIngestService(session)
        summary = service.ingest_qc_results(qc_results)

    logger.info("QC result ingestion completed")
    logger.info("Summary: %s", summary)


if __name__ == "__main__":
    main()