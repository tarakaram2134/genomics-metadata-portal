from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import streamlit as st

from app.db import SessionLocal
from app.repositories.provenance_repository import ProvenanceRepository

st.title("Provenance Trace")
st.caption(
    "Trace how a sample moved from sequencing through pipeline execution, "
    "references/tools, files, QC results, and variant summaries."
)


def load_sample_ids() -> list[str]:
    with SessionLocal() as session:
        repo = ProvenanceRepository(session)
        return repo.list_sample_ids()


def load_trace(sample_id: str):
    with SessionLocal() as session:
        repo = ProvenanceRepository(session)
        return repo.get_sample_trace(sample_id)


sample_ids = load_sample_ids()

if not sample_ids:
    st.warning("No samples available.")
    st.stop()

selected_sample = st.selectbox("Select Sample", sample_ids)
trace = load_trace(selected_sample)

detail = trace["detail"]
provenance = trace["provenance"]
file_assets = trace["file_assets"]
qc_results = trace["qc_results"]
variants = trace["variants"]

if detail is None:
    st.error(f"Sample {selected_sample} not found.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Sample ID", detail["sample_id"])
col2.metric("Subject", detail["external_subject_id"])
col3.metric("Disease", detail["disease_type"])
col4.metric("Assay", detail["assay_type"])

st.markdown("## Trace Overview")
st.json(
    {
        "sample_id": detail["sample_id"],
        "patient_id": detail["patient_id"],
        "external_subject_id": detail["external_subject_id"],
        "disease_type": detail["disease_type"],
        "sample_type": detail["sample_type"],
        "assay_type": detail["assay_type"],
        "received_date": str(detail["received_date"]),
    },
    expanded=False,
)

st.markdown("## Sequencing Lineage")
seq_df = pd.DataFrame(provenance["sequencing"])
if seq_df.empty:
    st.info("No sequencing lineage available.")
else:
    st.dataframe(seq_df, use_container_width=True, hide_index=True)

st.markdown("## Pipeline Execution Trace")
pipeline_runs = provenance["pipeline_runs"]
if not pipeline_runs:
    st.info("No pipeline runs available.")
else:
    for idx, run in enumerate(reversed(pipeline_runs), start=1):
        st.markdown(
            f"### Step {idx}: {run['pipeline_id']} / {run['pipeline_version_id']} "
            f"({run['run_status']})"
        )
        left, right = st.columns(2)

        with left:
            st.write(f"**Run ID:** {run['pipeline_run_id']}")
            st.write(f"**Started:** {run['run_started_at']}")
            st.write(f"**Finished:** {run['run_finished_at']}")
            st.write(f"**Triggered By:** {run['triggered_by']}")
            st.write(f"**Execution Environment:** {run['execution_environment']}")

        with right:
            st.write(f"**Workflow UUID:** {run['workflow_run_uuid']}")
            st.write(f"**Failure Reason:** {run['failure_reason'] or 'N/A'}")
            st.write(f"**Log Path:** `{run['log_path']}`")
            st.write(f"**Work Dir:** `{run['work_dir_path']}`")

        sub1, sub2 = st.columns(2)
        with sub1:
            st.markdown("**References**")
            ref_df = pd.DataFrame(run["references"])
            if ref_df.empty:
                st.info("No references linked.")
            else:
                st.dataframe(ref_df, use_container_width=True, hide_index=True)

        with sub2:
            st.markdown("**Tools**")
            tool_df = pd.DataFrame(run["tools"])
            if tool_df.empty:
                st.info("No tools linked.")
            else:
                st.dataframe(tool_df, use_container_width=True, hide_index=True)

        run_files = [row for row in file_assets if row["pipeline_run_id"] == run["pipeline_run_id"]]
        run_qc = [row for row in qc_results if row["pipeline_run_id"] == run["pipeline_run_id"]]
        run_vars = [row for row in variants if row["pipeline_run_id"] == run["pipeline_run_id"]]

        sub3, sub4, sub5 = st.columns(3)

        with sub3:
            st.markdown("**Files Generated**")
            if run_files:
                st.dataframe(pd.DataFrame(run_files), use_container_width=True, hide_index=True)
            else:
                st.info("No files linked.")

        with sub4:
            st.markdown("**QC Results**")
            if run_qc:
                st.dataframe(pd.DataFrame(run_qc), use_container_width=True, hide_index=True)
            else:
                st.info("No QC results linked.")

        with sub5:
            st.markdown("**Variant Summaries**")
            if run_vars:
                st.dataframe(pd.DataFrame(run_vars), use_container_width=True, hide_index=True)
            else:
                st.info("No variants linked.")

        st.divider()

st.markdown("## All Sample File Assets")
all_files_df = pd.DataFrame(file_assets)
if all_files_df.empty:
    st.info("No file assets available.")
else:
    st.dataframe(all_files_df, use_container_width=True, hide_index=True)