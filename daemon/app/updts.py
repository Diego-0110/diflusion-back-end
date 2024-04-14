from utils.data import JSON
import consts.config as config
from utils.db import Neo4jDB, MongoDB
from pymongo import collection
from neo4j import Session
import os
import copy
class Updater:
    def __init__(self, data_id: str) -> None:
        self.data_id = data_id

    def read_data(self) -> list[dict]:
        filename = os.path.join(config.OUTPUT_PATH, f'{self.data_id}.json')
        return JSON(filename).read_all()

    def get_neo4j_session(self) -> Session:
        neo4j_client = Neo4jDB().get_client(config.NEO4J_URL, config.NEO4J_USER,
                                            config.NEO4J_PWD)
        return neo4j_client.session(database=config.NEO4J_DB)

    def get_model_session(self) -> collection.Collection:
        mongo_client = MongoDB().get_client(config.MODEL_DB_URL)
        mongo_db = mongo_client[config.MODEL_DB_NAME]
        return mongo_db[self.data_id]
    
    def get_web_session(self) -> collection.Collection:
        mongo_client = MongoDB().get_client(config.WEB_DB_URL)
        mongo_db = mongo_client[config.WEB_DB_NAME]
        return mongo_db[self.data_id]

    def update_model_db(self, data_list: list[dict]):
        pass

    def update_web_db(self, data_list: list[dict]):
        pass

    def filter_data(self, data_list: list[dict]) -> list[dict]:
        return data_list

    def run(self):
        data_list = self.filter_data(self.read_data())
        data_list_cp = copy.deepcopy(data_list)
        self.update_model_db(data_list)
        self.update_web_db(data_list_cp)
        # TODO handle exceptions

class OutbreaksUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('outbreaks')
    
    def update_neo4j(self, data_list: list[dict]):
        print('Neo4j starting')
        neo_db = self.get_neo4j_session()
        # TODO performance
        for outbreak in data_list:
            # TODO add id
            neo_db.run("""CREATE (:Outbreak {
                    coords: $coords,
                    animalType: $animalType
            })""", outbreak)
        print('Neo4j finished')

    def update_model_db(self, data_list: list[dict]):
        mongo_coll = self.get_model_session()
        for outbreak in data_list:
            outbreak['loc'] = {
                'type': 'Point',
                'coordinates': outbreak['coords']
            }
            outbreak['_id'] = outbreak['id']
            del outbreak['id']
            del outbreak['coords']
        mongo_coll.insert_many(data_list)
        # TODO check how many have been inserted
    
    def update_web_db(self, data_list: list[dict]):
        for outbreak in data_list:
            outbreak['_id'] = outbreak['id']
            del outbreak['id']
        mongo_coll = self.get_web_session()
        mongo_coll.insert_many(data_list)
        # TODO check how many have been inserted
    
    def filter_data(self, data_list: list[dict]) -> list[dict]:
        ids = []
        unique_data = []
        for data in data_list:
            if data['id'] not in ids:
                ids.append(data['id'])
                unique_data.append(data)
        return unique_data

class WeatherUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('weather')
    
    def update_neo4j_db(self, data_list: list[dict]):
        neo_db = self.get_neo4j_session()
        for weather in data_list:
            neo_db.run("""CREATE (:Weather {
                    coords: $coords,
                    minTemperatures: $minTemperatures
            })""", weather)

    def update_model_db(self, data_list: list[dict]):
        for weather in data_list:
            weather['_id'] = weather['id']
            weather['loc'] = {
                'type': 'Point',
                'coordinates': weather['coords']
            }
            del weather['id']
            del weather['coords']
        mongo_coll = self.get_model_session()
        mongo_coll.insert_many(data_list)
    
    def filter_data(self, data_list: list[dict]) -> list[dict]:
        ids = []
        unique_data = []
        for data in data_list:
            if data['id'] not in ids:
                ids.append(data['id'])
                unique_data.append(data)
        return unique_data


class RegionsUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('regions')
    
    def update_neo4j(self, data_list: list[dict]):
        neo_db = self.get_neo4j_session()
        for region in data_list:
            # TODO check fields: coords can't be added
            neo_db.run("""CREATE (:Region {
                    id: $id,
                    geoType: $geoType
            })""", region)
    
    def update_model_db(self, data_list: list[dict]):
        for region in data_list:
            region['_id'] = region['id']
            region['geo'] = {
                'type': region['geoType'],
                'coordinates': region['coords']
            }
            del region['id']
            del region['geoType']
            del region['coords']
        mongo_coll = self.get_model_session()
        mongo_coll.insert_many(data_list)
    
    def update_web_db(self, data_list: list[dict]):
        for region in data_list:
            region['_id'] = region['id']
            del region['id']
        mongo_coll = self.get_web_session()
        mongo_coll.insert_many(data_list)

class MigrationsUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('migrations')
    
    def update_neo4j(self, data_list: list[dict]):
        neo_db = self.get_neo4j_session()
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

    def update_model_db(self, data_list: list[dict]):
        for mig in data_list:
            mig['_id'] = mig['id']
            mig['from']['loc'] = {
                'type': 'Point',
                'coordinates': mig['from']['coords']
            }
            mig['to']['loc'] = {
                'type': 'Point',
                'coordinates': mig['to']['coords']
            }
            del mig['id']
            del mig['from']['coords']
            del mig['to']['coords']
        mongo_coll = self.get_model_session()
        mongo_coll.insert_many(data_list)
    
    def update_web_db(self, data_list: list[dict]):
        for mig in data_list:
            mig['_id'] = mig['id']
            del mig['id']
        mongo_coll = self.get_web_session()
        mongo_coll.insert_many(data_list)

    def filter_data(self, data_list: list[dict]) -> list[dict]:
        ids = []
        unique_data = []
        for data in data_list:
            if data['id'] not in ids:
                ids.append(data['id'])
                unique_data.append(data)
        return unique_data

class BirdsUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('birds')
    
    def update_neo4j_db(self, data_list: list[dict]):
        neo_db = self.get_neo4j_session()
        for bird in data_list:
            # TODO check fields
            neo_db.run("""CREATE (:migration {
                    scientificName: $scientificName,
                    migrationProb: $migrationProb
            })""", bird)
        # TODO update migrations' relations

    def update_model_db(self, data_list: list[dict]):
        for bird in data_list:
            bird['_id'] = bird['id']
            del bird['id']
        mongo_coll = self.get_model_session()
        mongo_coll.insert_many(data_list)
    
    def filter_data(self, data_list: list[dict]) -> list[dict]:
        ids = []
        unique_data = []
        for data in data_list:
            if data['id'] not in ids:
                ids.append(data['id'])
                unique_data.append(data)
        return unique_data

# TODO class RiskRoutesUpdt