from examples.papyrus import PapyrusBattle
from modules.battle import Battle
from modules.game import Game
from modules.testmode import TestMode

game_instance = Game()
test_mode = PapyrusBattle()
game_instance.set_mode(test_mode)
game_instance.run()
