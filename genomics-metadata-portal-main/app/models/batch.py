from sqlalchemy import TIMESTAMP, Date, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Batch(Base):
    __tablename__ = "batches"

    batch_id: Mapped[str] = mapped_column(Text, primary_key=True)
    batch_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    project_code: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_by: Mapped[str] = mapped_column(Text, nullable=False)
    submission_date: Mapped[object] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    samples = relationship("Sample", back_populates="batch")
