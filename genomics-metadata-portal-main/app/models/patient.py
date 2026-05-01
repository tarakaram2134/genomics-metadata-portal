from sqlalchemy import TIMESTAMP, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[str] = mapped_column(Text, primary_key=True)
    external_subject_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    disease_type: Mapped[str] = mapped_column(Text, nullable=False)
    condition_group: Mapped[str] = mapped_column(Text, nullable=False)
    sex: Mapped[str | None] = mapped_column(Text, nullable=True)
    age_band: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    samples = relationship("Sample", back_populates="patient")
