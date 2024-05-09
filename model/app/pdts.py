from utils.db import MongoDB
from utils.scripts import centroid_geopoly, idw_shepard, hash_from_dict
import consts.config as config

from pymongo import database
from datetime import datetime, timedelta
from calendar import monthrange
import os
import time
import math
import uuid
import pandas as pd

class PredictorError(Exception):
    pass

class Predictor():
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

    def exists_prediction(self, ini_date: datetime, days: int):
        fin_date = ini_date + timedelta(days=days-1)
        mongo_db_w = self.get_web_db_session()
        w_lvl_coll = mongo_db_w['riskLevels']
        return len(list(w_lvl_coll.find({'fromDate': ini_date.timestamp(),
                         'toDate': fin_date.timestamp()}))) > 0

    def delete_existing_preds(self, ini_date: datetime, days: int):
        fin_date = ini_date + timedelta(days=days-1)
        mongo_db_w = self.get_web_db_session()
        w_lvl_coll = mongo_db_w['riskLevels']
        w_rts_coll = mongo_db_w['riskRoutes']
        filter_dict = {'fromDate': ini_date.timestamp(),
                         'toDate': fin_date.timestamp()}
        w_lvl_coll.delete_many(filter_dict)
        w_rts_coll.delete_many(filter_dict)
        mongo_db_h = self.get_history_db_session()
        h_lvl_coll = mongo_db_h['riskLevels']
        h_lvl_coll.delete_many(filter_dict)

    def run(self, ini_date: datetime, days: int, compare_mode = False, update = False):
        if not compare_mode and self.exists_prediction(ini_date, days):
            if not update:
                raise PredictorError(f'Prediction already exists')
            else:
                self.delete_existing_preds(ini_date, days)
        mongo_db = self.get_model_db_session()
        try:
            data_list = self.get_data(mongo_db, ini_date, days)
        except Exception as e:
            raise PredictorError(f'Error while getting data from model database: {e}')
        try:
            (levels_list, routes_list) = self.get_prediction(data_list, ini_date, days)
        except Exception as e:
            raise PredictorError(f'Error while getting prediction: {e}')
        try:
            if not compare_mode:
                self.save(levels_list, routes_list)
            else:
                df = pd.DataFrame.from_dict(levels_list)
                f_date = ini_date.strftime('%d-%m-%Y')
                preds_filename = f'{f_date}-{days}-{uuid.uuid4().hex}.xlsx'
                df.to_excel(os.path.join(config.PREDS_PATH, preds_filename))
                return preds_filename
        except Exception as e:
            raise PredictorError(f'Error while saving results: {e}')

