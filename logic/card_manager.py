from flask_sqlalchemy import SQLAlchemy

from db_models.cardtype import CardType, CardTypeEnum


class CardManager:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_type(self, typ: CardTypeEnum):
        return self.db.session.query(CardType).filter_by(enumType=typ)[0]