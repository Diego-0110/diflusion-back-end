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

class OutbreaksUpdater(Updater):
    def __init__(self) -> None:
        super().__init__('outbreaks')
    
    def update_neo4j(self, data_list: list[dict]):
        print('Neo4j starting')
        neo_db = Neo4jDB()
        # TODO performance
        for outbreak in data_list:
            # TODO add id
            neo_db.run("""CREATE (:outbreak {
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
