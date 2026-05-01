from sqlalchemy import TIMESTAMP, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class QcMetricDefinition(Base):
    __tablename__ = "qc_metric_definitions"

    qc_metric_def_id: Mapped[str] = mapped_column(Text, primary_key=True)
    metric_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    metric_category: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_type: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    lower_bound: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    upper_bound: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    failure_rule_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    qc_results = relationship("QcResult", back_populates="qc_metric_definition")
