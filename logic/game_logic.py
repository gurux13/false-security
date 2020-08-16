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

    def notify(self):
        print("Notifying everyone in room", self.model.uniqueCode)
        socketio.emit('upd', room=self.model.uniqueCode)

    def get_state(self) -> State:
        if self.model.isComplete:
            return GameLogic.State.FINISHED
        if self.model.isStarted:
            return GameLogic.State.RUNNING
        return GameLogic.State.WAITROOM

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

    def on_accident_played(self):
        pass

    def start_battle(self, offender: PlayerLogic, defender: PlayerLogic):
        rb = RoundBattle(
            offendingPlayer=None if offender is None else offender.model,
            defendingPlayer=defender.model,
            isComplete=False,
            round=self.cur_round,
        )
        self.db.session.add(rb)
        return rb

    def play_accident(self):
        if random.random() > self.params.accident_probability:
            self.on_accident_played()
            return
        card = self.get_from_deck(self.card_manager.get_type(CardTypeEnum.ACCIDENT), 1)
        if len(card) == 0:
            self.on_accident_played()
            return
        for player in self.get_players():
            rb = self.start_battle(None, player)
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
        # There can be at most one battle the player belongs to
        return next(iter([x for x in
                          self.cur_round.battles
                          if x.defendingPlayer == player.model or x.offendingPlayer == player.model
                          ]), None)

    def get_battle_curdamage(self, battle: RoundBattle) -> int:
        if battle.offensiveCard is None:
            return None
        if battle.defensiveCards is None:
            return battle.offensiveCard.damage
        total_defence_value = 0
        for defensive_card in battle.defensiveCards:
            defence_value = CardLogic(self.db, defensive_card).get_defence_from(battle.offensiveCard)
            if defence_value is not None:
                total_defence_value += defence_value
        return max(0, battle.offensiveCard.damage - total_defence_value)

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
        if my_battle.offendingPlayer == player:
            # Card is already played
            if my_battle.offensiveCard is not None:
                return False
            return card.model.type.enumType == CardTypeEnum.OFFENCE

        # We're on defence then
        if card.model.type.enumType != CardTypeEnum.DEFENCE:
            return False
        cur_damage = self.get_battle_curdamage(my_battle)
        if cur_damage is None or cur_damage <= 0:
            # The round is either fully played, or has no offensive card yet
            return False
        return replace_none(card.get_defence_from(my_battle.offensiveCard), 0) > 0

    def can_attack(self, me: PlayerLogic, defender: PlayerLogic):

        if me == defender:
            # Logically, the rules don't forbid attacking self... But it's nonsense, right?
            # We don't have tail loss here, but the player might want to get rid of defense cards?..
            return False
        my_battle = self.get_player_battle(me)
        if my_battle is None:
            return False
        if my_battle.offendingPlayer != me.model:
            return False
        if my_battle.defendingPlayer is None:
            return self.params.can_attack_anyone or me.model.neighbourRight == defender.model
        return False

    def attack(self, me: PlayerLogic, defender: PlayerLogic):
        if not self.can_attack(me, defender):
            raise UserError("Сейчас нельзя атаковать этого игрока")

    def play_card(self, card: CardLogic, player: PlayerLogic):
        if not self.can_play_card(card, player):
            raise UserError("Сейчас нельзя сыграть эту карту")
