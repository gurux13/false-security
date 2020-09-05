from flask_sqlalchemy import SQLAlchemy
from globals import db
import db_models.game
import db_models.card

class RoundBattle(db.Model):
    __tablename__ = 'roundbattle'
    id = db.Column(db.Integer, primary_key=True)
    roundId = db.Column(db.Integer, db.ForeignKey('gameround.id'), nullable=False)
    round = db.relationship('GameRound', back_populates="battles")
    offendingPlayerId = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    offendingPlayer = db.relationship('Player', foreign_keys=[offendingPlayerId])

    defendingPlayerId = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    defendingPlayer = db.relationship('Player', foreign_keys=[defendingPlayerId])

    offensiveCardId = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=True)
    offensiveCard = db.relationship('Card')

    defensiveCards = db.Column(db.Text, nullable=True)
    isComplete = db.Column(db.Boolean, default=False)

    creationOrder = db.Column(db.Integer, nullable=False)