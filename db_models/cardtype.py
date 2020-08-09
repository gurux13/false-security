from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from globals import db

class CardTypeEnum(Enum):
    UNKNOWN = 0
    DEFENCE = 1
    OFFENCE = 2
    ACCIDENT = 3

class CardType(db.Model):
    __tablename__ = 'cardtype'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    color = db.Column(db.String(128), nullable=False) 
    enumType = db.Column(db.Enum(CardTypeEnum), nullable=False)
    cards = db.relationship('Card', back_populates='type', lazy=True)

    def __repr__(self):
        return '<Card Type %r>'%self.name