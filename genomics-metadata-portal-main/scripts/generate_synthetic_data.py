from __future__ import annotations

import csv
import hashlib
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

from app.logging_config import configure_logging, get_logger
from app.utils.date_utils import add_hours, add_minutes, days_before, random_datetime_on_date
from app.utils.enums import (
    AgeBand,
    AssayType,
    ClinicalSignificance,
    FileFormat,
    FileRole,
    MsiStatus,
    PipelineRunStatus,
    Platform,
    QcStatus,
    SampleStatus,
    SampleType,
    SequencingRunStatus,
    Sex,
    TumorNormalStatus,
    VariantClass,
)
from app.utils.id_generators import (
    barcode_id,
    ensure_unique,
    external_subject_id,
    lane_label,
    library_id,
    make_audit_event_id,
    make_batch_id,
    make_file_asset_id,
    make_patient_id,
    make_pipeline_run_id,
    make_qc_result_id,
    make_sample_analysis_summary_id,
    make_sample_id,
    make_seq_run_id,
    make_variant_summary_id,
)

configure_logging()
logger = get_logger(__name__)

faker = Faker()
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
Faker.seed(RANDOM_SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
EXAMPLES_DIR = BASE_DIR / "data" / "examples"

ANCHOR_DATE = date(2026, 2, 20)

DISEASES = [
    "lung adenocarcinoma",
    "colorectal cancer",
    "AML",
    "breast cancer",
    "healthy control",
]

DISEASE_WEIGHTS = [0.24, 0.20, 0.16, 0.22, 0.18]

SPECIMEN_SITES = {
    "lung adenocarcinoma": ["lung", "pleural fluid", "lymph node"],
    "colorectal cancer": ["colon", "rectum", "liver metastasis"],
    "AML": ["bone marrow", "peripheral blood"],
    "breast cancer": ["breast", "axillary node", "liver metastasis"],
    "healthy control": ["blood"],
}

LIBRARY_PREP_BY_ASSAY = {
    AssayType.WES.value: ["Agilent SureSelect XT HS2", "Twist Exome 2.0"],
    AssayType.RNA_SEQ.value: ["TruSeq Stranded mRNA", "KAPA RNA HyperPrep"],
    AssayType.TARGETED_PANEL.value: ["Illumina TruSight Oncology", "Custom Amplicon Panel"],
}

PIPELINE_VERSIONS_BY_ASSAY = {
    AssayType.WES.value: {
        "alignment": ["PLV_DNA_ALIGN_1_0_0", "PLV_DNA_ALIGN_1_1_0"],
        "somatic": ["PLV_SOM_VAR_2_1_0", "PLV_SOM_VAR_2_2_0", "PLV_SOM_VAR_2_0_0"],
        "qc": ["PLV_MULTI_QC_1_0_0"],
    },
    AssayType.TARGETED_PANEL.value: {
        "alignment": ["PLV_DNA_ALIGN_1_0_0", "PLV_DNA_ALIGN_1_1_0"],
        "somatic": ["PLV_SOM_VAR_2_0_0", "PLV_SOM_VAR_2_1_0", "PLV_SOM_VAR_2_2_0"],
        "qc": ["PLV_MULTI_QC_1_0_0"],
    },
    AssayType.RNA_SEQ.value: {
        "rna": ["PLV_RNA_QUANT_1_0_0", "PLV_RNA_QUANT_1_1_0"],
        "qc": ["PLV_MULTI_QC_1_0_0"],
    },
}

PIPELINE_REFERENCE_PLAN = {
    "DNA_ALIGN": [
        {
            "reference_id": "REF_GRCH38",
            "usage_role": "GENOME",
            "execution_order": 1,
            "step_label": "alignment",
        },
        {
            "reference_id": "REF_DBSNP_155",
            "usage_role": "KNOWN_SITES",
            "execution_order": 2,
            "step_label": "alignment",
        },
    ],
    "SOM_VAR": [
        {
            "reference_id": "REF_GRCH38",
            "usage_role": "GENOME",
            "execution_order": 1,
            "step_label": "somatic_calling",
        },
        {
            "reference_id": "REF_DBSNP_155",
            "usage_role": "KNOWN_SITES",
            "execution_order": 2,
            "step_label": "somatic_calling",
        },
        {
            "reference_id": "REF_CLINVAR_2025",
            "usage_role": "CLINICAL_ANNOTATION",
            "execution_order": 3,
            "step_label": "annotation",
        },
        {
            "reference_id": "REF_COSMIC_99",
            "usage_role": "CANCER_ANNOTATION",
            "execution_order": 4,
            "step_label": "annotation",
        },
    ],
    "RNA_QUANT": [
        {
            "reference_id": "REF_GRCH38",
            "usage_role": "GENOME",
            "execution_order": 1,
            "step_label": "alignment",
        },
        {
            "reference_id": "REF_GENCODE_V44",
            "usage_role": "ANNOTATION",
            "execution_order": 2,
            "step_label": "quantification",
        },
        {
            "reference_id": "REF_STAR_INDEX_V1",
            "usage_role": "ALIGNMENT_INDEX",
            "execution_order": 3,
            "step_label": "alignment",
        },
        {
            "reference_id": "REF_TRANSCRIPTOME_GENCODE_V44",
            "usage_role": "TRANSCRIPTOME",
            "execution_order": 4,
            "step_label": "quantification",
        },
    ],
    "MULTI_QC": [
        {
            "reference_id": "REF_GRCH38",
            "usage_role": "GENOME_CONTEXT",
            "execution_order": 1,
            "step_label": "qc_review",
        }
    ],
}

PIPELINE_TOOL_PLAN = {
    "DNA_ALIGN": [
        {
            "tool_id": "TOOL_FASTQC_0_11_9",
            "usage_role": "PRE_QC",
            "execution_order": 1,
            "step_label": "pre_qc",
        },
        {
            "tool_id": "TOOL_BWA_0_7_17",
            "usage_role": "ALIGNER",
            "execution_order": 2,
            "step_label": "alignment",
        },
        {
            "tool_id": "TOOL_SAMTOOLS_1_19",
            "usage_role": "BAM_PROCESSING",
            "execution_order": 3,
            "step_label": "post_alignment",
        },
        {
            "tool_id": "TOOL_PICARD_3_1_1",
            "usage_role": "DUP_MARKING",
            "execution_order": 4,
            "step_label": "post_alignment",
        },
        {
            "tool_id": "TOOL_GATK_4_5_0",
            "usage_role": "BQSR",
            "execution_order": 5,
            "step_label": "post_alignment",
        },
    ],
    "SOM_VAR": [
        {
            "tool_id": "TOOL_SAMTOOLS_1_19",
            "usage_role": "BAM_ACCESS",
            "execution_order": 1,
            "step_label": "somatic_calling",
        },
        {
            "tool_id": "TOOL_MUTECT2_4_5_0",
            "usage_role": "VARIANT_CALLER",
            "execution_order": 2,
            "step_label": "somatic_calling",
        },
        {
            "tool_id": "TOOL_BCFTOOLS_1_19",
            "usage_role": "VCF_PROCESSING",
            "execution_order": 3,
            "step_label": "post_call_filtering",
        },
        {
            "tool_id": "TOOL_VEP_111",
            "usage_role": "ANNOTATION",
            "execution_order": 4,
            "step_label": "annotation",
        },
    ],
    "RNA_QUANT": [
        {
            "tool_id": "TOOL_FASTQC_0_11_9",
            "usage_role": "PRE_QC",
            "execution_order": 1,
            "step_label": "pre_qc",
        },
        {
            "tool_id": "TOOL_STAR_2_7_11A",
            "usage_role": "ALIGNER",
            "execution_order": 2,
            "step_label": "alignment",
        },
        {
            "tool_id": "TOOL_RSEM_1_3_3",
            "usage_role": "QUANTIFICATION",
            "execution_order": 3,
            "step_label": "quantification",
        },
    ],
    "MULTI_QC": [
        {
            "tool_id": "TOOL_MULTIQC_1_18",
            "usage_role": "QC_AGGREGATION",
            "execution_order": 1,
            "step_label": "qc_review",
        },
        {
            "tool_id": "TOOL_MOSDEPTH_0_3_5",
            "usage_role": "COVERAGE_QC",
            "execution_order": 2,
            "step_label": "qc_review",
        },
    ],
}

QC_NUMERIC_METRICS = [
    "total_reads",
    "pct_q30_bases",
    "mean_target_coverage",
    "pct_target_bases_100x",
    "mapping_rate",
    "duplicate_rate",
    "median_insert_size",
    "estimated_contamination",
    "tumor_purity_qc",
    "rna_mapping_rate",
    "exonic_rate",
    "rrna_rate",
]

QC_TEXT_METRICS = [
    "sex_concordance",
    "qc_summary_flag",
]

GENES = [
    "TP53",
    "KRAS",
    "EGFR",
    "PIK3CA",
    "BRAF",
    "NRAS",
    "IDH1",
    "IDH2",
    "FLT3",
    "NPM1",
    "ERBB2",
    "ALK",
    "ROS1",
    "PTEN",
    "APC",
    "SMAD4",
    "KIT",
    "JAK2",
]

KRAS_PROTEINS = ["p.G12D", "p.G12V", "p.G13D", "p.Q61H"]
GENE_TO_CHR = {
    "TP53": "17",
    "KRAS": "12",
    "EGFR": "7",
    "PIK3CA": "3",
    "BRAF": "7",
    "NRAS": "1",
    "IDH1": "2",
    "IDH2": "15",
    "FLT3": "13",
    "NPM1": "5",
    "ERBB2": "17",
    "ALK": "2",
    "ROS1": "6",
    "PTEN": "10",
    "APC": "5",
    "SMAD4": "18",
    "KIT": "4",
    "JAK2": "9",
}


@dataclass
class CounterState:
    sample: int = 1
    seq_run: int = 1
    pipeline_run: int = 1
    file_asset: int = 1
    qc_result: int = 1
    variant: int = 1
    analysis_summary: int = 1
    audit: int = 1


def write_tsv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: list[dict] | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)


