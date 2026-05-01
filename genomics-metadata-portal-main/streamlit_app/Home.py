from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

st.set_page_config(
    page_title="Genomics Metadata, Provenance & Analysis Portal",
    layout="wide",
)

st.title("Genomics Metadata, Provenance & Analysis Portal")
st.caption(
    "Bioinformatics metadata, provenance, QC, and variant exploration system."
)

st.markdown(
    """
Use the pages in the sidebar to explore:
- Sample Explorer
- future run, QC, variant, and provenance views
"""
)