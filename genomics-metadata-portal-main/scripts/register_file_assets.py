from __future__ import annotations

from pathlib import Path
from typing import Any

from app.db import SessionLocal
from app.logging_config import configure_logging, get_logger
from app.services.file_asset_service import FileAssetService
from app.utils.manifest_parsers import read_tsv

configure_logging()
logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_ASSETS_PATH = BASE_DIR / "data" / "raw" / "file_manifests" / "file_assets.tsv"


def _load_required_tsv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Required manifest not found: {path}")

    df = read_tsv(path)
    records = df.to_dict(orient="records")

    if not isinstance(records, list):
        raise ValueError(f"Expected list payload in {path}, got {type(records).__name__}")

    return records


def main() -> None:
    logger.info("Starting file asset registration")

    file_assets = _load_required_tsv(FILE_ASSETS_PATH)

    with SessionLocal() as session:
        service = FileAssetService(session)
        summary = service.register_file_assets(file_assets)

    logger.info("File asset registration completed")
    logger.info("Summary: %s", summary)


if __name__ == "__main__":
    main()