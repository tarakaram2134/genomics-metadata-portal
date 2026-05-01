from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Patient, Sample
from app.repositories.sample_repository import SampleRepository

st.set_page_config(page_title="Sample Explorer", layout="wide")


@st.cache_data(ttl=60)
def load_filter_options() -> dict[str, list[str]]:
    with SessionLocal() as session:
        disease_types = sorted(
            value
            for value in session.scalars(
                select(Patient.disease_type).distinct().order_by(Patient.disease_type)
            ).all()
            if value
        )
        assay_types = sorted(
            value
            for value in session.scalars(
                select(Sample.assay_type).distinct().order_by(Sample.assay_type)
            ).all()
            if value
        )
        sample_statuses = sorted(
            value
            for value in session.scalars(
                select(Sample.sample_status).distinct().order_by(Sample.sample_status)
            ).all()
            if value
        )
        tumor_normal_statuses = sorted(
            value
            for value in session.scalars(
                select(Sample.tumor_normal_status)
                .distinct()
                .order_by(Sample.tumor_normal_status)
            ).all()
            if value
        )

    return {
        "disease_types": disease_types,
        "assay_types": assay_types,
        "sample_statuses": sample_statuses,
        "tumor_normal_statuses": tumor_normal_statuses,
    }


def _safe_json_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, default=str)


def _format_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    formatted = df.copy()
    for column in formatted.columns:
        if pd.api.types.is_datetime64_any_dtype(formatted[column]):
            formatted[column] = formatted[column].astype(str)
    return formatted


