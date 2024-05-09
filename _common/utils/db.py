from .decorators import th_sf_singleton
from pymongo import MongoClient

@th_sf_singleton
class MongoDB:
    def __init__(self):
        self.clients: dict[str, MongoClient] = {}
    
    def get_client(self, url: str) -> MongoClient:
        if self.clients.get(url) is None:
            self.clients[url] = MongoClient(url)
        return self.clients[url]
    