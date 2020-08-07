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
    currentPlayer = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    ### stage: is  played
    #stage = db.Column()
