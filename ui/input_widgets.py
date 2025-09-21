import streamlit as st

def input_section():
    """
    Input section: Text, File Upload, or URL
    """
    text_input = st.text_area("✍️ Enter text here:")
    file_input = st.file_uploader("📂 Upload file", type=["txt", "pdf"])
    url_input = st.text_input("🌐 Enter website URL:")

    return text_input, file_input, url_input