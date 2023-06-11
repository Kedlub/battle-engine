from modules.game import GameMode


class Overworld(GameMode):
    def __init__(self):
        super().__init__()

    def init(self, game):
        self.game = game

    def render(self, screen):
        # Implement 2D topdown world rendering here
        pass

    def update(self, screen):
        pass

    def process_input(self, events):
        # Implement player movement and input handling here
        pass