def sha_like(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]


def choose_disease() -> str:
    return random.choices(DISEASES, weights=DISEASE_WEIGHTS, k=1)[0]


def choose_age_band(disease: str) -> str:
    if disease == "AML" and random.random() < 0.15:
        return AgeBand.PEDIATRIC.value
    return random.choices(
        [
            AgeBand.YOUNG_ADULT.value,
            AgeBand.ADULT.value,
            AgeBand.OLDER_ADULT.value,
            AgeBand.UNKNOWN.value,
        ],
        weights=[0.18, 0.50, 0.27, 0.05],
        k=1,
    )[0]


def condition_group_for_disease(disease: str) -> str:
    return "control" if disease == "healthy control" else "case"


def assays_for_disease(disease: str) -> list[str]:
    if disease == "healthy control":
        return random.choices(
            [
                [AssayType.WES.value],
                [AssayType.RNA_SEQ.value],
                [AssayType.WES.value, AssayType.RNA_SEQ.value],
            ],
            weights=[0.35, 0.25, 0.40],
            k=1,
        )[0]
    return random.choices(
        [
            [AssayType.WES.value],
            [AssayType.RNA_SEQ.value],
            [AssayType.TARGETED_PANEL.value],
            [AssayType.WES.value, AssayType.RNA_SEQ.value],
            [AssayType.WES.value, AssayType.TARGETED_PANEL.value],
        ],
        weights=[0.20, 0.12, 0.15, 0.35, 0.18],
        k=1,
    )[0]


def sample_type_for_assay(disease: str, assay: str) -> tuple[str, str]:
    if disease == "healthy control":
        if assay == AssayType.RNA_SEQ.value:
            return SampleType.RNA.value, TumorNormalStatus.NORMAL.value
        return SampleType.BLOOD.value, TumorNormalStatus.NORMAL.value

    if assay == AssayType.RNA_SEQ.value:
        return SampleType.RNA.value, TumorNormalStatus.TUMOR.value

    if assay == AssayType.TARGETED_PANEL.value and random.random() < 0.15:
        return SampleType.CFDNA.value, TumorNormalStatus.TUMOR.value

    return SampleType.TUMOR.value, TumorNormalStatus.TUMOR.value


def make_patients() -> list[dict]:
    rows: list[dict] = []
    for i in range(1, 51):
        disease = choose_disease()
        rows.append(
            {
                "patient_id": make_patient_id(i),
                "external_subject_id": external_subject_id(i),
                "disease_type": disease,
                "condition_group": condition_group_for_disease(disease),
                "sex": random.choices(
                    [Sex.FEMALE.value, Sex.MALE.value, Sex.UNKNOWN.value],
                    weights=[0.48, 0.48, 0.04],
                    k=1,
                )[0],
                "age_band": choose_age_band(disease),
                "created_at": str(
                    random_datetime_on_date(days_before(ANCHOR_DATE, random.randint(120, 300)))
                ),
            }
        )
    return rows


def make_batches() -> list[dict]:
    submitters = [
        "amy.clark",
        "li.chen",
        "sara.nguyen",
        "maria.garcia",
        "rahul.patel",
    ]
    rows: list[dict] = []
    for i in range(1, 6):
        rows.append(
            {
                "batch_id": make_batch_id(i),
                "batch_name": f"ONC_BATCH_2026_{i:02d}",
                "project_code": random.choice(["ONC-PORTAL", "SOLID-TUMOR", "HEME-TRACK"]),
                "submitted_by": submitters[i - 1],
                "submission_date": str(days_before(ANCHOR_DATE, 120 - (i * 12))),
                "notes": random.choice(
                    [
                        "Routine intake batch",
                        "Mixed DNA/RNA submission",
                        "Priority review batch",
                        "Includes paired tumor-normal cases",
                        "Contains several reprocessed samples",
                    ]
                ),
                "created_at": str(
                    random_datetime_on_date(days_before(ANCHOR_DATE, 125 - (i * 12)))
                ),
            }
        )
    return rows


