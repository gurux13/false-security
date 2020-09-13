from flask_sqlalchemy import SQLAlchemy

from Exceptions.internal_error import InternalError
from Exceptions.user_error import UserError
from db_models.game import Game, Player
import logic.game_logic
from logic.gameparams import GameParams
import string
from random import random
from sqlalchemy.exc import IntegrityError

from logic.player_logic import PlayerLogic
from session import SessionHelper, SessionKeys
from utils.memoize import Memoize


class PlayerManager:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def create_player(self, name: str, game: 'GameLogic') -> PlayerLogic:
        player = Player(name=name, game=game.model, money=0, isAdmin=False, isOnline=False)
        self.db.session.add(player)
        try:
            self.db.session.commit()
        except IntegrityError as e:
            print("Player creation problem: " + str(e))
            self.db.session.rollback()
            raise UserError("Игрок с таким именем уже существует. Пожалуйста, измените имя.",
                            UserError.ErrorType.INVALID_NAME)
        return PlayerLogic(self.db, player)

    def delete_player(self, player: PlayerLogic):
        try:
            if player is not None:
                self.db.session.delete(player.model)
                self.db.session.commit()
        except IntegrityError as e:
            print("Player deletion problem: " + str(e))
            self.db.session.rollback()
            raise UserError("Не удалось удалить игрока из игры. По идее, вы не должны видеть эту ошибку",
                            UserError.ErrorType.INVALID_DELITION)

    def get_player(self, id: int) -> PlayerLogic:
        player = Player.query.filter_by(id=id).first()
        if player is None:
            return None
        return PlayerLogic(self.db, player)

    def get_my_player(self) -> PlayerLogic:
        player = self.get_player(SessionHelper.get(SessionKeys.PLAYER_ID))
        if player is None or player.model.hasLeft:
            return None
        return player

    def seat_game_players(self, game: 'GameLogic'):
        all_players = game.get_players(False)
        neighbours = all_players[1:] + [all_players[0]]
        for player, neighbour in zip(all_players, neighbours):
            player.model.neighbourRight = neighbour.model
