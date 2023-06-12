import pygame
import math
from modules.util import draw_gradient, draw_text

from modules.game import GameMode

min_yOffset = 0.0
max_yOffset = 50.0
amplitude = (max_yOffset - min_yOffset) / 2


# TestMode - A derived class from GameMode that runs a specialized game loop for a testing environment#
class TestMode(GameMode):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.y_offset = 0
        self.y_reverse = False

    def init(self, game):
        self.game = game

    def render(self, surface):
        surface.fill((0, 0, 0))

        draw_gradient(surface, 15, 10, (0, 255, 255), surface.get_height() / 2 - self.y_offset)

        draw_text(surface, "Hello World!", 36, (255, 255, 255), surface.get_width() // 2, surface.get_height() // 2,
                  centered=True, rotation=self.angle)
        pass

    def update(self, surface):
        self.angle += 1
        if self.angle > 360:
            self.game.shake(50)
            self.angle = 0

        time = pygame.time.get_ticks() / 5000
        self.y_offset = min_yOffset + amplitude + amplitude * math.sin(2 * math.pi * time)
        pass

    def process_input(self, events):
        # Implement input handling in Battle mode here
        pass
