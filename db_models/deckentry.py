from globals import db
import db_models.game
from db_models.card import Card

class DeckEntry(db.Model):
    #__table_args__ = {'extend_existing': True}
    __tablename__ = 'deckentry'
    id = db.Column(db.Integer, primary_key=True)
    # TODO: Undo nullable
    cardId = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=True)
    gameId = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    card = db.relationship('Card', lazy=False)
    game = db.relationship('Game', back_populates='deck', lazy=False)
    order = db.Column(db.Integer, nullable=False)