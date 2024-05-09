from utils.data import JSON, Excel
from utils.scripts import cast, hash_from_dict, noneless_dict, clean_geopoly, \
    value_or_none as vn, schema_geopoint, schema_geopoly, country_code_A3_to_A2
import os
import requests
import consts.config as config
import time
import datetime
from schema import Schema, SchemaError, Optional, And, Or

class FormatterError(Exception):
    pass

class Formatter:
    # Read and format data without checking uniqueness
    def __init__(self, data_id: str, ids: list[str], schema: Schema):
        self.data_id = data_id
        self.ids = ids
        self.schema: Schema = schema

    def read_data(self) -> list[dict]:
        pass

    def format_data(self, data: dict) -> dict:
        pass

    def generate_id(self, formatted_data: dict) -> dict:
        return hash_from_dict(formatted_data, self.ids)

    def filter_data(self, data_list: list[dict]) -> list[dict]:
        return data_list

    def save(self, data_list: list[dict]):
        # By default save as JSON
        filename = os.path.join(config.OUTPUT_PATH, f'{self.data_id}.json')
        JSON(filename).write_all(data_list)

    def run(self) -> tuple[int, int]:
        try:
            data_list = self.read_data()
        except Exception as e:
            raise FormatterError(f'Error while reading data: {e}')
        try:
            formatted_list = []
            invalid_data_count = 0
            for data in data_list:
                f_data = self.format_data(data)
                f_data = noneless_dict(f_data)
                try:
                    f_data['id'] = self.generate_id(f_data)
                except Exception as e:
                    FormatterError(f'Error while generating the id: {e}')
                    invalid_data_count += 1
                    continue
                try:
                    self.schema.validate(f_data)
                except SchemaError as se:
                    invalid_data_count += 1
                    continue
                formatted_list.append(f_data)
        except Exception as e:
            raise FormatterError(f'Error while formatting data: {e}')
        try:
            self.save(formatted_list)
        except Exception as e:
            raise FormatterError(f'Error while saving formatted data: {e}')
        return (len(formatted_list), invalid_data_count)


class OutbreaksFmt(Formatter):
    def __init__(self) -> None:
        super().__init__('outbreaks', [
            'diseaseId', 'loc', 'reportDate'
        ], Schema({
            'id': str,
            'diseaseId': int,
            Optional('serotype'): str,
            'loc': schema_geopoint(),
            Optional('city'): And(str, lambda x: len(x) > 0),
            Optional('adminDivNUT1'): And(str, lambda x: len(x) > 0),
            Optional('country'): And(str, lambda x: len(x) > 0),
            'region': And(str, lambda x: len(x) > 0),
            'reportDate': int,
            Optional('species'): And(str, lambda x: len(x) > 0),
            'animalType': lambda x: x in [0, 1, 2],
            'cases': And(int, lambda x: x >= 0),
            'deaths': And(int, lambda x: x >= 0)
        }))
        self._ref_date = datetime.datetime(1900, 1, 1)
    
    def pre_filter(self, data: dict):
        return (data.get('disease_id') in [584, 585, 561, 573, 578] or
                (data.get('disease_eng') == 'High pathogenicity avian influenza viruses (poultry) (Inf. with)' or
                data.get('disease_eng') == 'Influenza A viruses of high pathogenicity (Inf. with) (non-poultry including wild birds) (2017-)')) and \
                data.get('region') == 'Europe' # TODO consts

    def read_data(self) -> list[dict]:
        filename = os.path.join(config.INPUT_PATH, 'raw_outbreaks.xlsx')
        return Excel(filename).read_all(self.pre_filter)
    
    def _get_animal_type(self, is_wild: bool, wild_type: str):
        if not is_wild:
            return 0 # Domestic
        if wild_type == 'captive':
            return 2 # Captive
        return 1 # Wild
    
    def _get_report_date(self, date_str: str) -> int:
        if '/' in date_str:
            try:
                date = datetime.datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
            except Exception:
                try:
                    date = datetime.datetime.strptime(date_str, '%d/%m/%Y')
                except Exception:
                    return None
        else:
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except Exception:
                try:
                    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                except Exception:
                    return None
        # (self._ref_date + datetime.timedelta(days=days))
        return int(date.timestamp())

    def format_data(self, data: dict) -> dict:
        res = {
            'diseaseId': cast(data['disease_id'], int),
            'serotype': vn(data['sero_sub_genotype_eng'], str),
            'loc': {
                'type': 'Point',
                'coordinates': [cast(data['Longitude'], float),
                       cast(data['Latitude'], float)]
            },
            # 'city': vn(data['level3_name'], str),
            'adminDivNUT1': vn(data['level3_name'], str),
            'country': country_code_A3_to_A2(vn(data['iso_code'], str)),
            'region': vn(data['region'], str),
            'reportDate': self._get_report_date(cast(data['Reporting_date'], str)),
            'species': vn(data['Species'], str), # TODO generic values (Birds, ...)
            'animalType': self._get_animal_type(cast(data['is_wild'], bool),
                                                data['wild_type']),
            'cases': cast(data['cases'], int, 0),
            'deaths': cast(data['dead'], int, 0)
        }
        return res


