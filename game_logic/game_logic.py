from enum import Enum

from flask_sqlalchemy import SQLAlchemy

from Exceptions.user_error import UserError
from db_models.game import Game
from game_logic.player_logic import PlayerLogic


class GameLogic:

    class State(Enum):
        UNKNOWN = 0
        WAITROOM = 1
        RUNNING = 2
        FINISHED = 3
    def __init__(self, db: SQLAlchemy, model: Game):
        self.db = db
        self.model = model

    def get_state(self) -> State:
        if self.model.isComplete:
            return GameLogic.State.FINISHED
        if self.model.isStarted:
            return GameLogic.State.RUNNING
        return GameLogic.State.WAITROOM
    def is_running(self):
        return self.model.isStarted
    def is_complete(self):
        return self.model.isComplete

    def join_player(self, player: PlayerLogic, is_admin: bool) -> None:
        if self.get_state() != GameLogic.State.WAITROOM:
            raise UserError("Невозможно присоединиться к запущенной игре")
        if is_admin:
            player.make_admin()
