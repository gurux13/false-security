from utils.json_util import to_dicts


class Response:
    @staticmethod
    def Ok(result):
        return Response(True, result)

    @staticmethod
    def Error(message):
        return Response(False, None, message)

    def __init__(self, ok, value, message=None):
        self.ok = ok
        self.value = value
        self.message = message

    def as_dicts(self):
        return to_dicts(self)
