from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.models.sample import Sample
from app.models.sequencing_run import SampleRunAssignment, SequencingRun
from app.services.validation_service import ValidationService
from app.utils.enums import Platform, SequencingRunStatus
from app.utils.manifest_parsers import normalize_nullable_strings, read_tsv

logger = get_logger(__name__)


class RunRegistrationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def register_sequencing_runs_and_assignments(
        self,
        sequencing_runs_path: str,
        sample_run_assignments_path: str,
    ) -> dict[str, int]:
        sequencing_runs_df = normalize_nullable_strings(read_tsv(sequencing_runs_path))
        assignments_df = normalize_nullable_strings(read_tsv(sample_run_assignments_path))

        self._validate_sequencing_runs(sequencing_runs_df)
        self._validate_sample_run_assignments(assignments_df)

        sequencing_runs_loaded = self._upsert_sequencing_runs(sequencing_runs_df)
        assignments_loaded = self._upsert_sample_run_assignments(assignments_df)

        self.session.commit()

        summary = {
            "sequencing_runs_loaded": sequencing_runs_loaded,
            "sample_run_assignments_loaded": assignments_loaded,
        }
        logger.info("Sequencing registration summary: %s", summary)
        return summary

    def _validate_sequencing_runs(self, df) -> None:
        ValidationService.raise_if_invalid(
            [
                ValidationService.require_columns(
                    df,
                    [
                        "seq_run_id",
                        "instrument_run_name",
                        "platform",
                        "instrument_model",
                        "flowcell_id",
                        "run_date",
                        "read_length",
                        "paired_end",
                        "center_name",
                        "run_status",
                        "notes",
                        "created_at",
                    ],
                    "sequencing_runs",
                ),
                ValidationService.require_non_null(
                    df,
                    [
                        "seq_run_id",
                        "instrument_run_name",
                        "platform",
                        "flowcell_id",
                        "run_date",
                        "center_name",
                        "run_status",
                    ],
                    "sequencing_runs",
                ),
                ValidationService.require_unique(df, ["seq_run_id"], "sequencing_runs"),
                ValidationService.require_unique(df, ["instrument_run_name"], "sequencing_runs"),
                ValidationService.validate_allowed_values(
                    df,
                    "platform",
                    {item.value for item in Platform},
                    "sequencing_runs",
                ),
                ValidationService.validate_allowed_values(
                    df,
                    "run_status",
                    {item.value for item in SequencingRunStatus},
                    "sequencing_runs",
                ),
            ]
        )

    def _validate_sample_run_assignments(self, df) -> None:
        ValidationService.raise_if_invalid(
            [
                ValidationService.require_columns(
                    df,
                    [
                        "sample_id",
                        "seq_run_id",
                        "lane_or_partition",
                        "library_id",
                        "barcode",
                        "created_at",
                    ],
                    "sample_run_assignments",
                ),
                ValidationService.require_non_null(
                    df,
                    ["sample_id", "seq_run_id"],
                    "sample_run_assignments",
                ),
            ]
        )

        sample_ids = {row[0] for row in self.session.query(Sample.sample_id).all()}
        run_ids = {row[0] for row in self.session.query(SequencingRun.seq_run_id).all()} | set(
            df["seq_run_id"].dropna().astype(str).unique()
        )

        missing_samples = sorted(set(df["sample_id"].dropna().astype(str).unique()) - sample_ids)
        missing_runs = sorted(set(df["seq_run_id"].dropna().astype(str).unique()) - run_ids)

        errors: list[str] = []
        if missing_samples:
            errors.append(
                "sample_run_assignments: unknown sample_ids: " + ", ".join(missing_samples[:10])
            )
        if missing_runs:
            errors.append(
                "sample_run_assignments: unknown seq_run_ids: " + ", ".join(missing_runs[:10])
            )

        if errors:
            raise ValueError("Validation failed:\n- " + "\n- ".join(errors))

    def _upsert_sequencing_runs(self, df) -> int:
        loaded = 0
        for row in df.to_dict(orient="records"):
            existing = self.session.get(SequencingRun, row["seq_run_id"])
            if existing:
                continue

            self.session.add(
                SequencingRun(
                    seq_run_id=row["seq_run_id"],
                    instrument_run_name=row["instrument_run_name"],
                    platform=row["platform"],
                    instrument_model=row["instrument_model"],
                    flowcell_id=row["flowcell_id"],
                    run_date=self._parse_date(row["run_date"]),
                    read_length=row["read_length"],
                    paired_end=self._parse_bool(row["paired_end"]),
                    center_name=row["center_name"],
                    run_status=row["run_status"],
                    notes=row["notes"],
                    created_at=self._parse_datetime(row["created_at"]),
                )
            )
            loaded += 1

        self.session.flush()
        return loaded

    def _upsert_sample_run_assignments(self, df) -> int:
        loaded = 0

        existing_keys = {
            (
                row.sample_id,
                row.seq_run_id,
                row.lane_or_partition or "",
                row.library_id or "",
                row.barcode or "",
            )
            for row in self.session.query(SampleRunAssignment).all()
        }

        for row in df.to_dict(orient="records"):
            lookup_key = (
                row["sample_id"],
                row["seq_run_id"],
                row["lane_or_partition"] or "",
                row["library_id"] or "",
                row["barcode"] or "",
            )
            if lookup_key in existing_keys:
                continue

            self.session.add(
                SampleRunAssignment(
                    sample_id=row["sample_id"],
                    seq_run_id=row["seq_run_id"],
                    lane_or_partition=row["lane_or_partition"],
                    library_id=row["library_id"],
                    barcode=row["barcode"],
                    created_at=self._parse_datetime(row["created_at"]),
                )
            )
            existing_keys.add(lookup_key)
            loaded += 1

        return loaded

    @staticmethod
    def _parse_date(value: str | None):
        if value in (None, ""):
            return None
        return datetime.strptime(value, "%Y-%m-%d").date()

    @staticmethod
    def _parse_datetime(value: str | None):
        if value in (None, ""):
            return None
        return datetime.fromisoformat(value)

    @staticmethod
    def _parse_bool(value: str | None) -> bool:
        if value is None:
            return False
        return str(value).strip().lower() in {"true", "1", "yes", "y"}
