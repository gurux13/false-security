from flask_sqlalchemy import SQLAlchemy
from app import db
from db_models.card import Card

class Defence(db.Model):
    __tablename__ = 'defence'
    id = db.Column(db.Integer, primary_key=True)
    # TODO: Add relationships
    defenceCardId = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    offenceCardId = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Defence card value is %r>'%self.value
