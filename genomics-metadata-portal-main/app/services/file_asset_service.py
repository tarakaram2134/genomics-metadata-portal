from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.models import FileAsset, PipelineRun, Sample

logger = get_logger(__name__)


class FileAssetService:
    """
    Registers file assets into the relational model.

    Responsibilities:
    - validate manifest structure
    - validate foreign-key readiness
    - insert file assets with idempotent behavior
    """

    REQUIRED_FILE_ASSET_FIELDS = {
        "file_asset_id",
        "sample_id",
        "file_role",
        "file_format",
        "path_uri",
        "checksum",
        "file_size_bytes",
        "source_system",
        "is_current",
        "created_at",
    }

    def __init__(self, session: Session) -> None:
        self.session = session

    def register_file_assets(self, file_assets: list[dict[str, Any]]) -> dict[str, int]:
        logger.info("Starting file asset registration")

        self._validate_required_fields(file_assets)
        self._validate_foreign_keys(file_assets)

        inserted = self._insert_file_assets(file_assets)

        self.session.commit()

        summary = {
            "file_assets_loaded": inserted,
        }
        logger.info("File asset registration summary: %s", summary)
        return summary

    def _validate_required_fields(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            raise ValueError("file_assets payload is empty")

        for index, row in enumerate(rows, start=1):
            missing = [field for field in self.REQUIRED_FILE_ASSET_FIELDS if field not in row]
            if missing:
                raise ValueError(
                    f"file_assets row {index} is missing required fields: {', '.join(sorted(missing))}"
                )

    def _validate_foreign_keys(self, rows: list[dict[str, Any]]) -> None:
        sample_ids = {str(row["sample_id"]) for row in rows if self._present(row.get("sample_id"))}
        pipeline_run_ids = {
            str(row["pipeline_run_id"])
            for row in rows
            if self._present(row.get("pipeline_run_id"))
        }

        existing_sample_ids = set(self.session.scalars(select(Sample.sample_id)).all())
        existing_pipeline_run_ids = set(
            self.session.scalars(select(PipelineRun.pipeline_run_id)).all()
        )

        missing_samples = sorted(sample_ids - existing_sample_ids)
        missing_pipeline_runs = sorted(pipeline_run_ids - existing_pipeline_run_ids)

        if missing_samples:
            raise ValueError(
                f"file_assets contains unknown sample_id values: {missing_samples[:10]}"
            )
        if missing_pipeline_runs:
            raise ValueError(
                f"file_assets contains unknown pipeline_run_id values: {missing_pipeline_runs[:10]}"
            )

    def _insert_file_assets(self, rows: list[dict[str, Any]]) -> int:
        existing_ids = set(self.session.scalars(select(FileAsset.file_asset_id)).all())
        inserted = 0

        for row in rows:
            file_asset_id = str(row["file_asset_id"])
            if file_asset_id in existing_ids:
                continue

            self.session.add(
                FileAsset(
                    file_asset_id=file_asset_id,
                    sample_id=str(row["sample_id"]),
                    pipeline_run_id=self._clean_nullable_text(row.get("pipeline_run_id")),
                    file_role=str(row["file_role"]),
                    file_format=str(row["file_format"]),
                    path_uri=str(row["path_uri"]),
                    checksum=str(row["checksum"]),
                    file_size_bytes=self._coerce_int(row["file_size_bytes"]),
                    source_system=str(row["source_system"]),
                    is_current=self._coerce_bool(row["is_current"]),
                    created_at=row["created_at"],
                )
            )
            inserted += 1

        self.session.flush()
        return inserted

    @staticmethod
    def _present(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        try:
            return bool(value == value)
        except Exception:
            return True

    @staticmethod
    def _clean_nullable_text(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        try:
            if value != value:
                return None
        except Exception:
            pass
        return str(value)

    @staticmethod
    def _coerce_int(value: Any) -> int:
        if isinstance(value, str):
            return int(value.strip())
        return int(value)

    @staticmethod
    def _coerce_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "t", "1", "yes", "y"}:
                return True
            if normalized in {"false", "f", "0", "no", "n"}:
                return False
            raise ValueError(f"Cannot coerce string to bool: {value}")
        return bool(value)