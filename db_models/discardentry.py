from flask_sqlalchemy import SQLAlchemy
from app import db
from db_models.gameround import Game
from db_models.card import Card

class DiscardEntry(db.Model):
    __tablename__ = 'discardentry'
    id = db.Column(db.Integer, primary_key=True)
    card = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    game = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    def __init__(self, card, game):
        self.card = card
        self.game = game
