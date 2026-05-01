from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import streamlit as st

from app.db import SessionLocal
from app.repositories.qc_repository import QcRepository

st.title("QC Dashboard")
st.caption("Monitor QC result distribution and inspect recent QC measurements.")

def load_filter_options() -> tuple[list[str], list[str]]:
    with SessionLocal() as session:
        repo = QcRepository(session)
        return repo.list_assay_types(), repo.list_metric_names()

def load_qc_payload(
    *,
    assay_type: str | None,
    qc_status: str | None,
    metric_name: str | None,
    limit: int,
):
    with SessionLocal() as session:
        repo = QcRepository(session)
        return {
            "status_summary": repo.get_qc_status_summary(assay_type=assay_type),
            "recent_results": repo.get_recent_qc_results(
                assay_type=assay_type,
                qc_status=qc_status,
                metric_name=metric_name,
                limit=limit,
            ),
        }

assay_types, metric_names = load_filter_options()

with st.sidebar:
    st.header("Filters")
    assay_type = st.selectbox("Assay Type", ["All"] + assay_types)
    qc_status = st.selectbox("QC Status", ["All", "PASS", "WARN", "FAIL"])
    metric_name = st.selectbox("Metric Name", ["All"] + metric_names)
    row_limit = st.slider("Max rows", min_value=25, max_value=500, value=150, step=25)

payload = load_qc_payload(
    assay_type=None if assay_type == "All" else assay_type,
    qc_status=None if qc_status == "All" else qc_status,
    metric_name=None if metric_name == "All" else metric_name,
    limit=row_limit,
)

status_df = pd.DataFrame(payload["status_summary"])
results_df = pd.DataFrame(payload["recent_results"])

metric_col1, metric_col2, metric_col3 = st.columns(3)

status_counts = {
    row["qc_status"]: row["result_count"]
    for row in payload["status_summary"]
}

metric_col1.metric("PASS", status_counts.get("PASS", 0))
metric_col2.metric("WARN", status_counts.get("WARN", 0))
metric_col3.metric("FAIL", status_counts.get("FAIL", 0))

st.markdown("## QC Status Distribution")
if status_df.empty:
    st.info("No QC status summary available.")
else:
    st.bar_chart(status_df.set_index("qc_status"))

st.markdown("## Recent QC Results")
if results_df.empty:
    st.info("No QC results matched the current filters.")
else:
    st.dataframe(results_df, use_container_width=True, hide_index=True)