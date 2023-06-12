import pygame
import math

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

        y_offset = int(self.y_offset)
        step_size = math.floor((surface.get_height() - self.y_offset) / 15)
        for y in range(surface.get_height() // 2, surface.get_height(), step_size):
            color_value = int(255 * ((y - surface.get_height() // 2) / surface.get_height()))
            pygame.draw.rect(surface, (0, color_value, color_value), (0, y + y_offset, surface.get_width(), step_size))

        font = pygame.font.Font(None, 36)
        text = font.render("Hello World", True, (255, 255, 255))
        text_rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        rotated_text = pygame.transform.rotate(text, self.angle)
        rotated_rect = rotated_text.get_rect(center=text_rect.center)
        surface.blit(rotated_text, rotated_rect)
        font = pygame.font.Font(None, 24)
        step_size_text = font.render(str(step_size), True, (255, 255, 255))
        surface.blit(step_size_text, (0, 0))
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
