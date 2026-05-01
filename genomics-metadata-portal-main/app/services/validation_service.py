from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


class ValidationService:
    @staticmethod
    def require_columns(
        df: pd.DataFrame, required_columns: list[str], dataset_name: str
    ) -> ValidationResult:
        missing = [column for column in required_columns if column not in df.columns]
        if missing:
            return ValidationResult(
                is_valid=False,
                errors=[f"{dataset_name}: missing required columns: {', '.join(missing)}"],
            )
        return ValidationResult(is_valid=True, errors=[])

    @staticmethod
    def require_non_null(
        df: pd.DataFrame, required_columns: list[str], dataset_name: str
    ) -> ValidationResult:
        errors: list[str] = []
        for column in required_columns:
            null_count = int(df[column].isna().sum())
            empty_count = int((df[column].astype(str).str.strip() == "").sum())
            bad_count = null_count + empty_count
            if bad_count > 0:
                errors.append(
                    f"{dataset_name}: column '{column}' has {bad_count} null/empty values"
                )
        return ValidationResult(is_valid=(len(errors) == 0), errors=errors)

    @staticmethod
    def require_unique(
        df: pd.DataFrame, unique_columns: list[str], dataset_name: str
    ) -> ValidationResult:
        duplicates = df[df.duplicated(subset=unique_columns, keep=False)]
        if not duplicates.empty:
            joined_columns = ", ".join(unique_columns)
            return ValidationResult(
                is_valid=False,
                errors=[
                    (
                        f"{dataset_name}: duplicate rows found for unique key columns: "
                        f"{joined_columns}"
                    )
                ],
            )
        return ValidationResult(is_valid=True, errors=[])

    @staticmethod
    def validate_allowed_values(
        df: pd.DataFrame,
        column_name: str,
        allowed_values: set[str],
        dataset_name: str,
    ) -> ValidationResult:
        series = df[column_name].dropna().astype(str).str.strip()
        invalid = sorted(set(series) - allowed_values)
        if invalid:
            joined_invalid = ", ".join(invalid)
            return ValidationResult(
                is_valid=False,
                errors=[
                    (
                        f"{dataset_name}: column '{column_name}' has invalid values: "
                        f"{joined_invalid}"
                    )
                ],
            )
        return ValidationResult(is_valid=True, errors=[])

    @staticmethod
    def raise_if_invalid(results: list[ValidationResult]) -> None:
        errors: list[str] = []
        for result in results:
            errors.extend(result.errors)

        if errors:
            raise ValueError("Validation failed:\n- " + "\n- ".join(errors))
