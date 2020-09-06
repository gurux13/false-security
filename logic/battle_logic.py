import json

from flask_sqlalchemy import SQLAlchemy

from db_models.card import Card
from db_models.roundbattle import RoundBattle
from logic.card_logic import CardLogic
from mod_game.game_state import UiBattle
from utils.conversion import map_opt


class BattleLogic:
    def __init__(self, db: SQLAlchemy, model: RoundBattle):
        self.db = db
        self.model = model

    def get_defensive_cards(self):
        if self.model.defensiveCards is None:
            return []
        return [CardLogic(self.db, card) for card in
                [self.db.session.query(Card).filter_by(id=cardId).first() for cardId in
                 json.loads(self.model.defensiveCards)]]

    def add_defensive_card(self, card: CardLogic):
        lst = []
        if self.model.defensiveCards is not None:
            lst = json.loads(self.model.defensiveCards)
        lst.append(card.model.id)
        self.model.defensiveCards = json.dumps(lst)

    def get_curdamage(self) -> int:
        if self.model.offensiveCard is None:
            return None
        if self.model.defensiveCards is None:
            return self.model.offensiveCard.damage
        total_defence_value = 0
        for defensive_card in self.get_defensive_cards():
            defence_value = defensive_card.get_defence_from(self.model.offensiveCard)
            if defence_value is not None:
                total_defence_value += defence_value
        return max(0, self.model.offensiveCard.damage - total_defence_value)

    def to_ui(self):
        return UiBattle(
            offender=self.model.offendingPlayerId,
            defender=self.model.defendingPlayerId,
            offensive_card=self.model.offensiveCardId,
            defensive_cards=None if self.model.defensiveCards is None else json.loads(self.model.defensiveCards),
            damage_remains=self.get_curdamage(),
            is_complete=self.model.isComplete,
            creation_order=self.model.creationOrder,
            round_no=self.model.round.roundNo,
        )