class WeatherFmt(Formatter):
    def __init__(self) -> None:
        super().__init__('weather', [
            'fromDate', 'toDate', 'loc'
        ], Schema({
            'id': str,
            'fromDate': int,
            'toDate': int,
            'loc': schema_geopoint(),
            'predictions': [{
                'minTemperature': Or(int, float)
            }]
        }))

    def read_data(self) -> list[dict]:
        filename = os.path.join(config.INPUT_PATH, 'weather_stations.xlsx')
        stations = Excel(filename).read_all()
        api_params = {
            'lan': 'es',
            'apid': config.WEATHER_API_KEY,
            'll': ''
        }
        api_url = f'https://api.tutiempo.net/json'
        res = []
        for station in stations:
            lat = station['latitud_D']
            lon = station['longitud_D']
            api_params['ll'] = f'{lat},{lon}'
            response = requests.get(api_url, api_params)
            if response.status_code != 200:
                continue
            api_data = response.json()
            if 'error' in api_data:
                continue
            api_data['coords'] = [lon, lat]
            res.append(api_data)
        return res

    def format_data(self, data: dict) -> dict:
        from_date = datetime.datetime.strptime(data['day1']['date'], '%Y-%m-%d')
        to_date = from_date + datetime.timedelta(days=6) # TODO Const
        predictions = []
        for i in range(1, 8):
            predictions.append({
                'minTemperature': data[f'day{i}']['temperature_min']
            })
        return {
            'fromDate': int(from_date.timestamp()),
            'toDate': int(to_date.timestamp()),
            'loc': {
                'type': 'Point',
                'coordinates': data['coords']
            },
            'predictions': predictions
        }

class MigrationsFmt(Formatter):
    def __init__(self) -> None:
        super().__init__('migrations', [], Schema({
            'id': str,
            'from': {
                Optional('country'): And(str, lambda x: len(x) == 2),
                'loc': schema_geopoint()
            },
            'to': {
                Optional('country'): And(str, lambda x: len(x) == 2),
                'loc': schema_geopoint(),
                'region': And(str, lambda x: len(x) > 0)
            },
            'species': And(str, lambda x: len(x) > 0)
        }))
    
    def read_data(self) -> list[dict]:
        filename = os.path.join(config.INPUT_PATH, 'raw_migrations.xlsx')
        return Excel(filename).read_all()

    def format_data(self, data: dict) -> dict:
        return {
            'from': {
                'country': vn(data['PAIS'], str),
                'loc': {
                    'type': 'Point',
                    'coordinates': [cast(data['long_a'], float),
                           cast(data['Lat_A'], float)],
                },
            },
            'to': {
                'country': vn(data['PAIS2'], str),
                'loc': {
                    'type': 'Point',
                    'coordinates': [cast(data['LON_R'], float),
                           cast(data['LAT_R'], float)],
                },
                'region': cast(data['comarca_sg'], str)
            },
            'species': cast(data['ESPECIE2'], str)
        }
    
    def generate_id(self, formatted_data: dict) -> dict:
        id_dict = {
            'toCoords': formatted_data['to']['loc']['coordinates'],
            'fromCoords': formatted_data['from']['loc']['coordinates'],
            'species': formatted_data['species']
        }
        return hash_from_dict(id_dict)

class RegionsFmt(Formatter):
    def __init__(self) -> None:
        super().__init__('regions', [], Schema({
            'id': str,
            'geo': schema_geopoly(),
            Optional('name'): And(str, lambda x: len(x) > 0),
            Optional('adminDivNUT3'): And(str, lambda x: len(x) > 0),
            Optional('adminDivNUT2'): And(str, lambda x: len(x) > 0)
        }))
    
    def read_data(self) -> list[dict]:
        filename = os.path.join(config.INPUT_PATH, 'raw_regions.geojson')
        ft_col = JSON(filename).read_all()
        return ft_col['features']
    
    def format_data(self, data: dict) -> dict:
        props = data['properties']
        geo = data['geometry']
        return {
            'id': props['comarca_sg'],
            'geo': {
                'type': geo['type'],
                'coordinates': clean_geopoly(geo['coordinates'], geo['type'])
            },
            'name': props.get('comarca'),
            'adminDivNUT3': props.get('provincia'),
            'adminDivNUT2': props.get('comAutonoma')
        }

    def generate_id(self, formatted_data: dict) -> dict:
        return formatted_data['id']


class BirdsFmt(Formatter):
    def __init__(self) -> None:
        super().__init__('birds', ['scientificName'], Schema({
            'id': str,
            'scientificName': And(str, lambda x: len(x) > 0),
            'ringCode': int,
            'migrationProb': And([float, int], lambda x: len(x) == 48)
        }))
    
    def filter(self, data: dict):
        return len(cast(data.get('Nombre científico'), str)) > 0

    def read_data(self) -> list[dict]:
        # TODO add equivalent birds
        filename = os.path.join(config.INPUT_PATH, 'raw_migrations.xlsx')
        return Excel(filename, 1, 3).read_all(condition=self.filter)
    
    def _get_probabilities(self, data: dict) -> list:
        probs = []
        for i in range(1, 49):
            probs.append(cast(data[i], float, 0))
        return probs

    def format_data(self, data: dict) -> dict:
        return {
            # TODO additional birds
            'scientificName': cast(data['Nombre científico'], str),
            'ringCode': cast(data['codigo anilla'], int),
            'migrationProb': self._get_probabilities(data)
        }
