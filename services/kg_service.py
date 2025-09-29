from utils.logger import logger
from utils.llm import llm
from configs.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from utils.text_cleaner import text_cleaner, clean_cypher

import streamlit as st
from neo4j import GraphDatabase
import ast

class kg_service:

    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
            logger.info("✅ Connected to Neo4j.")
        except Exception as e:
            logger.error(f"❌ Failed to establish a connection: {e}")
            self.driver = None

    # ----------------- Helpers -----------------
    def parse_triples(self, raw_triples: str):
        """Parse triples from LLM response (expects JSON-like list of lists)."""
        try:
            triples = ast.literal_eval(raw_triples)
            if isinstance(triples, list):
                return [tuple(item) for item in triples if len(item) >= 3]
        except Exception:
            pass
        return []

    # ----------------- Insert into Neo4j -----------------
    def insert_triples(self, triples):
        """Insert triples as (h)-[:REL]->(t) edges only."""
        try:
            if not self.driver:
                st.error("❌ Neo4j driver is not initialized. Check URI/user/pass.")
                return

            if not triples:
                st.warning("⚠️ No triples to insert.")
                return

            with self.driver.session() as session:
                for head, relation, tail in triples:
                    safe_rel = text_cleaner(relation).upper().replace(" ", "_")

                    query = f"""
                        MERGE (h:ENTITY {{name: $head}})
                        MERGE (t:ENTITY {{name: $tail}})
                        MERGE (h)-[:{safe_rel}]->(t)
                    """
                    session.run(query, head=head, tail=tail)

            st.success(f"✅ Inserted {len(triples)} triples into Neo4j")
            self.show_all_triples()

        except Exception as e:
            st.error(f"⚠️ Failed to insert triples: {str(e)}")

    # ----------------- Build KG -----------------
    def build_kg(self, user_input: str):
        prompt = f"""
                Extract knowledge triples strictly in JSON list format:
                [["Entity1", "RELATION", "Entity2"], ...]

                Rules:
                - Output only a valid Python list of lists. Do not add explanations, notes, or any extra text.
                - Relation should be short, uppercase, and noun or verb-like.
                - Examples of relations: "BORN_IN", "PROFESSION", "FOUNDED", "KNOWN_FOR", "HEADQUARTERED".
                - Entity names should be in title case (e.g., "Javed Akhtar", "Apple Inc.").
                - Entity2 can be a literal value (date, number, string) or another entity.
                - Format literal values as strings.
                - If the relation is ambiguous, choose the closest meaningful relation from the examples.
                - Avoid generic relations like "is" or "has". Use specific relations that describe the fact.

                Text: "{user_input}"
                """

        response = llm.invoke(prompt)
        st.write("✅ Raw Response:", response.content)
        raw_triples = response.content.strip()

        triples = self.parse_triples(raw_triples)
        self.insert_triples(triples)

    # ----------------- Show Data -----------------
    def show_all_triples(self):
        with self.driver.session() as session:
            query = """
            MATCH (h:ENTITY)-[r]->(t:ENTITY)
            RETURN h.name AS head, type(r) AS relation, t.name AS tail
            LIMIT 3
            """
            results = session.run(query)
            triples = [
                (record["head"], record["relation"], record["tail"]) for record in results
            ]
        st.write("📊 Current triples in Neo4j:", triples)

    # ----------------- Query KG -----------------
    def generate_query(self, user_question: str):
        try:
            prompt = f"""
                    You are an expert in Cypher for Neo4j.

                    Schema:
                    (:ENTITY {{name}})-[:RELATION]->(:ENTITY {{name}})
                    Nodes only have the `name` property.
                    All facts are stored as relationships wherever possible.

                    Important Rules:
                    - Direction matters! 
                    * :ACTED_IN → goes from an ACTOR entity → MOVIE entity.
                    * :DIRECTED → goes from a DIRECTOR entity → MOVIE entity.
                    * :PROFESSION → goes from PERSON entity → PROFESSION entity.
                    * :BORN_IN → goes from PERSON entity → LOCATION entity.
                    - When asking "Who acted in <movie>?" the query must start from the ACTOR node connected via `-[:ACTED_IN]->` to the movie.
                    - When asking "Which movies did <actor> act in?" the query must start from the ACTOR node and follow `-[:ACTED_IN]->` to the MOVIE.
                    - Questions may use different terms for the same relationship (e.g., "birthplace" → BORN_IN, "job" → PROFESSION).
                    - Always interpret the intent of the question and map to the correct relationship and direction.

                    Use `MATCH ... RETURN ...` queries.
                    Always alias return values (e.g., `AS result`).

                    Examples:
                    Q: Who acted in Screamers?
                    A: MATCH (a:ENTITY)-[:ACTED_IN]->(m:ENTITY {{name:"Screamers"}}) RETURN a.name AS result

                    Q: What movies did Pamela Adlon act in?
                    A: MATCH (a:ENTITY {{name:"Pamela Adlon"}})-[:ACTED_IN]->(m:ENTITY) RETURN m.name AS result

                    Q: Where was Javed Akhtar born?
                    A: MATCH (j:ENTITY {{name:"Javed Akhtar"}})-[:BORN_IN]->(b:ENTITY) RETURN b.name AS result

                    Now generate ONLY the Cypher query for:
                    Question: "{user_question}"
                    """

            response = llm.invoke(prompt)
            cypher_query = clean_cypher(response.content.strip())

            st.write("📝 Generated Cypher:", cypher_query)

            return self.query_kg(cypher_query)

        except Exception as e:
            st.error(f"❌ Query generation failed: {e}")
            return []

    def query_kg(self, cypher_query: str):
        with self.driver.session() as session:
            try:
                results = session.run(cypher_query)
                data = [dict(record) for record in results]
                if not data:
                    st.info("⚠️ No results found.")
                    return []

                # Show only values
                values = [list(record.values())[0] for record in data]
                st.success("✅ Query Results:")
                st.write(values)

                return values
            except Exception as e:
                st.error(f"❌ KG query failed: {e}")
                return []
    
    def reset_kg(self):
        """Delete all nodes and relationships in Neo4j"""
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            logger.info("🗑️ Deleted all existing triples from Neo4j")
            st.info("🗑️ Knowledge Graph reset (all old triples deleted)")
        except Exception as e:
            logger.error(f"⚠️ Failed to reset KG: {e}")
            st.error(f"⚠️ Failed to reset KG: {e}")