from utils.db import MongoDB
import consts.config as config
from pymongo import database

import time
import math
from datetime import datetime, timedelta
from calendar import monthrange
from utils.scripts import centroid_geopoly, idw_shepard

class Predictor():
    # TODO check there are enough data to run the predictor (custom error)
    # TOODO parameters
    def __init__(self, pred_id: str):
        self.id = pred_id

    def get_model_db_session(self) -> database.Database:
        mongo_client = MongoDB().get_client(config.MODEL_DB_URL)
        return mongo_client[config.MODEL_DB_NAME]
    
    def get_web_db_session(self) -> database.Database:
        mongo_client = MongoDB().get_client(config.WEB_DB_URL)
        return mongo_client[config.WEB_DB_NAME]
    
    def get_history_db_session(self) -> database.Database:
        mongo_client = MongoDB().get_client(config.HISTORY_DB_URL)
        return mongo_client[config.HISTORY_DB_NAME]

    def get_data(self, db: database.Database) -> list[dict]:
        pass

    def get_prediction(self, data_list: list[dict], ini_date: datetime,
                       days: int) -> tuple[list[dict], list[dict]]:
        pass

    def save(self, levels_list: list[dict], routes_list: list[dict]):
        # Save to web database
        mongo_db_w = self.get_web_db_session()
        w_lvl_coll = mongo_db_w['riskLevels']
        w_rts_coll = mongo_db_w['riskRoutes']
        w_lvl_coll.insert_many(levels_list)
        w_rts_coll.insert_many(routes_list)
        # Save to history database
        mongo_db_h = self.get_history_db_session()
        h_lvl_coll = mongo_db_h['riskLevels']
        h_lvl_coll.insert_many(levels_list)

    def run(self, ini_date: datetime, days: int):
        fin_date = ini_date + timedelta(days=days)
        mongo_db = self.get_model_db_session()
        data_list = self.get_data(mongo_db, ini_date, days)
        (levels_list, routes_list) = self.get_prediction(data_list, ini_date, days)
        self.save(levels_list, routes_list) # TODO not save mode

