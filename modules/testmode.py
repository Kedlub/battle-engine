import pygame

from modules.game import GameMode


class TestMode(GameMode):
    def __init__(self):
        super().__init__()
        self.angle = 0

    def init(self, game):
        self.game = game

    def render(self, surface):
        surface.fill((255, 0, 0))
        font = pygame.font.Font(None, 36)
        text = font.render("Hello World", True, (255, 255, 255))
        text_rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        rotated_text = pygame.transform.rotate(text, self.angle)
        rotated_rect = rotated_text.get_rect(center=text_rect.center)
        surface.blit(rotated_text, rotated_rect)
        pass

    def update(self, surface):
        self.angle += 1
        if self.angle > 360:
            self.game.shake(50)
            self.angle = 0
        pass

    def process_input(self, events):
        # Implement input handling in Battle mode here
        pass
