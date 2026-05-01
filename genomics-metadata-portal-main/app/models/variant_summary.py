from sqlalchemy import TIMESTAMP, BigInteger, Boolean, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class VariantSummary(Base):
    __tablename__ = "variant_summary"

    variant_summary_id: Mapped[str] = mapped_column(Text, primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id"), nullable=False)
    pipeline_run_id: Mapped[str] = mapped_column(
        ForeignKey("pipeline_runs.pipeline_run_id"), nullable=False
    )
    gene_symbol: Mapped[str] = mapped_column(Text, nullable=False)
    variant_class: Mapped[str] = mapped_column(Text, nullable=False)
    protein_change: Mapped[str | None] = mapped_column(Text, nullable=True)
    chromosome: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ref_allele: Mapped[str | None] = mapped_column(Text, nullable=True)
    alt_allele: Mapped[str | None] = mapped_column(Text, nullable=True)
    tumor_vaf: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    clinical_significance: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_driver: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    reported_flag: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    source_file_asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("file_assets.file_asset_id"), nullable=True
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    sample = relationship("Sample", back_populates="variant_summaries")
    pipeline_run = relationship("PipelineRun", back_populates="variant_summaries")
    source_file_asset = relationship("FileAsset", back_populates="variant_summaries")
