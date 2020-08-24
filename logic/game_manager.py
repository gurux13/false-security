from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from Exceptions.internal_error import InternalError
from Exceptions.user_error import UserError
from db_models.game import Game
from logic.game_logic import GameLogic
from logic.gameparams import GameParams
import string
import random
from sqlalchemy.exc import IntegrityError

from session import SessionHelper, SessionKeys


def get_random_string(length: int) -> str:
    letters = string.ascii_uppercase + string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class GameManager:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def create_game(self, params: GameParams) -> GameLogic:
        retries = 5
        while retries > 0:
            # TODO: Make sure this is cryptographically secure
            game_key = get_random_string(6)
            game = Game(uniqueCode=game_key, params=params.to_db(), roundsCompleted=0, isComplete=False,
                        lastActionAt=datetime.now())
            try:
                self.db.session.add(game)
                self.db.session.commit()
                return GameLogic(self.db, game)
            except IntegrityError as e:
                self.db.session.rollback()
                retries -= 1
                continue
        else:
            raise InternalError("Не удалось создать игру. Это странно.")

    def delete_game(self, game: GameLogic):
        try:
            self.db.session.delete(game.model)
            self.db.session.commit()
        except IntegrityError as e:
            print("Game deletion problem: " + str(e))
            self.db.session.rollback()
            # TODO: Fix "NOT NULL constraint failed: deckentry.gameId": Cascade delete?
            raise UserError("Не удалось удалить игру. По идее, вы не должны видеть эту ошибку",
                            UserError.ErrorType.INVALID_GAME_DELETION)

    def get_game(self, game_key: str, optional=False) -> GameLogic:
        game = Game.query.filter_by(uniqueCode=game_key).first()
        if game is None and not optional:
            raise UserError("К сожалению, такая игра не найдена. Проверьте уникальный код.",
                            UserError.ErrorType.INVALID_GAME)
        if game is None:
            return None
        return GameLogic(self.db, game)

    def get_my_game(self, optional=False) -> GameLogic:
        return self.get_game(SessionHelper.get(SessionKeys.GAME_KEY), optional)
