from utils.data import JSON
import consts.config as config
from utils.db import Neo4jDB, MongoDB
import os
import threading
import copy
class Updater:
    def __init__(self, data_id: str) -> None:
        self.data_id = data_id

    def read_data(self) -> list[dict]:
        filename = os.path.join(config.OUTPUT_PATH, f'{self.data_id}.json')
        return JSON(filename).read_all()
    
    def update_db(self, data_list: list[dict]):
        pass

    def run(self):
        data_list = self.read_data()
        self.update_db(data_list)
        # TODO handle exceptions

class OutbreaksUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('outbreaks')
    
    def update_neo4j(self, data_list: list[dict]):
        print('Neo4j starting')
        neo_db = Neo4jDB()
        # TODO performance
        for outbreak in data_list:
            # TODO add id
            neo_db.run("""CREATE (:Outbreak {
                    coords: $coords,
                    animalType: $animalType
            })""", outbreak)
        print('Neo4j finished')

    def update_mongo(self, data_list: list[dict]):
        print('Mongo started')
        mongo_db = MongoDB()
        mongo_coll = mongo_db[self.data_id]
        mongo_coll.insert_many(data_list)
        print('Mongo finished')

    def update_db(self, data_list: list[dict]):
        data_list_cp = copy.deepcopy(data_list)
        neo4j_th = threading.Thread(target=self.update_neo4j, args=(data_list,))
        mongo_th = threading.Thread(target=self.update_mongo, 
                                    args=(data_list_cp,))
        neo4j_th.start()
        mongo_th.start()
        neo4j_th.join()
        mongo_th.join()

class WeatherUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('weather')
    
    def update_db(self, data_list: list[dict]):
        neo_db = Neo4jDB()
        for weather in data_list:
            neo_db.run("""CREATE (:Weather {
                    coords: $coords,
                    minTemperatures: $minTemperatures
            })""", weather)

class RegionsUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('regions')
    
    def update_neo4j(self, data_list: list[dict]):
        neo_db = Neo4jDB()
        for region in data_list:
            # TODO check fields
            neo_db.run("""CREATE (:Region {
                    id: $id,
                    coords: $coords,
                    geoType: $geoType
            })""", region)

    def update_mongo(self, data_list: list[dict]):
        mongo_db = MongoDB()
        mongo_coll = mongo_db[self.data_id]
        mongo_coll.insert_many(data_list)
    
    def update_db(self, data_list: list[dict]):
        data_list_cp = copy.deepcopy(data_list)
        neo4j_th = threading.Thread(target=self.update_neo4j, args=(data_list,))
        mongo_th = threading.Thread(target=self.update_mongo, 
                                    args=(data_list_cp,))
        neo4j_th.start()
        mongo_th.start()
        neo4j_th.join()
        mongo_th.join()

class MigrationsUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('migrations')
    
    def update_neo4j(self, data_list: list[dict]):
        neo_db = Neo4jDB()
        for migration in data_list:
            # TODO check fields: id
            neo_db.run("""
                CREATE (m:Migration {
                    fromCountry: $from.country,
                    fromCoords: $from.coords,
                    toCountry: $to.country,
                    toCoords: $to.coords,
                    toRegion: $to.region
                })
                WITH m
                MATCH (r:Region)
                WHERE m.toRegion = r.id
                MERGE (m)-[:TO]->(r)
            """, migration)

    def update_mongo(self, data_list: list[dict]):
        mongo_db = MongoDB()
        mongo_coll = mongo_db[self.data_id]
        mongo_coll.insert_many(data_list)

    def update_db(self, data_list: list[dict]):
        data_list_cp = copy.deepcopy(data_list)
        neo4j_th = threading.Thread(target=self.update_neo4j, args=(data_list,))
        mongo_th = threading.Thread(target=self.update_mongo, 
                                    args=(data_list_cp,))
        neo4j_th.start()
        mongo_th.start()
        neo4j_th.join()
        mongo_th.join()

class BirdsUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('birds')
    
    def update_db(self, data_list: list[dict]):
        neo_db = Neo4jDB()
        for bird in data_list:
            # TODO check fields
            neo_db.run("""CREATE (:migration {
                    scientificName: $scientificName,
                    migrationProb: $migrationProb
            })""", bird)
        # TODO update migrations' relations

# TODO class RiskRoutesUpdt