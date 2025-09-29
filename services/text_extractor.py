import logging
import requests
import logging
from bs4 import BeautifulSoup
import certifi
import streamlit as st
import pandas as pd
import certifi

logger = logging.getLogger(__name__)

def chunk_text(text, max_length=10000):
    """Split the text into chunks of max_length, without cutting words."""
    chunks = []
    while len(text) > max_length:
        split_point = text.rfind(" ", 0, max_length)
        if split_point == -1:
            split_point = max_length
        chunks.append(text[:split_point].strip())
        text = text[split_point:].strip()
    if text:
        chunks.append(text.strip())
    return chunks

def extract_text_from_file(uploaded_file, max_length=3000):
    """
    Extract text from a file and return as a list of chunks.
    """
    if uploaded_file is None:
        return []

    try:
        content = uploaded_file.read().decode("utf-8")
        return chunk_text(content, max_length)
    except Exception as e:
        st.error(f"❌ Failed to extract text from file {uploaded_file.name}: {e}")
        return []

def extract_text_from_url(url, max_length=3000):
    """
    Extract text from a URL (HTML or CSV) and return as a list of chunks.
    - If HTML: grab text from <p> tags
    - If CSV: read via pandas and flatten into text
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, verify=certifi.where())

        if r.status_code != 200:
            st.warning(f"⚠️ Failed to fetch URL: {url}\nResponse: {r.status_code}")
            return []

        content_type = r.headers.get("Content-Type", "")

        text = ""

        if "text/html" in content_type:  # Handle HTML
            soup = BeautifulSoup(r.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)

        elif "text/csv" in content_type or url.endswith(".csv"):  # Handle CSV
            df = pd.read_csv(url)
            # Convert dataframe to text (you can format this better if needed)
            text = df.to_csv(index=False)

        else:  # Fallback for plain text or unknown content
            text = r.text

        return chunk_text(text, max_length)

    except Exception as e:
        st.error(f"⚠️ Error extracting text from URL: {str(e)}")
        return []