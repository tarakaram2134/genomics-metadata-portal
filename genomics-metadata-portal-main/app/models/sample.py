from sqlalchemy import TIMESTAMP, Date, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Sample(Base):
    __tablename__ = "samples"

    sample_id: Mapped[str] = mapped_column(Text, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)
    batch_id: Mapped[str | None] = mapped_column(ForeignKey("batches.batch_id"), nullable=True)
    sample_type: Mapped[str] = mapped_column(Text, nullable=False)
    assay_type: Mapped[str] = mapped_column(Text, nullable=False)
    collection_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    received_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    specimen_site: Mapped[str | None] = mapped_column(Text, nullable=True)
    condition_label: Mapped[str] = mapped_column(Text, nullable=False)
    sample_status: Mapped[str] = mapped_column(Text, nullable=False)
    tumor_normal_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    library_prep_kit: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    patient = relationship("Patient", back_populates="samples")
    batch = relationship("Batch", back_populates="samples")
    sample_run_assignments = relationship("SampleRunAssignment", back_populates="sample")
    pipeline_runs = relationship("PipelineRun", back_populates="sample")
    file_assets = relationship("FileAsset", back_populates="sample")
    qc_results = relationship("QcResult", back_populates="sample")
    variant_summaries = relationship("VariantSummary", back_populates="sample")
    sample_analysis_summary = relationship(
        "SampleAnalysisSummary", back_populates="sample", uselist=False
    )
