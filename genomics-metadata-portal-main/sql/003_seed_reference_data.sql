BEGIN;

INSERT INTO pipelines (
    pipeline_id,
    pipeline_name,
    pipeline_category,
    description,
    repo_url,
    maintainer,
    active_flag
)
VALUES
    (
        'PL_DNA_ALIGN',
        'dna_alignment_preprocess',
        'ALIGNMENT',
        'Alignment and preprocessing workflow for DNA sequencing data.',
        'https://example.org/repos/dna_alignment_preprocess',
        'Bioinformatics Platform Team',
        TRUE
    ),
    (
        'PL_SOM_VAR',
        'somatic_variant_calling',
        'SOMATIC_VARIANT',
        'Somatic small variant calling and filtering workflow.',
        'https://example.org/repos/somatic_variant_calling',
        'Clinical Bioinformatics Team',
        TRUE
    ),
    (
        'PL_RNA_QUANT',
        'rna_expression_quant',
        'RNA_QUANT',
        'RNA-seq expression quantification and transcript summarization workflow.',
        'https://example.org/repos/rna_expression_quant',
        'Transcriptomics Team',
        TRUE
    ),
    (
        'PL_MULTI_QC',
        'multiqc_qc_aggregate',
        'QC_AGGREGATION',
        'Aggregates QC outputs and produces summary reports.',
        'https://example.org/repos/multiqc_qc_aggregate',
        'Bioinformatics Platform Team',
        TRUE
    )
ON CONFLICT (pipeline_id) DO NOTHING;

INSERT INTO pipeline_versions (
    pipeline_version_id,
    pipeline_id,
    version_label,
    container_image,
    container_tag,
    workflow_definition_version,
    release_date,
    is_current
)
VALUES
    ('PLV_DNA_ALIGN_1_0_0', 'PL_DNA_ALIGN', 'v1.0.0', 'ghcr.io/example/dna_alignment_preprocess', '1.0.0', 'wf.v1', '2025-01-15', FALSE),
    ('PLV_DNA_ALIGN_1_1_0', 'PL_DNA_ALIGN', 'v1.1.0', 'ghcr.io/example/dna_alignment_preprocess', '1.1.0', 'wf.v2', '2025-07-10', TRUE),

    ('PLV_SOM_VAR_2_0_0', 'PL_SOM_VAR', 'v2.0.0', 'ghcr.io/example/somatic_variant_calling', '2.0.0', 'wf.v3', '2024-11-01', FALSE),
    ('PLV_SOM_VAR_2_1_0', 'PL_SOM_VAR', 'v2.1.0', 'ghcr.io/example/somatic_variant_calling', '2.1.0', 'wf.v4', '2025-04-15', FALSE),
    ('PLV_SOM_VAR_2_2_0', 'PL_SOM_VAR', 'v2.2.0', 'ghcr.io/example/somatic_variant_calling', '2.2.0', 'wf.v5', '2025-10-20', TRUE),

    ('PLV_RNA_QUANT_1_0_0', 'PL_RNA_QUANT', 'v1.0.0', 'ghcr.io/example/rna_expression_quant', '1.0.0', 'wf.v1', '2025-02-05', FALSE),
    ('PLV_RNA_QUANT_1_1_0', 'PL_RNA_QUANT', 'v1.1.0', 'ghcr.io/example/rna_expression_quant', '1.1.0', 'wf.v2', '2025-08-01', TRUE),

    ('PLV_MULTI_QC_1_0_0', 'PL_MULTI_QC', 'v1.0.0', 'ghcr.io/example/multiqc_qc_aggregate', '1.0.0', 'wf.v1', '2025-03-01', TRUE)
ON CONFLICT (pipeline_version_id) DO NOTHING;

