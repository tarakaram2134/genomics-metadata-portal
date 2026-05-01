from sqlalchemy import JSON, TIMESTAMP, BigInteger, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    pipeline_run_id: Mapped[str] = mapped_column(Text, primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id"), nullable=False)
    seq_run_id: Mapped[str | None] = mapped_column(
        ForeignKey("sequencing_runs.seq_run_id"), nullable=True
    )
    pipeline_version_id: Mapped[str] = mapped_column(
        ForeignKey("pipeline_versions.pipeline_version_id"), nullable=False
    )
    run_started_at: Mapped[object] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    run_finished_at: Mapped[object | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    run_status: Mapped[str] = mapped_column(Text, nullable=False)
    parameter_set_json: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict, server_default="{}"
    )
    execution_environment: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    workflow_run_uuid: Mapped[str | None] = mapped_column(Text, nullable=True)
    log_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    work_dir_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    sample = relationship("Sample", back_populates="pipeline_runs")
    sequencing_run = relationship("SequencingRun", back_populates="pipeline_runs")
    pipeline_version = relationship("PipelineVersion", back_populates="pipeline_runs")
    pipeline_run_references = relationship("PipelineRunReference", back_populates="pipeline_run")
    pipeline_run_tools = relationship("PipelineRunTool", back_populates="pipeline_run")
    file_assets = relationship("FileAsset", back_populates="pipeline_run")
    qc_results = relationship("QcResult", back_populates="pipeline_run")
    variant_summaries = relationship("VariantSummary", back_populates="pipeline_run")


class PipelineRunReference(Base):
    __tablename__ = "pipeline_run_references"

    pipeline_run_reference_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    pipeline_run_id: Mapped[str] = mapped_column(
        ForeignKey("pipeline_runs.pipeline_run_id"), nullable=False
    )
    reference_id: Mapped[str] = mapped_column(
        ForeignKey("reference_resources.reference_id"), nullable=False
    )
    usage_role: Mapped[str] = mapped_column(Text, nullable=False)
    execution_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    step_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    pipeline_run = relationship("PipelineRun", back_populates="pipeline_run_references")
    reference_resource = relationship("ReferenceResource", back_populates="pipeline_run_references")


class PipelineRunTool(Base):
    __tablename__ = "pipeline_run_tools"

    pipeline_run_tool_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    pipeline_run_id: Mapped[str] = mapped_column(
        ForeignKey("pipeline_runs.pipeline_run_id"), nullable=False
    )
    tool_id: Mapped[str] = mapped_column(ForeignKey("tool_registry.tool_id"), nullable=False)
    usage_role: Mapped[str] = mapped_column(Text, nullable=False)
    execution_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    step_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    pipeline_run = relationship("PipelineRun", back_populates="pipeline_run_tools")
    tool = relationship("ToolRegistry", back_populates="pipeline_run_tools")