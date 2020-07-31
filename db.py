from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from db_models.cardtype import CardType
from db_models.card import Card
from db_models.defence import Defence
from db_models.game import Game, Player
from db_models.gameround import GameRound
from db_models.roundbattle import RoundBattle
from db_models.deckentry import DeckEntry
from db_models.discardentry import DiscardEntry

from globals import app, db

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

