import os
from .decorators import th_sf_singleton
from neo4j import GraphDatabase, Driver
from pymongo import MongoClient

@th_sf_singleton
class Neo4jDB:
    def __init__(self):
        self.clients: dict[str, Driver] = {}
    
    def get_client(self, url: str, user: str, pwd: str) -> Driver:
        if self.clients.get(url) is None:
            self.clients[url] = GraphDatabase.driver(url, auth=(user, pwd))
        return self.clients[url]

@th_sf_singleton
class MongoDB:
    def __init__(self):
        self.clients: dict[str, MongoClient] = {}
    
    def get_client(self, url: str) -> MongoClient:
        if self.clients.get(url) is None:
            self.clients[url] = MongoClient(url)
        return self.clients[url]
    