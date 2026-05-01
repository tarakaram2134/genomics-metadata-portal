from enum import StrEnum


class Sex(StrEnum):
    FEMALE = "FEMALE"
    MALE = "MALE"
    UNKNOWN = "UNKNOWN"


class AgeBand(StrEnum):
    PEDIATRIC = "PEDIATRIC"
    YOUNG_ADULT = "YOUNG_ADULT"
    ADULT = "ADULT"
    OLDER_ADULT = "OLDER_ADULT"
    UNKNOWN = "UNKNOWN"


class SampleType(StrEnum):
    TUMOR = "TUMOR"
    NORMAL = "NORMAL"
    BLOOD = "BLOOD"
    RNA = "RNA"
    CFDNA = "CFDNA"


class AssayType(StrEnum):
    WES = "WES"
    RNA_SEQ = "RNA_SEQ"
    TARGETED_PANEL = "TARGETED_PANEL"


class SampleStatus(StrEnum):
    RECEIVED = "RECEIVED"
    REGISTERED = "REGISTERED"
    IN_PROCESS = "IN_PROCESS"
    COMPLETE = "COMPLETE"
    HOLD = "HOLD"


class TumorNormalStatus(StrEnum):
    TUMOR = "TUMOR"
    NORMAL = "NORMAL"
    PAIRED_NORMAL = "PAIRED_NORMAL"
    UNKNOWN = "UNKNOWN"


class Platform(StrEnum):
    ILLUMINA = "ILLUMINA"
    ONT = "ONT"


class SequencingRunStatus(StrEnum):
    PLANNED = "PLANNED"
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class PipelineCategory(StrEnum):
    ALIGNMENT = "ALIGNMENT"
    RNA_QUANT = "RNA_QUANT"
    SOMATIC_VARIANT = "SOMATIC_VARIANT"
    QC_AGGREGATION = "QC_AGGREGATION"


class PipelineRunStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class FileRole(StrEnum):
    RAW_FASTQ = "RAW_FASTQ"
    BAM = "BAM"
    CRAM = "CRAM"
    BAI = "BAI"
    CRAI = "CRAI"
    VCF = "VCF"
    MAF = "MAF"
    QC_JSON = "QC_JSON"
    QC_TSV = "QC_TSV"
    COUNTS_MATRIX = "COUNTS_MATRIX"
    LOG = "LOG"
    REPORT = "REPORT"


class FileFormat(StrEnum):
    FASTQ_GZ = "FASTQ_GZ"
    BAM = "BAM"
    CRAM = "CRAM"
    BAI = "BAI"
    CRAI = "CRAI"
    VCF_GZ = "VCF_GZ"
    TSV = "TSV"
    JSON = "JSON"
    TXT = "TXT"
    MAF = "MAF"


class QcStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class VariantClass(StrEnum):
    SNV = "SNV"
    INDEL = "INDEL"
    CNV = "CNV"
    FUSION = "FUSION"


class ClinicalSignificance(StrEnum):
    PATHOGENIC = "PATHOGENIC"
    LIKELY_PATHOGENIC = "LIKELY_PATHOGENIC"
    VUS = "VUS"
    BENIGN = "BENIGN"
    UNKNOWN = "UNKNOWN"


class MsiStatus(StrEnum):
    MSI_HIGH = "MSI_HIGH"
    MSI_STABLE = "MSI_STABLE"
    INDETERMINATE = "INDETERMINATE"
