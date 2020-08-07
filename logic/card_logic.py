from flask_sqlalchemy import SQLAlchemy

from db_models.card import Card
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from logic.player_logic import PlayerLogic
from mod_game.game_state import UiCard, UiCardType, CardPairing


class CardLogic:
    def __init__(self, db: SQLAlchemy, model: Card, owner: 'PlayerLogic' = None):
        self.db = db
        self.model = model
        self.owner = owner

    def to_ui(self) -> UiCard:
        card_type = UiCardType.Defence if any(self.model.defensiveFrom) else (
            UiCardType.Accident if self.model.type.isAccident else UiCardType.Offence
        )
        return UiCard(
            id=self.model.id,
            name=self.model.name,
            text=self.model.text,
            type=card_type,
            off_against=None if card_type == UiCardType.Defence else
                [CardPairing(o.defensiveCardId, o.value) for o in self.model.offensiveAgainst],
            def_against=None if card_type != UiCardType.Defence else
                [CardPairing(o.offensiveCardId, o.value) for o in self.model.defensiveFrom],
            dealt_by_player=None if self.owner is None else self.owner.model.id,
        )
