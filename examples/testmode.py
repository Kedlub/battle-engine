import pygame
import math

from battle_engine import GameMode, draw_gradient, draw_text

min_yOffset = 0.0
max_yOffset = 50.0
amplitude = (max_yOffset - min_yOffset) / 2


class TestMode(GameMode):
    def __init__(self, game):
        super().__init__(game)
        self.angle = 0
        self.y_offset = 0
        self.y_reverse = False

    def render(self, surface):
        surface.fill((0, 0, 0))

        draw_gradient(
            surface, 15, 10, (0, 255, 255), surface.get_height() / 2 - self.y_offset
        )

        draw_text(
            surface,
            "Hello World!",
            36,
            (255, 255, 255),
            surface.get_width() // 2,
            surface.get_height() // 2,
            anchor="center",
            rotation=self.angle,
        )
        pass

    def update(self, surface):
        self.angle += 2
        if self.angle > 360:
            self.game.shake(50)
            self.angle = 0

        time = pygame.time.get_ticks() / 5000
        self.y_offset = (
            min_yOffset + amplitude + amplitude * math.sin(2 * math.pi * time)
        )
        pass

    def process_input(self, events):
        pass
