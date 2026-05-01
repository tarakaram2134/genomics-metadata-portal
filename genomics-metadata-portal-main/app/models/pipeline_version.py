from sqlalchemy import TIMESTAMP, Boolean, Date, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class PipelineVersion(Base):
    __tablename__ = "pipeline_versions"

    pipeline_version_id: Mapped[str] = mapped_column(Text, primary_key=True)
    pipeline_id: Mapped[str] = mapped_column(ForeignKey("pipelines.pipeline_id"), nullable=False)
    version_label: Mapped[str] = mapped_column(Text, nullable=False)
    container_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    container_tag: Mapped[str | None] = mapped_column(Text, nullable=True)
    workflow_definition_version: Mapped[str | None] = mapped_column(Text, nullable=True)
    release_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    pipeline = relationship("Pipeline", back_populates="pipeline_versions")
    pipeline_runs = relationship("PipelineRun", back_populates="pipeline_version")
