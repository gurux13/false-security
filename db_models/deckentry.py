from flask_sqlalchemy import SQLAlchemy
from app import db
from db_models.gameround import Game
from db_models.card import Card

class DeckEntry(db.Model):
    #__table_args__ = {'extend_existing': True}
    __tablename__ = 'deckentry'
    id = db.Column(db.Integer, primary_key=True)
    card = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    game = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    def __init__(self, card, game, order):
        self.card = card
        self.game = game
        self.order = order