INSERT INTO reference_resources (
    reference_id,
    reference_name,
    reference_type,
    reference_version,
    source_uri,
    description
)
VALUES
    ('REF_GRCH38', 'GRCh38 primary assembly', 'GENOME', 'GRCh38', 's3://reference/genome/grch38.fa', 'Primary human genome assembly for DNA alignment.'),
    ('REF_GENCODE_V44', 'GENCODE comprehensive annotation', 'ANNOTATION', 'v44', 's3://reference/annotation/gencode.v44.gtf', 'Gene annotation for expression and variant annotation workflows.'),
    ('REF_EXOME_BED_V1', 'Exome target intervals', 'TARGET_BED', 'v1', 's3://reference/targets/exome_targets_v1.bed', 'Target intervals for WES coverage assessment.'),
    ('REF_PANEL_BED_V2', 'Pan-cancer targeted panel intervals', 'TARGET_BED', 'v2', 's3://reference/targets/panel_targets_v2.bed', 'Target intervals for targeted panel assay.'),
    ('REF_STAR_INDEX_V1', 'STAR transcriptome index', 'TRANSCRIPTOME', 'v1', 's3://reference/transcriptome/star_index_v1', 'Transcriptome index used by RNA quantification workflow.'),
    ('REF_BLACKLIST_ENCODE', 'ENCODE blacklist regions', 'BLACKLIST', 'hg38.v1', 's3://reference/blacklist/encode_hg38_blacklist.bed', 'Blacklist regions used for QC and filtering.'),
    ('REF_DBSNP_155', 'dbSNP common variants', 'ANNOTATION', '155', 's3://reference/annotation/dbsnp_155.vcf.gz', 'Common variant annotation resource.'),
    ('REF_CLINVAR_2025', 'ClinVar clinical annotations', 'ANNOTATION', '2025.01', 's3://reference/annotation/clinvar_2025_01.vcf.gz', 'Clinical significance annotation resource.'),
    ('REF_COSMIC_99', 'COSMIC somatic variants', 'ANNOTATION', '99', 's3://reference/annotation/cosmic_v99.vcf.gz', 'Somatic mutation annotation reference.'),
    ('REF_TRANSCRIPTOME_GENCODE_V44', 'GENCODE transcriptome reference', 'TRANSCRIPTOME', 'v44', 's3://reference/transcriptome/gencode_v44_transcripts.fa', 'Transcriptome FASTA resource for RNA workflows.')
ON CONFLICT (reference_id) DO NOTHING;

INSERT INTO tool_registry (
    tool_id,
    tool_name,
    tool_version,
    tool_category,
    container_image,
    notes
)
VALUES
    ('TOOL_BWA_0_7_17', 'bwa', '0.7.17', 'ALIGNER', 'biocontainers/bwa:0.7.17', 'DNA aligner used in alignment pipeline.'),
    ('TOOL_SAMTOOLS_1_19', 'samtools', '1.19', 'UTILITY', 'biocontainers/samtools:1.19', 'BAM/CRAM processing and indexing.'),
    ('TOOL_PICARD_3_1_1', 'picard', '3.1.1', 'UTILITY', 'broadinstitute/picard:3.1.1', 'Duplicate marking and alignment metrics.'),
    ('TOOL_GATK_4_5_0', 'gatk', '4.5.0', 'UTILITY', 'broadinstitute/gatk:4.5.0.0', 'Base recalibration and supporting preprocessing steps.'),
    ('TOOL_MUTECT2_4_5_0', 'mutect2', '4.5.0', 'VARIANT_CALLER', 'broadinstitute/gatk:4.5.0.0', 'Somatic SNV and INDEL caller.'),
    ('TOOL_BCFTOOLS_1_19', 'bcftools', '1.19', 'UTILITY', 'biocontainers/bcftools:1.19', 'VCF normalization and filtering utility.'),
    ('TOOL_VEP_111', 'vep', '111', 'ANNOTATOR', 'ensemblorg/ensembl-vep:release_111', 'Variant annotation tool.'),
    ('TOOL_VARDICT_1_8_3', 'vardict', '1.8.3', 'VARIANT_CALLER', 'biocontainers/vardict-java:1.8.3', 'Supplemental somatic caller for targeted panels.'),
    ('TOOL_STAR_2_7_11A', 'STAR', '2.7.11a', 'RNA_TOOL', 'biocontainers/star:2.7.11a', 'RNA-seq aligner.'),
    ('TOOL_SALMON_1_10_2', 'salmon', '1.10.2', 'RNA_TOOL', 'combinelab/salmon:1.10.2', 'Transcript quantification tool.'),
    ('TOOL_RSEM_1_3_3', 'rsem', '1.3.3', 'RNA_TOOL', 'biocontainers/rsem:1.3.3', 'Gene and isoform expression quantification.'),
    ('TOOL_FASTQC_0_11_9', 'fastqc', '0.11.9', 'QC_TOOL', 'biocontainers/fastqc:0.11.9', 'Read-level sequencing QC.'),
    ('TOOL_MULTIQC_1_18', 'multiqc', '1.18', 'QC_TOOL', 'ewels/multiqc:1.18', 'QC report aggregation.'),
    ('TOOL_QUALIMAP_2_3', 'qualimap', '2.3', 'QC_TOOL', 'biocontainers/qualimap:2.3', 'Coverage and alignment QC.'),
    ('TOOL_MOSDEPTH_0_3_5', 'mosdepth', '0.3.5', 'QC_TOOL', 'quay.io/biocontainers/mosdepth:0.3.5', 'Depth of coverage calculation.'),
    ('TOOL_KALLISTO_0_48_0', 'kallisto', '0.48.0', 'RNA_TOOL', 'quay.io/biocontainers/kallisto:0.48.0', 'Alternative RNA quantification tool.'),
    ('TOOL_HTSLIB_1_19', 'htslib', '1.19', 'UTILITY', 'biocontainers/htslib:1.19', 'Core file manipulation utilities.'),
    ('TOOL_BEDTOOLS_2_31_1', 'bedtools', '2.31.1', 'UTILITY', 'biocontainers/bedtools:2.31.1', 'Interval overlap and target region operations.')
