import hashlib

def get_hash_from_dict(input: dict):
    if not isinstance(input, dict):
        raise TypeError
    keys = list(input.keys())
    keys.sort()
    concated_str = ' - '.join(str(input[key]) for key in keys)
    return hashlib.sha256(concated_str.encode()).hexdigest()

def get_sub_dict(input: dict, key_list: list[str]) -> dict:
    res = {}
    for key in key_list:
        value = input.get(key)
        if value is not None:
            res[key] = value

    return res