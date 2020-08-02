from flask_sqlalchemy import SQLAlchemy

from Exceptions.internal_error import InternalError
from Exceptions.user_error import UserError
from db_models.game import Game, Player
from game_logic.game_logic import GameLogic
from game_logic.gameparams import GameParams
import string
from random import random
from sqlalchemy.exc import IntegrityError

from game_logic.player_logic import PlayerLogic
from session import SessionHelper, SessionKeys
from utils.memoize import Memoize


class PlayerManager:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def create_player(self, name: str, game: GameLogic) -> PlayerLogic:
        player = Player(name=name, game=game.model, money=0, isAdmin=False)
        self.db.session.add(player)
        try:
            self.db.session.commit()
        except IntegrityError as e:
            print("Player creation problem: " + str(e))
            self.db.session.rollback()
            raise UserError("Игрок с таким именем уже существует. Пожалуйста, измените имя.",
                            UserError.ErrorType.INVALID_NAME)
        return PlayerLogic(self.db, player)

    def get_player(self, id: int) -> PlayerLogic:
        player = Player.query.filter_by(id=id).first()
        if player is None:
            return None
        return PlayerLogic(self.db, player)

    def get_my_player(self) -> PlayerLogic:
        return self.get_player(SessionHelper.get(SessionKeys.PLAYER_ID))
