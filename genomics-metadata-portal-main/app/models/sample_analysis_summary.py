from sqlalchemy import JSON, TIMESTAMP, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class SampleAnalysisSummary(Base):
    __tablename__ = "sample_analysis_summary"

    sample_analysis_summary_id: Mapped[str] = mapped_column(Text, primary_key=True)
    sample_id: Mapped[str] = mapped_column(
        ForeignKey("samples.sample_id"), nullable=False, unique=True
    )
    tmb_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    msi_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    purity_estimate: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    ploidy_estimate: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    expression_subtype: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis_summary_json: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict, server_default="{}"
    )
    last_updated_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    sample = relationship("Sample", back_populates="sample_analysis_summary")
