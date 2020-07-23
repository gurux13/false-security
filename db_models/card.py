from flask_sqlalchemy import SQLAlchemy
from app import db
from db_models.cardtype import CardType

class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False) 
    imageURL = db.Column(db.Text, nullable=False)
    typeId = db.Column(db.Integer, db.ForeignKey('cardtype.id'), nullable=False)
    type = db.relationship('CardType', back_populates='cards', uselist=False, lazy=False)
    isCovid = db.Column(db.Boolean, default=False)
    damage = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Card %r>'%self.name

