from sqlalchemy import TIMESTAMP, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Pipeline(Base):
    __tablename__ = "pipelines"

    pipeline_id: Mapped[str] = mapped_column(Text, primary_key=True)
    pipeline_name: Mapped[str] = mapped_column(Text, nullable=False)
    pipeline_category: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    repo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    maintainer: Mapped[str | None] = mapped_column(Text, nullable=True)
    active_flag: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    pipeline_versions = relationship("PipelineVersion", back_populates="pipeline")
