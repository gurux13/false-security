import json


class GameParams:
    def __init__(self, initialFalsics):
        self.initialFalsics = initialFalsics

    def to_db(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_db(str_value: str):
        as_dict = json.loads(str_value)
        return GameParams(**as_dict)
