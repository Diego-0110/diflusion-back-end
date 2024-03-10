from types import FunctionType
import csv
import pandas as pd
import json

class Data:
    def __init__(self, filename) -> None:
        self.filename = filename
        # TODO iterable

    def read_all(self, condition: FunctionType = lambda x: x):
        pass

    def write_all(self, data_list: list[dict]):
        pass

class CSV(Data):
    def __init__(self, filename, delimiter) -> None:
        super().__init__(filename)
        self.delimiter = delimiter
    
    def read_all(self, condition: FunctionType = lambda x: x):
        res = []
        with open(self.filename, 'r', newline='', encoding='utf8') as file:
            data = csv.DictReader(file, delimiter=self.delimiter)
            count = 0
            for row in data:
                if count == 0:
                    count += 1
                    continue
                if condition(row):
                    res.append(row)

        return res
    
    def write_all(self, data_list: list[dict]):
        fieldnames = list(data_list[0].keys())
        with open(self.filename, 'w', newline='', encoding='utf8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_list)

class Excel(Data):
    def __init__(self, filename, sheet_name = 0, skiprows = 0) -> None:
        super().__init__(filename)
        self.sheet_name = sheet_name
        self.skiprows = skiprows
    
    def read_all(self, condition: FunctionType = lambda x: x):
        dataframe = pd.read_excel(self.filename, sheet_name=self.sheet_name, 
                                    skiprows=self.skiprows)
        dict_list = dataframe.to_dict('records')
        return [row for row in dict_list if condition(row)]

    def write_all(self, data_list: list[dict]):
        return super().write_all(data_list)
    
class JSON(Data):
    def __init__(self, filename) -> None:
        super().__init__(filename)

    def read_all(self, condition: FunctionType = lambda x: x):
        with open(self.filename, 'r', encoding='utf8') as file:
            raw_data = json.load(file)
        if isinstance(raw_data, list):
            return [d for d in raw_data if condition(d)]
        return raw_data

    def write_all(self, data_list: list[dict]):
        with open(self.filename, 'w', encoding='utf8') as file:
            json.dump(data_list, file, indent=2)
