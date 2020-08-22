from typing import List

from flask_sqlalchemy import SQLAlchemy

from db_models.gameround import GameRound
from logic.battle_logic import BattleLogic
from mod_game.game_state import UiRound, UiBattle


class RoundLogic(object):
    def __init__(self, db:SQLAlchemy, model: GameRound):
        self.db = db
        self.model = model

    def get_battles(self)->List[BattleLogic]:
        return [BattleLogic(self.db, x) for x in self.model.battles]

    def to_ui(self) -> UiRound:
        return UiRound(
            round_no=self.model.roundNo,
            battles=[x.to_ui() for x in self.get_battles()]
        )
