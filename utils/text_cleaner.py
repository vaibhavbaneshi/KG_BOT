import re

def text_cleaner(relation: str) -> str:
        # Uppercase and replace invalid chars with underscore
        rel = relation.upper()
        rel = re.sub(r'[^A-Z0-9_]', '_', rel)  # only allow letters, numbers, underscores
        return rel

def clean_cypher(cypher_query: str) -> str:
    cypher_query = cypher_query.strip()
    if cypher_query.startswith("```"):
        cypher_query = cypher_query.strip("`")
        cypher_query = cypher_query.replace("cypher", "").strip()
    return cypher_query