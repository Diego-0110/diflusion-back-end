from utils.data import JSON
import consts.config as config
from utils.db import MongoDB
from pymongo import collection
from utils.scripts import rename_list_dict
import os

class UpdaterError(Exception):
    pass
class Updater:
    def __init__(self, id: str) -> None:
        self.id = id

    def read_data(self) -> list[dict]:
        filename = os.path.join(config.OUTPUT_PATH, f'{self.id}.json')
        return JSON(filename).read_all()

    def get_model_session(self) -> collection.Collection:
        try:
            mongo_client = MongoDB().get_client(config.MODEL_DB_URL)
            mongo_db = mongo_client[config.MODEL_DB_NAME]
            return mongo_db[self.id]
        except Exception:
            raise UpdaterError(f'Error while starting connection to {config.MODEL_DB_NAME}')
    
    def get_web_session(self) -> collection.Collection:
        try:
            mongo_client = MongoDB().get_client(config.WEB_DB_URL)
            mongo_db = mongo_client[config.WEB_DB_NAME]
            return mongo_db[self.id]
        except Exception:
            raise UpdaterError(f'Error while starting connection to {config.WEB_DB_NAME}')

    def update_model_db(self, data_list: list[dict], updt_dupl: bool) -> int:
        coll = self.get_model_session()
        if updt_dupl:
            # TODO update
            return 0
        else:
            db_ids = list(coll.find({
                '_id': {'$in': [data['_id'] for data in data_list]}}))
            db_ids = [d['_id'] for d in db_ids]
            uniq_db_data = [d for d in data_list if d['_id'] not in db_ids]
            if uniq_db_data:
                coll.insert_many(uniq_db_data)
            return len(db_ids)

    def update_web_db(self, data_list: list[dict], updt_dupl: bool) -> int:
        coll = self.get_web_session()
        if updt_dupl:
            # TODO update
            return 0
        else:
            db_ids = list(coll.find({
                '_id': {'$in': [data['_id'] for data in data_list]}}))
            db_ids = [d['_id'] for d in db_ids]
            uniq_db_data = [d for d in data_list if d['_id'] not in db_ids]
            if uniq_db_data:
                coll.insert_many(uniq_db_data)
            return len(db_ids)

    def filter_unique(self, data_list: list[dict]) -> list[dict]:
        ids = []
        unique_data = []
        for data in data_list:
            if data['id'] not in ids:
                ids.append(data['id'])
                unique_data.append(data)
        return unique_data

    def run(self, updt_dupl = False):
        try:
            data_list = self.read_data()
        except Exception:
            raise UpdaterError(f'Error while reading input data')
        # Remove duplicate data and count
        dup_num = len(data_list)
        data_list = self.filter_unique(data_list)
        dup_num -= len(data_list)
        # Formatting for Mongo
        rename_list_dict(data_list, {'id': '_id'})
        try:
            dup_m_num = self.update_model_db(data_list, updt_dupl)
        except UpdaterError as e:
            raise e
        except Exception:
            raise UpdaterError(f'Error while updating model database')
        try:
            dup_w_num = self.update_web_db(data_list, updt_dupl)
        except UpdaterError as e:
            raise e
        except Exception:
            raise UpdaterError(f'Error while updating web database')
        return (dup_num, dup_m_num, dup_w_num)

class OutbreaksUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('outbreaks')

class WeatherUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('weather')

    def update_web_db(self, data_list: list[dict], updt_dupl: bool) -> int:
        pass

class RegionsUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('regions')

class MigrationsUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('migrations')

class BirdsUpdt(Updater):
    def __init__(self) -> None:
        super().__init__('birds')

    def update_web_db(self, data_list: list[dict], updt_dupl: bool) -> int:
        pass

# TODO class RiskRoutesUpdt