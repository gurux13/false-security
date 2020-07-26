from flask_sqlalchemy import SQLAlchemy

from db_models.game import Game
from game_logic.player_logic import PlayerLogic


class GameLogic:

    def __init__(self, db: SQLAlchemy, model: Game):
        self.db = db
        self.model = model

    def join_player(self, player: PlayerLogic, is_admin: bool) -> None:
        pass
