from collections.abc import Iterable


def make_id(prefix: str, number: int, width: int = 4) -> str:
    return f"{prefix}{number:0{width}d}"


def make_patient_id(number: int) -> str:
    return make_id("PAT", number)


def make_batch_id(number: int) -> str:
    return make_id("BAT", number, width=3)


def make_sample_id(number: int) -> str:
    return make_id("SMP", number)


def make_seq_run_id(number: int) -> str:
    return make_id("RUN", number, width=3)


def make_pipeline_run_id(number: int) -> str:
    return make_id("PRUN", number, width=4)


def make_file_asset_id(number: int) -> str:
    return make_id("FILE", number, width=5)


def make_qc_result_id(number: int) -> str:
    return make_id("QCR", number, width=5)


def make_variant_summary_id(number: int) -> str:
    return make_id("VAR", number, width=5)


def make_sample_analysis_summary_id(number: int) -> str:
    return make_id("SAS", number, width=4)


def make_audit_event_id(number: int) -> str:
    return make_id("AUD", number, width=5)


def external_subject_id(number: int) -> str:
    return f"EXT-SUBJ-{number:04d}"


def lane_label(number: int) -> str:
    return f"L{number:03d}"


def library_id(sample_id: str, suffix: int) -> str:
    return f"LIB-{sample_id}-{suffix:02d}"


def barcode_id(number: int) -> str:
    return f"BC{number:04d}"


def ensure_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered
