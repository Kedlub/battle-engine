import pygame
import sys
import random
from pygame._sdl2 import Window

DESIGN_RESOLUTION = (640, 480)


# GameMode is an abstract class that represents the game state and processes necessary game actions such as 
# rendering, updating, and handling input events.
class GameMode:
    def __init__(self):
        self.game = None
        pass

    def init(self, game):
        pass

    def render(self, surface):
        pass

    def update(self, surface):
        pass

    def process_input(self, event):
        pass


class Game:
    def __init__(self, game_mode=GameMode()):
        pygame.init()
        screen_info = pygame.display.Info()
        self.native_resolution = (screen_info.current_w, screen_info.current_h)
        scaling_factor = min(self.native_resolution[0] / DESIGN_RESOLUTION[0],
                             self.native_resolution[1] / DESIGN_RESOLUTION[1])
        self.scaled_resolution = (
            int(DESIGN_RESOLUTION[0] * scaling_factor), int(DESIGN_RESOLUTION[1] * scaling_factor))
        self.screen = pygame.display.set_mode((640, 480))
        self.surface = pygame.Surface((640, 480))
        pygame.display.set_caption("battle-engine")
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.shaking_ticks = 0
        self.original_position = None
        self.game_mode = game_mode
        self.window = Window.from_display_module()
        self.running = True
        self.fullscreen = False
        self.game_mode.init(self)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
                self.toggle_fullscreen()
            self.game_mode.process_input(event)

    def update(self):
        if self.shaking_ticks > 0:
            random_position = (
                self.original_position[0] + random.randint(-5, 5),
                self.original_position[1] + random.randint(-5, 5)
            )
            self.window.position = random_position
            self.shaking_ticks -= 1
        else:
            if self.original_position is not None:
                self.window.position = self.original_position
                self.original_position = None
        self.game_mode.update(self.surface)

    def render(self):
        self.screen.fill((0, 0, 0))
        self.surface.fill((0, 0, 0))
        self.game_mode.render(self.surface)

        if self.fullscreen:
            scaled_position = ((self.native_resolution[0] - self.scaled_resolution[0]) // 2,
                               (self.native_resolution[1] - self.scaled_resolution[1]) // 2)
            scaled = pygame.transform.scale(self.surface, (self.scaled_resolution[0], self.scaled_resolution[1]))
        else:
            scaled_position = (0, 0)
            scaled = self.surface

        self.screen.blit(scaled, scaled_position)
        pygame.display.flip()

    def shake(self, ticks):
        if self.fullscreen:
            self.toggle_fullscreen()
        self.original_position = self.window.position
        self.shaking_ticks = ticks

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        else:
            self.screen = pygame.display.set_mode(self.native_resolution, pygame.FULLSCREEN)
        self.fullscreen = not self.fullscreen

    def run(self):
        while self.running:
            self.process_events()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
