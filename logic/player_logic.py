from typing import List

from flask_sqlalchemy import SQLAlchemy

from db_models.game import Player
from db_models.card import Card
import json

from logic.card_logic import CardLogic
from utils.conversion import replace_none


class PlayerLogic:
    def __init__(self, db: SQLAlchemy, model: Player, game: 'GameLogic' = None):
        self.db = db
        self.model = model
        self.game = game
        self.hand: List[int] = [] if self.model.hand is None else json.loads(self.model.hand)

    def make_admin(self):
        self.model.isAdmin = True

    def set_online(self, is_online: bool):
        self.model.isOnline = is_online

    def leave(self):
        self.model.hasLeft = True

    def is_alive(self):
        if self.model.hasLeft:
            return False
        # A player is still alive if they have no money, but they had some when round started
        return self.model.money > 0 or replace_none(self.model.moneyAfterRound, -1) > 0

    def get_hand(self) -> List[CardLogic]:
        if self.hand is None:
            return []
        cards = Card.query.filter(Card.id.in_(self.hand))
        card_dict = {}
        for card in cards:
            card_dict[card.id] = card
        return [CardLogic(self.db, card_dict[card_id]) for card_id in self.hand]

    def updated_hand(self):
        self.model.hand = json.dumps(self.hand)

    def add_cards(self, cards: List[CardLogic]):
        self.hand.extend((c.model.id for c in cards))
        self.updated_hand()

    def drop_card(self, card: CardLogic):
        self.hand.remove(card.model.id)
        self.updated_hand()

    def on_new_round(self):
        self.model.moneyAfterRound = self.model.money

    def on_round_completed(self):
        self.model.money = self.model.moneyAfterRound

    def change_money(self, delta: int):
        self.model.moneyAfterRound += delta

    def get_money(self):
        if self.model.moneyAfterRound is None:
            return self.model.money
        return self.model.moneyAfterRound
