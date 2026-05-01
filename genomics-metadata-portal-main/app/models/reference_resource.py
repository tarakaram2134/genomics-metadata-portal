from sqlalchemy import TIMESTAMP, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ReferenceResource(Base):
    __tablename__ = "reference_resources"

    reference_id: Mapped[str] = mapped_column(Text, primary_key=True)
    reference_name: Mapped[str] = mapped_column(Text, nullable=False)
    reference_type: Mapped[str] = mapped_column(Text, nullable=False)
    reference_version: Mapped[str] = mapped_column(Text, nullable=False)
    source_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    pipeline_run_references = relationship(
        "PipelineRunReference", back_populates="reference_resource"
    )
