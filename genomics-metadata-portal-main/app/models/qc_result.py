from sqlalchemy import TIMESTAMP, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class QcResult(Base):
    __tablename__ = "qc_results"

    qc_result_id: Mapped[str] = mapped_column(Text, primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id"), nullable=False)
    pipeline_run_id: Mapped[str] = mapped_column(
        ForeignKey("pipeline_runs.pipeline_run_id"), nullable=False
    )
    qc_metric_def_id: Mapped[str] = mapped_column(
        ForeignKey("qc_metric_definitions.qc_metric_def_id"), nullable=False
    )
    metric_value_numeric: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    metric_value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    qc_status: Mapped[str] = mapped_column(Text, nullable=False)
    measured_at: Mapped[object] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    source_file_asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("file_assets.file_asset_id"), nullable=True
    )

    sample = relationship("Sample", back_populates="qc_results")
    pipeline_run = relationship("PipelineRun", back_populates="qc_results")
    qc_metric_definition = relationship("QcMetricDefinition", back_populates="qc_results")
    source_file_asset = relationship("FileAsset", back_populates="qc_results")