def make_samples(patients: list[dict], counters: CounterState) -> list[dict]:
    rows: list[dict] = []

    for patient in patients:
        assays = assays_for_disease(patient["disease_type"])
        for assay in assays:
            sample_type, tumor_normal_status = sample_type_for_assay(patient["disease_type"], assay)
            collection_date = days_before(ANCHOR_DATE, random.randint(30, 240))
            received_date = collection_date + timedelta(days=random.randint(1, 8))
            sample_id = make_sample_id(counters.sample)
            counters.sample += 1

            rows.append(
                {
                    "sample_id": sample_id,
                    "patient_id": patient["patient_id"],
                    "batch_id": make_batch_id(random.randint(1, 5)),
                    "sample_type": sample_type,
                    "assay_type": assay,
                    "collection_date": str(collection_date),
                    "received_date": str(received_date),
                    "specimen_site": random.choice(SPECIMEN_SITES[patient["disease_type"]]),
                    "condition_label": patient["disease_type"],
                    "sample_status": random.choices(
                        [
                            SampleStatus.COMPLETE.value,
                            SampleStatus.IN_PROCESS.value,
                            SampleStatus.REGISTERED.value,
                            SampleStatus.HOLD.value,
                        ],
                        weights=[0.78, 0.10, 0.08, 0.04],
                        k=1,
                    )[0],
                    "tumor_normal_status": tumor_normal_status,
                    "library_prep_kit": random.choice(LIBRARY_PREP_BY_ASSAY[assay]),
                    "notes": random.choice(
                        [
                            "",
                            "Low input material",
                            "Repeat extraction requested",
                            "Matched to downstream clinical review",
                            "Processing priority elevated",
                        ]
                    ),
                    "created_at": str(random_datetime_on_date(received_date, hour=10)),
                }
            )

    while len(rows) < 85:
        patient = random.choice(patients)
        assay = random.choice(
            [AssayType.WES.value, AssayType.RNA_SEQ.value, AssayType.TARGETED_PANEL.value]
        )
        sample_type, tumor_normal_status = sample_type_for_assay(patient["disease_type"], assay)
        collection_date = days_before(ANCHOR_DATE, random.randint(20, 180))
        received_date = collection_date + timedelta(days=random.randint(1, 5))
        sample_id = make_sample_id(counters.sample)
        counters.sample += 1

        rows.append(
            {
                "sample_id": sample_id,
                "patient_id": patient["patient_id"],
                "batch_id": make_batch_id(random.randint(1, 5)),
                "sample_type": sample_type,
                "assay_type": assay,
                "collection_date": str(collection_date),
                "received_date": str(received_date),
                "specimen_site": random.choice(SPECIMEN_SITES[patient["disease_type"]]),
                "condition_label": patient["disease_type"],
                "sample_status": SampleStatus.COMPLETE.value,
                "tumor_normal_status": tumor_normal_status,
                "library_prep_kit": random.choice(LIBRARY_PREP_BY_ASSAY[assay]),
                "notes": "Supplemental profiling request",
                "created_at": str(random_datetime_on_date(received_date, hour=11)),
            }
        )

    return rows[:85]


def make_sequencing_runs() -> list[dict]:
    models = ["NovaSeq 6000", "NextSeq 2000", "MiSeq", "GridION"]
    statuses = [
        SequencingRunStatus.COMPLETE.value,
        SequencingRunStatus.COMPLETE.value,
        SequencingRunStatus.COMPLETE.value,
        SequencingRunStatus.PARTIAL.value,
        SequencingRunStatus.FAILED.value,
        SequencingRunStatus.COMPLETE.value,
    ]

    rows: list[dict] = []
    for i in range(1, 7):
        platform = (
            Platform.ILLUMINA.value
            if i < 6
            else random.choice([Platform.ILLUMINA.value, Platform.ONT.value])
        )
        run_date = days_before(ANCHOR_DATE, 90 - (i * 7))
        rows.append(
            {
                "seq_run_id": make_seq_run_id(i),
                "instrument_run_name": f"INST_RUN_2026_{i:02d}",
                "platform": platform,
                "instrument_model": random.choice(models),
                "flowcell_id": f"FCELL{i:03d}{random.randint(1000,9999)}",
                "run_date": str(run_date),
                "read_length": random.choice(["2x150", "2x100", "151", "75"]),
                "paired_end": True,
                "center_name": random.choice(
                    ["North Bay Genomics", "Clinical Genomics Core", "Research Sequencing Lab"]
                ),
                "run_status": statuses[i - 1],
                "notes": random.choice(
                    [
                        "Standard production run",
                        "Partial lane yield loss observed",
                        "Repeat sequencing required for subset of libraries",
                        "Flowcell quality concern flagged",
                        "",
                    ]
                ),
                "created_at": str(random_datetime_on_date(run_date, hour=7)),
            }
        )
    return rows


def assign_samples_to_runs(samples: list[dict], seq_runs: list[dict]) -> list[dict]:
    eligible_runs = [r for r in seq_runs if r["run_status"] != SequencingRunStatus.FAILED.value]
    rows: list[dict] = []
    barcode_counter = 1

    for sample in samples:
        seq_run = random.choice(eligible_runs)
        rows.append(
            {
                "sample_id": sample["sample_id"],
                "seq_run_id": seq_run["seq_run_id"],
                "lane_or_partition": lane_label(random.randint(1, 8)),
                "library_id": library_id(sample["sample_id"], 1),
                "barcode": barcode_id(barcode_counter),
                "created_at": str(
                    random_datetime_on_date(date.fromisoformat(sample["received_date"]), hour=14)
                ),
            }
        )
        barcode_counter += 1

    return rows


def choose_pipeline_versions(assay: str, rerun: bool = False) -> list[tuple[str, str]]:
    if assay == AssayType.RNA_SEQ.value:
        rna_version = random.choices(
            PIPELINE_VERSIONS_BY_ASSAY[assay]["rna"],
            weights=[0.25, 0.75] if not rerun else [0.15, 0.85],
            k=1,
        )[0]
        return [
            ("rna", rna_version),
            ("qc", "PLV_MULTI_QC_1_0_0"),
        ]

    align_version = random.choices(
        PIPELINE_VERSIONS_BY_ASSAY[assay]["alignment"],
        weights=[0.30, 0.70] if not rerun else [0.10, 0.90],
        k=1,
    )[0]
    somatic_version = random.choices(
        PIPELINE_VERSIONS_BY_ASSAY[assay]["somatic"],
        weights=[0.15, 0.25, 0.60] if not rerun else [0.05, 0.15, 0.80],
        k=1,
    )[0]
    return [
        ("alignment", align_version),
        ("somatic", somatic_version),
        ("qc", "PLV_MULTI_QC_1_0_0"),
    ]


def pipeline_status_for_stage(stage: str) -> str:
    if stage == "qc":
        return random.choices(
            [PipelineRunStatus.SUCCESS.value, PipelineRunStatus.PARTIAL.value],
            weights=[0.9, 0.1],
            k=1,
        )[0]
    return random.choices(
        [
            PipelineRunStatus.SUCCESS.value,
            PipelineRunStatus.FAILED.value,
            PipelineRunStatus.PARTIAL.value,
        ],
        weights=[0.84, 0.08, 0.08],
        k=1,
    )[0]


