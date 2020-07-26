from enum import Enum


class HackAttemptError(Exception):
    class ErrorType(Enum):
        GENERIC_ERROR = 0
        CSRF = 1

    def __init__(self, message, error_type=ErrorType.GENERIC_ERROR):
        self.message = message
        self.error_type = error_type

    def __str__(self):
        return "Небезопасное содержимое: " + self.message
