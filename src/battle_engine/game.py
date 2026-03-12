from __future__ import annotations

import os
import random
import sys
from typing import TYPE_CHECKING

import pygame
from pygame._sdl2 import Window

from .interpolation import InterpolationManager
from .singleton import Singleton

if TYPE_CHECKING:
    from .battle.core import Battle
    from .text import ProgressiveText

DESIGN_RESOLUTION = (640, 480)
FPS = 30
BORDERLESS = os.name == "nt"

os.environ["SDL_VIDEO_CENTERED"] = "1"


class GameMode:
    def __init__(self, game: Game) -> None:
        self.game = game

    def post_init(self) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass

    def update(self, surface: pygame.Surface) -> None:
        pass

    def process_input(self, event: pygame.event.Event) -> None:
        pass


class Game(metaclass=Singleton):
    def __init__(self) -> None:
        pygame.init()
        screen_info = pygame.display.Info()
        self.native_resolution: tuple[int, int] = (
            screen_info.current_w,
            screen_info.current_h,
        )
        scaling_factor = min(
            self.native_resolution[0] / DESIGN_RESOLUTION[0],
            self.native_resolution[1] / DESIGN_RESOLUTION[1],
        )
        self.scaled_resolution: tuple[int, int] = (
            int(DESIGN_RESOLUTION[0] * scaling_factor),
            int(DESIGN_RESOLUTION[1] * scaling_factor),
        )
        self.screen: pygame.Surface = pygame.display.set_mode(DESIGN_RESOLUTION)
        self.surface: pygame.Surface = pygame.Surface(DESIGN_RESOLUTION)
        pygame.display.set_caption("battle-engine")
        self.clock = pygame.time.Clock()
        self.shaking_ticks: int = 0
        self.original_position: tuple[int, int] | None = None
        self.game_mode: GameMode = GameMode(self)
        self.window = Window.from_display_module()
        self.interpolation_manager: InterpolationManager = InterpolationManager()
        self.running: bool = True
        self.fullscreen: bool = False
        self.progressive_texts: list[ProgressiveText] = []
        self.keys_pressed: list[bool] | pygame.key.ScancodeWrapper = []
        self.delta_time: int = 0

    @property
    def battle(self) -> Battle:
        from .battle.core import Battle

        assert isinstance(self.game_mode, Battle)
        return self.game_mode

    def process_events(self) -> None:
        self.keys_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
                self.toggle_fullscreen()
            self.game_mode.process_input(event)

    def update(self) -> None:
        if self.shaking_ticks > 0:
            if not self.fullscreen:
                if self.shaking_ticks <= 30:
                    factor = self.shaking_ticks / 30
                else:
                    factor = 1
                assert self.original_position is not None
                random_position = (
                    self.original_position[0]
                    + random.randint(int(-5 * factor), int(5 * factor)),
                    self.original_position[1]
                    + random.randint(int(-5 * factor), int(5 * factor)),
                )
                self.window.position = random_position
                self.shaking_ticks -= 1
        else:
            if self.original_position is not None:
                self.window.position = self.original_position
                self.original_position = None
        for text in self.progressive_texts:
            text.update()
        self.interpolation_manager.update(self.delta_time)
        self.game_mode.update(self.surface)

    def render(self) -> None:
        self.screen.fill((0, 0, 0))
        self.surface.fill((0, 0, 0))
        self.game_mode.render(self.surface)

        if self.shaking_ticks > 0 and self.fullscreen:
            if self.shaking_ticks <= 30:
                factor = self.shaking_ticks / 30
            else:
                factor = 1
            offset_x = random.randint(int(-5 * factor), int(5 * factor))
            offset_y = random.randint(int(-5 * factor), int(5 * factor))
            self.surface.scroll(dx=offset_x, dy=offset_y)
            self.shaking_ticks -= 1

        if self.fullscreen:
            scaled_position = (
                (self.native_resolution[0] - self.scaled_resolution[0]) // 2,
                (self.native_resolution[1] - self.scaled_resolution[1]) // 2,
            )
            scaled = pygame.transform.scale(
                self.surface, (self.scaled_resolution[0], self.scaled_resolution[1])
            )
        else:
            scaled_position = (0, 0)
            scaled = self.surface

        self.screen.blit(scaled, scaled_position)
        pygame.display.flip()

    def shake(self, ticks: int) -> None:
        pos = self.window.position
        assert isinstance(pos, tuple)
        self.original_position = (int(pos[0]), int(pos[1]))
        self.shaking_ticks = ticks

    def toggle_fullscreen(self) -> None:
        if self.fullscreen:
            self.screen = pygame.display.set_mode(DESIGN_RESOLUTION)
        else:
            self.screen = pygame.display.set_mode(
                self.native_resolution,
                pygame.NOFRAME if BORDERLESS else pygame.FULLSCREEN,
            )
        self.fullscreen = not self.fullscreen

    def set_mode(self, mode: GameMode) -> None:
        self.game_mode = mode
        self.game_mode.post_init()

    def run(self) -> None:
        while self.running:
            self.process_events()
            self.update()
            self.render()
            self.delta_time = self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
