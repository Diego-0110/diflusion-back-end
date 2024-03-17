import os
from neo4j import GraphDatabase
from pymongo import MongoClient

NEO4J_URL = os.getenv('NEO4J_URL')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PWD = os.getenv('NEO4J_PWD')
NEO4J_DB = os.getenv('NEO4J_DB')

MONGO_URL = os.getenv('MONGO_URL')
MONGO_DB = os.getenv('MONGO_DB')

class Neo4jDB:
    instance = None
    def __new__(cls, *args, **kargs):
        if cls.instance is None:
            driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PWD))
            cls.instance = driver.session(database=NEO4J_DB)
        return cls.instance

class MongoDB:
    instance = None
    def __new__(cls, *args, **kargs):
        if cls.instance is None:
            client = MongoClient(MONGO_URL)
            cls.instance = client[MONGO_DB]
        return cls.instance
