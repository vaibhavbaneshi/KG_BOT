from apscheduler.schedulers.background import BackgroundScheduler
from neo4j import GraphDatabase
import atexit
from configs.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import streamlit as st

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def ping_neo4j():
    try:
        with driver.session() as session:
            session.run("RETURN 1")
        st.success("✅ Neo4j is online")
    except Exception as e:
        st.error("❌ Neo4j connection failed: {e}")
        # here you can send email/slack alert if needed

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(ping_neo4j, "interval", minutes=30)
    scheduler.start()

    # Ensure scheduler stops when app exits
    atexit.register(lambda: scheduler.shutdown())