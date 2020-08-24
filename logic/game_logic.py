import json
from datetime import datetime
from enum import Enum
import random
from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from Exceptions.user_error import UserError
from db_models.card import Card
from db_models.cardtype import CardTypeEnum
from db_models.deckentry import DeckEntry
from db_models.gameround import GameRound
from db_models.roundbattle import RoundBattle
from globals import socketio
from db_models.game import Game
from logic.battle_logic import BattleLogic
from logic.card_logic import CardLogic
from logic.card_manager import CardManager
from logic.gameparams import GameParams
from logic.player_logic import PlayerLogic
from logic.player_manager import PlayerManager
from logic.round_logic import RoundLogic
from utils.conversion import first_or_none, replace_none


class GameLogic:
    class State(Enum):
        UNKNOWN = 0
        WAITROOM = 1
        RUNNING = 2
        FINISHED = 3

    def __init__(self, db: SQLAlchemy, model: Game):
        self.db = db
        self.model = model
        self.params = GameParams.from_db(model.params)
        self.card_manager = CardManager(self.db)
        self.player_manager = PlayerManager(self.db)
        self.cur_round: GameRound = next(iter(self.model.rounds), None)

    def keep_alive(self):
        self.model.lastActionAt = datetime.now()

    def notify(self):
        print("Notifying everyone in room", self.model.uniqueCode)
        socketio.emit('upd', room=self.model.uniqueCode)

    def get_state(self) -> State:
        if self.model.isComplete:
            return GameLogic.State.FINISHED
        if self.model.isStarted:
            return GameLogic.State.RUNNING
        return GameLogic.State.WAITROOM

    def get_old_rounds(self, starting_from: int) -> List[RoundLogic]:
        return [RoundLogic(self.db, x) for x in
                self.db.session.query(GameRound).filter_by(game=self.model).filter(GameRound.roundNo >= starting_from)]

    def get_battles(self) -> List[BattleLogic]:
        return [BattleLogic(self.db, b) for b in self.cur_round.battles]

    def is_running(self):
        return self.model.isStarted

    def is_complete(self):
        return self.model.isComplete

    def is_waitroom(self):
        return self.get_state() == GameLogic.State.WAITROOM

    def join_player(self, player: PlayerLogic, is_admin: bool) -> None:
        if self.get_state() != GameLogic.State.WAITROOM:
            raise UserError("Невозможно присоединиться к запущенной игре")
        if is_admin:
            player.make_admin()
        self.db.session.commit()
        self.notify()

    def get_players(self):
        return [PlayerLogic(self.db, x, self) for x in self.model.players]

    def can_start(self, player: PlayerLogic):
        if self.params.only_admin_starts:
            return player.model.isAdmin
        else:
            return True

    def initialize_player(self, player):
        player.model.money = self.params.initial_falsics
        self.deal(player, self.card_manager.get_type(CardTypeEnum.DEFENCE), self.params.initial_defence_cards)
        self.deal(player, self.card_manager.get_type(CardTypeEnum.OFFENCE), self.params.initial_offence_cards)

    def make_deck(self):
        deck_size = self.params.deck_size
        if deck_size is None:
            deck_size = self.db.session.query(func.sum(Card.countInDeck).label('count')).scalar()
        all_cards = self.db.session.query(Card).all()
        all_cards_dup = []
        for card in all_cards:
            all_cards_dup.extend([card] * card.countInDeck)
        rv = []
        while len(rv) < deck_size:
            random.shuffle(all_cards_dup)
            rv.extend(all_cards_dup[:deck_size - len(rv)])
        for card in rv:
            de = DeckEntry(
                cardId=card.id,
                game=self.model,
                order=random.randint(0, 2 ** 31),
            )
            self.db.session.add(de)

    def start_battle(self, offendingPlayer: PlayerLogic):
        new_battle = RoundBattle(
            round=self.cur_round,
            offendingPlayer=None if offendingPlayer is None else offendingPlayer.model,
            isComplete=False,
        )
        self.db.session.add(new_battle)
        return new_battle

    def on_accident_played(self):
        self.cur_round.isAccidentComplete = True
        self.start_battle(self.get_players()[0])

    def calculate_battle_falsics(self, battle: BattleLogic):
        btl_model = battle.model
        if btl_model.offensiveCard.isCovid:
            transfer_amount = btl_model.defendingPlayer.money // 2
            PlayerLogic(self.db, btl_model.defendingPlayer.neighbourRight).change_money(transfer_amount)
            PlayerLogic(self.db, btl_model.defendingPlayer).change_money(-transfer_amount)
            return
        PlayerLogic(self.db, btl_model.defendingPlayer).change_money(-battle.get_curdamage())

    def complete_battle(self, battle: BattleLogic):
        btl_model = battle.model
        if btl_model.offensiveCard is None:
            raise UserError("Нельзя завершить битву без карты атаки!")
        self.calculate_battle_falsics(battle)
        btl_model.isComplete = True
        if self.cur_round.isAccidentComplete:
            next_player = btl_model.offendingPlayer.neighbourRight
            if next_player != self.get_players()[0].model:
                self.start_battle(PlayerLogic(self.db, next_player))

        if all(map(lambda b: b.model.isComplete, self.get_battles())):
            if btl_model.offensiveCard.type.enumType == CardTypeEnum.ACCIDENT:
                print("Round", self.cur_round.roundNo, "has accident completed")
                self.on_accident_played()
            else:
                print("Round", self.cur_round.roundNo, "is complete")
                self.on_round_completed()
                self.new_round()

    def play_accident(self):
        if random.random() > self.params.accident_probability:
            self.on_accident_played()
            return
        card = self.get_from_deck(self.card_manager.get_type(CardTypeEnum.ACCIDENT), 1)
        if len(card) == 0:
            self.on_accident_played()
            return
        for player in self.get_players():
            rb = self.start_battle(None)
            rb.defendingPlayer = player.model
            rb.offensiveCard = card[0].card

    def new_round(self):
        round_no = 0 if self.cur_round is None else self.cur_round.roundNo + 1
        the_round = GameRound(
            game=self.model,
            roundNo=round_no,
            isComplete=False,
            currentPlayer=None
        )
        self.db.session.add(the_round)
        self.cur_round = the_round

        for player in self.get_players():
            player.on_new_round()

        self.play_accident()

    def start(self):
        self.model.isStarted = True
        self.player_manager.seat_game_players(self)
        self.make_deck()
        for player in self.get_players():
            self.initialize_player(player)
        self.new_round()
        self.db.session.commit()
        self.notify()

    def get_from_deck(self, typ, count):
        return self.db.session.query(DeckEntry) \
                   .filter_by(game=self.model) \
                   .filter(DeckEntry.card.has(type=typ)) \
                   .order_by(DeckEntry.order)[:count]

    def deal(self, player, typ, count):
        deck_entries = self.get_from_deck(typ, count)
        player.add_cards([CardLogic(self.db, x.card) for x in deck_entries])
        for entry in deck_entries:
            self.db.session.delete(entry)

    def get_player_battle(self, player: PlayerLogic) -> RoundBattle:
        # There can be at most one btl_model the player belongs to
        return first_or_none([x for x in
                              self.cur_round.battles
                              if (x.defendingPlayer == player.model or x.offendingPlayer == player.model)
                              and not x.isComplete])

    def get_player_battlelogic(self, player: PlayerLogic) -> BattleLogic:
        # There can be at most one btl_model the player belongs to
        model = self.get_player_battle(player)
        return None if model is None else BattleLogic(self.db, model)

    def can_attack(self, me: PlayerLogic, defender: PlayerLogic):
        if me.model == defender.model:
            # Logically, the rules don't forbid attacking self... But it's nonsense, right?
            # We don't have tail loss here, but the player might want to get rid of defense cards?..
            return False
        if not self.cur_round.isAccidentComplete:
            return False
        my_battle = self.get_player_battle(me)
        if my_battle is None:
            return False
        if my_battle.offendingPlayer != me.model:
            return False
        return my_battle.defendingPlayer is None

    def attack(self, me: PlayerLogic, defender: PlayerLogic):
        if defender is None:
            raise UserError("Игрок не найден!")
        if not self.can_attack(me, defender):
            raise UserError("Сейчас нельзя атаковать этого игрока")
        cur_battle = self.get_player_battle(me)
        if cur_battle is not None:
            cur_battle.defendingPlayer = defender.model
        else:
            battle = self.start_battle(me)
            battle.defendingPlayer = defender.model

    def can_play_card(self, card: CardLogic, player: PlayerLogic) -> bool:
        my_battle = self.get_player_battle(player)
        if my_battle is None:
            return False
        if my_battle.isComplete:
            return False
        # Can't play a card we don't have
        if not any(map(lambda x: x.model == card.model, player.get_hand())):
            return False
        # If we're on offence
        if my_battle.offendingPlayer == player.model:
            # Card is already played
            if my_battle.offensiveCard is not None:
                return False
            return card.model.type.enumType == CardTypeEnum.OFFENCE

        # We're on defence then
        if card.model.type.enumType != CardTypeEnum.DEFENCE:
            return False
        cur_damage = BattleLogic(self.db, my_battle).get_curdamage()
        if cur_damage is None or cur_damage <= 0:
            # The round is either fully played, or has no offensive card yet
            return False
        return replace_none(card.get_defence_from(my_battle.offensiveCard), 0) > 0

    def play_card(self, card: CardLogic, player: PlayerLogic):
        if not self.can_play_card(card, player):
            raise UserError("Сейчас нельзя сыграть эту карту")
        battle = self.get_player_battle(player)
        if battle.offendingPlayer == player.model:
            battle.offensiveCard = card.model
        else:
            BattleLogic(self.db, battle).add_defensive_card(card)
        player.drop_card(card)

    def end_battle(self, player: PlayerLogic):
        battle = self.get_player_battle(player)
        if battle.defendingPlayer != player.model:
            raise UserError("Нельзя завершить раунд, если Вы не защищаетесь!")

        self.complete_battle(BattleLogic(self.db, battle))

    def on_round_completed(self):
        for player in self.get_players():
            player.on_round_completed()
