from flask_sqlalchemy import SQLAlchemy
from globals import db
from db_models.game import Game, Player

class GameRound(db.Model):
    __tablename__ = 'gameround'
    # TODO: Add relationships
    id = db.Column(db.Integer, primary_key=True)
    game = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    roundNo = db.Column(db.Integer, nullable=False)
    isComplete = db.Column(db.Boolean, default=False)
    currentPlayer = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    ### stage: is  played
    #stage = db.Column()


    def __repr__(self):
        return '<GameRound %r>'%self.roundNo

    def __init__(self, game, roundNo, isComplete, currentPlayer):
        self.game = game
        self.roundNo = roundNo
        self.isComplete = isComplete
        self.currentPlayer = currentPlayer