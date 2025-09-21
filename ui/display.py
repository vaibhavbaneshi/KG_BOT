import streamlit as st
from services.visualization import visualize_graph

def show_graph(graph):
    st.subheader("📊 Knowledge Graph Visualization")
    visualize_graph(graph)

def show_text(result):
    st.subheader("📜 Query Result")
    st.write(result)