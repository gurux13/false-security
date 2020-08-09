import json
from enum import Enum


class DictObjEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def deep_serialize(obj):
    return json.dumps(obj.__dict__, cls=DictObjEncoder, indent=4)


def to_dicts(obj):
    if obj is None:
        return obj

    primitives = [str, int, float, bool]
    if any([isinstance(obj, t) for t in primitives]):
        return obj

    if isinstance(obj, list):
        return [to_dicts(x) for x in obj]

    if isinstance(obj, dict):
        return {k: to_dicts(obj[k]) for k in obj}

    if isinstance(obj, map):
        return [to_dicts(x) for x in obj]

    if isinstance(obj, Enum):
        return obj.value
    print("Serializing", obj, "...")
    return to_dicts(obj.__dict__)