def make_pipeline_runs(
    samples: list[dict], assignments: list[dict], counters: CounterState
) -> list[dict]:
    seq_run_by_sample = {row["sample_id"]: row["seq_run_id"] for row in assignments}
    rows: list[dict] = []

    rerun_sample_ids = set(random.sample([s["sample_id"] for s in samples], k=20))

    for sample in samples:
        created_base = date.fromisoformat(sample["received_date"]) + timedelta(
            days=random.randint(2, 18)
        )
        pipeline_plan = choose_pipeline_versions(sample["assay_type"], rerun=False)

        for stage, pipeline_version_id in pipeline_plan:
            start_ts = random_datetime_on_date(created_base, hour=random.randint(1, 10))
            status = pipeline_status_for_stage(stage)
            finish_ts = (
                add_hours(start_ts, random.randint(1, 18))
                if status != PipelineRunStatus.RUNNING.value
                else None
            )

            row = {
                "pipeline_run_id": make_pipeline_run_id(counters.pipeline_run),
                "sample_id": sample["sample_id"],
                "seq_run_id": seq_run_by_sample.get(sample["sample_id"]),
                "pipeline_version_id": pipeline_version_id,
                "run_started_at": str(start_ts),
                "run_finished_at": str(finish_ts) if finish_ts else "",
                "run_status": status,
                "parameter_set_json": json.dumps(
                    {
                        "min_coverage": 80 if sample["assay_type"] == AssayType.WES.value else 250,
                        "caller_mode": (
                            "tumor_only"
                            if sample["condition_label"] == "healthy control"
                            else "somatic"
                        ),
                        "emit_qc": True,
                        "assay_type": sample["assay_type"],
                        "stage": stage,
                    }
                ),
                "execution_environment": random.choice(
                    ["docker-local", "slurm-cluster", "gcp-batch"]
                ),
                "triggered_by": random.choice(
                    ["analyst_user", "pipeline_scheduler", "bioinfo_ops"]
                ),
                "workflow_run_uuid": faker.uuid4(),
                "log_path": f"s3://genomics-portal/logs/{sample['sample_id']}/{stage}/{make_pipeline_run_id(counters.pipeline_run)}.log",
                "work_dir_path": f"s3://genomics-portal/work/{sample['sample_id']}/{make_pipeline_run_id(counters.pipeline_run)}",
                "failure_reason": (
                    random.choice(
                        [
                            "",
                            "",
                            "",
                            "low coverage detected",
                            "executor node preemption",
                            "input validation failure",
                        ]
                    )
                    if status in {PipelineRunStatus.FAILED.value, PipelineRunStatus.PARTIAL.value}
                    else ""
                ),
                "created_at": str(add_minutes(start_ts, 5)),
            }
            rows.append(row)
            counters.pipeline_run += 1

        if sample["sample_id"] in rerun_sample_ids:
            rerun_date = created_base + timedelta(days=random.randint(7, 28))
            rerun_plan = choose_pipeline_versions(sample["assay_type"], rerun=True)
            rerun_stage = (
                rerun_plan[-2:]
                if sample["assay_type"] == AssayType.RNA_SEQ.value
                else rerun_plan[1:]
            )
            for stage, pipeline_version_id in rerun_stage:
                start_ts = random_datetime_on_date(rerun_date, hour=random.randint(2, 11))
                row = {
                    "pipeline_run_id": make_pipeline_run_id(counters.pipeline_run),
                    "sample_id": sample["sample_id"],
                    "seq_run_id": seq_run_by_sample.get(sample["sample_id"]),
                    "pipeline_version_id": pipeline_version_id,
                    "run_started_at": str(start_ts),
                    "run_finished_at": str(add_hours(start_ts, random.randint(2, 16))),
                    "run_status": PipelineRunStatus.SUCCESS.value,
                    "parameter_set_json": json.dumps(
                        {
                            "rerun": True,
                            "trigger_reason": random.choice(
                                [
                                    "qc_warn_review",
                                    "updated_pipeline_version",
                                    "panel_hotspot_recall",
                                    "reportable_variant_confirmation",
                                ]
                            ),
                            "assay_type": sample["assay_type"],
                            "stage": stage,
                        }
                    ),
                    "execution_environment": random.choice(["docker-local", "slurm-cluster"]),
                    "triggered_by": "bioinfo_ops",
                    "workflow_run_uuid": faker.uuid4(),
                    "log_path": f"s3://genomics-portal/logs/{sample['sample_id']}/{stage}/{make_pipeline_run_id(counters.pipeline_run)}.log",
                    "work_dir_path": f"s3://genomics-portal/work/{sample['sample_id']}/{make_pipeline_run_id(counters.pipeline_run)}",
                    "failure_reason": "",
                    "created_at": str(add_minutes(start_ts, 5)),
                }
                rows.append(row)
                counters.pipeline_run += 1

    return rows[:105]


def pipeline_family_from_version(pipeline_version_id: str) -> str:
    if "DNA_ALIGN" in pipeline_version_id:
        return "DNA_ALIGN"
    if "SOM_VAR" in pipeline_version_id:
        return "SOM_VAR"
    if "RNA_QUANT" in pipeline_version_id:
        return "RNA_QUANT"
    if "MULTI_QC" in pipeline_version_id:
        return "MULTI_QC"
    raise ValueError(f"Unsupported pipeline version id family: {pipeline_version_id}")


def make_pipeline_run_references(pipeline_runs: list[dict]) -> list[dict]:
    rows: list[dict] = []

    for run in pipeline_runs:
        pipeline_family = pipeline_family_from_version(run["pipeline_version_id"])
        reference_plan = PIPELINE_REFERENCE_PLAN[pipeline_family]

        for reference_link in reference_plan:
            rows.append(
                {
                    "pipeline_run_id": run["pipeline_run_id"],
                    "reference_id": reference_link["reference_id"],
                    "usage_role": reference_link["usage_role"],
                    "execution_order": reference_link["execution_order"],
                    "step_label": reference_link["step_label"],
                    "created_at": run["created_at"],
                }
            )

    return rows


def make_pipeline_run_tools(pipeline_runs: list[dict]) -> list[dict]:
    rows: list[dict] = []

    for run in pipeline_runs:
        pipeline_family = pipeline_family_from_version(run["pipeline_version_id"])
        tool_plan = PIPELINE_TOOL_PLAN[pipeline_family]

        for tool_link in tool_plan:
            rows.append(
                {
                    "pipeline_run_id": run["pipeline_run_id"],
                    "tool_id": tool_link["tool_id"],
                    "usage_role": tool_link["usage_role"],
                    "execution_order": tool_link["execution_order"],
                    "step_label": tool_link["step_label"],
                    "created_at": run["created_at"],
                }
            )

    return rows