ON CONFLICT (tool_id) DO NOTHING;

INSERT INTO qc_metric_definitions (
    qc_metric_def_id,
    metric_name,
    metric_category,
    description,
    data_type,
    unit,
    lower_bound,
    upper_bound,
    failure_rule_text
)
VALUES
    ('QMD_TOTAL_READS', 'total_reads', 'GENERAL', 'Total sequenced reads observed for the sample.', 'NUMERIC', 'reads', 1000000, NULL, 'Fail if total reads are below 1,000,000.'),
    ('QMD_PCT_Q30', 'pct_q30_bases', 'GENERAL', 'Percentage of bases with quality score >= Q30.', 'NUMERIC', 'percent', 75, 100, 'Warn below 85; fail below 75.'),
    ('QMD_MEAN_COVERAGE', 'mean_target_coverage', 'COVERAGE', 'Mean target coverage across assayed intervals.', 'NUMERIC', 'x', 80, NULL, 'Fail if mean coverage below 80x for DNA assays.'),
    ('QMD_PCT_TARGET_100X', 'pct_target_bases_100x', 'COVERAGE', 'Percent of target bases covered at >=100x.', 'NUMERIC', 'percent', 85, 100, 'Warn below 90; fail below 85.'),
    ('QMD_MAPPING_RATE', 'mapping_rate', 'ALIGNMENT', 'Fraction of reads aligned to reference.', 'NUMERIC', 'fraction', 0.9, 1.0, 'Warn below 0.95; fail below 0.90.'),
    ('QMD_DUP_RATE', 'duplicate_rate', 'ALIGNMENT', 'Fraction of duplicate reads after marking duplicates.', 'NUMERIC', 'fraction', 0, 1.0, 'Warn above 0.35; fail above 0.50.'),
    ('QMD_INSERT_SIZE', 'median_insert_size', 'ALIGNMENT', 'Median insert size for paired-end libraries.', 'NUMERIC', 'bp', 100, NULL, 'Warn for unusually short inserts; fail below 100bp.'),
    ('QMD_CONTAMINATION', 'estimated_contamination', 'VARIANT_QC', 'Estimated sample contamination.', 'NUMERIC', 'fraction', 0, 1.0, 'Warn above 0.03; fail above 0.05.'),
    ('QMD_TUMOR_PURITY_QC', 'tumor_purity_qc', 'VARIANT_QC', 'Tumor purity estimate from QC workflow.', 'NUMERIC', 'fraction', 0.2, 1.0, 'Warn below 0.30; fail below 0.20.'),
    ('QMD_RNA_MAPPING_RATE', 'rna_mapping_rate', 'RNA_QC', 'Fraction of RNA-seq reads aligned or pseudoaligned.', 'NUMERIC', 'fraction', 0.75, 1.0, 'Warn below 0.85; fail below 0.75.'),
    ('QMD_EXONIC_RATE', 'exonic_rate', 'RNA_QC', 'Fraction of RNA reads assigned to exonic regions.', 'NUMERIC', 'fraction', 0.5, 1.0, 'Warn below 0.65; fail below 0.50.'),
    ('QMD_RRNA_RATE', 'rrna_rate', 'RNA_QC', 'Fraction of reads mapping to rRNA.', 'NUMERIC', 'fraction', 0, 1.0, 'Warn above 0.20; fail above 0.35.'),
    ('QMD_SEX_CONCORDANCE', 'sex_concordance', 'GENERAL', 'Expected sex agrees with inferred sex from data.', 'TEXT', NULL, NULL, NULL, 'Fail if inferred and recorded sex are discordant.'),
    ('QMD_QC_SUMMARY', 'qc_summary_flag', 'GENERAL', 'Overall QC summary classification.', 'TEXT', NULL, NULL, NULL, 'PASS, WARN, or FAIL summary emitted by QC aggregation.')
ON CONFLICT (qc_metric_def_id) DO NOTHING;

COMMIT;