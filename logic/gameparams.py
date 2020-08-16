import json
import copy
from enum import Enum


class EndGameDeaths(Enum):
    NotEnabled = 0
    OneDead = 1
    AllButOneDead = 2


class GameParams:
    def __init__(self, initial_falsics, initial_defence_cards, initial_offence_cards, accident_probability,
                 end_game_deaths, deck_size, num_rounds, only_admin_starts, can_attack_anyone):
        self.initial_falsics = initial_falsics
        self.initial_defence_cards = initial_defence_cards
        self.initial_offence_cards = initial_offence_cards
        self.accident_probability = accident_probability
        self.end_game_deaths = EndGameDeaths(end_game_deaths)
        self.deck_size = deck_size
        self.num_rounds = num_rounds
        self.only_admin_starts = only_admin_starts
        self.can_attack_anyone = can_attack_anyone

    def to_db(self):
        # Hack to serialize an enum
        tmp_obj = copy.deepcopy(self)
        tmp_obj.end_game_deaths = tmp_obj.end_game_deaths.value
        return json.dumps(tmp_obj.__dict__)

    @staticmethod
    def from_db(str_value: str):
        as_dict = json.loads(str_value)
        return GameParams(**as_dict)
