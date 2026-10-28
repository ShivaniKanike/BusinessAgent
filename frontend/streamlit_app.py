"""
streamlit_app.py - Streamlit Frontend (Simple Version)
A basic Streamlit UI to ask questions about sales data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from ai_engine.query_engine import execute_query
from database.db_setup import create_database, DB_PATH

# Setup database if not exists
if not os.path.exists(DB_PATH):
    create_database()

# --- Page Config ---
st.set_page_config(page_title="Mini BI Assistant", page_icon="📊", layout="centered")

st.title("📊 Mini BI Assistant")
st.caption("Ask questions about sales data in plain English")

# --- Question Input ---
question = st.text_input("Enter your question:", placeholder="e.g. What is the total revenue?")

# --- Quick Buttons ---
st.markdown("**Try these:**")
col1, col2, col3, col4, col5 = st.columns(5)
if col1.button("Total Revenue"):
    question = "What is the total revenue?"
if col2.button("Top Product"):
    question = "Which product generated the highest revenue?"
if col3.button("Monthly Trend"):
    question = "What is the monthly revenue trend?"
if col4.button("Top Region"):
    question = "Which region generated the highest sales?"
if col5.button("Table Columns"):
    question = "How are the tables columns?"

# --- Process Question ---
if question:
    with st.spinner("Thinking..."):
        result = execute_query(question)

    if result["error"]:
        st.error(f"❌ {result['error']}")
    else:
        # Show answer
        st.success(f"✅ {result['answer']}")

        # Show data as table
        if result["data"]:
            st.subheader("Supporting Data")
            df = pd.DataFrame(result["data"])
            st.dataframe(df, use_container_width=True)

        # Show SQL query
        if result["sql_query"]:
            with st.expander("View SQL Query"):
                st.code(result["sql_query"], language="sql")

        # Show method used
        st.caption(f"Method: {result['method']}")

# --- Sidebar Info ---
st.sidebar.header("About")
st.sidebar.info(
    "This is a simple BI assistant that answers "
    "questions about sales data using SQL queries. "
    "Currently uses keyword matching. "
    "LLM integration via LangChain is planned."
)
st.sidebar.header("Supported Questions")
st.sidebar.markdown("""
- What is the total revenue?
- Which product generated the highest revenue?
- What is the monthly revenue trend?
- Which region generated the highest sales?
""")

# TODO: Add charts for monthly trend visualization
# TODO: Add file upload to use custom CSV data

