from flask_sqlalchemy import SQLAlchemy

from db_models.game import Player


class PlayerLogic:
    def __init__(self, db: SQLAlchemy, model: Player):
        self.db = db
        self.model = model