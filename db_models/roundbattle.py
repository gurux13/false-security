from flask_sqlalchemy import SQLAlchemy
from globals import db
from db_models.gameround import Player
from db_models.card import Card

class RoundBattle(db.Model):
    __tablename__ = 'roundbattle'
    # TODO: Add relationships
    id = db.Column(db.Integer, primary_key=True)
    offendingPlayer = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    defendingPlayer = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    offensiveCard = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    defensiveCards = db.Column(db.Text, nullable=False)
    isComplete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Battle round >'

    def __init__(self, offendingPlayer, defendingPlayer, offensiveCard, defensiveCards, isComplete):
        self.offendingPlayer = offendingPlayer
        self.defendingPlayer = defendingPlayer
        self.offensiveCard = offensiveCard
        self.defensiveCards = defensiveCards
        self.isComplete = isComplete