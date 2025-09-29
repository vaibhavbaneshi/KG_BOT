import streamlit as st
import re
from utils.logger import logger
from services.text_extractor import extract_text_from_file, extract_text_from_url
from services.kg_service import kg_service
import pandas as pd
kg = kg_service()

from neo4j import GraphDatabase
import time

import streamlit as st
from utils.scheduler import start_scheduler

st.set_page_config(page_title="OmniAI - Knowledge Graph", layout="wide")
st.title("🧠 OmniAI - Knowledge Graph Tool")

# Initialize session state variables
if "input_valid" not in st.session_state:
    st.session_state.input_valid = False
if "final_chunk" not in st.session_state:
    st.session_state.final_chunk = []
if "query_kg_flag" not in st.session_state:
    st.session_state.query_kg_flag = False
if "final_text" not in st.session_state:
    st.session_state.final_text = ""
    # Run the scheduler only once
if "scheduler_started" not in st.session_state:
    start_scheduler()
    st.session_state.scheduler_started = True

# Input Section
input_type = st.radio("Select input type for Knowledge Graph:", ("Text", "URL", "File"))
user_text = ""
file_input = None
url_input = ""
query_kg_flag = False

if input_type == "Text":
    user_text = st.text_area("✍️ Enter text to build KG:")

elif input_type == "URL":
    url_input = st.text_input("🔗 Enter a URL:")

elif input_type == "File":
    file_input = st.file_uploader("📂 Upload your KG file", type=["txt", "csv"])

def is_gibberish(text):
    """Check if the input text is likely gibberish."""
    if len(text.strip().split()) < 5:
        return True
    if re.fullmatch(r"[a-zA-Z\s]{0,10}", text.strip()):
        return True
    if len(set(text.strip())) < 5:
        return True
    return False

if st.button("🔍 Check Neo4j Now"):
    from utils.scheduler import ping_neo4j
    ping_neo4j()

# Button to check input
if st.button("✅ Check Input"):
    try:
        if input_type == "Text":
            final_chunk = [user_text]
        elif input_type == "URL":
            if url_input:
                final_chunk = extract_text_from_url(url_input)
            else:
                final_chunk = []
        elif input_type == "File":
            if file_input:
                final_chunk = extract_text_from_file(file_input)
            else:
                final_chunk = []

        full_text = " ".join(final_chunk) 
        if not full_text or is_gibberish(full_text):
            st.session_state.input_valid = False
            st.warning("⚠️ The input is incomplete or unclear. Please provide more meaningful information.")
        else:
            kg.reset_kg()
            st.session_state.input_valid = True
            st.session_state.final_chunk = final_chunk
            st.session_state.query_kg_flag = False
            st.success("✅ Input is valid and ready to build the KG!")

    except Exception as e:
        st.error(f"❌ Error processing input: {e}")
        st.session_state.input_valid = False

# Build KG Button (enabled only if input is valid)
if st.session_state.input_valid:
    if st.button("🚀 Build Knowledge Graph"):
        try:
            for chunk in st.session_state.final_chunk:
                kg.build_kg(chunk)
            st.session_state.query_kg_flag = True
        except Exception as e:
            st.error(f"❌ KG build failed: {e}")
else:
    st.button("🚀 Build Knowledge Graph", disabled=True)
    st.info("ℹ️ Please check the input first.")

# Query KG
if st.session_state.query_kg_flag:
    user_question = st.text_input("🔍 Ask a question about the Knowledge Graph:")
    if st.button("Query Graph"):
        if not user_question or user_question.strip() == "":
            st.warning("⚠️ Please enter a question.")
        else:
            try:
                result = kg.generate_query(user_question)
            except Exception as e:
                logger.error(f"Query failed: {e}")
                st.error("Error querying Knowledge Graph. Check logs.")