from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import streamlit as st

from app.db import SessionLocal
from app.repositories.data_dictionary_repository import DataDictionaryRepository

st.title("Data Dictionary")
st.caption(
    "Interactive schema reference for the Genomics Metadata, Provenance & Analysis Portal."
)


def load_tables():
    with SessionLocal() as session:
        repo = DataDictionaryRepository(session)
        return repo.list_tables()


def load_table_dictionary(table_name: str):
    with SessionLocal() as session:
        repo = DataDictionaryRepository(session)
        return repo.get_table_dictionary(table_name)


tables = load_tables()
tables_df = pd.DataFrame(tables)

if tables_df.empty:
    st.warning("No database tables found.")
    st.stop()

st.markdown("## Table Inventory")
st.dataframe(tables_df, use_container_width=True, hide_index=True)

table_names = tables_df["table_name"].tolist()
selected_table = st.selectbox("Select Table", table_names)

table_dict = load_table_dictionary(selected_table)

col1, col2, col3 = st.columns(3)
col1.metric("Columns", len(table_dict["columns"]))
col2.metric("Foreign Keys", len(table_dict["foreign_keys"]))
col3.metric("Indexes", len(table_dict["indexes"]))

st.markdown("## Table Description")
st.write(table_dict["description"] or "No description available.")

st.markdown("## Columns")
columns_df = pd.DataFrame(table_dict["columns"])

if not columns_df.empty:
    columns_display = columns_df.copy()
    columns_display["foreign_keys"] = columns_display["foreign_keys"].apply(
        lambda x: ", ".join(
            f"{item['referred_table']}.{item['referred_column']}" for item in x
        )
        if x
        else ""
    )
    st.dataframe(columns_display, use_container_width=True, hide_index=True)
else:
    st.info("No columns found.")

st.markdown("## Primary Key")
if table_dict["primary_key"]:
    st.code(", ".join(table_dict["primary_key"]))
else:
    st.info("No primary key metadata found.")

st.markdown("## Foreign Key Constraints")
if table_dict["foreign_keys"]:
    st.dataframe(pd.DataFrame(table_dict["foreign_keys"]), use_container_width=True, hide_index=True)
else:
    st.info("No foreign keys found.")

st.markdown("## Indexes")
if table_dict["indexes"]:
    st.dataframe(pd.DataFrame(table_dict["indexes"]), use_container_width=True, hide_index=True)
else:
    st.info("No indexes found.")