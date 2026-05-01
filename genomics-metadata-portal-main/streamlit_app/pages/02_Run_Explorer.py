from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import pandas as pd
import streamlit as st

from app.db import SessionLocal
from app.repositories.run_repository import RunRepository

st.title("Run Explorer")

def load_runs(filters):
    with SessionLocal() as session:
        repo = RunRepository(session)
        return repo.list_runs(**filters)

def load_run_detail(run_id):
    with SessionLocal() as session:
        repo = RunRepository(session)
        return repo.get_run_detail(run_id), repo.get_run_provenance(run_id)

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    run_status = st.selectbox("Run Status", ["All", "SUCCESS", "FAILED", "PARTIAL"])
    search_text = st.text_input("Search")

filters = {
    "run_status": None if run_status == "All" else run_status,
    "pipeline_id": None,
    "search_text": search_text or None,
    "limit": 100,
}

runs = load_runs(filters)
df = pd.DataFrame(runs)

st.subheader("Pipeline Runs")

if df.empty:
    st.warning("No runs found.")
    st.stop()

st.dataframe(df, use_container_width=True)

run_ids = df["pipeline_run_id"].tolist()
selected_run = st.selectbox("Select Run", run_ids)

detail, provenance = load_run_detail(selected_run)

st.markdown("## Run Detail")

col1, col2, col3 = st.columns(3)
col1.metric("Run ID", detail["pipeline_run_id"])
col2.metric("Sample", detail["sample_id"])
col3.metric("Status", detail["run_status"])

st.markdown("### Metadata")
st.json(detail)

st.markdown("### Parameter Set")
st.code(json.dumps(detail["parameter_set_json"], indent=2), language="json")

st.markdown("## Provenance")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### References")
    st.dataframe(pd.DataFrame(provenance["references"]), use_container_width=True)

with col2:
    st.markdown("### Tools")
    st.dataframe(pd.DataFrame(provenance["tools"]), use_container_width=True)