def load_sample_listing(
    *,
    disease_type: str | None,
    assay_type: str | None,
    sample_status: str | None,
    tumor_normal_status: str | None,
    search_text: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        repo = SampleRepository(session)
        return repo.list_samples(
            disease_type=disease_type,
            assay_type=assay_type,
            sample_status=sample_status,
            tumor_normal_status=tumor_normal_status,
            search_text=search_text,
            limit=limit,
            offset=0,
        )


def load_sample_payload(sample_id: str) -> dict[str, Any]:
    with SessionLocal() as session:
        repo = SampleRepository(session)
        return {
            "detail": repo.get_sample_detail(sample_id),
            "provenance": repo.get_sample_provenance(sample_id),
            "qc_results": repo.get_sample_qc_results(sample_id),
            "variants": repo.get_sample_variants(sample_id),
        }


st.title("Sample Explorer")
st.caption(
    "Explore sample metadata, sequencing lineage, pipeline provenance, QC results, "
    "and variant summaries from the Genomics Metadata, Provenance & Analysis Portal."
)

filter_options = load_filter_options()

with st.sidebar:
    st.header("Filters")

    disease_type = st.selectbox(
        "Disease Type",
        options=["All"] + filter_options["disease_types"],
        index=0,
    )
    assay_type = st.selectbox(
        "Assay Type",
        options=["All"] + filter_options["assay_types"],
        index=0,
    )
    sample_status = st.selectbox(
        "Sample Status",
        options=["All"] + filter_options["sample_statuses"],
        index=0,
    )
    tumor_normal_status = st.selectbox(
        "Tumor/Normal Status",
        options=["All"] + filter_options["tumor_normal_statuses"],
        index=0,
    )
    search_text = st.text_input(
        "Search",
        placeholder="sample id, subject id, disease, specimen site...",
    )
    row_limit = st.slider("Max rows", min_value=10, max_value=200, value=50, step=10)

samples = load_sample_listing(
    disease_type=None if disease_type == "All" else disease_type,
    assay_type=None if assay_type == "All" else assay_type,
    sample_status=None if sample_status == "All" else sample_status,
    tumor_normal_status=None if tumor_normal_status == "All" else tumor_normal_status,
    search_text=search_text.strip() or None,
    limit=row_limit,
)

samples_df = pd.DataFrame(samples)

st.subheader("Sample List")
if samples_df.empty:
    st.warning("No samples matched the current filters.")
    st.stop()

display_df = _format_datetime_columns(samples_df)
st.dataframe(display_df, use_container_width=True, hide_index=True)

sample_ids = samples_df["sample_id"].tolist()
default_index = 0
if "selected_sample_id" in st.session_state and st.session_state["selected_sample_id"] in sample_ids:
    default_index = sample_ids.index(st.session_state["selected_sample_id"])

selected_sample_id = st.selectbox(
    "Select Sample",
    options=sample_ids,
    index=default_index,
)
st.session_state["selected_sample_id"] = selected_sample_id

payload = load_sample_payload(selected_sample_id)
detail = payload["detail"]
provenance = payload["provenance"]
qc_results = payload["qc_results"]
variants = payload["variants"]

if detail is None:
    st.error(f"Sample {selected_sample_id} was not found.")
    st.stop()

overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
overview_col1.metric("Sample ID", detail["sample_id"])
overview_col2.metric("Subject", detail["external_subject_id"])
overview_col3.metric("Disease", detail["disease_type"])
overview_col4.metric("Assay", detail["assay_type"])

tab_overview, tab_provenance, tab_qc, tab_variants = st.tabs(
    ["Overview", "Provenance", "QC Results", "Variant Summaries"]
)

with tab_overview:
    left, right = st.columns([1, 1])

    with left:
        st.markdown("### Sample Metadata")
        st.json(
            {
                "sample_id": detail["sample_id"],
                "patient_id": detail["patient_id"],
                "external_subject_id": detail["external_subject_id"],
                "disease_type": detail["disease_type"],
                "condition_group": detail["condition_group"],
                "sex": detail["sex"],
                "age_band": detail["age_band"],
                "batch_id": detail["batch_id"],
                "batch_name": detail["batch_name"],
                "sample_type": detail["sample_type"],
                "assay_type": detail["assay_type"],
                "collection_date": str(detail["collection_date"]),
                "received_date": str(detail["received_date"]),
                "specimen_site": detail["specimen_site"],
                "condition_label": detail["condition_label"],
                "sample_status": detail["sample_status"],
                "tumor_normal_status": detail["tumor_normal_status"],
                "library_prep_kit": detail["library_prep_kit"],
                "notes": detail["notes"],
                "created_at": str(detail["created_at"]),
            },
            expanded=False,
        )

    with right:
        st.markdown("### Analysis Summary")
        if detail["analysis_summary"] is None:
            st.info("No analysis summary available for this sample.")
        else:
            analysis_summary = detail["analysis_summary"]
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            metric_col1.metric("TMB Score", analysis_summary["tmb_score"])
            metric_col2.metric("MSI Status", analysis_summary["msi_status"])
            metric_col3.metric("Purity", analysis_summary["purity_estimate"])
            metric_col4.metric("Ploidy", analysis_summary["ploidy_estimate"])

            st.write(f"**Expression Subtype:** {analysis_summary['expression_subtype'] or 'N/A'}")
            st.write(f"**Last Updated:** {analysis_summary['last_updated_at']}")
            st.markdown("**Analysis Summary JSON**")
            st.code(_safe_json_text(analysis_summary["analysis_summary_json"]), language="json")

with tab_provenance:
    st.markdown("### Sequencing Lineage")
    sequencing_df = pd.DataFrame(provenance["sequencing"])
    if sequencing_df.empty:
        st.info("No sequencing lineage found for this sample.")
    else:
        st.dataframe(
            _format_datetime_columns(sequencing_df),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### Pipeline Provenance")
    pipeline_runs = provenance["pipeline_runs"]
    if not pipeline_runs:
        st.info("No pipeline runs found for this sample.")
    else:
        for run in pipeline_runs:
            title = (
                f"{run['pipeline_run_id']} — {run['pipeline_id']} / "
                f"{run['pipeline_version_id']} ({run['run_status']})"
            )
            with st.expander(title, expanded=False):
                meta_col1, meta_col2 = st.columns([1, 1])

                with meta_col1:
                    st.write(f"**Version Label:** {run['version_label']}")
                    st.write(f"**Started:** {run['run_started_at']}")
                    st.write(f"**Finished:** {run['run_finished_at']}")
                    st.write(f"**Triggered By:** {run['triggered_by']}")
                    st.write(f"**Execution Environment:** {run['execution_environment']}")
                    st.write(f"**Failure Reason:** {run['failure_reason'] or 'N/A'}")

                with meta_col2:
                    st.write(f"**Workflow UUID:** {run['workflow_run_uuid']}")
                    st.write(f"**Log Path:** `{run['log_path']}`")
                    st.write(f"**Work Dir:** `{run['work_dir_path']}`")

                st.markdown("**Parameter Set**")
                st.code(_safe_json_text(run["parameter_set_json"]), language="json")

                ref_df = pd.DataFrame(run["references"])
                tool_df = pd.DataFrame(run["tools"])

                sub_col1, sub_col2 = st.columns(2)

                with sub_col1:
                    st.markdown("**References Used**")
                    if ref_df.empty:
                        st.info("No references linked.")
                    else:
                        st.dataframe(
                            _format_datetime_columns(ref_df),
                            use_container_width=True,
                            hide_index=True,
                        )

                with sub_col2:
                    st.markdown("**Tools Used**")
                    if tool_df.empty:
                        st.info("No tools linked.")
                    else:
                        st.dataframe(
                            _format_datetime_columns(tool_df),
                            use_container_width=True,
                            hide_index=True,
                        )

with tab_qc:
    st.markdown("### QC Results")
    qc_df = pd.DataFrame(qc_results)
    if qc_df.empty:
        st.info("No QC results found for this sample.")
    else:
        qc_df = _format_datetime_columns(qc_df)
        st.dataframe(qc_df, use_container_width=True, hide_index=True)

with tab_variants:
    st.markdown("### Variant Summaries")
    variant_df = pd.DataFrame(variants)
    if variant_df.empty:
        st.info("No variant summaries found for this sample.")
    else:
        variant_df = _format_datetime_columns(variant_df)
        st.dataframe(variant_df, use_container_width=True, hide_index=True)