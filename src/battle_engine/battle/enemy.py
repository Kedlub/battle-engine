from __future__ import annotations

from typing import Any

import pygame

from ..game import Game
from ..interpolation import Interpolation, InterpolationManager
from .ui import HitVisual


class Enemy:
    def __init__(
        self,
        sprite: pygame.Surface,
        name: str = "TestMon",
        position: tuple[int, int] = (0, 0),
        rotation: int = 0,
        health: int = 20,
    ) -> None:
        self.sprite = sprite
        self.position = position
        self.base_position = position
        self.rotation = rotation
        self.health = health
        self.current_health: float = health
        self.max_health = health
        self.name = name
        self.acts: list[Any] = []
        self.hit_power: float = 0
        self.shake_ticks: int = 0
        self.shake_dist: float = 0
        self.shake_speed: int = 1
        self.being_attacked: bool = False
        self.hit_visual = HitVisual(5, Game().battle.hit_visual)
        self.healthbar_ticks = 0
        rect = self.get_rect()
        self.health_bar_width = 200
        self.health_bar_height = 15
        self.health_bar_position = (
            rect.centerx - self.health_bar_width / 2,
            rect.y - self.health_bar_height - 5,
        )

    def get_rect(self) -> pygame.Rect:
        width, height = self.sprite.get_size()
        return pygame.Rect(self.position[0], self.position[1], width, height)

    def add_act(self, name: str, func: Any) -> None:
        self.acts.append({name: func})

    def update(self, surface: pygame.Surface) -> None:
        if self.being_attacked:
            if not self.hit_visual.active and not self.shake_ticks:
                power_ratio = min(self.hit_power / float(self.max_health), 1.0)
                self.shake_dist = int(power_ratio * (self.sprite.get_width() / 2))
                self.shake_speed = max(1, int(20 * power_ratio))
                self.shake_ticks = 6 * self.shake_speed
                self.health -= self.hit_power
                InterpolationManager().add_interpolation(
                    Interpolation(
                        self, "current_health", self.current_health, self.health, 1000
                    )
                )
                self.healthbar_ticks = 100
            elif self.hit_visual.active:
                self.hit_visual.update()

        if self.shake_ticks > 0:
            self.shake_ticks -= 1
            if self.shake_ticks % self.shake_speed == 0:
                sign = 1 if (self.shake_ticks / self.shake_speed) % 2 == 0 else -1
                shake_offset = sign * self.shake_dist
                self.position = (
                    self.base_position[0] + shake_offset,
                    self.base_position[1],
                )
                self.shake_dist *= 0.9
            if self.shake_ticks == 0:
                self.shake_dist = 0
                self.position = self.base_position
                self.being_attacked = False
                from .states import DefendingState

                Game().battle.gameStateStack[-1].target.hide()
                Game().battle.gameStateStack.append(DefendingState())

    def hit(self, damage: float) -> None:
        self.being_attacked = True
        self.hit_visual.activate(self.get_rect())
        self.hit_power = damage

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(pygame.transform.rotate(self.sprite, self.rotation), self.position)
        if self.hit_visual.active:
            self.hit_visual.render(surface)
        if self.healthbar_ticks > 0:
            self.healthbar_ticks -= 1
            self.draw_health_bar(surface)

    def draw_health_bar(self, surface: pygame.Surface) -> None:
        health_bar_x = self.health_bar_position[0]
        health_bar_y = self.health_bar_position[1]
        max_health_bar_color = (255, 0, 0)
        current_health_bar_color = (0, 255, 0)

        max_health_width = self.health_bar_width
        current_health_width = (
            self.current_health / self.max_health
        ) * self.health_bar_width

        pygame.draw.rect(
            surface,
            max_health_bar_color,
            (health_bar_x, health_bar_y, max_health_width, self.health_bar_height),
        )

        pygame.draw.rect(
            surface,
            current_health_bar_color,
            (health_bar_x, health_bar_y, current_health_width, self.health_bar_height),
        )
