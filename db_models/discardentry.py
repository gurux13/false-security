from globals import db
import db_models.game
from db_models.card import Card

class DiscardEntry(db.Model):
    __tablename__ = 'discardentry'
    id = db.Column(db.Integer, primary_key=True)
    cardId = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    gameId = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    card = db.relationship('Card', lazy=False)
    game = db.relationship('Game', back_populates='discard', lazy=False)
