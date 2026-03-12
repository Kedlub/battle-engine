import pygame

from .game import Game, GameMode


class Overworld(GameMode):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

    def render(self, surface: pygame.Surface) -> None:
        pass

    def update(self, surface: pygame.Surface) -> None:
        pass

    def process_input(self, event: pygame.event.Event) -> None:
        pass
