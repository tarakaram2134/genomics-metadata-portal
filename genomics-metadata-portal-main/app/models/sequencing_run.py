from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Date, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class SequencingRun(Base):
    __tablename__ = "sequencing_runs"

    seq_run_id: Mapped[str] = mapped_column(Text, primary_key=True)
    instrument_run_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    platform: Mapped[str] = mapped_column(Text, nullable=False)
    instrument_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    flowcell_id: Mapped[str] = mapped_column(Text, nullable=False)
    run_date: Mapped[object] = mapped_column(Date, nullable=False)
    read_length: Mapped[str | None] = mapped_column(Text, nullable=True)
    paired_end: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    center_name: Mapped[str] = mapped_column(Text, nullable=False)
    run_status: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    sample_run_assignments = relationship("SampleRunAssignment", back_populates="sequencing_run")
    pipeline_runs = relationship("PipelineRun", back_populates="sequencing_run")


class SampleRunAssignment(Base):
    __tablename__ = "sample_run_assignments"

    sample_run_assignment_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id"), nullable=False)
    seq_run_id: Mapped[str] = mapped_column(
        ForeignKey("sequencing_runs.seq_run_id"), nullable=False
    )
    lane_or_partition: Mapped[str | None] = mapped_column(Text, nullable=True)
    library_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    barcode: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    sample = relationship("Sample", back_populates="sample_run_assignments")
    sequencing_run = relationship("SequencingRun", back_populates="sample_run_assignments")
