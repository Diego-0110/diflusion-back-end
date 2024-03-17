from utils.data import JSON, Excel
from utils.types import cast
import os
import consts.config as config

class Formatter:
    def __init__(self, data_id: str) -> None:
        self.data_id = data_id

    def read_data(self) -> list[dict]:
        pass

    def format_data(self, data: dict) -> dict:
        pass

    def filter_data(self, data_list: list[dict]) -> list[dict]:
        return data_list

    def save(self, data_list: list[dict]):
        # By default save as JSON
        filename = os.path.join(config.OUTPUT_PATH, f'{self.data_id}.json')
        JSON(filename).write_all(data_list)

    def run(self):
        # TODO error handling
        data_list = self.read_data()
        formatted_list = [self.format_data(data) for data in data_list]
        self.save(self.filter_data(formatted_list))


class OutbreaksFmt(Formatter):
    def __init__(self) -> None:
        super().__init__('outbreaks')
    
    def filter(self, data: dict):
        return data.get('disease_id') in [584, 585, 561, 573, 578] and \
            data.get('region') == 'Europe'

    def read_data(self) -> list[dict]:
        # TODO read raw_outbreaks.xlsx and filter by disease_id and region
        filename = os.path.join(config.INPUT_PATH, 'raw_outbreaks.xlsx')
        return Excel(filename).read_all(self.filter)
    
    def format_data(self, data: dict) -> dict:
        # TODO outbreak id?
        # TODO remove fields with no value
        # TODO nan values
        return {
            'eventId': cast(data['epi_event_id'], int), # TODO remove?
            'diseaseId': cast(data['disease_id'], int), # TODO remove?
            'serotype': cast(data['sero_sub_genotype_eng'], str),
            'coords': [cast(data['Longitude'], float),
                       cast(data['Latitude'], float)],
            'city': cast(data['level3_name'], str, ''), # TODO Location_name?
            'country': cast(data['country'], str, ''),
            'region': cast(data['region'], str, ''), # TODO ISO code?
            'reportDate': cast(data['Reporting_date'], int), # TODO format date
            'species': cast(data['Species'], str, ''), # TODO generic values (Birds, ...)
            'animalType': cast(data['is_wild'], bool), # TODO is_wild and wild_type
            'cases': cast(data['cases'], int, 0),
            'deaths': cast(data['dead'], int, 0)
        }


class MigrationsFmt(Formatter):
    def __init__(self) -> None:
        super().__init__('migrations')
    
    def read_data(self) -> list[dict]:
        filename = os.path.join(config.INPUT_PATH, 'raw_migrations.xlsx')
        return Excel(filename).read_all()

    def format_data(self, data: dict) -> dict:
        return {
            # 'id': cast(data['id'], int),
            'from': {
                'countryCode': cast(data['PAIS'], str, ''),
                'coords': [cast(data['Lat_A'], float),
                            cast(data['long_a'], float)],
            },
            'to': {
                'countryCode': cast(data['PAIS2'], str, ''),
                'coords': [cast(data['LAT_R'], float),
                            cast(data['LON_R'], float)],
                'regionId': cast(data['comarca_sg'], str, ''),
            },
            'species': cast(data['ESPECIE2'], str, '')
        }
    
    def filter_data(self, data_list: list[dict]) -> list[dict]:
        uniques = []
        for data in data_list:
            if data not in uniques:
                uniques.append(data)
        
        return uniques


class RegionsFmt(Formatter):
    def __init__(self) -> None:
        super().__init__('regions')
    
    def read_data(self) -> list[dict]:
        return super().read_data()


class BirdsFmt(Formatter):
    def __init__(self) -> None:
        super().__init__('birds')
    
    def filter(self, data: dict):
        return len(cast(data.get('Nombre científico'), str)) > 0

    def read_data(self) -> list[dict]:
        # TODO add equivalent birds
        filename = os.path.join(config.INPUT_PATH, 'raw_migrations.xlsx')
        return Excel(filename, 1, 3).read_all(self.filter)
    
    def get_probabilities(self, data: dict) -> list:
        probs = []
        for i in range(1, 48):
            probs.append(cast(data[i], float, 0))
        return probs

    def format_data(self, data: dict) -> dict:
        return {
            'scientificName': cast(data.get('Nombre científico'), str),
            'migrationProb': self.get_probabilities(data)
        }