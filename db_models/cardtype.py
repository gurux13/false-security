from flask_sqlalchemy import SQLAlchemy
from app import db

class CardType(db.Model):
    __tablename__ = 'cardtype'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    color = db.Column(db.String(128), nullable=False) 
    isAccident = db.Column(db.Boolean, default=False)
    cards = db.relationship('Card', back_populates='type', lazy=True)

    def __repr__(self):
        return '<Card Type %r>'%self.name