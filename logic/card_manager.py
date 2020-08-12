from typing import List

from flask_sqlalchemy import SQLAlchemy

from db_models.card import Card
from db_models.cardtype import CardType, CardTypeEnum
from logic.card_logic import CardLogic


class CardManager:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_type(self, typ: CardTypeEnum):
        return self.db.session.query(CardType).filter_by(enumType=typ)[0]

    def get_card(self, card_id: int) -> CardLogic:
        return CardLogic(self.db, self.db.session.query(Card).filter_by(id=card_id)[0])

    def get_all_cards(self) -> List[CardLogic]:
        return [CardLogic(self.db, c) for c in self.db.session.query(Card)]