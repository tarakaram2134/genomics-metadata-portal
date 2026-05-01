from sqlalchemy import TIMESTAMP, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ToolRegistry(Base):
    __tablename__ = "tool_registry"

    tool_id: Mapped[str] = mapped_column(Text, primary_key=True)
    tool_name: Mapped[str] = mapped_column(Text, nullable=False)
    tool_version: Mapped[str] = mapped_column(Text, nullable=False)
    tool_category: Mapped[str] = mapped_column(Text, nullable=False)
    container_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    pipeline_run_tools = relationship("PipelineRunTool", back_populates="tool")
