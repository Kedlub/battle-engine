from __future__ import annotations

import pygame

from .._assets import asset_surface
from ..game import Game
from ..player import Player
from ..singleton import Singleton


class PlayerObject(pygame.sprite.Sprite, metaclass=Singleton):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        color: tuple[int, int, int] = (255, 0, 0),
    ) -> None:
        super().__init__()
        self.sprite = asset_surface("battle/soul/soul.png")
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rotation: float = 0
        self.speed: int = 5
        self.game = Game()
        self.player = Player()
        self.set_color(color)
        self.mask = pygame.mask.from_surface(self.sprite)

    def set_color(self, color: tuple[int, int, int]) -> None:
        new_surface = pygame.Surface(self.sprite.get_size())
        new_surface.fill(color)
        new_surface.set_colorkey((0, 0, 0))
        new_surface.set_alpha(self.sprite.get_alpha())
        new_surface.blit(self.sprite, (0, 0), None, pygame.BLEND_RGBA_MULT)
        self.sprite = new_surface.convert_alpha()

    def set_position(self, x: float, y: float) -> None:
        self.rect.x = int(x)
        self.rect.y = int(y)

    def set_rotation(self, angle: float) -> None:
        self.rotation = angle

    def move(self, dx: int, dy: int) -> None:
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def rotate(self, angle: float) -> None:
        self.rotation += angle

    def check_collision(self) -> None:
        battle_rect = self.game.battle.battle_box.get_internal_rect()
        self.rect.left = max(self.rect.left, battle_rect.left)
        self.rect.right = min(self.rect.right, battle_rect.right)
        self.rect.top = max(self.rect.top, battle_rect.top)
        self.rect.bottom = min(self.rect.bottom, battle_rect.bottom)

    def update(self) -> None:
        if self.player.invulnerability_time > 0:
            self.player.invulnerability_time -= self.game.delta_time
        if self.game.keys_pressed[pygame.K_UP]:
            self.move(0, -1)
        if self.game.keys_pressed[pygame.K_LEFT]:
            self.move(-1, 0)
        if self.game.keys_pressed[pygame.K_DOWN]:
            self.move(0, 1)
        if self.game.keys_pressed[pygame.K_RIGHT]:
            self.move(1, 0)
        if self.game.keys_pressed[pygame.K_q]:
            self.rotate(-5)
        if self.game.keys_pressed[pygame.K_e]:
            self.rotate(5)
        rotated = pygame.transform.rotate(self.sprite, self.rotation)
        self.mask = pygame.mask.from_surface(rotated)
        self.check_collision()

    def render(self, surface: pygame.Surface) -> None:
        if self.player.invulnerability_time > 0:
            self.sprite.set_alpha(128)
        else:
            self.sprite.set_alpha(255)
        rotated = pygame.transform.rotate(self.sprite, self.rotation)
        rotated_rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, rotated_rect)


class BattleObject:
    def __init__(
        self,
        sprite: pygame.Surface,
        position: tuple[int, int] = (0, 0),
        rotation: float = 0,
        damage: int = 1,
    ) -> None:
        self.sprite = sprite
        self.position = position
        self.rotation = rotation
        self.mask = pygame.mask.from_surface(self.sprite)
        self.damage = damage
        self.destroyed = False
        self.player_stats = Game().battle.player_stats

    def update(self) -> None:
        self.mask = pygame.mask.from_surface(
            pygame.transform.rotate(self.sprite, self.rotation)
        )
        if self.player_stats.player.invulnerability_time <= 0 and self.collides_with(
            Game().battle.player_object
        ):
            self.player_stats.player.health = max(
                0, self.player_stats.player.health - self.damage
            )
            self.player_stats.player.invulnerability_time = 1000
            Game().shake(20)

    def render(self, surface: pygame.Surface) -> None:
        pass

    def collides_with(self, other: PlayerObject) -> bool:
        offset = (other.rect.x - self.position[0], other.rect.y - self.position[1])
        return self.mask.overlap(other.mask, offset) is not None
