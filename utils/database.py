"""Database connection utilities."""

import os
from neo4j import GraphDatabase


def get_driver():
    """Get Neo4j driver instance."""
    uri = os.getenv("NEO4J_URI")
    password = os.getenv("NEO4J_PASSWORD")
    auth = ("neo4j", password)
    return GraphDatabase.driver(uri, auth=auth)