DEFAULT_MIG_PROB = [0.5 for i in range(0, 48)]
class PredictorA(Predictor):
    def __init__(self):
        super().__init__('A')
        self.config = { # TODO move to config
            'outbreakDistance': 50000,
            'outbreakDays': 180,
            'tempThreshold': 0.5,
            'levelThresholds': [
                (lambda x: x < 1, None),
                (lambda x: x >= 1 and x <= 100, 0),
                (lambda x: x > 100 and x <= 150, 1),
                (lambda x: x > 150 and x <= 200, 2),
                (lambda x: x > 200 and x <= 300, 3),
                (lambda x: x > 300 and x <= 600, 4),
                (lambda x: x > 600, 5),
                (lambda x: True, None)
            ],
            'animalTypeProb': {
                0: 0.1,
                1: 1,
                2:  0.3
            }
        }

    def _get_regions_migs(self, db: database.Database) -> list[dict]:
        # MIGRATONS -> REGIONS
        # Get all regions with a list of all migrations with that region as
        #   destiny
        reg_coll = db['regions']
        return list(reg_coll.aggregate([
            {
                '$lookup': {
                'from': 'migrations', 
                'localField': '_id', 
                'foreignField': 'to.region', 
                'as': 'migs'
                }
            }
        ]))
    
    def _get_mig_outs_birds(self, db: database.Database, ids: list[str],
                            ini_date: datetime, days: int) -> list[dict]:
        max_date = ini_date - timedelta(days=7) # TODO const
        min_date = max_date - timedelta(days=self.config['outbreakDays'])
        max_date = max_date.timestamp()
        min_date = min_date.timestamp()
        # OUTBREAKS -- MIGRATIONS + BIRDS
        mig_coll = db['migrations']
        return list(mig_coll.aggregate([
                    { # Only migrations with destiny 'region'
                    '$match': {
                            '_id': { '$in': ids },
                        }
                    }, { # For every migration: outbreaks at x meter at most
                    '$lookup': {
                        'from': 'outbreaks', 
                        'let': {
                            'pt': '$from.loc'
                        }, 
                        'pipeline': [{
                                '$geoNear': {
                                    'near': '$$pt',
                                    'query': {
                                        'reportDate': { '$gte': min_date, '$lt': max_date }
                                    },
                                    'distanceField': 'd', 
                                    'maxDistance': self.config['outbreakDistance']
                                },
                            }], 
                        'as': 'outs'
                    }
                    }, { # Remove migrations with no nearby outbreaks:
                        #   Only risk routes
                        '$match': {
                            'outs': {
                                '$exists': True, 
                                '$not': { '$size': 0 }
                            }
                        }
                    }, { # Join bird data
                        '$lookup': {
                            'from': 'birds', 
                            'localField': 'species', 
                            'foreignField': 'scientificName', 
                            'as': 'bird'
                        }
                    }, { # Remove unnecessary fields
                        '$project': {
                            '_id': 1, 
                            'outs._id': 1, 
                            'outs.animalType': 1, 
                            'bird': 1
                        }
                    }
                ]))
    def _get_mean_temp(self, db: database.Database, region: dict,
                       ini_date: datetime, days: int) -> int:
        min_date = ini_date.timestamp()
        max_date = (ini_date + timedelta(days=days)).timestamp()
        weather_coll = db['weather']
        centroid = centroid_geopoly(region['geo']['coordinates'],
                                    region['geo']['type'])
        weather = weather_coll.aggregate([{
            '$geoNear': {
                'near': {
                    'type': 'Point', 
                    'coordinates': centroid
                },
                'query': {
                    '$or': [
                        {
                            'fromDate': {'$lte': min_date},
                            'toDate': {'$gte': min_date}
                        }, {
                            'fromDate': {'$lte': max_date},
                            'toDate': {'$gte': max_date}
                        }
                    ]
                },
                'distanceField': 'd'
            }
        }])
        # TODO raise when not enough data
        weather_tuple_list = []
        for w in weather:
            mean = sum([pred['minTemperature'] for pred in w['predictions']])
            mean = mean / days
            weather_tuple_list.append((w['d'], mean))
        return idw_shepard(centroid, weather_tuple_list, distance=True)
        

    def get_data(self, db: database.Database, ini_date: datetime,
                       days: int) -> list[dict]:
        mongo_db = self.get_model_db_session()
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(f' {current_time} regions...')
        # MIGRATONS -> REGIONS
        regions = self._get_regions_migs(db)
        data_by_reg = {}
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(f' {current_time} risk routes...')
        # OUTBREAKS -- MIGRATIONS + BIRDS -> REGIONS
        # For every region search for every migration outbreaks near to x meters
        #   at most to origin of the migration.
        for region in regions:
            risk_routes = []
            if region['migs']:
                migs_ids = [mig['_id'] for mig in region['migs']]
                risk_routes = self._get_mig_outs_birds(db, migs_ids, ini_date, days)
            data_by_reg[region['_id']] = {
                'riskRoutes': risk_routes,
                'temperature': 0
            }
        for region in regions:
            weather = self._get_mean_temp(db, region, ini_date, days)
            data_by_reg[region['_id']]['temperature'] = weather
        res = []
        for reg_key in data_by_reg:
            data_by_reg[reg_key]['regionId'] = reg_key
            res.append(data_by_reg[reg_key])
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(f' {current_time} end...')
        return res
    
    def get_prediction(self, data_list: list[dict], ini_date: datetime,
                       days: int) -> tuple[list[dict], list[dict]]:
        # { regionId: x, riskRoutes: x, temperature: x}
        fin_date = ini_date + timedelta(days=days)
        default_prob = []
        risk_routes = []
        for region in data_list:
            for mig in region['riskRoutes']:
                outbreaks = [o['_id'] for o in mig['outs']]
                risk_routes.append({
                    'regionId': region['regionId'],
                    'fromDate': ini_date.timestamp(),
                    'toDate': fin_date.timestamp(),
                    'migrationId': mig['_id'],
                    'outbreaks': outbreaks
                })
        risk_levels = []
        for region in data_list:
            if not region['riskRoutes']:
                risk_levels.append({
                    'regionId': region['regionId'],
                    'fromDate': ini_date.timestamp(),
                    'toDate': fin_date.timestamp(),
                    # 'level': 0,
                    'value': 0
                })
                continue
            # Temperature Weight
            temperature_w = 29.94
            if region['temperature'] > self.config['tempThreshold']:
                temperature_w += -7.82 * math.log(region['temperature'], math.e)
            else:
                temperature_w = 66
            outbreak_date = ini_date - timedelta(days=7) # const
            (_, month_days) = monthrange(outbreak_date.year, outbreak_date.month)
            month_week = math.ceil(outbreak_date.day / (month_days / 4))
            year_week = month_week + ((outbreak_date.month - 1) * 4)
            contribution = 0
            for mig in region['riskRoutes']:
                bird = mig['bird']
                if bird:
                    prob_mig = bird[0]['migrationProb'][year_week]
                else:
                    prob_mig = DEFAULT_MIG_PROB[year_week]
                for out in mig['outs']:
                    animal_prob = self.config['animalTypeProb'][out['animalType']]
                    contribution += prob_mig * animal_prob
            risk_value = contribution * temperature_w
            risk_dict = {
                'regionId': region['regionId'],
                'fromDate': ini_date.timestamp(),
                'toDate': fin_date.timestamp(),
                'value': risk_value
            }
            if risk_value > 150:
                print(f'riskvalue {risk_value}:')
                print(f'mt: {region["temperature"]}, tw: {temperature_w}, c: {contribution}')
            for (thres_func, value) in self.config['levelThresholds']:
                if thres_func(risk_value):
                    if value is not None:
                        risk_dict['level'] = value
                    break
            risk_levels.append(risk_dict)

        return (risk_levels, risk_routes)