def file_size_for_role(file_role: str) -> int:
    ranges = {
        FileRole.RAW_FASTQ.value: (500_000_000, 2_500_000_000),
        FileRole.BAM.value: (1_500_000_000, 12_000_000_000),
        FileRole.BAI.value: (2_000_000, 20_000_000),
        FileRole.VCF.value: (1_000_000, 25_000_000),
        FileRole.MAF.value: (100_000, 2_000_000),
        FileRole.QC_JSON.value: (20_000, 500_000),
        FileRole.QC_TSV.value: (5_000, 200_000),
        FileRole.COUNTS_MATRIX.value: (2_000_000, 20_000_000),
        FileRole.LOG.value: (10_000, 5_000_000),
        FileRole.REPORT.value: (20_000, 1_000_000),
    }
    low, high = ranges.get(file_role, (1_000, 50_000))
    return random.randint(low, high)


def file_format_for_role(file_role: str) -> str:
    mapping = {
        FileRole.RAW_FASTQ.value: FileFormat.FASTQ_GZ.value,
        FileRole.BAM.value: FileFormat.BAM.value,
        FileRole.BAI.value: FileFormat.BAI.value,
        FileRole.VCF.value: FileFormat.VCF_GZ.value,
        FileRole.MAF.value: FileFormat.MAF.value,
        FileRole.QC_JSON.value: FileFormat.JSON.value,
        FileRole.QC_TSV.value: FileFormat.TSV.value,
        FileRole.COUNTS_MATRIX.value: FileFormat.TSV.value,
        FileRole.LOG.value: FileFormat.TXT.value,
        FileRole.REPORT.value: FileFormat.TXT.value,
    }
    return mapping[file_role]


def make_file_assets(
    samples: list[dict], pipeline_runs: list[dict], counters: CounterState
) -> list[dict]:
    runs_by_sample: dict[str, list[dict]] = {}
    for run in pipeline_runs:
        runs_by_sample.setdefault(run["sample_id"], []).append(run)

    rows: list[dict] = []

    for sample in samples:
        raw_roles = [FileRole.RAW_FASTQ.value]
        for role in raw_roles:
            file_id = make_file_asset_id(counters.file_asset)
            counters.file_asset += 1
            rows.append(
                {
                    "file_asset_id": file_id,
                    "sample_id": sample["sample_id"],
                    "pipeline_run_id": "",
                    "file_role": role,
                    "file_format": file_format_for_role(role),
                    "path_uri": f"s3://genomics-portal/raw/{sample['sample_id']}/{sample['sample_id']}_R1.fastq.gz",
                    "checksum": sha_like(file_id),
                    "file_size_bytes": file_size_for_role(role),
                    "source_system": "synthetic_generator",
                    "is_current": True,
                    "created_at": sample["created_at"],
                }
            )

        sample_runs = runs_by_sample.get(sample["sample_id"], [])
        latest_success_by_prefix: dict[str, str] = {}
        for run in sample_runs:
            pv = run["pipeline_version_id"]
            if "DNA_ALIGN" in pv:
                latest_success_by_prefix["align"] = run["pipeline_run_id"]
            elif "SOM_VAR" in pv:
                latest_success_by_prefix["somatic"] = run["pipeline_run_id"]
            elif "RNA_QUANT" in pv:
                latest_success_by_prefix["rna"] = run["pipeline_run_id"]
            elif "MULTI_QC" in pv:
                latest_success_by_prefix["qc"] = run["pipeline_run_id"]

        for run in sample_runs:
            status = run["run_status"]
            if "DNA_ALIGN" in run["pipeline_version_id"]:
                roles = [FileRole.BAM.value, FileRole.BAI.value, FileRole.LOG.value]
            elif "SOM_VAR" in run["pipeline_version_id"]:
                roles = [FileRole.VCF.value, FileRole.MAF.value, FileRole.LOG.value]
            elif "RNA_QUANT" in run["pipeline_version_id"]:
                roles = [FileRole.COUNTS_MATRIX.value, FileRole.LOG.value]
            else:
                roles = [
                    FileRole.QC_JSON.value,
                    FileRole.QC_TSV.value,
                    FileRole.REPORT.value,
                    FileRole.LOG.value,
                ]

            if status == PipelineRunStatus.FAILED.value:
                roles = [FileRole.LOG.value]
            elif status == PipelineRunStatus.PARTIAL.value and FileRole.REPORT.value in roles:
                roles.remove(FileRole.REPORT.value)

            for role in roles:
                file_id = make_file_asset_id(counters.file_asset)
                counters.file_asset += 1

                current = False
                if (
                    "DNA_ALIGN" in run["pipeline_version_id"]
                    and latest_success_by_prefix.get("align") == run["pipeline_run_id"]
                ):
                    current = True
                elif (
                    "SOM_VAR" in run["pipeline_version_id"]
                    and latest_success_by_prefix.get("somatic") == run["pipeline_run_id"]
                ):
                    current = True
                elif (
                    "RNA_QUANT" in run["pipeline_version_id"]
                    and latest_success_by_prefix.get("rna") == run["pipeline_run_id"]
                ):
                    current = True
                elif (
                    "MULTI_QC" in run["pipeline_version_id"]
                    and latest_success_by_prefix.get("qc") == run["pipeline_run_id"]
                ):
                    current = True

                rows.append(
                    {
                        "file_asset_id": file_id,
                        "sample_id": sample["sample_id"],
                        "pipeline_run_id": run["pipeline_run_id"],
                        "file_role": role,
                        "file_format": file_format_for_role(role),
                        "path_uri": f"s3://genomics-portal/derived/{sample['sample_id']}/{run['pipeline_run_id']}/{role.lower()}.{file_format_for_role(role).lower()}",
                        "checksum": sha_like(file_id),
                        "file_size_bytes": file_size_for_role(role),
                        "source_system": "synthetic_generator",
                        "is_current": current,
                        "created_at": run["created_at"],
                    }
                )

    return rows[:280]


def summary_qc_status(sample: dict) -> str:
    if sample["condition_label"] == "healthy control":
        return random.choices([QcStatus.PASS.value, QcStatus.WARN.value], weights=[0.9, 0.1], k=1)[
            0
        ]
    return random.choices(
        [QcStatus.PASS.value, QcStatus.WARN.value, QcStatus.FAIL.value],
        weights=[0.72, 0.18, 0.10],
        k=1,
    )[0]


def get_latest_qc_run(sample_id: str, pipeline_runs: list[dict]) -> dict | None:
    runs = [
        r
        for r in pipeline_runs
        if r["sample_id"] == sample_id and "MULTI_QC" in r["pipeline_version_id"]
    ]
    if not runs:
        return None
    runs.sort(key=lambda x: x["run_started_at"])
    return runs[-1]


