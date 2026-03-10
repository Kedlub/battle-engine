from .game import GameMode


class Overworld(GameMode):
    def __init__(self):
        super().__init__()

    def init(self, game):
        self.game = game

    def render(self, screen):
        pass

    def update(self, screen):
        pass

    def process_input(self, events):
        pass
