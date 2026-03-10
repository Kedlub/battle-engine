from battle_engine import Game
from examples.papyrus.main import PapyrusBattle

game_instance = Game()
game_instance.set_mode(PapyrusBattle())
game_instance.run()
