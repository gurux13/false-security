from flask_sqlalchemy import SQLAlchemy
from globals import db
import db_models.deckentry
import db_models.discardentry
import db_models.gameround

class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    uniqueCode = db.Column(db.String(20), unique=True, nullable=False)
    params = db.Column(db.Text, nullable=False)
    roundsCompleted = db.Column(db.Integer, nullable=False)
    isComplete = db.Column(db.Boolean, default=False)
    isStarted = db.Column(db.Boolean, default=False)
    players = db.relationship('Player', back_populates='game', cascade='all,delete', order_by='asc(Player.id)')
    deck = db.relationship('DeckEntry', back_populates='game', cascade='all,delete', lazy=True)
    discard = db.relationship('DiscardEntry', back_populates='game', cascade='all,delete', lazy=True)
    rounds = db.relationship('GameRound', back_populates='game', cascade='all,delete', order_by='desc(GameRound.roundNo)')
    lastActionAt = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Game %r>' % self.uniqueCode


class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    gameId = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', back_populates='players')
    name = db.Column(db.String(20), nullable=False)
    money = db.Column(db.Integer, nullable=False)
    moneyAfterRound = db.Column(db.Integer, nullable=True)
    hand = db.Column(db.Text, nullable=True)
    neighbourId = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    neighbourRight = db.relationship('Player', backref='neighbourLeft', remote_side='Player.id', uselist=False, post_update=True)
    isAdmin = db.Column(db.Boolean, nullable=False)
    isOnline = db.Column(db.Boolean, nullable=False)
    hasLeft = db.Column(db.Boolean, nullable=False, default=False)
    __table_args__ = (db.UniqueConstraint('name', 'gameId', name='_name_gameid_uc'),
                      )

    def __repr__(self):
        return '<Player %r>' % self.name
