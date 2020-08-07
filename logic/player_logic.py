from typing import List

from flask_sqlalchemy import SQLAlchemy

from db_models.game import Player
from db_models.card import Card
import json

from logic.card_logic import CardLogic

class PlayerLogic:
    def __init__(self, db: SQLAlchemy, model: Player, game: 'GameLogic' = None):
        self.db = db
        self.model = model
        self.game = game
        self.hand: List[int] = None if self.model.hand is None else json.loads(self.model.hand)

    def make_admin(self):
        self.model.isAdmin = True

    def set_online(self, is_online: bool):
        self.model.isOnline = is_online

    def get_hand(self) -> List[CardLogic]:
        if self.hand is None:
            return None
        return [CardLogic(self.db, c) for c in Card.query.filter(Card.id.in_(self.hand))]

