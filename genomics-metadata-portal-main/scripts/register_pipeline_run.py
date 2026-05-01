from __future__ import annotations

from pathlib import Path
from typing import Any

from app.db import SessionLocal
from app.logging_config import configure_logging, get_logger
from app.services.provenance_service import ProvenanceService
from app.utils.manifest_parsers import read_json_records

configure_logging()
logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PIPELINE_RUNS_DIR = BASE_DIR / "data" / "raw" / "pipeline_runs"


def _load_required_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Required manifest not found: {path}")

    df = read_json_records(path)
    records = df.to_dict(orient="records")

    if not isinstance(records, list):
        raise ValueError(f"Expected list payload in {path}, got {type(records).__name__}")

    return records


def main() -> None:
    logger.info("Starting pipeline provenance registration")

    pipeline_runs = _load_required_json(PIPELINE_RUNS_DIR / "pipeline_runs.json")
    pipeline_run_references = _load_required_json(
        PIPELINE_RUNS_DIR / "pipeline_run_references.json"
    )
    pipeline_run_tools = _load_required_json(PIPELINE_RUNS_DIR / "pipeline_run_tools.json")
    sample_analysis_summary = _load_required_json(
        PIPELINE_RUNS_DIR / "sample_analysis_summary.json"
    )

    with SessionLocal() as session:
        service = ProvenanceService(session)
        summary = service.register_provenance(
            pipeline_runs=pipeline_runs,
            pipeline_run_references=pipeline_run_references,
            pipeline_run_tools=pipeline_run_tools,
            sample_analysis_summaries=sample_analysis_summary,
        )

    logger.info("Pipeline provenance registration completed")
    logger.info("Summary: %s", summary)


if __name__ == "__main__":
    main()