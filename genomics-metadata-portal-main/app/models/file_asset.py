from sqlalchemy import TIMESTAMP, BigInteger, Boolean, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class FileAsset(Base):
    __tablename__ = "file_assets"

    file_asset_id: Mapped[str] = mapped_column(Text, primary_key=True)
    sample_id: Mapped[str | None] = mapped_column(ForeignKey("samples.sample_id"), nullable=True)
    pipeline_run_id: Mapped[str | None] = mapped_column(
        ForeignKey("pipeline_runs.pipeline_run_id"), nullable=True
    )
    file_role: Mapped[str] = mapped_column(Text, nullable=False)
    file_format: Mapped[str] = mapped_column(Text, nullable=False)
    path_uri: Mapped[str] = mapped_column(Text, nullable=False)
    checksum: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    source_system: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_current: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    sample = relationship("Sample", back_populates="file_assets")
    pipeline_run = relationship("PipelineRun", back_populates="file_assets")
    qc_results = relationship("QcResult", back_populates="source_file_asset")
    variant_summaries = relationship("VariantSummary", back_populates="source_file_asset")