def make_qc_value(
    metric_name: str, assay_type: str, overall_status: str
) -> tuple[float | None, str | None, str]:
    if metric_name == "total_reads":
        if assay_type == AssayType.RNA_SEQ.value:
            value = random.randint(15_000_000, 90_000_000)
        elif assay_type == AssayType.TARGETED_PANEL.value:
            value = random.randint(2_500_000, 20_000_000)
        else:
            value = random.randint(25_000_000, 180_000_000)
        status = QcStatus.PASS.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.35:
            value = random.randint(300_000, 900_000)
            status = QcStatus.FAIL.value
        return float(value), None, status

    if metric_name == "pct_q30_bases":
        value = round(random.uniform(78, 96), 2)
        status = QcStatus.PASS.value if value >= 85 else QcStatus.WARN.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.25:
            value = round(random.uniform(60, 74), 2)
            status = QcStatus.FAIL.value
        return value, None, status

    if metric_name == "mean_target_coverage":
        if assay_type == AssayType.RNA_SEQ.value:
            return None, None, ""
        base = (
            round(random.uniform(90, 220), 2)
            if assay_type == AssayType.WES.value
            else round(random.uniform(250, 900), 2)
        )
        status = QcStatus.PASS.value
        if base < 90:
            status = QcStatus.WARN.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.35:
            base = round(random.uniform(20, 79), 2)
            status = QcStatus.FAIL.value
        return base, None, status

    if metric_name == "pct_target_bases_100x":
        if assay_type == AssayType.RNA_SEQ.value:
            return None, None, ""
        value = round(random.uniform(86, 99), 2)
        status = QcStatus.PASS.value if value >= 90 else QcStatus.WARN.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.30:
            value = round(random.uniform(55, 84), 2)
            status = QcStatus.FAIL.value
        return value, None, status

    if metric_name == "mapping_rate":
        if assay_type == AssayType.RNA_SEQ.value:
            return None, None, ""
        value = round(random.uniform(0.91, 0.995), 4)
        status = QcStatus.PASS.value if value >= 0.95 else QcStatus.WARN.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.25:
            value = round(random.uniform(0.60, 0.89), 4)
            status = QcStatus.FAIL.value
        return value, None, status

    if metric_name == "duplicate_rate":
        if assay_type == AssayType.RNA_SEQ.value:
            return None, None, ""
        value = round(random.uniform(0.08, 0.42), 4)
        status = QcStatus.PASS.value if value <= 0.35 else QcStatus.WARN.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.20:
            value = round(random.uniform(0.51, 0.72), 4)
            status = QcStatus.FAIL.value
        return value, None, status

    if metric_name == "median_insert_size":
        if assay_type == AssayType.RNA_SEQ.value:
            return None, None, ""
        value = round(random.uniform(140, 350), 2)
        status = QcStatus.PASS.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.15:
            value = round(random.uniform(60, 95), 2)
            status = QcStatus.FAIL.value
        return value, None, status

    if metric_name == "estimated_contamination":
        if assay_type == AssayType.RNA_SEQ.value:
            return None, None, ""
        value = round(random.uniform(0.0, 0.04), 4)
        status = QcStatus.PASS.value if value <= 0.03 else QcStatus.WARN.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.20:
            value = round(random.uniform(0.051, 0.12), 4)
            status = QcStatus.FAIL.value
        return value, None, status

    if metric_name == "tumor_purity_qc":
        if assay_type == AssayType.RNA_SEQ.value:
            return None, None, ""
        value = round(random.uniform(0.25, 0.86), 4)
        status = QcStatus.PASS.value if value >= 0.30 else QcStatus.WARN.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.20:
            value = round(random.uniform(0.05, 0.19), 4)
            status = QcStatus.FAIL.value
        return value, None, status

    if metric_name == "rna_mapping_rate":
        if assay_type != AssayType.RNA_SEQ.value:
            return None, None, ""
        value = round(random.uniform(0.78, 0.98), 4)
        status = QcStatus.PASS.value if value >= 0.85 else QcStatus.WARN.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.30:
            value = round(random.uniform(0.45, 0.74), 4)
            status = QcStatus.FAIL.value
        return value, None, status

    if metric_name == "exonic_rate":
        if assay_type != AssayType.RNA_SEQ.value:
            return None, None, ""
        value = round(random.uniform(0.52, 0.88), 4)
        status = QcStatus.PASS.value if value >= 0.65 else QcStatus.WARN.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.25:
            value = round(random.uniform(0.20, 0.49), 4)
            status = QcStatus.FAIL.value
        return value, None, status

    if metric_name == "rrna_rate":
        if assay_type != AssayType.RNA_SEQ.value:
            return None, None, ""
        value = round(random.uniform(0.03, 0.24), 4)
        status = QcStatus.PASS.value if value <= 0.20 else QcStatus.WARN.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.30:
            value = round(random.uniform(0.36, 0.60), 4)
            status = QcStatus.FAIL.value
        return value, None, status

    if metric_name == "sex_concordance":
        text_value = "CONCORDANT"
        status = QcStatus.PASS.value
        if overall_status == QcStatus.FAIL.value and random.random() < 0.10:
            text_value = "DISCORDANT"
            status = QcStatus.FAIL.value
        return None, text_value, status

    if metric_name == "qc_summary_flag":
        return None, overall_status, overall_status

    raise ValueError(f"Unhandled metric: {metric_name}")


def make_qc_results(
    samples: list[dict], pipeline_runs: list[dict], file_assets: list[dict], counters: CounterState
) -> list[dict]:
    qc_json_by_run = {
        asset["pipeline_run_id"]: asset["file_asset_id"]
        for asset in file_assets
        if asset["file_role"] == FileRole.QC_JSON.value
    }

    rows: list[dict] = []
    for sample in samples:
        qc_run = get_latest_qc_run(sample["sample_id"], pipeline_runs)
        if not qc_run:
            continue

        overall_status = summary_qc_status(sample)
        measured_at = qc_run["run_finished_at"] or qc_run["run_started_at"]
        source_file_asset_id = qc_json_by_run.get(qc_run["pipeline_run_id"], "")

        metric_names = []
        if sample["assay_type"] == AssayType.RNA_SEQ.value:
            metric_names.extend(
                [
                    "total_reads",
                    "pct_q30_bases",
                    "rna_mapping_rate",
                    "exonic_rate",
                    "rrna_rate",
                ]
            )
        else:
            metric_names.extend(
                [
                    "total_reads",
                    "pct_q30_bases",
                    "mean_target_coverage",
                    "pct_target_bases_100x",
                    "mapping_rate",
                    "duplicate_rate",
                    "median_insert_size",
                    "estimated_contamination",
                    "tumor_purity_qc",
                ]
            )

        metric_names.extend(["sex_concordance", "qc_summary_flag"])

        for metric_name in metric_names:
            numeric_value, text_value, qc_status = make_qc_value(
                metric_name, sample["assay_type"], overall_status
            )
            if qc_status == "":
                continue

            rows.append(
                {
                    "qc_result_id": make_qc_result_id(counters.qc_result),
                    "sample_id": sample["sample_id"],
                    "pipeline_run_id": qc_run["pipeline_run_id"],
                    "qc_metric_name": metric_name,
                    "metric_value_numeric": numeric_value if numeric_value is not None else "",
                    "metric_value_text": text_value or "",
                    "qc_status": qc_status,
                    "measured_at": measured_at,
                    "source_file_asset_id": source_file_asset_id,
                }
            )
            counters.qc_result += 1

    return rows[:550]


