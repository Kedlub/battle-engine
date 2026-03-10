from .game import GameMode


class Overworld(GameMode):
    def __init__(self, game):
        super().__init__(game)

    def render(self, surface):
        pass

    def update(self, surface):
        pass

    def process_input(self, event):
        pass