DEFAULT_MIG_PROB = [0.5 for i in range(0, 48)]
class PredictorA(Predictor):
    def __init__(self):
        super().__init__('A')
        self.config = { # TODO move to config
            'outbreakDistance': 40000,
            'outbreakDays': 120,
            'travelDays': 7,
            'minTempPoints': 50,
            'minDaysPercentage': 0.9,
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
        mig_coll = db['migrations']
        mig_coll.create_index({'to.region': 1})
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
        max_date = ini_date - timedelta(days=self.config['travelDays'])
        min_date = max_date - timedelta(days=self.config['outbreakDays'])
        max_date = math.floor(max_date.timestamp())
        min_date = math.floor(min_date.timestamp())
        # OUTBREAKS -- MIGRATIONS + BIRDS
        mig_coll = db['migrations']
        mig_coll.create_index({'from.loc': '2dsphere'})
        mig_coll.create_index({'to.loc': '2dsphere'})
        mig_coll.create_index({'to.region': 1})
        birds_coll = db['birds']
        birds_coll.create_index({'scientificName': 1})
        outs_coll = db['outbreaks']
        outs_coll.create_index({'loc': '2dsphere'})
        outs_coll.create_index({'reportDate': 1})
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
        min_date = math.floor(ini_date.timestamp())
        max_date = math.floor((ini_date + timedelta(days=days)).timestamp())
        weather_coll = db['weather']
        weather_coll.create_index({'loc': '2dsphere'})
        weather_coll.create_index({'fromDate': 1})
        weather_coll.create_index({'toDate': 1})
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
        weather_grouped = {}
        for w in weather:
            w_hash = hash_from_dict(w['loc'])
            if not weather_grouped.get(w_hash):
                weather_grouped[w_hash] = [w]
            else:
                weather_grouped[w_hash].append(w)
        if len(weather_grouped) < self.config['minTempPoints']:
            raise PredictorError(f'Not enough weather points (min: {self.config['minTempPoints']})')
        fin_date = ini_date + timedelta(days=days-1)
        weather_tuple_list = []
        for w_key in weather_grouped:
            w_list: list = weather_grouped[w_key]
            w_list.sort(key=lambda x: x['fromDate'])
            temp_list = []
            for index, w in enumerate(w_list):
                f_date = w['fromDate']
                to_date = w['toDate']
                fn_date = w_list[index + 1]['fromDate'] if index < len(w_list) - 1 else None
                d_iter = ini_date.timestamp() if ini_date.timestamp() > f_date else f_date
                while d_iter <= fin_date.timestamp() and d_iter <= to_date and (not fn_date or d_iter < fn_date):
                    delta_index = datetime.fromtimestamp(d_iter) - datetime.fromtimestamp(f_date)
                    temp_list.append(w['predictions'][delta_index.days]['minTemperature'])
                    d_iter = (datetime.fromtimestamp(d_iter) + timedelta(days=1)).timestamp()
            
            if len(temp_list) / days >= self.config['minDaysPercentage']:
                distance = w_list[0]['d']
                mean = sum(temp_list) / len(temp_list)
                weather_tuple_list.append((distance, mean))
        if len(weather_tuple_list) < self.config['minTempPoints']:
            raise PredictorError(f'Not enough weather points (min: {self.config['minTempPoints']})')
        return idw_shepard(centroid, weather_tuple_list, distance=True)
        

    def get_data(self, db: database.Database, ini_date: datetime,
                       days: int) -> list[dict]:
        # MIGRATONS -> REGIONS
        regions = self._get_regions_migs(db)
        if not regions:
            raise PredictorError('Not enough data: regions')
        data_by_reg = {}
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
        return res
    
    def get_prediction(self, data_list: list[dict], ini_date: datetime,
                       days: int) -> tuple[list[dict], list[dict]]:
        fin_date = ini_date + timedelta(days=days-1)
        risk_routes = []
        for region in data_list:
            for mig in region['riskRoutes']:
                outbreaks = [o['_id'] for o in mig['outs']]
                risk_route = {
                    'regionId': region['regionId'],
                    'fromDate': math.floor(ini_date.timestamp()),
                    'toDate': math.floor(fin_date.timestamp()),
                    'migrationId': mig['_id'],
                    'outbreakIds': outbreaks
                }
                risk_route['_id'] = hash_from_dict(risk_route)
                risk_routes.append(risk_route)
        risk_levels = []
        for region in data_list:
            if not region['riskRoutes']:
                risk_dict = {
                    'regionId': region['regionId'],
                    'temperature': region['temperature'],
                    'fromDate': math.floor(ini_date.timestamp()),
                    'toDate': math.floor(fin_date.timestamp()),
                    # 'level': 0,
                    'value': 0
                }
                risk_dict['_id'] = hash_from_dict(risk_dict, ['regionId',
                                                        'fromDate', 'toDate'])
                risk_levels.append(risk_dict)
                continue
            # Temperature Weight
            temperature_w = 29.94
            if region['temperature'] > self.config['tempThreshold']:
                temperature_w += -7.82 * math.log(region['temperature'], math.e)
            else:
                temperature_w = 66
            outbreak_date = ini_date - timedelta(days=self.config['travelDays'])
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
                'temperature': region['temperature'],
                'fromDate': math.floor(ini_date.timestamp()),
                'toDate': math.floor(fin_date.timestamp()),
                'value': risk_value
            }
            risk_dict['_id'] = hash_from_dict(risk_dict, ['regionId',
                                                          'fromDate', 'toDate'])
            for (thres_func, value) in self.config['levelThresholds']:
                if thres_func(risk_value):
                    if value is not None:
                        risk_dict['level'] = value
                    break
            risk_levels.append(risk_dict)

        return (risk_levels, risk_routes)
