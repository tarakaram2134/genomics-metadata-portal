from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import streamlit as st

from app.db import SessionLocal
from app.repositories.variant_repository import VariantRepository

st.title("Variant Search")
st.caption("Search variants across samples by gene and clinical significance.")

def load_filter_options():
    with SessionLocal() as session:
        repo = VariantRepository(session)
        return repo.list_genes(), repo.list_clinical_significance()

def load_variants(filters):
    with SessionLocal() as session:
        repo = VariantRepository(session)
        return repo.search_variants(**filters)

genes, clinical_values = load_filter_options()

with st.sidebar:
    st.header("Filters")

    gene = st.selectbox("Gene", ["All"] + genes)
    clinical = st.selectbox("Clinical Significance", ["All"] + clinical_values)
    reported_only = st.checkbox("Reported only", value=False)
    limit = st.slider("Max rows", 50, 500, 200, step=50)

filters = {
    "gene_symbol": None if gene == "All" else gene,
    "clinical_significance": None if clinical == "All" else clinical,
    "reported_only": reported_only,
    "limit": limit,
}

variants = load_variants(filters)
df = pd.DataFrame(variants)

st.subheader("Variant Results")

if df.empty:
    st.warning("No variants found.")
    st.stop()

st.dataframe(df, use_container_width=True)