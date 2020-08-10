from enum import Enum


class UserError(Exception):
    class ErrorType(Enum):
        GENERIC_ERROR = 0,
        INVALID_NAME = 1,
        INVALID_GAME = 2,
        INVALID_DELETION = 3,
        INVALID_GAME_DELETION = 4,

    def __init__(self, message, error_type=ErrorType.GENERIC_ERROR):
        self.message = message
        self.error_type = error_type

    def __str__(self):
        return "Ошибка: " + self.message
