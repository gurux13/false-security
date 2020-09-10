from flask_sqlalchemy import SQLAlchemy

from db_models.card import Card
from typing import TYPE_CHECKING

from db_models.cardtype import CardTypeEnum
from utils.conversion import first_or_none

if TYPE_CHECKING:
    from logic.player_logic import PlayerLogic
from mod_game.game_state import UiCard, UiCardType, CardPairing


class CardLogic:
    def __init__(self, db: SQLAlchemy, model: Card, owner: 'PlayerLogic' = None):
        self.db = db
        self.model = model
        self.owner = owner

    def get_defence_from(self, offenciveCard: Card) -> int:
        if self.model.type.enumType != CardTypeEnum.DEFENCE:
            return None
        return first_or_none(
            [defence.value for defence in self.model.defensiveFrom if
             defence.offence == offenciveCard]
        )

    def to_ui(self, extended=False) -> UiCard:
        mapping = {
            CardTypeEnum.ACCIDENT: UiCardType.Accident,
            CardTypeEnum.OFFENCE: UiCardType.Offence,
            CardTypeEnum.DEFENCE: UiCardType.Defence,
        }
        card_type = mapping[self.model.type.enumType]
        return UiCard(
            id=self.model.id,
            name=self.model.name,
            text=self.model.text,
            pop_up_text=self.model.popUpText if extended else None,
            pop_up_url=self.model.popUpURL if extended else None,
            type=card_type,
            off_against=None if card_type == UiCardType.Defence else
            [CardPairing(o.defenceCardId, o.value) for o in self.model.offensiveAgainst],
            def_against=None if card_type != UiCardType.Defence else
            [CardPairing(o.offenceCardId, o.value) for o in self.model.defensiveFrom],
            dealt_by_player=None if self.owner is None else self.owner.model.id,
            damage=self.model.damage,
        )
