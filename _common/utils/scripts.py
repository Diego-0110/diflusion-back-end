import hashlib
import datetime
from schema import Schema, And, Or
import math

# Type scripts
def cast(value, caster, fallback = None):
    # Try to casta a value and return fallback on error
    try:
        return caster(value)
    except ValueError:
        return fallback

def value_or_none(value, type_callable):
    if isinstance(value, type_callable):
        return value
    return None

# Dict scripts
def sub_dict(data: dict, key_list: list[str]) -> dict:
    # Return a new dict with just the selected key values (key_list)
    res = {}
    for key in key_list:
        value = data.get(key)
        if value is not None:
            res[key] = value

    return res

def hash_from_dict(data: dict, id_keys: list[str] = None) -> str:
    # Return a unique id as a str based on key values (id_keys)
    if not id_keys:
        id_keys = list(data.keys())
    id_keys.sort()
    concated_str = ' - '.join(str(data[key]) for key in id_keys)
    return hashlib.sha256(concated_str.encode()).hexdigest()

def noneless_dict(data: dict) -> dict:
    # Return a new dict without None values
    res = {}
    for key in data:
        if data[key] is not None:
            if isinstance(data[key], dict):
                res[key] = noneless_dict(data[key])
            else:
                res[key] = data[key]
    return res

def rename_dict(data: dict, names: dict):
    # Modify 'data' renaming keys from 'names'
    for key in names:
        if key in data:
            new_name = names[key]
            data[new_name] = data[key]
            del data[key]

def rename_list_dict(data: list[dict], names: list[dict]):
    # Rename dictionaries of the list 'data'
    for d in data:
        rename_dict(d, names)

# Date scripts
def date_zero(date: datetime.datetime) -> datetime.datetime:
    # Return a new datetime with time set to zero (00:00:00)
    return date.replace(hour=0, second=0, microsecond=0)

# GeoJson scripts
def clean_geopoly(coords, geo_type: str):
    # Return a new geojson polygon without duplicate points
    if geo_type == 'Polygon':
        res = []
        for points in coords:
            uniques = []
            for point in points:
                clean_point = [point[0], point[1]] # point could have more items
                if [point[0], point[1]] not in uniques:
                    uniques.append(clean_point)
            last_point= points[len(points) - 1]
            uniques.append([last_point[0], last_point[1]]) # Close polygon
            res.append(uniques)
        return res
    elif geo_type == 'MultiPolygon':
        res = []
        for poly in coords:
            res.append(clean_geopoly(poly, 'Polygon'))
        return res
    return None

def points_from_geopoly(coords, geo_type: str) -> list[list[float]]:
    # Return a list of the points which make up the geopolygon
    res = []
    if geo_type == 'Polygon':
        for points in coords:
            for point in points[:-1]:
                res.append([point[0], point[1]])
        return res
    elif geo_type == 'MultiPolygon':
        for poly in coords:
            res.extend(points_from_geopoly(poly, 'Polygon'))
        return res
    return None

def centroid_geopoly(coords, geo_type: str) -> list[float]:
    points = points_from_geopoly(coords, geo_type)
    if points is None:
        return None
    centroid = [0, 0]
    for point in points:
        centroid[0] += point[0]
        centroid[1] += point[1]
    centroid[0] /= len(points)
    centroid[1] /= len(points)
    return centroid

# Schema scripts
def schema_geocoords():
    return And([float, int], lambda x: len(x) == 2,
               lambda x: x[0] >= -180 and x[0] <= 180,
               lambda x: x[1] >= -90 and x[1] <= 90)

def schema_geopoint():
    return Schema({
        'type': 'Point',
        'coordinates': schema_geocoords()
    })

def schema_geopoly():
    return Or({
        'type': 'Polygon',
        'coordinates': [[schema_geocoords()]]
    }, {
        'type': 'MultiPolygon',
        'coordinates': [[[schema_geocoords()]]]
    })

def schema_len_eq(length: int) -> Schema:
    return Schema(lambda x: len(x) == length,
               error=f'length should be equal to {length}')

def schema_len_lt(length: int) -> Schema:
    return Schema(lambda x: len(x) < length,
               error=f'length should be lower than {length}')

def schema_len_gt(length: int) -> Schema:
    return Schema(lambda x: len(x) > length,
               error=f'length should be greater than {length}')

# Other
def points_distance(point1: list[float], point2: list[float]):
    return 1

def idw_shepard(ref_point: list[float],
                points: list[tuple[list[float] | float, float]],
                p: int = 2, distance = False):
    d_func = lambda x, y: y if distance else points_distance
    num = 0
    den = 0
    for p_tuple in points:
        (point, value) = p_tuple
        d = d_func(ref_point, point)
        if d == 0:
            return value
        w = 1 / (math.pow(d, p))
        num += w * value
        den += w
    return num / den
