import json
from enum import Enum


class DictObjEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def deep_serialize(obj):
    return json.dumps(obj.__dict__, cls=DictObjEncoder, indent=4)


def filter_nones(dictionary):
    rv = {}
    for k in dictionary:
        if dictionary[k] is not None:
            rv[k] = dictionary[k]
    return rv


def to_dicts(obj):
    if obj is None:
        return obj

    primitives = [str, int, float, bool]
    if any([isinstance(obj, t) for t in primitives]):
        return obj

    if isinstance(obj, list):
        return [to_dicts(x) for x in obj]

    if isinstance(obj, dict):
        return filter_nones({k: to_dicts(obj[k]) for k in obj})

    if isinstance(obj, map):
        return [to_dicts(x) for x in obj]

    if isinstance(obj, Enum):
        return obj.value
    return to_dicts(filter_nones(obj.__dict__))