def choose_latest_variant_run(sample_id: str, pipeline_runs: list[dict]) -> dict | None:
    runs = [
        r
        for r in pipeline_runs
        if r["sample_id"] == sample_id and "SOM_VAR" in r["pipeline_version_id"]
    ]
    if not runs:
        return None
    success_runs = [r for r in runs if r["run_status"] == PipelineRunStatus.SUCCESS.value]
    target = success_runs if success_runs else runs
    target.sort(key=lambda x: x["run_started_at"])
    return target[-1]


def make_variant_record(
    sample: dict, pipeline_run: dict, gene: str, counters: CounterState, file_assets: list[dict]
) -> dict:
    maf_by_run = {
        asset["pipeline_run_id"]: asset["file_asset_id"]
        for asset in file_assets
        if asset["file_role"] == FileRole.MAF.value
    }
    protein_change = (
        random.choice(KRAS_PROTEINS)
        if gene == "KRAS"
        else random.choice(
            ["p.R175H", "p.V600E", "p.H1047R", "p.L858R", "p.G13R", "p.R132H", "p.D835Y", "p.E545K"]
        )
    )
    clinical_significance = random.choices(
        [
            ClinicalSignificance.PATHOGENIC.value,
            ClinicalSignificance.LIKELY_PATHOGENIC.value,
            ClinicalSignificance.VUS.value,
            ClinicalSignificance.BENIGN.value,
            ClinicalSignificance.UNKNOWN.value,
        ],
        weights=[0.28, 0.22, 0.34, 0.05, 0.11],
        k=1,
    )[0]

    if gene == "KRAS":
        clinical_significance = random.choice(
            [
                ClinicalSignificance.PATHOGENIC.value,
                ClinicalSignificance.LIKELY_PATHOGENIC.value,
            ]
        )

    return {
        "variant_summary_id": make_variant_summary_id(counters.variant),
        "sample_id": sample["sample_id"],
        "pipeline_run_id": pipeline_run["pipeline_run_id"],
        "gene_symbol": gene,
        "variant_class": random.choices(
            [
                VariantClass.SNV.value,
                VariantClass.INDEL.value,
                VariantClass.CNV.value,
                VariantClass.FUSION.value,
            ],
            weights=[0.72, 0.16, 0.08, 0.04],
            k=1,
        )[0],
        "protein_change": protein_change,
        "chromosome": GENE_TO_CHR.get(gene, str(random.randint(1, 22))),
        "position": random.randint(1_000_000, 190_000_000),
        "ref_allele": random.choice(["A", "C", "G", "T"]),
        "alt_allele": random.choice(["A", "C", "G", "T"]),
        "tumor_vaf": round(random.uniform(0.03, 0.78), 4),
        "clinical_significance": clinical_significance,
        "is_driver": gene in {"KRAS", "EGFR", "BRAF", "IDH1", "IDH2", "FLT3", "ALK", "ROS1"},
        "reported_flag": clinical_significance
        in {
            ClinicalSignificance.PATHOGENIC.value,
            ClinicalSignificance.LIKELY_PATHOGENIC.value,
        },
        "source_file_asset_id": maf_by_run.get(pipeline_run["pipeline_run_id"], ""),
        "created_at": pipeline_run["created_at"],
    }


def make_variant_summaries(
    samples: list[dict], pipeline_runs: list[dict], file_assets: list[dict], counters: CounterState
) -> list[dict]:
    tumor_like = [
        s
        for s in samples
        if s["condition_label"] != "healthy control"
        and s["assay_type"] in {AssayType.WES.value, AssayType.TARGETED_PANEL.value}
    ]

    kras_samples = {s["sample_id"] for s in random.sample(tumor_like, k=min(18, len(tumor_like)))}
    high_tmb_samples = {
        s["sample_id"] for s in random.sample(tumor_like, k=min(12, len(tumor_like)))
    }

    rows: list[dict] = []
    for sample in tumor_like:
        variant_run = choose_latest_variant_run(sample["sample_id"], pipeline_runs)
        if not variant_run:
            continue

        variant_count = random.randint(1, 3)
        if sample["sample_id"] in high_tmb_samples:
            variant_count += random.randint(3, 6)

        chosen_genes = random.sample(GENES, k=min(variant_count, len(GENES)))
        if sample["sample_id"] in kras_samples and "KRAS" not in chosen_genes:
            chosen_genes[0] = "KRAS"

        chosen_genes = ensure_unique(chosen_genes)

        for gene in chosen_genes:
            rows.append(make_variant_record(sample, variant_run, gene, counters, file_assets))
            counters.variant += 1

    while len(rows) < 220:
        sample = random.choice(tumor_like)
        variant_run = choose_latest_variant_run(sample["sample_id"], pipeline_runs)
        if variant_run is None:
            continue
        gene = random.choice(GENES)
        rows.append(make_variant_record(sample, variant_run, gene, counters, file_assets))
        counters.variant += 1

    return rows[:220]


def make_sample_analysis_summary(
    samples: list[dict], variant_rows: list[dict], counters: CounterState
) -> list[dict]:
    variant_count_by_sample: dict[str, int] = {}
    for row in variant_rows:
        variant_count_by_sample[row["sample_id"]] = (
            variant_count_by_sample.get(row["sample_id"], 0) + 1
        )

    rows: list[dict] = []
    for sample in samples:
        if sample["assay_type"] not in {
            AssayType.WES.value,
            AssayType.TARGETED_PANEL.value,
            AssayType.RNA_SEQ.value,
        }:
            continue

        count = variant_count_by_sample.get(sample["sample_id"], 0)
        high_tmb = count >= 6 and sample["condition_label"] != "healthy control"

        if sample["condition_label"] == "healthy control":
            msi_status = MsiStatus.MSI_STABLE.value
            tmb_score = round(random.uniform(0.1, 1.5), 2)
        else:
            msi_status = random.choices(
                [
                    MsiStatus.MSI_STABLE.value,
                    MsiStatus.MSI_HIGH.value,
                    MsiStatus.INDETERMINATE.value,
                ],
                weights=[0.74, 0.16, 0.10],
                k=1,
            )[0]
            tmb_score = round(random.uniform(1.2, 8.0), 2)
            if high_tmb:
                tmb_score = round(random.uniform(10.0, 28.0), 2)

        rows.append(
            {
                "sample_analysis_summary_id": make_sample_analysis_summary_id(
                    counters.analysis_summary
                ),
                "sample_id": sample["sample_id"],
                "tmb_score": tmb_score,
                "msi_status": msi_status,
                "purity_estimate": (
                    round(random.uniform(0.18, 0.92), 4)
                    if sample["condition_label"] != "healthy control"
                    else round(random.uniform(0.95, 1.0), 4)
                ),
                "ploidy_estimate": round(random.uniform(1.6, 5.2), 2),
                "expression_subtype": random.choice(
                    ["immune_high", "proliferative", "basal_like", "luminal", "mesenchymal", ""]
                ),
                "analysis_summary_json": json.dumps(
                    {
                        "variant_burden_count": count,
                        "high_tmb_flag": high_tmb,
                        "reportable_variant_count": count if count < 4 else random.randint(1, 4),
                    }
                ),
                "last_updated_at": str(
                    random_datetime_on_date(
                        days_before(ANCHOR_DATE, random.randint(1, 20)), hour=16
                    )
                ),
            }
        )
        counters.analysis_summary += 1

    return rows


