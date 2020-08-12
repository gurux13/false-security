from flask_sqlalchemy import SQLAlchemy

from db_models.roundbattle import RoundBattle
from mod_game.game_state import UiBattle
from utils.conversion import map_opt


class BattleLogic:
    def __init__(self, db:SQLAlchemy, model: RoundBattle):
        self.db = db
        self.model = model

    def to_ui(self):
        return UiBattle(
            offender=self.model.offendingPlayerId,
            defender=self.model.defendingPlayerId,
            offencive_card=self.model.offensiveCardId,
            defensive_cards=map_opt(lambda x: x.id, self.model.defensiveCards)
        )