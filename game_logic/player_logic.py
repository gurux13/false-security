from flask_sqlalchemy import SQLAlchemy

from db_models.game import Player


class PlayerLogic:
    def __init__(self, db: SQLAlchemy, model: Player):
        self.db = db
        self.model = model

    def make_admin(self):
        self.model.isAdmin = True

    def set_online(self, is_online: bool):
        self.model.isOnline = is_online
