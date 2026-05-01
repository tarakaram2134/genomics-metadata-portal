from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def read_tsv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    return df


def read_json_records(path: str | Path) -> pd.DataFrame:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        return pd.DataFrame(payload)

    if isinstance(payload, dict):
        return pd.DataFrame([payload])

    raise ValueError(f"Unsupported JSON structure in {path}")


def normalize_nullable_strings(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for column in normalized.columns:
        if normalized[column].dtype == object:
            normalized[column] = normalized[column].replace({"": None})
    return normalized