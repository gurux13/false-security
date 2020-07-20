from flask_sqlalchemy import SQLAlchemy
from app import db
#import Player

class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    uniqueCode = db.Column(db.Integer, unique=True, nullable=False)
    params = db.Column(db.Text, nullable=False) 
    roundsCompleted = db.Column(db.Integer, nullable=False)
    isComplete = db.Column(db.Boolean, default=False)
    adminPlayer = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)


    def __repr__(self):
        return '<Game %r>'%self.uniqueCode

    def __init__(self, uniqueCode, params, roundsCompleted, isComplete, adminPlayer):
        self.uniqueCode = uniqueCode
        self.params = params
        self.roundsCompleted = roundsCompleted
        self.isComplete = isComplete
        self.adminPlayer = adminPlayer

class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    gameId = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False) 
    playerStateId = db.Column(db.Integer, db.ForeignKey('playerstate.id'), nullable=False)


    def __repr__(self):
        return '<Player %r>'%self.name

    def __init__(self, gameId, name, playerStateId):
        self.gameId = gameId
        self.name = name
        self.playerStateId = playerStateId



class PlayerState(db.Model):
    __tablename__ = 'playerstate'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    money = db.Column(db.Integer, nullable=False) 
    hand = db.Column(db.Text, nullable=False)
    neighbour = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)

    def __repr__(self):
        return '<PlayerState %r>'%self.money

    def __init__(self, money, hand, neighbour):
        self.money = money
        self.hand = hand
        self.neighbour = neighbour