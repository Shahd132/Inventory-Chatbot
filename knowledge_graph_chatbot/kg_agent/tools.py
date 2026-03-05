import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jTool:
    def __init__(self):
        uri=os.getenv("NEO4J_URI")
        username=os.getenv("NEO4J_USERNAME")
        password=os.getenv("NEO4J_PASSWORD")
        self.driver=GraphDatabase.driver(
            uri,
            auth=(username, password)
        )
        self.driver.verify_connectivity()

    def run_query(self, cypher: str, params: dict = {}) -> list:
        with self.driver.session() as session:   
            result = session.run(cypher, params)
            return [record.data() for record in result]

    def close(self):
        self.driver.close()

    def verify_connection(self) -> bool:
        try:
            self.run_query("RETURN 1 AS test")
            return True
        except Exception as e:
            print(f"Neo4j connection failed: {e}")
            return False