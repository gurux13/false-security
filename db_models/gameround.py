from flask_sqlalchemy import SQLAlchemy
from globals import db
import db_models.game


class GameRound(db.Model):
    __tablename__ = 'gameround'
    # TODO: Add relationships
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', back_populates='rounds')
    roundNo = db.Column(db.Integer, nullable=False)
    isComplete = db.Column(db.Boolean, default=False)
    isAccidentComplete = db.Column(db.Boolean, default=False)
    currentPlayerId = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    currentPlayer = db.relationship('Player')
    battles = db.relationship('RoundBattle', back_populates="round", cascade='all,delete')
    ### stage: is  played
    #stage = db.Column()
