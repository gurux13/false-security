from flask_sqlalchemy import SQLAlchemy
from globals import db
import db_models.card

class Defence(db.Model):
    __tablename__ = 'defence'
    id = db.Column(db.Integer, primary_key=True)

    defenceCardId = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    offenceCardId = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)

    defence = db.relationship("Card", back_populates='defensiveFrom', foreign_keys=[defenceCardId], uselist=False)
    offence = db.relationship("Card", back_populates='offensiveAgainst', foreign_keys=[offenceCardId], uselist=False)

    def __repr__(self):
        return '<Defence card value is %r>'%self.value
