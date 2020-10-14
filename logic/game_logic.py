import json
from datetime import datetime
from enum import Enum
import random
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from Exceptions.user_error import UserError
from db_models.card import Card
from db_models.cardtype import CardTypeEnum, CardType
from db_models.deckentry import DeckEntry
from db_models.gameround import GameRound
from db_models.roundbattle import RoundBattle
from globals import socketio, db
from db_models.game import Game
from logic.battle_logic import BattleLogic
from logic.card_logic import CardLogic
from logic.card_manager import CardManager
from logic.gameparams import GameParams, DefCardDeal, EndGameDeaths
from logic.player_logic import PlayerLogic
from logic.player_manager import PlayerManager
from logic.round_logic import RoundLogic
from session import SessionHelper, SessionKeys
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
        self.is_dirty_ = False

    def is_dirty(self):
        return self.is_dirty_

    def set_dirty(self):
        self.is_dirty_ = True

    def keep_alive(self):
        self.model.lastActionAt = datetime.now()

    def notify(self):
        socketio.emit('upd', room=self.model.uniqueCode)
        self.is_dirty_ = False

    def get_state(self) -> State:
        if self.model.isComplete:
            return GameLogic.State.FINISHED
        if self.model.isStarted:
            return GameLogic.State.RUNNING
        return GameLogic.State.WAITROOM

    def get_old_rounds(self, starting_from: int) -> List[RoundLogic]:
        return [RoundLogic(self.db, x) for x in
                self.db.session.query(GameRound).filter_by(game=self.model).filter(GameRound.roundNo >= starting_from)]

    def get_battles(self, includePrevRound=False) -> List[BattleLogic]:
        if self.model.isComplete:
            return []
        extra = []
        if includePrevRound:
            prev_round = self.db.session.query(GameRound).filter(GameRound.game == self.model).filter(
                GameRound.roundNo == self.cur_round.roundNo - 1).all()
            if (len(prev_round) != 0):
                extra = prev_round[0].battles
        return [BattleLogic(self.db, b) for b in extra + self.cur_round.battles]

    def is_running(self):
        return self.model.isStarted and not self.model.isComplete

    def is_complete(self):
        return self.model.isComplete

    def is_waitroom(self):
        return self.get_state() == GameLogic.State.WAITROOM

    def join_player(self, player: PlayerLogic, is_admin: bool) -> None:
        if self.get_state() != GameLogic.State.WAITROOM:
            raise UserError("Невозможно присоединиться к запущенной игре", error_type=UserError.ErrorType.INVALID_GAME)
        if is_admin:
            player.make_admin()
        self.set_dirty()

    def get_players(self, only_live):
        all_players = [PlayerLogic(self.db, x, self) for x in self.model.players]
        if only_live:
            return [p for p in all_players if p.is_alive()]
        else:
            return all_players

    def can_start(self, player: PlayerLogic):
        if self.get_state() != GameLogic.State.WAITROOM:
            return False
        if self.params.only_admin_starts:
            return player.model.isAdmin
        else:
            return True

    def initialize_player(self, player):
        player.model.money = self.params.initial_falsics
        self.deal(player, self.card_manager.get_type(CardTypeEnum.DEFENCE), self.params.initial_defence_cards)
        self.deal(player, self.card_manager.get_type(CardTypeEnum.OFFENCE), self.params.initial_offence_cards)
        self.set_dirty()

    def make_deck(self, typ: CardType = None):
        deck_size = self.params.deck_size
        all_cards = self.db.session.query(Card)
        if typ is not None:
            all_cards = all_cards.filter(Card.type == typ)
        all_cards = all_cards.all()
        all_cards_dup = []
        for card in all_cards:
            all_cards_dup.extend([card] * card.countInDeck)
        rv = []
        if deck_size is None:
            rv = all_cards_dup
        else:
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
        self.set_dirty()

    def assert_running(self):
        if self.get_state() != GameLogic.State.RUNNING:
            raise UserError("Невозможно выполнить действие, если игра не запущена")

    def start_battle(self, offendingPlayer: PlayerLogic):
        self.assert_running()
        new_battle_no = 0
        if any(self.cur_round.battles):
            new_battle_no = max(map(lambda x: x.creationOrder, self.cur_round.battles)) + 1
        new_battle = RoundBattle(
            round=self.cur_round,
            offendingPlayer=None if offendingPlayer is None else offendingPlayer.model,
            isComplete=False,
            creationOrder=new_battle_no
        )
        self.db.session.add(new_battle)
        self.set_dirty()
        if not self.params.can_attack_anyone:
            self.attack(offendingPlayer, PlayerLogic(self.db, self.get_neighbour(offendingPlayer), game=self))
        return new_battle

    def on_accident_played(self):
        self.cur_round.isAccidentComplete = True
        self.complete_game_if_needed()
        if not self.is_complete():
            self.start_battle(self.get_players(True)[0])
        self.set_dirty()

    def calculate_battle_falsics(self, battle: BattleLogic):
        btl_model = battle.model
        if btl_model.offensiveCard.isCovid:
            transfer_amount = btl_model.defendingPlayer.money // 2
            PlayerLogic(self.db, self.get_neighbour(PlayerLogic(self.db, btl_model.defendingPlayer))).change_money(transfer_amount)
            PlayerLogic(self.db, btl_model.defendingPlayer).change_money(-transfer_amount)
        else:
            PlayerLogic(self.db, btl_model.defendingPlayer).change_money(-battle.get_curdamage())

    def get_neighbour(self, player: PlayerLogic):
        next_player = player.model.neighbourRight
        alive = [x.model for x in self.get_players(True)]
        while not (next_player in alive):
            next_player = next_player.neighbourRight
        return next_player

    def complete_battle(self, battle: BattleLogic, bypass=False):
        if not bypass:
            self.assert_running()
        self.set_dirty()
        btl_model = battle.model
        if not bypass and btl_model.offensiveCard is None:
            raise UserError("Нельзя завершить битву без карты атаки!")
        if not bypass:
            self.calculate_battle_falsics(battle)
        btl_model.isComplete = True
        if self.cur_round.isAccidentComplete:
            next_player = self.get_neighbour(PlayerLogic(self.db, btl_model.offendingPlayer))
            if next_player != self.get_players(True)[0].model:
                self.start_battle(PlayerLogic(self.db, next_player))

        if all(map(lambda b: b.model.isComplete, self.get_battles())):
            if btl_model.offensiveCard is not None and btl_model.offensiveCard.type.enumType == CardTypeEnum.ACCIDENT:
                print("Round", self.cur_round.roundNo, "has accident completed")
                self.on_accident_played()
            else:
                print("Round", self.cur_round.roundNo, "is complete")
                self.on_round_completed()
                if not self.is_complete():
                    self.new_round()

    def play_accident(self):
        self.assert_running()
        self.set_dirty()
        if random.random() > self.params.accident_probability:
            self.on_accident_played()
            return
        card = self.get_from_deck(self.card_manager.get_type(CardTypeEnum.ACCIDENT), 1)
        if len(card) == 0:
            self.on_accident_played()
            return
        self.db.session.delete(card[0])
        for player in self.get_players(True):
            rb = self.start_battle(None)
            rb.defendingPlayer = player.model
            rb.offensiveCard = card[0].card

    def new_round(self):
        self.assert_running()
        self.set_dirty()
        round_no = 0 if self.cur_round is None else self.cur_round.roundNo + 1
        the_round = GameRound(
            game=self.model,
            roundNo=round_no,
            isComplete=False,
            currentPlayer=None
        )
        self.db.session.add(the_round)
        self.cur_round = the_round

        for player in self.get_players(True):
            player.on_new_round()

        self.play_accident()

    def start(self):
        self.set_dirty()
        self.model.isStarted = True
        self.player_manager.seat_game_players(self)
        self.make_deck()
        for player in self.get_players(False):
            self.initialize_player(player)
        self.new_round()

    def get_from_deck(self, typ: CardType, count: int):
        return self.db.session.query(DeckEntry) \
                   .filter_by(game=self.model) \
                   .filter(DeckEntry.card.has(type=typ)) \
                   .order_by(DeckEntry.order)[:count]

    def deal(self, player, typ, count):
        self.set_dirty()
        deck_entries = self.get_from_deck(typ, count)
        if len(deck_entries) < count and self.params.deck_size is None:
            self.make_deck(typ)
            deck_entries.extend(self.get_from_deck(typ, count - len(deck_entries)))
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
        if not self.is_running():
            return False
        if me.model == defender.model:
            # Logically, the rules don't forbid attacking self... But it's nonsense, right?
            # We don't have tail loss here, but the player might want to get rid of defense cards?..
            return False
        if not defender.is_alive():
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
        if defender.model.game != me.model.game:
            raise UserError("Игрок не найден!")
        if not self.can_attack(me, defender):
            raise UserError("Сейчас нельзя атаковать этого игрока")
        self.set_dirty()
        cur_battle = self.get_player_battle(me)
        if cur_battle is not None:
            cur_battle.defendingPlayer = defender.model
        else:
            battle = self.start_battle(me)
            battle.defendingPlayer = defender.model

    def can_play_card(self, card: CardLogic, player: PlayerLogic) -> bool:
        if not self.is_running():
            return False
        my_battle = self.get_player_battle(player)
        if my_battle is None:
            return False
        if my_battle.isComplete:
            return False
        if my_battle.defendingPlayer is None:
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
        return self.params.hardcore_mode or replace_none(card.get_defence_from(my_battle.offensiveCard), 0) > 0

    def play_card(self, card: CardLogic, player: PlayerLogic):
        if not self.can_play_card(card, player):
            raise UserError("Сейчас нельзя сыграть эту карту")
        self.set_dirty()
        battle = self.get_player_battle(player)
        if battle.offendingPlayer == player.model:
            battle.offensiveCard = card.model
        else:
            BattleLogic(self.db, battle).add_defensive_card(card)
        player.drop_card(card)

    def end_battle(self, player: PlayerLogic):
        self.assert_running()
        self.set_dirty()
        battle = self.get_player_battle(player)

        if battle is None or battle.defendingPlayer != player.model:
            raise UserError("Нельзя завершить раунд, если Вы не защищаетесь!")
        self.complete_battle(BattleLogic(self.db, battle))

    def deal_roundcompleted(self, player: PlayerLogic, avg_spend: int):
        player_off_cards_count = len([x for x in player.get_hand() if x.model.type.enumType == CardTypeEnum.OFFENCE])
        self.deal(player, self.card_manager.get_type(CardTypeEnum.OFFENCE),
                  self.params.initial_offence_cards - player_off_cards_count)

        player_def_cards_count = len([x for x in player.get_hand() if x.model.type.enumType == CardTypeEnum.DEFENCE])
        def_card_count = 0
        if self.params.def_card_deal == DefCardDeal.DealFixed:
            def_card_count = self.params.def_card_deal_size
        elif self.params.def_card_deal == DefCardDeal.KeepSize:
            def_card_count = self.params.initial_defence_cards - player_def_cards_count
        elif self.params.def_card_deal == DefCardDeal.RemainingPlusFixed:
            def_card_count = player_def_cards_count + self.params.def_card_deal_size
        elif self.params.def_card_deal == DefCardDeal.DealPlayerCount:
            def_card_count = len(self.model.players)
        elif self.params.def_card_deal == DefCardDeal.DealAverageSpend:
            def_card_count = avg_spend
        def_card_count = max(0, def_card_count)
        self.deal(player, self.card_manager.get_type(CardTypeEnum.DEFENCE), def_card_count)

    def on_round_completed(self):
        for player in self.get_players(True):
            player.on_round_completed()
        num_alive_players = len(self.get_players(True))
        if num_alive_players == 0:
            num_alive_players = 1  # doesn't matter, the game is over anyway
        avg_spend = sum(
            len([x for x in player.get_hand() if x.model.type.enumType == CardTypeEnum.DEFENCE])
            for player in self.get_players(True)
        ) / num_alive_players
        for player in self.get_players(True):
            self.deal_roundcompleted(player, avg_spend)
        self.complete_game_if_needed()

    def should_complete_game(self):
        n_players = len(self.get_players(False))
        n_live_players = len(self.get_players(True))
        if n_live_players == 0:
            return True  # Graveyard
        if self.params.end_game_deaths == EndGameDeaths.OneDead and n_players != n_live_players:
            return True
        if self.params.end_game_deaths == EndGameDeaths.AllButOneDead and n_live_players <= 1:
            return True
        if self.params.num_rounds is not None and self.cur_round is not None:
            return self.cur_round.roundNo + 1 >= self.params.num_rounds
        if self.params.deck_size is not None:
            return not any(self.model.deck)
        return False

    def complete_game_if_needed(self):
        if self.should_complete_game():
            self.set_dirty()
            self.model.isComplete = True

    def leave_player(self, player: PlayerLogic):
        player.leave()
        if self.is_running():
            player.model.neighbourLeft.neighbourRight = player.model.neighbourRight
            for battle in self.get_battles(False):
                if battle.model.offendingPlayer == player.model \
                        or battle.model.defendingPlayer == player.model \
                        and not battle.model.isComplete:
                    self.complete_battle(battle, True)
                    self.db.session.delete(battle.model)


def game2redirect(game: GameLogic, player: PlayerLogic) -> Optional[str]:
    if not (SessionHelper.has(SessionKeys.PLAYER_ID) and SessionHelper.has(SessionKeys.GAME_KEY)):
        return '/'
    if game is None:
        return '/'
    if game.get_state() == GameLogic.State.WAITROOM:
        return '/waitroom'
    if game.get_state() == GameLogic.State.RUNNING:
        return '/game'
    if game.get_state() == GameLogic.State.FINISHED:
        return '/endgame'
    if player is None or player.model.game != game.model:
        return '/'
    return None
