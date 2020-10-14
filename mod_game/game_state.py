from enum import Enum
from typing import List

from dataclasses import dataclass


class UiCardType(Enum):
    Defence = 0
    Offence = 1
    Accident = 2


@dataclass
class CardPairing:
    other_card: int
    value: int


@dataclass
class UiPlayer:
    id: int
    name: str
    is_admin: bool
    is_online: bool
    has_left: bool
    on_offence: bool
    on_defence: bool
    neighbour_right: int
    can_attack: bool
    money: int


@dataclass
class UiCard:
    id: int
    name: str
    text: str
    type: UiCardType
    damage: int
    def_against: List[CardPairing]
    off_against: List[CardPairing]
    dealt_by_player: int
    can_play: bool = None
    pop_up_text: str = None
    pop_up_url: str = None


@dataclass
class UiBattle:
    offender: int
    defender: int
    offensive_card: int
    defensive_cards: List[int]
    damage_remains: int
    is_complete: bool
    round_no: int
    creation_order: int


# Game references other objects directly, and other objects reference each other by IDs
@dataclass
class UiGame:
    game_name: str
    players: List[UiPlayer]
    self_player: int
    hand: List[UiCard]
    current_battles: List[UiBattle]
    round_no: int
    is_complete: bool


@dataclass
class UiRound:
    round_no: int
    battles: List[UiBattle]
