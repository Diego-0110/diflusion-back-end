from utils.db import MongoDB
import consts.config as config
from pymongo import database

import time

class Predictor():
    def __init__(self, pred_id: str) -> None:
        self.id = pred_id

    def get_model_db_session(self) -> database.Database:
        mongo_client = MongoDB().get_client(config.MODEL_DB_URL)
        return mongo_client[config.MODEL_DB_NAME]

    def get_data(self) -> list[dict]:
        pass

    def run(self):
        pass

class PredictorA(Predictor):
    def __init__(self) -> None:
        super().__init__('predA')

    def get_data(self) -> list[dict]:
        mongo_db = self.get_model_db_session()
        reg_coll = mongo_db['regions']
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(f' {current_time} regions...')
        regions = list(reg_coll.aggregate([
            {
                '$lookup': {
                'from': 'migrations', 
                'localField': 'id', 
                'foreignField': 'to.region', 
                'as': 'migs'
                }
            }
        ]))
        data = []
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(f' {current_time} risk routes...')
        mig_coll = mongo_db['migrations']
        for region in regions:
            risk_routes = []
            if region['migs']:
                risk_routes = list(mig_coll.aggregate([
                    {
                    '$match': {
                        'id': {
                        '$in': [mig['id'] for mig in region['migs']]
                        }
                    }
                    }, {
                    '$lookup': {
                        'from': 'outbreaks', 
                        'let': {
                        'pt': '$from.loc'
                        }, 
                        'pipeline': [
                        {
                            '$geoNear': {
                            'near': '$$pt', 
                            'distanceField': 'd', 
                            'maxDistance': 50000
                            }
                        }
                        ], 
                        'as': 'outs'
                    }
                    }, {
                        '$match': {
                            'outs': {
                                '$exists': True, 
                                '$not': {
                                    '$size': 0
                                }
                            }
                        }
                    }, {
                        '$lookup': {
                            'from': 'birds', 
                            'localField': 'species', 
                            'foreignField': 'scientificName', 
                            'as': 'birds'
                        }
                    }
                ]))

            data.append({
                'regionId': region['_id'],
                'riskRoutes': risk_routes
            })
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(f' {current_time} end...')
        return data
    
    def run(self):
        data_list = self.get_data()
        for data in data_list:
            if data['riskRoutes']:
                print(data)
