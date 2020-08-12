from flask_sqlalchemy import SQLAlchemy
from globals import db
from db_models.cardtype import CardType
from db_models.defence import Defence

class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=True)
    ### TODO imageURL should not be nullable at future
    imageURL = db.Column(db.Text, nullable=True)
    popUpText = db.Column(db.Text, nullable=True)
    popUpURL = db.Column(db.Text, nullable=True)
    typeId = db.Column(db.Integer, db.ForeignKey('cardtype.id'), nullable=False)
    type = db.relationship('CardType', back_populates='cards', uselist=False, lazy=False)
    isCovid = db.Column(db.Boolean, default=False)
    damage = db.Column(db.Integer, nullable=True)
    countInDeck = db.Column(db.Integer, nullable=False)

    offensiveAgainst = db.relationship('Defence', foreign_keys='Defence.offenceCardId', back_populates='offence', lazy=False)
    defensiveFrom = db.relationship('Defence', foreign_keys='Defence.defenceCardId', back_populates='defence', lazy=False)


    def __repr__(self):
        return '<Card %r>'%self.name

