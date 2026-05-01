from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.models.batch import Batch
from app.models.patient import Patient
from app.models.sample import Sample
from app.services.validation_service import ValidationService
from app.utils.enums import AgeBand, AssayType, SampleStatus, SampleType, Sex, TumorNormalStatus
from app.utils.manifest_parsers import normalize_nullable_strings, read_tsv

logger = get_logger(__name__)


class SampleIngestService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def ingest_patients_batches_samples(
        self,
        patients_path: str,
        batches_path: str,
        samples_path: str,
    ) -> dict[str, int]:
        patients_df = normalize_nullable_strings(read_tsv(patients_path))
        batches_df = normalize_nullable_strings(read_tsv(batches_path))
        samples_df = normalize_nullable_strings(read_tsv(samples_path))

        self._validate_patients(patients_df)
        self._validate_batches(batches_df)
        self._validate_samples(samples_df)

        patients_loaded = self._upsert_patients(patients_df)
        batches_loaded = self._upsert_batches(batches_df)
        samples_loaded = self._upsert_samples(samples_df)

        self.session.commit()

        summary = {
            "patients_loaded": patients_loaded,
            "batches_loaded": batches_loaded,
            "samples_loaded": samples_loaded,
        }
        logger.info("Sample ingest summary: %s", summary)
        return summary

    def _validate_patients(self, df) -> None:
        ValidationService.raise_if_invalid(
            [
                ValidationService.require_columns(
                    df,
                    [
                        "patient_id",
                        "external_subject_id",
                        "disease_type",
                        "condition_group",
                        "sex",
                        "age_band",
                        "created_at",
                    ],
                    "patients",
                ),
                ValidationService.require_non_null(
                    df,
                    ["patient_id", "external_subject_id", "disease_type", "condition_group"],
                    "patients",
                ),
                ValidationService.require_unique(df, ["patient_id"], "patients"),
                ValidationService.require_unique(df, ["external_subject_id"], "patients"),
                ValidationService.validate_allowed_values(
                    df,
                    "sex",
                    {item.value for item in Sex},
                    "patients",
                ),
                ValidationService.validate_allowed_values(
                    df,
                    "age_band",
                    {item.value for item in AgeBand},
                    "patients",
                ),
            ]
        )

    def _validate_batches(self, df) -> None:
        ValidationService.raise_if_invalid(
            [
                ValidationService.require_columns(
                    df,
                    [
                        "batch_id",
                        "batch_name",
                        "project_code",
                        "submitted_by",
                        "submission_date",
                        "notes",
                        "created_at",
                    ],
                    "batches",
                ),
                ValidationService.require_non_null(
                    df,
                    ["batch_id", "batch_name", "project_code", "submitted_by", "submission_date"],
                    "batches",
                ),
                ValidationService.require_unique(df, ["batch_id"], "batches"),
                ValidationService.require_unique(df, ["batch_name"], "batches"),
            ]
        )

    def _validate_samples(self, df) -> None:
        ValidationService.raise_if_invalid(
            [
                ValidationService.require_columns(
                    df,
                    [
                        "sample_id",
                        "patient_id",
                        "batch_id",
                        "sample_type",
                        "assay_type",
                        "collection_date",
                        "received_date",
                        "specimen_site",
                        "condition_label",
                        "sample_status",
                        "tumor_normal_status",
                        "library_prep_kit",
                        "notes",
                        "created_at",
                    ],
                    "samples",
                ),
                ValidationService.require_non_null(
                    df,
                    [
                        "sample_id",
                        "patient_id",
                        "sample_type",
                        "assay_type",
                        "condition_label",
                        "sample_status",
                    ],
                    "samples",
                ),
                ValidationService.require_unique(df, ["sample_id"], "samples"),
                ValidationService.validate_allowed_values(
                    df,
                    "sample_type",
                    {item.value for item in SampleType},
                    "samples",
                ),
                ValidationService.validate_allowed_values(
                    df,
                    "assay_type",
                    {item.value for item in AssayType},
                    "samples",
                ),
                ValidationService.validate_allowed_values(
                    df,
                    "sample_status",
                    {item.value for item in SampleStatus},
                    "samples",
                ),
                ValidationService.validate_allowed_values(
                    df,
                    "tumor_normal_status",
                    {item.value for item in TumorNormalStatus},
                    "samples",
                ),
            ]
        )

    def _upsert_patients(self, df) -> int:
        loaded = 0
        for row in df.to_dict(orient="records"):
            existing = self.session.get(Patient, row["patient_id"])
            if existing:
                continue

            self.session.add(
                Patient(
                    patient_id=row["patient_id"],
                    external_subject_id=row["external_subject_id"],
                    disease_type=row["disease_type"],
                    condition_group=row["condition_group"],
                    sex=row["sex"],
                    age_band=row["age_band"],
                    created_at=self._parse_datetime(row["created_at"]),
                )
            )
            loaded += 1
        return loaded

    def _upsert_batches(self, df) -> int:
        loaded = 0
        for row in df.to_dict(orient="records"):
            existing = self.session.get(Batch, row["batch_id"])
            if existing:
                continue

            self.session.add(
                Batch(
                    batch_id=row["batch_id"],
                    batch_name=row["batch_name"],
                    project_code=row["project_code"],
                    submitted_by=row["submitted_by"],
                    submission_date=self._parse_date(row["submission_date"]),
                    notes=row["notes"],
                    created_at=self._parse_datetime(row["created_at"]),
                )
            )
            loaded += 1
        return loaded

    def _upsert_samples(self, df) -> int:
        loaded = 0
        for row in df.to_dict(orient="records"):
            existing = self.session.get(Sample, row["sample_id"])
            if existing:
                continue

            self.session.add(
                Sample(
                    sample_id=row["sample_id"],
                    patient_id=row["patient_id"],
                    batch_id=row["batch_id"],
                    sample_type=row["sample_type"],
                    assay_type=row["assay_type"],
                    collection_date=self._parse_date(row["collection_date"]),
                    received_date=self._parse_date(row["received_date"]),
                    specimen_site=row["specimen_site"],
                    condition_label=row["condition_label"],
                    sample_status=row["sample_status"],
                    tumor_normal_status=row["tumor_normal_status"],
                    library_prep_kit=row["library_prep_kit"],
                    notes=row["notes"],
                    created_at=self._parse_datetime(row["created_at"]),
                )
            )
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
