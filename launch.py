from examples.papyrus.main import PapyrusBattle

from battle_engine import Game

game_instance = Game()
game_instance.set_mode(PapyrusBattle())
game_instance.run()