def make_audit_events(
    patients: list[dict],
    samples: list[dict],
    pipeline_runs: list[dict],
    file_assets: list[dict],
    qc_results: list[dict],
    variants: list[dict],
    counters: CounterState,
) -> list[dict]:
    rows: list[dict] = []

    def add_event(
        entity_type: str,
        entity_id: str,
        event_type: str,
        actor: str,
        details: dict,
        event_date: str,
    ) -> None:
        rows.append(
            {
                "audit_event_id": make_audit_event_id(counters.audit),
                "entity_type": entity_type,
                "entity_id": entity_id,
                "event_type": event_type,
                "event_timestamp": event_date,
                "actor": actor,
                "details_json": json.dumps(details),
            }
        )
        counters.audit += 1

    for patient in patients:
        add_event(
            "PATIENT",
            patient["patient_id"],
            "CREATED",
            "synthetic_loader",
            {"source": "synthetic_generator"},
            patient["created_at"],
        )

    for sample in samples:
        add_event(
            "SAMPLE",
            sample["sample_id"],
            "REGISTERED",
            "sample_intake",
            {"assay_type": sample["assay_type"], "sample_status": sample["sample_status"]},
            sample["created_at"],
        )

    for run in pipeline_runs:
        event_type = "FAILED" if run["run_status"] == PipelineRunStatus.FAILED.value else "INGESTED"
        add_event(
            "PIPELINE_RUN",
            run["pipeline_run_id"],
            event_type,
            run["triggered_by"],
            {"pipeline_version_id": run["pipeline_version_id"], "run_status": run["run_status"]},
            run["created_at"],
        )

    for asset in file_assets[:60]:
        add_event(
            "FILE_ASSET",
            asset["file_asset_id"],
            "REGISTERED",
            "file_registry",
            {"file_role": asset["file_role"], "is_current": asset["is_current"]},
            asset["created_at"],
        )

    for result in qc_results[:70]:
        add_event(
            "QC_RESULT",
            result["qc_result_id"],
            "INGESTED",
            "qc_ingest",
            {"metric_name": result["qc_metric_name"], "qc_status": result["qc_status"]},
            result["measured_at"],
        )

    for variant in variants[:70]:
        add_event(
            "VARIANT_SUMMARY",
            variant["variant_summary_id"],
            "INGESTED",
            "variant_ingest",
            {"gene_symbol": variant["gene_symbol"], "reported_flag": variant["reported_flag"]},
            variant["created_at"],
        )

    return rows[:250]


def make_example_files(
    samples: list[dict],
    seq_runs: list[dict],
    pipeline_runs: list[dict],
    qc_results: list[dict],
    variants: list[dict],
    file_assets: list[dict],
) -> None:
    write_tsv(EXAMPLES_DIR / "sample_manifest.tsv", samples[:10])
    write_tsv(EXAMPLES_DIR / "sequencing_run_manifest.tsv", seq_runs[:6])
    write_json(EXAMPLES_DIR / "pipeline_run_manifest.json", pipeline_runs[:10])
    write_json(EXAMPLES_DIR / "qc_metrics.json", qc_results[:15])
    write_tsv(EXAMPLES_DIR / "variant_summary.tsv", variants[:20])
    write_tsv(EXAMPLES_DIR / "file_asset_manifest.tsv", file_assets[:20])


def main() -> None:
    logger.info("Starting synthetic data generation")
    counters = CounterState()

    patients = make_patients()
    batches = make_batches()
    samples = make_samples(patients, counters)
    sequencing_runs = make_sequencing_runs()
    sample_run_assignments = assign_samples_to_runs(samples, sequencing_runs)
    pipeline_runs = make_pipeline_runs(samples, sample_run_assignments, counters)
    pipeline_run_references = make_pipeline_run_references(pipeline_runs)
    pipeline_run_tools = make_pipeline_run_tools(pipeline_runs)
    file_assets = make_file_assets(samples, pipeline_runs, counters)
    qc_results = make_qc_results(samples, pipeline_runs, file_assets, counters)
    variant_summaries = make_variant_summaries(samples, pipeline_runs, file_assets, counters)
    sample_analysis_summary = make_sample_analysis_summary(samples, variant_summaries, counters)
    audit_events = make_audit_events(
        patients,
        samples,
        pipeline_runs,
        file_assets,
        qc_results,
        variant_summaries,
        counters,
    )

    write_tsv(RAW_DIR / "sample_metadata" / "patients.tsv", patients)
    write_tsv(RAW_DIR / "sample_metadata" / "batches.tsv", batches)
    write_tsv(RAW_DIR / "sample_metadata" / "samples.tsv", samples)

    write_tsv(RAW_DIR / "sequencing_runs" / "sequencing_runs.tsv", sequencing_runs)
    write_tsv(RAW_DIR / "sequencing_runs" / "sample_run_assignments.tsv", sample_run_assignments)

    write_json(RAW_DIR / "pipeline_runs" / "pipeline_runs.json", pipeline_runs)
    write_json(
        RAW_DIR / "pipeline_runs" / "pipeline_run_references.json",
        pipeline_run_references,
    )
    write_json(
        RAW_DIR / "pipeline_runs" / "pipeline_run_tools.json",
        pipeline_run_tools,
    )
    write_tsv(RAW_DIR / "file_manifests" / "file_assets.tsv", file_assets)
    write_json(RAW_DIR / "qc_metrics" / "qc_results.json", qc_results)
    write_tsv(RAW_DIR / "variant_summaries" / "variant_summary.tsv", variant_summaries)
    write_json(RAW_DIR / "pipeline_runs" / "sample_analysis_summary.json", sample_analysis_summary)
    write_json(RAW_DIR / "logs" / "audit_events.json", audit_events)

    make_example_files(
        samples, sequencing_runs, pipeline_runs, qc_results, variant_summaries, file_assets
    )

    manifest_summary = {
        "patients": len(patients),
        "batches": len(batches),
        "samples": len(samples),
        "sequencing_runs": len(sequencing_runs),
        "sample_run_assignments": len(sample_run_assignments),
        "pipeline_runs": len(pipeline_runs),
        "pipeline_run_references": len(pipeline_run_references),
        "pipeline_run_tools": len(pipeline_run_tools),
        "file_assets": len(file_assets),
        "qc_results": len(qc_results),
        "variant_summary": len(variant_summaries),
        "sample_analysis_summary": len(sample_analysis_summary),
        "audit_events": len(audit_events),
        "random_seed": RANDOM_SEED,
    }
    write_json(RAW_DIR / "manifest_summary.json", manifest_summary)

    logger.info("Synthetic data generation completed")
    logger.info("Summary: %s", manifest_summary)


if __name__ == "__main__":
    main()
